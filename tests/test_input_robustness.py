from __future__ import annotations
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]

class InputRobustnessTests(unittest.TestCase):
    def _run(self,payload: str):
        with tempfile.NamedTemporaryFile('w',suffix='.json',encoding='utf-8',delete=False) as f:
            f.write(payload); p=Path(f.name)
        try:
            return subprocess.run([sys.executable,str(ROOT/'staged_check.py'),'analyze',str(p)],cwd=ROOT,
                                  text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=8)
        finally:
            p.unlink(missing_ok=True)

    def test_malformed_json_rejected_without_traceback(self):
        p=self._run('{')
        self.assertNotEqual(p.returncode,0)
        self.assertNotIn('Traceback (most recent call last)',p.stdout+p.stderr)

    def test_wrong_root_type_rejected_without_traceback(self):
        p=self._run('[]')
        self.assertNotEqual(p.returncode,0)
        self.assertNotIn('Traceback (most recent call last)',p.stdout+p.stderr)

    def test_campaign_is_deterministic(self):
        from reviewer_hardening.input_robustness import run_campaign
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
            ra=run_campaign(ROOT,Path(a)); rb=run_campaign(ROOT,Path(b))
            self.assertEqual(ra,rb)
            self.assertEqual(ra['status'],'PASS')

if __name__=='__main__': unittest.main()
