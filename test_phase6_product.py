import base64
import io
import json
import unittest

from marketer_app import Handler, MAX_BODY, validate_payload
from research_dashboard import dashboard_data


class InputValidationTests(unittest.TestCase):
    def test_requires_ad_content_and_text_fields(self):
        for payload in ({}, {"targeting": "age:25-34"}, {"text": ["buy now"]}, {"text": "x" * 20_001}):
            with self.subTest(payload=payload), self.assertRaises(ValueError):
                validate_payload(payload)

    def test_rejects_spoofed_and_broken_image(self):
        for data in ("data:image/png;base64," + base64.b64encode(b"not a PNG").decode(),
                     "data:image/png;base64,!!!", "data:image/gif;base64,R0lGODlh"):
            with self.subTest(data=data[:25]), self.assertRaises(ValueError):
                validate_payload({"image_data": data})

    def test_accepts_supported_signature_and_preserves_fields(self):
        encoded = base64.b64encode(b"\x89PNG\r\n\x1a\nplaceholder").decode()
        text, targeting, visual, raw, mime = validate_payload({
            "text": " Offer ", "targeting": " age:25-34 ",
            "visual_description": " arrow ", "image_data": "data:image/png;base64," + encoded,
        })
        self.assertEqual((text, targeting, visual, mime), ("Offer", "age:25-34", "arrow", "image/png"))
        self.assertTrue(raw.startswith(b"\x89PNG"))


class ResearchDataTests(unittest.TestCase):
    def test_sources_stay_separate_and_threshold_abstains(self):
        data = dashboard_data()
        self.assertEqual(data["threshold"]["status"], "insufficient_evidence")
        self.assertIsNone(data["threshold"]["recommended_level"])
        self.assertEqual(len(data["threshold"]["levels"]), 5)
        self.assertEqual(data["intrusiveness"]["romano_han"]["respondents"], 837)
        self.assertEqual(data["intrusiveness"]["independent_web_ads"]["respondents"], 1511)
        self.assertEqual(data["privacy_trust"]["vietnam"]["respondents"], 467)


class HttpSmokeTests(unittest.TestCase):
    def request(self, method, path, body=None, headers=None):
        handler = Handler.__new__(Handler)
        handler.path = path
        content = body.encode("utf-8") if isinstance(body, str) else body or b""
        handler.headers = {"Content-Length": str(len(content)), **(headers or {})}
        handler.rfile = io.BytesIO(content)
        captured = {}
        handler.send_bytes = lambda status, data, mime: captured.update(status=status, body=data, mime=mime)
        getattr(handler, "do_" + method)()
        return captured["status"], captured["body"]

    def test_research_route_serves_aggregate_results(self):
        status, body = self.request("GET", "/api/research")
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(body)["threshold"]["status"], "insufficient_evidence")
        page_status, page = self.request("GET", "/research")
        self.assertEqual(page_status, 200)
        self.assertIn(b"research.js", page)

    def test_text_response_schema_and_bad_requests(self):
        headers = {"Content-Type": "application/json"}
        status, body = self.request("POST", "/api/analyze", json.dumps({"text": "Discover our new collection."}), headers)
        self.assertEqual(status, 200)
        data = json.loads(body)
        self.assertEqual(data["threshold_decision"]["status"], "insufficient_evidence")
        self.assertTrue({"tier", "score", "score_out_of_10", "privacy_score", "pressure_score",
                         "evidence", "recommendations", "reason", "input_text", "image",
                         "ocr_text", "visual_description", "targeting", "threshold_decision",
                         "model_version"}.issubset(data))
        for bad in ("{}", "not-json", json.dumps({"text": 123})):
            status, body = self.request("POST", "/api/analyze", bad, headers)
            self.assertEqual(status, 400)
            self.assertIn("error", json.loads(body))

    def test_content_type_and_oversized_body(self):
        status, _ = self.request("POST", "/api/analyze", '{"text":"Hi"}', {"Content-Type": "text/plain"})
        self.assertEqual(status, 400)
        status, body = self.request("POST", "/api/analyze", b"{}", {
            "Content-Type": "application/json", "Content-Length": str(MAX_BODY + 1),
        })
        self.assertEqual(status, 413)
        self.assertIn("too large", json.loads(body)["error"])


if __name__ == "__main__":
    unittest.main()
