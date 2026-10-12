"""Offline behavioral tests of shared GitHub request semantics; not live auth proof."""
import importlib.util
import unittest
from pathlib import Path
from unittest.mock import patch

FILE = Path(__file__).resolve().parents[1] / "bin" / "gh_common.py"
spec = importlib.util.spec_from_file_location("gh_common_tested", FILE)
github = importlib.util.module_from_spec(spec)
spec.loader.exec_module(github)

class GithubBehavior(unittest.TestCase):
    def test_unauthenticated_request_fails_closed(self):
        with patch.object(github, "get_key", return_value=""):
            result=github.rest_request("GET","/user",no_retry=True)
        self.assertEqual(result["status"],0)
        self.assertIn("no GitHub auth",result["body"]["error"])
    def test_authenticated_get_uses_expected_api(self):
        recorded=[]
        def fake_send(req,timeout):
            recorded.append((req.full_url,req.get_method(),timeout))
            return {"status":200,"body":{"login":"fixture"},"headers":{}}
        with patch.object(github,"get_key",return_value="test-token"),patch.object(github,"_send",side_effect=fake_send):
            result=github.rest_request("GET","/user",no_retry=True)
        self.assertEqual(result["status"],200)
        self.assertEqual(result["body"]["login"],"fixture")
        self.assertEqual(recorded[0][0],"https://api.github.com/user")

if __name__=="__main__": unittest.main()
