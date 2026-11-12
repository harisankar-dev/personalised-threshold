"""Local browser interface for the 49C ad intrusion-risk screen.

Run: python marketer_app.py
Test without opening a browser: python marketer_app.py --no-browser --port 8765
"""
from __future__ import annotations

import argparse
import base64
import binascii
import json
import os
import tempfile
import threading
import webbrowser
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from intrusive_ad_model import predict
from phase8_compatibility import assess as assess_compatibility
from research_dashboard import dashboard_data
from synthetic_simulation import evaluate as simulate, MODEL as SIMULATION_MODEL
from stp_advisory import evaluate as evaluate_strategy, survey_personas


ROOT = Path(__file__).resolve().parent
ASSETS = {
    "/simulation": (ROOT / "web" / "simulation.html", "text/html; charset=utf-8"),
    "/simulation.js": (ROOT / "web" / "simulation.js", "text/javascript; charset=utf-8"),
    "/": (ROOT / "web" / "index.html", "text/html; charset=utf-8"),
    "/app.css": (ROOT / "web" / "app.css", "text/css; charset=utf-8"),
    "/app.js": (ROOT / "web" / "app.js", "text/javascript; charset=utf-8"),
    "/research": (ROOT / "web" / "research.html", "text/html; charset=utf-8"),
    "/research.js": (ROOT / "web" / "research.js", "text/javascript; charset=utf-8"),
}
MIME_EXT = {"image/png": ".png", "image/jpeg": ".jpg", "image/webp": ".webp",
            "image/bmp": ".bmp", "image/tiff": ".tiff"}
MAX_BODY = 14 * 1024 * 1024
MAX_IMAGE = 10 * 1024 * 1024
FIELD_LIMITS = {"text": 20_000, "targeting": 5_000, "visual_description": 5_000}


def image_matches_type(raw: bytes, mime: str) -> bool:
    return {
        "image/png": lambda: raw.startswith(b"\x89PNG\r\n\x1a\n"),
        "image/jpeg": lambda: raw.startswith(b"\xff\xd8\xff"),
        "image/webp": lambda: raw.startswith(b"RIFF") and raw[8:12] == b"WEBP",
        "image/bmp": lambda: raw.startswith(b"BM"),
        "image/tiff": lambda: raw.startswith((b"II*\x00", b"MM\x00*")),
    }[mime]()


def validate_payload(payload: object) -> tuple[str, str, str, bytes | None, str | None]:
    """Reject malformed input before passing ad content to OCR or the rubric."""
    if not isinstance(payload, dict):
        raise ValueError("Send an ad as a JSON object.")
    fields = {}
    for key, limit in FIELD_LIMITS.items():
        value = payload.get(key, "")
        if not isinstance(value, str):
            raise ValueError(f"{key.replace('_', ' ').capitalize()} must be text.")
        if len(value) > limit:
            raise ValueError(f"{key.replace('_', ' ').capitalize()} is too long (maximum {limit:,} characters).")
        fields[key] = value.strip()
    image_data = payload.get("image_data")
    raw = None
    mime = None
    if image_data is not None:
        if not isinstance(image_data, str):
            raise ValueError("Image data must be a supported image file.")
        head, sep, encoded = image_data.partition(",")
        mime = head.removeprefix("data:").split(";", 1)[0]
        if not sep or head != f"data:{mime};base64" or mime not in MIME_EXT:
            raise ValueError("Use a PNG, JPEG, WebP, BMP, or TIFF image.")
        try:
            raw = base64.b64decode(encoded, validate=True)
        except binascii.Error as exc:
            raise ValueError("The image file could not be decoded.") from exc
        if not raw or len(raw) > MAX_IMAGE:
            raise ValueError("Choose a non-empty image under 10 MB.")
        if not image_matches_type(raw, mime):
            raise ValueError("The image content does not match its file type.")
    if not fields["text"] and raw is None and not fields["visual_description"]:
        raise ValueError("Add ad copy, an image, or a visual description to analyze.")
    return fields["text"], fields["targeting"], fields["visual_description"], raw, mime


