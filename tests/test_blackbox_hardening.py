import json,os,subprocess,sys,tempfile,unittest,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CLI=ROOT/'staged_check.py'
CASES=sorted((ROOT/'staged_cases').glob('*.json'))

def run(*args,seed='0',timeout=60):
 return subprocess.run([sys.executable,str(CLI),*map(str,args)],cwd=ROOT,text=True,capture_output=True,timeout=timeout,env={**os.environ,'PYTHONHASHSEED':seed})

class BlackBoxHardeningTests(unittest.TestCase):
 def test_named_cases_exist(self):self.assertGreater(len(CASES),0)
 def test_named_cases_analyze_under_three_hash_seeds(self):
  for c in CASES:
   runs=[run('analyze',c,seed=s) for s in ('0','1','999')]
   self.assertTrue(all(x.returncode==0 for x in runs),c)
   self.assertEqual(runs[0].stdout,runs[1].stdout,c);self.assertEqual(runs[0].stdout,runs[2].stdout,c)
 def test_invalid_json_is_rejected(self):
  with tempfile.TemporaryDirectory() as td:
   p=Path(td)/'bad.json';p.write_text('{');r=run('analyze',p);self.assertNotEqual(r.returncode,0)
 def test_empty_object_is_rejected(self):
  with tempfile.TemporaryDirectory() as td:
   p=Path(td)/'bad.json';p.write_text('{}');r=run('analyze',p);self.assertNotEqual(r.returncode,0)
 def test_unknown_command_is_rejected(self):self.assertNotEqual(run('not-a-command').returncode,0)
 def test_all_repository_json_is_parseable(self):
  bad=[]
  for p in ROOT.rglob('*.json'):
   try:json.loads(p.read_text())
   except Exception as e:bad.append((str(p.relative_to(ROOT)),repr(e)))
  self.assertEqual(bad,[])
 def test_source_avoids_unsafe_dynamic_execution(self):
  hits=[]
  for p in ROOT.rglob('*.py'):
   if any(x in p.parts for x in ('__pycache__','.git')):continue
   s=p.read_text(errors='replace')
   for needle in ('eval(', 'exec(', 'pickle.loads(', 'yaml.load('):
    if needle in s:hits.append((str(p.relative_to(ROOT)),needle))
  self.assertEqual(hits,[])
if __name__=='__main__':unittest.main()
