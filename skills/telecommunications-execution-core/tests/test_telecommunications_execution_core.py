from __future__ import annotations
import importlib.util
from datetime import datetime, timezone, timedelta
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("telecom", ROOT/"skill.py")
mod=importlib.util.module_from_spec(spec); assert spec.loader; spec.loader.exec_module(mod)
NOW=datetime(2026,9,10,12,0,tzinfo=timezone.utc)
def mission(**kw):
    base={"mission_id":"m1","action_id":"a1","idempotency_key":"k1","source_freshness_at":NOW.isoformat(),"authorized":True,"channel":"VOICE_CALL","destination":{"value":"+18085551212","allowlisted":True}}
    base.update(kw); return base
class TelecomCoreTests(unittest.TestCase):
    def test_ready(self): self.assertEqual(mod.preflight(mission(),NOW)["status"],"READY")
    def test_stale_fails(self):
        m=mission(source_freshness_at=(NOW-timedelta(hours=2)).isoformat())
        self.assertIn("STALE_CONTEXT",mod.preflight(m,NOW)["blocking_reasons"])
    def test_authority_fails(self): self.assertIn("AUTHORIZATION_MISSING",mod.preflight(mission(authorized=False),NOW)["blocking_reasons"])
    def test_allowlist_fails(self):
        m=mission(destination={"value":"+18085551212","allowlisted":False})
        self.assertIn("DESTINATION_NOT_ALLOWLISTED",mod.preflight(m,NOW)["blocking_reasons"])
    def test_voicemail_not_ack(self):
        r={"contact_state":"VOICEMAIL","acknowledgement_state":"FORMAL","mission_state":"FAILED","transport_state":"COMPLETED","provider_run_id":"r1"}
        self.assertIn("VOICEMAIL_IS_NOT_ACKNOWLEDGEMENT",mod.verify_receipt(r)["false_success_findings"])
    def test_tracking_not_investigation(self):
        r={"tracking_numbers":["T1"],"investigation_opened":True,"mission_state":"OBJECTIVE_SATISFIED","provider_run_id":"r1"}
        self.assertIn("TRACKING_IS_NOT_INVESTIGATION",mod.verify_receipt(r)["false_success_findings"])
    def test_missing_native_receipt_requires_repair(self): self.assertEqual(mod.verify_receipt({})["verdict"],"REPAIR")
    def test_clean_native_receipt_accepts(self):
        r={"transport_state":"COMPLETED","contact_state":"HUMAN_REACHED","mission_state":"OBJECTIVE_PARTIAL","acknowledgement_state":"INFORMAL","assigned_units":["Intake"],"provider_run_id":"r1"}
        self.assertEqual(mod.verify_receipt(r)["verdict"],"ACCEPT")
if __name__=="__main__": unittest.main()