class Handler(BaseHTTPRequestHandler):
    def send_bytes(self, status: int, content: bytes, mime: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", mime)
        self.send_header("Content-Length", str(len(content)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy", "default-src 'self'; img-src 'self' data: blob:; style-src 'self'; script-src 'self'")
        self.end_headers()
        self.wfile.write(content)

    def send_json(self, status: int, value: dict) -> None:
        self.send_bytes(status, json.dumps(value, ensure_ascii=False).encode("utf-8"), "application/json; charset=utf-8")

    def do_GET(self) -> None:
        route = self.path.split("?", 1)[0]
        if route == "/api/config":
            self.send_json(HTTPStatus.OK, {"hosted_ocr": bool(os.environ.get("VERCEL"))})
            return
        if route == "/api/simulation":
            self.send_json(HTTPStatus.OK, {"segments": SIMULATION_MODEL["segments"], "metrics": SIMULATION_MODEL["metrics"], "real_profiles": json.loads((ROOT / "results/phase7_segmentation_v1.json").read_text(encoding="utf-8"))})
            return
        if route == "/api/research":
            try:
                self.send_json(HTTPStatus.OK, dashboard_data())
            except (OSError, ValueError, KeyError, TypeError):
                self.send_json(HTTPStatus.SERVICE_UNAVAILABLE, {"error": "Research results are unavailable. Check the saved result files."})
            return
        if route not in ASSETS:
            self.send_json(HTTPStatus.NOT_FOUND, {"error": "Page not found"})
            return
        path, mime = ASSETS[route]
        self.send_bytes(HTTPStatus.OK, path.read_bytes(), mime)

    def do_POST(self) -> None:
        if self.path not in ("/api/analyze", "/api/simulation"):
            self.send_json(HTTPStatus.NOT_FOUND, {"error": "Endpoint not found"})
            return
        try:
            if self.headers.get("Content-Type", "").split(";", 1)[0].strip().lower() != "application/json":
                raise ValueError("Send JSON with Content-Type: application/json.")
            try:
                length = int(self.headers.get("Content-Length", "0"))
            except ValueError as exc:
                raise ValueError("A valid Content-Length header is required.") from exc
            if length <= 0:
                raise ValueError("The request body is empty.")
            if length > MAX_BODY:
                self.send_json(HTTPStatus.REQUEST_ENTITY_TOO_LARGE, {"error": "The request is too large. Choose an image under 10 MB."})
                return
            payload = json.loads(self.rfile.read(length))
            if self.path == "/api/simulation":
                self.send_json(HTTPStatus.OK, simulate(payload))
                return
            text, targeting, visual, raw, mime = validate_payload(payload)
            if "corrected_ocr_text" in payload:
                corrected = payload["corrected_ocr_text"]
                original = payload.get("original_ocr_text", "")
                if not isinstance(corrected,str) or not corrected.strip() or len(corrected)>20000 or not isinstance(original,str) or len(original)>20000:
                    raise ValueError("Corrected OCR must be non-empty text under 20,000 characters.")
                text, raw = corrected.strip(), None
            if raw is not None and os.environ.get("VERCEL"):
                raise ValueError("Use /api/ocr for hosted image extraction, then analyze the reviewed text.")
            if raw is not None:
                with tempfile.TemporaryDirectory(prefix="49c-ad-", dir=ROOT) as tmp:
                    path = Path(tmp) / ("ad" + MIME_EXT[mime])
                    path.write_bytes(raw)
                    result = predict(text=text, image=path, targeting=targeting, visual_description=visual)
                    result["image"] = None  # never return a temporary server path
            else:
                result = predict(text=text, targeting=targeting, visual_description=visual)
            if "corrected_ocr_text" in payload:
                result["corrected_ocr_text"] = text
                result["original_ocr_text"] = original
                result["analysis_text_source"] = "manual_ocr_correction"
            if "campaign" in payload:
                result["strategy"] = evaluate_strategy(payload["campaign"], result)
                result["strategy"]["survey_personas"] = survey_personas()
                result["compatibility"] = assess_compatibility(payload["campaign"], result, result["strategy"])
            self.send_json(HTTPStatus.OK, result)
        except (ValueError, json.JSONDecodeError) as exc:
            self.send_json(HTTPStatus.BAD_REQUEST, {"error": str(exc)})
        except RuntimeError:
            self.send_json(HTTPStatus.UNPROCESSABLE_ENTITY, {"error": "Could not read this image. Try a clearer image or paste its ad copy."})
        except Exception:
            self.send_json(HTTPStatus.INTERNAL_SERVER_ERROR, {"error": "Analysis failed. Check the input and try again."})

    def log_message(self, _format: str, *_args: object) -> None:
        pass


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--no-browser", action="store_true")
    args = parser.parse_args()
    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    url = f"http://127.0.0.1:{server.server_port}/"
    print(f"49C ad screen running at {url}", flush=True)
    if not args.no_browser:
        threading.Timer(0.5, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
