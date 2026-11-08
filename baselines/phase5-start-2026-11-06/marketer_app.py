"""Local browser interface for the 49C ad intrusion-risk screen.

Run: python marketer_app.py
Test without opening a browser: python marketer_app.py --no-browser --port 8765
"""
from __future__ import annotations

import argparse
import base64
import json
import tempfile
import threading
import webbrowser
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from intrusive_ad_model import predict


ROOT = Path(__file__).resolve().parent
ASSETS = {
    "/": (ROOT / "web" / "index.html", "text/html; charset=utf-8"),
    "/app.css": (ROOT / "web" / "app.css", "text/css; charset=utf-8"),
    "/app.js": (ROOT / "web" / "app.js", "text/javascript; charset=utf-8"),
}
MIME_EXT = {"image/png": ".png", "image/jpeg": ".jpg", "image/webp": ".webp",
            "image/bmp": ".bmp", "image/tiff": ".tiff"}
MAX_BODY = 14 * 1024 * 1024


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
        if route not in ASSETS:
            self.send_json(HTTPStatus.NOT_FOUND, {"error": "Page not found"})
            return
        path, mime = ASSETS[route]
        self.send_bytes(HTTPStatus.OK, path.read_bytes(), mime)

    def do_POST(self) -> None:
        if self.path != "/api/analyze":
            self.send_json(HTTPStatus.NOT_FOUND, {"error": "Endpoint not found"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length <= 0 or length > MAX_BODY:
                raise ValueError("The image is too large. Choose a file under 10 MB.")
            payload = json.loads(self.rfile.read(length))
            text = str(payload.get("text") or "")[:20_000]
            targeting = str(payload.get("targeting") or "")[:5_000]
            visual = str(payload.get("visual_description") or "")[:5_000]
            image_data = payload.get("image_data")
            if image_data:
                head, sep, encoded = image_data.partition(",")
                mime = head.removeprefix("data:").split(";", 1)[0]
                if not sep or mime not in MIME_EXT:
                    raise ValueError("Use a PNG, JPEG, WebP, BMP, or TIFF image.")
                raw = base64.b64decode(encoded, validate=True)
                if len(raw) > 10 * 1024 * 1024:
                    raise ValueError("The image is too large. Choose a file under 10 MB.")
                with tempfile.TemporaryDirectory(prefix="49c-ad-", dir=ROOT) as tmp:
                    path = Path(tmp) / ("ad" + MIME_EXT[mime])
                    path.write_bytes(raw)
                    result = predict(text=text, image=path, targeting=targeting, visual_description=visual)
                    result["image"] = None  # never return a temporary server path
            else:
                result = predict(text=text, targeting=targeting, visual_description=visual)
            self.send_json(HTTPStatus.OK, result)
        except (ValueError, json.JSONDecodeError) as exc:
            self.send_json(HTTPStatus.BAD_REQUEST, {"error": str(exc)})
        except Exception as exc:
            self.send_json(HTTPStatus.INTERNAL_SERVER_ERROR, {"error": f"Analysis failed: {exc}"})

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
