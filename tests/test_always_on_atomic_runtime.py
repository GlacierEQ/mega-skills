#!/usr/bin/env python3
import subprocess, sys, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SKILLS=["capability-admission","resource-preflight","claim-calibration"]
class AlwaysOnAtomicRuntimeTests(unittest.TestCase):
    def test_all_three_behavior_suites(self):
        for skill in SKILLS:
            path=ROOT/"skills"/skill/"tests"/("test_"+skill.replace("-","_")+".py")
            with self.subTest(skill=skill):
                result=subprocess.run([sys.executable,str(path),"-v"],cwd=ROOT,text=True,capture_output=True,check=False)
                self.assertEqual(result.returncode,0,result.stdout+result.stderr)
if __name__=="__main__": unittest.main()
