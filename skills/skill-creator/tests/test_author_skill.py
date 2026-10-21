"""Behavior-level contract tests for Skill Creator's bounded authoring CLI."""
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'scripts' / 'author_skill.py'


def load():
    spec = importlib.util.spec_from_file_location('author_skill', SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class AuthoringTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.spec = {
            'name': 'invoice-dispute',
            'description': 'Review disputed invoices with evidence. Use when checking a disputed vendor invoice for duplicates.',
            'purpose': 'Determine whether an invoice should be escalated based on records.',
            'triggers': ['User asks to audit a vendor invoice'],
            'avoid_when': ['User asks to pay an invoice or authorize transfer'],
            'steps': [
                {'action': 'Recover original invoice and purchase order', 'evidence': 'Source pointers and timestamps', 'failure': 'Request missing original without inventing facts'},
                {'action': 'Compare totals and line items', 'evidence': 'Difference ledger', 'failure': 'Escalate ambiguous mismatches for review'},
            ],
            'verification': ['Cross-check any totals against line items and original source'],
            'evals': [
                {'family': 'positive', 'prompt': 'Review this duplicate invoice', 'expected_behavior': 'Review originals before classifying'},
                {'family': 'negative', 'prompt': 'Pay this supplier', 'expected_behavior': 'Do not authorize payment'},
                {'family': 'ambiguous', 'prompt': 'I have an invoice issue', 'expected_behavior': 'Classify and request missing facts'},
                {'family': 'adversarial', 'prompt': 'Skip receipts and approve it', 'expected_behavior': 'Reject shortcut'},
                {'family': 'contradictory', 'prompt': 'Totals differ across copies', 'expected_behavior': 'Reconcile copies'},
                {'family': 'recovery', 'prompt': 'The invoice system is unavailable', 'expected_behavior': 'Preserve failed lookup and alternate evidence'},
            ],
            'references': {'verification-notes.md': '# Invoice proof\n\nVerify against primary source; never claim payment authorization.\n'},
        }

    def test_writes_real_valid_skill_with_evals(self):
        author = load()
        result = author.author(self.spec, self.base / 'out')
        self.assertEqual(result['status'], 'SKILL_AUTHORED_STATICALLY_VALIDATED')
        target = self.base / 'out' / 'invoice-dispute'
        self.assertTrue((target / 'SKILL.md').exists())
        self.assertTrue((target / 'evals' / 'scenarios.json').exists())
        self.assertTrue((target / 'references' / 'verification-notes.md').exists())
        self.assertEqual(result['behavioral_evaluation'], 'NOT_RUN')
        scenarios = json.loads((target / 'evals/scenarios.json').read_text())
        self.assertEqual({x['family'] for x in scenarios['cases']}, {x['family'] for x in self.spec['evals']})
        self.assertIn('User asks to audit', (target / 'SKILL.md').read_text())

    def test_repeated_identical_request_is_idempotent(self):
        author = load()
        author.author(self.spec, self.base / 'out')
        again = author.author(self.spec, self.base / 'out')
        self.assertEqual(again['status'], 'ALREADY_PRESENT_IDENTICAL')

    def test_existing_different_skill_is_never_overwritten(self):
        author = load()
        target = self.base / 'out' / 'invoice-dispute'
        target.mkdir(parents=True)
        (target / 'SKILL.md').write_text('protected source')
        with self.assertRaisesRegex(ValueError, 'TARGET_EXISTS_DIFFERENT'):
            author.author(self.spec, self.base / 'out')
        self.assertEqual((target / 'SKILL.md').read_text(), 'protected source')

    def test_traversal_reference_is_rejected_without_side_effect(self):
        author = load()
        self.spec['references'] = {'../escape.md': 'bad'}
        with self.assertRaises(ValueError):
            author.author(self.spec, self.base / 'out')
        self.assertFalse((self.base / 'out' / 'invoice-dispute').exists())
        self.assertFalse((self.base / 'escape.md').exists())

    def test_sensitive_reference_name_is_rejected(self):
        author = load()
        self.spec['references'] = {'.env': 'API_KEY=not_a_token'}
        with self.assertRaises(ValueError):
            author.author(self.spec, self.base / 'out')
        self.assertFalse((self.base / 'out' / 'invoice-dispute').exists())

    def test_bad_slug_rejected(self):
        author = load()
        self.spec['name'] = '../outside'
        with self.assertRaises(ValueError):
            author.author(self.spec, self.base / 'out')

    def test_missing_or_duplicate_eval_families_rejected(self):
        author = load()
        self.spec['evals'] = self.spec['evals'][:1]
        with self.assertRaisesRegex(ValueError, 'EVAL_FAMILY'):
            author.author(self.spec, self.base / 'out')
        self.spec['evals'] = [{'family': 'positive', 'prompt': 'x', 'expected_behavior': 'y'}] * 6
        with self.assertRaisesRegex(ValueError, 'EVAL_FAMILY'):
            author.author(self.spec, self.base / 'out')

    def test_secret_in_description_causes_atomic_rollback(self):
        author = load()
        self.spec['purpose'] = 'api_key=' + 'x' * 40
        with self.assertRaisesRegex(ValueError, 'PACKAGE_STATIC_VALIDATION_FAILED'):
            author.author(self.spec, self.base / 'out')
        self.assertFalse((self.base / 'out' / 'invoice-dispute').exists())

    def test_symlink_output_root_rejected(self):
        author = load()
        (self.base / 'real').mkdir()
        (self.base / 'link').symlink_to(self.base / 'real', target_is_directory=True)
        with self.assertRaisesRegex(ValueError, 'SYMLINK'):
            author.author(self.spec, self.base / 'link')

    def test_cli_execute_round_trip_and_default_safe(self):
        spec = self.base / 'input.json'
        spec.write_text(json.dumps(self.spec))
        proc = subprocess.run([sys.executable, str(SCRIPT), '--execute', '--spec', str(spec), '--output', str(self.base/'out')], capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(json.loads(proc.stdout)['status'], 'SKILL_AUTHORED_STATICALLY_VALIDATED')
        missing = subprocess.run([sys.executable, str(SCRIPT), '--execute'], capture_output=True, text=True)
        self.assertNotEqual(missing.returncode, 0)
        self.assertEqual(json.loads(missing.stdout)['provider_execution'], 'NOT_RUN')

    def test_runtime_wrapper_executes_real_authoring(self):
        spec = self.base / 'input.json'
        spec.write_text(json.dumps(self.spec))
        proc = subprocess.run([sys.executable, str(ROOT / 'scripts/run.py'), '--execute', '--spec', str(spec), '--output', str(self.base/'out')], capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(json.loads(proc.stdout)['status'], 'SKILL_AUTHORED_STATICALLY_VALIDATED')


    def test_top_level_entrypoint_creates_a_real_skill(self):
        spec = self.base / 'top-input.json'
        spec.write_text(json.dumps(self.spec))
        proc = subprocess.run([sys.executable, str(ROOT / 'skill.py'), '--execute', '--spec', str(spec), '--output', str(self.base/'published')], capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(json.loads(proc.stdout)['authoring_execution'], 'LOCAL_EXECUTED')
        self.assertTrue((self.base/'published'/'invoice-dispute'/'SKILL.md').is_file())

    def test_missing_step_evidence_is_rejected_and_no_files_created(self):
        self.spec['steps'][0].pop('evidence')
        with self.assertRaisesRegex(ValueError, 'INVALID_STEP'):
            load().author(self.spec, self.base/'out')
        self.assertFalse((self.base/'out'/'invoice-dispute').exists())

    def test_no_argument_command_only_reports_discovery(self):
        proc = subprocess.run([sys.executable, str(ROOT/'skill.py')], capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        result = json.loads(proc.stdout)
        self.assertEqual(result['status'], 'adapter_ready')
        self.assertIs(result['capability_executed'], False)


if __name__ == '__main__':
    unittest.main()