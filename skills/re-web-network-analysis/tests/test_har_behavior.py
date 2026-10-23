"""Behavioral tests for HAR validation and inventory."""
import copy
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import har_analysis

VALID = {
    "log": {
        "version": "1.2",
        "creator": {"name": "test", "version": "1"},
        "entries": [
            {"startedDateTime": "2026-10-23T00:00:00Z", "time": 12,
             "request": {"method": "GET", "url": "http://127.0.0.1:8931/pan?value=-40",
                         "headers": [{"name": "Authorization", "value": "Bearer x"}],
                         "cookies": []},
             "response": {"status": 200, "headers": [], "cookies": [],
                          "content": {"size": 30, "mimeType": "text/plain"}}},
            {"startedDateTime": "2026-10-23T00:00:01Z", "time": 9,
             "request": {"method": "POST", "url": "http://127.0.0.1:8931/mix",
                         "headers": [], "cookies": []},
             "response": {"status": 404, "headers": [], "cookies": [],
                          "content": {"size": 0, "mimeType": "text/plain"}}},
        ],
    }
}


class HarBehaviorTests(unittest.TestCase):
    def test_valid_har_inventoried(self):
        result = har_analysis.analyze(copy.deepcopy(VALID))
        self.assertTrue(result["valid"])
        self.assertEqual(result["entries"], 2)
        self.assertEqual(result["methods"], {"GET": 1, "POST": 1})
        self.assertEqual(result["status_classes"], {"2xx": 1, "4xx": 1})
        self.assertEqual(result["endpoints"]["GET 127.0.0.1:8931/pan"], 1)

    def test_sensitive_header_redacted(self):
        result = har_analysis.analyze(copy.deepcopy(VALID))
        sensitive = result["sensitive_headers"]
        self.assertEqual(len(sensitive), 1)
        self.assertEqual(sensitive[0]["header"], "Authorization")
        self.assertNotIn("Bearer x", str(sensitive))

    def test_missing_cookies_rejected_strict(self):
        broken = copy.deepcopy(VALID)
        del broken["log"]["entries"][0]["request"]["cookies"]
        result = har_analysis.analyze(broken)
        self.assertFalse(result["valid"])
        self.assertTrue(any("cookies" in p for p in result["problems"]))


if __name__ == "__main__":
    unittest.main()
