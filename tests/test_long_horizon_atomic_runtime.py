#!/usr/bin/env python3
import subprocess
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SKILLS=["mission-contract","roadmap-builder","evidence-register","context-capsule","work-packet","quality-gate","handoff-record"]
class LongHorizonAtomicRuntimeTests(unittest.TestCase):
    def test_all_seven_behavior_suites(self):
        for skill in SKILLS:
            path=ROOT/"skills"/skill/"tests"/("test_"+skill.replace("-","_")+".py")
            with self.subTest(skill=skill):
                result=subprocess.run([sys.executable,str(path),"-v"],cwd=ROOT,text=True,capture_output=True,check=False)
                self.assertEqual(result.returncode,0,result.stdout+result.stderr)
if __name__=="__main__":
    unittest.main()
