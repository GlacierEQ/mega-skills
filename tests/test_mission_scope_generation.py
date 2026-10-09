import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import faraway_party_candidate_swarm as swarm


class MissionScopeGenerationTests(unittest.TestCase):
    def test_generator_repairs_and_resumes_without_losing_original_scope(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skill = root / 'mission-test'
            skill.mkdir()
            original = '# Mission\n\nRecover existing system before rebuilding. Preserve all independent lanes.'
            path = skill / 'SKILL.md'
            path.write_text('---\nname: mission-test\ndescription: "Complete a cumulative mission."\n---\n\n' + original + '\n')
            record = {'id': 'mission-test', 'state': 'contract_incomplete',
                'description': 'Complete a cumulative mission.',
                'package': {'scripts': [], 'tests': [], 'references': [], 'assets': []}}
            old = swarm.SKILLS
            swarm.SKILLS = root
            try:
                self.assertTrue(swarm.repair_contract(record))
                first = path.read_text()
                self.assertIn(original, first)
                self.assertNotIn('Execute the narrowest complete workflow', first)
                self.assertIn('completion requires the requested outcome', first)
                self.assertFalse(swarm.repair_contract(record))
                self.assertEqual(first, path.read_text())
            finally:
                swarm.SKILLS = old


if __name__ == '__main__':
    unittest.main()
