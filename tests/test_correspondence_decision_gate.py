"""Source-state decisions are pure; no sending or provider writes in these tests."""
import importlib.util
from pathlib import Path
import unittest

MODULE = Path(__file__).resolve().parents[1] / 'skills' / 'linear-frontier-deduplicator' / 'scripts' / 'decision_gate.py'
spec = importlib.util.spec_from_file_location('decision_gate', MODULE)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


class CorrespondenceDecisionTests(unittest.TestCase):
    def invoke(self, events=None, expected='cherry@example.com', actual='cherry@example.com', authorized=False, key='case-1|custodian-1|records-request'):
        return gate.decide_correspondence(action_key=key, expected_sender=expected, authenticated_sender=actual, approved=authorized, events=events or [])

    def test_wrong_mailbox_blocks_even_with_explicit_approval(self):
        self.assertEqual(self.invoke(actual='casey@example.com', authorized=True)['decision'], 'BLOCK_WRONG_SENDER')

    def test_missing_sender_policy_blocks(self):
        self.assertEqual(self.invoke(expected='', authorized=True)['decision'], 'BLOCK_IDENTITY_UNRESOLVED')

    def test_missing_approval_yields_draft_only(self):
        self.assertEqual(self.invoke()['decision'], 'DRAFT_ONLY')

    def test_explicit_approval_of_new_action_allows_one_dispatch(self):
        self.assertEqual(self.invoke(authorized=True)['decision'], 'READY_FOR_DISPATCH')

    def test_draft_is_not_sent(self):
        self.assertEqual(self.invoke(events=[{'action_key':'case-1|custodian-1|records-request','stage':'DRAFT'}], authorized=True)['decision'], 'READY_FOR_DISPATCH')

    def test_already_sent_suppresses_repeat(self):
        self.assertEqual(self.invoke(events=[{'action_key':'case-1|custodian-1|records-request','stage':'SENT'}], authorized=True)['decision'], 'WAITING_EXTERNAL')

    def test_acknowledged_suppresses_repeat(self):
        self.assertEqual(self.invoke(events=[{'action_key':'case-1|custodian-1|records-request','stage':'ACKNOWLEDGED'}], authorized=True)['decision'], 'WAITING_EXTERNAL')

    def test_receipt_is_not_relief(self):
        o=self.invoke(events=[{'action_key':'case-1|custodian-1|records-request','stage':'ACKNOWLEDGED'}])
        self.assertFalse(o['outcome_verified'])

    def test_written_denial_goes_to_review(self):
        self.assertEqual(self.invoke(events=[{'action_key':'case-1|custodian-1|records-request','stage':'DENIED'}])['decision'], 'REVIEW_ADVERSE_DETERMINATION')

    def test_partial_production_needs_reconciliation(self):
        self.assertEqual(self.invoke(events=[{'action_key':'case-1|custodian-1|records-request','stage':'PARTIAL'}])['decision'], 'RECONCILE_PARTIAL')

    def test_full_production_requires_verification(self):
        o=self.invoke(events=[{'action_key':'case-1|custodian-1|records-request','stage':'PRODUCED'}])
        self.assertEqual(o['decision'],'VERIFY_PRODUCTION')
        self.assertFalse(o['outcome_verified'])

    def test_ambiguous_delivery_never_retries(self):
        self.assertEqual(self.invoke(events=[{'action_key':'case-1|custodian-1|records-request','stage':'AMBIGUOUS_SEND'}], authorized=True)['decision'], 'NEEDS_PROOF')

    def test_another_case_does_not_block_this_action(self):
        self.assertEqual(self.invoke(events=[{'action_key':'different-case|custodian-1|records-request','stage':'SENT'}], authorized=True)['decision'], 'READY_FOR_DISPATCH')

    def test_specific_reply_overrides_old_draft(self):
        ev=[{'action_key':'case-1|custodian-1|records-request','stage':'DRAFT', 'observed_at':'2026-10-11T00:00:00Z'}, {'action_key':'case-1|custodian-1|records-request','stage':'ACKNOWLEDGED','observed_at':'2026-10-16T00:00:00Z'}]
        self.assertEqual(self.invoke(events=ev)['decision'], 'WAITING_EXTERNAL')

    def test_missing_time_does_not_overwrite_ordered_event(self):
        ev=[{'action_key':'case-1|custodian-1|records-request','stage':'ACKNOWLEDGED','observed_at':'2026-10-16T00:00:00Z'}, {'action_key':'case-1|custodian-1|records-request','stage':'DRAFT'}]
        self.assertEqual(self.invoke(events=ev)['decision'], 'NEEDS_PROOF')

    def test_unrecognized_stage_blocks(self):
        self.assertEqual(self.invoke(events=[{'action_key':'case-1|custodian-1|records-request','stage':'HYPOTHETICAL_VICTORY'}])['decision'], 'NEEDS_PROOF')


if __name__ == '__main__':
    unittest.main()
