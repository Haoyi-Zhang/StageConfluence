import json,random,tempfile,unittest
from pathlib import Path
from case_study.residual_optimizer import *

class ResidualCaseStudyTests(unittest.TestCase):
 def test_known_peak_is_syntax_divergent(self):
  e=Add(Var('x'),Var('x'));self.assertEqual(len(normal_forms(e,'buggy')),2)
 def test_repairs_are_unique(self):
  e=Add(Var('x'),Var('x'))
  for mode in ('left','right','canonical'):self.assertEqual(len(normal_forms(e,mode)),1)
 def test_semantics_of_known_peak(self):
  e=Add(Mul(Var('x'),Const(1)),Mul(Var('x'),Const(1)))
  sig=semantic_signature(e,range(-4,5))
  self.assertTrue(all(semantic_signature(n,range(-4,5))==sig for n in normal_forms(e,'buggy')))
 def test_every_generated_step_strictly_decreases_rank(self):
  for e in generate_expressions(7,500):
   for _,n in one_step(e,'canonical'):self.assertLess(rank(n),rank(e))
 def test_generated_semantics(self):
  for e in generate_expressions(5,600):
   sig=semantic_signature(e)
   for mode in ('buggy','left','right','canonical'):
    self.assertTrue(all(semantic_signature(n)==sig for n in normal_forms(e,mode)))
 def test_canonical_repair_unique_on_generated_set(self):
  for e in generate_expressions(7,700):self.assertEqual(len(normal_forms(e,'canonical')),1)
 def test_random_holdout(self):
  for seed in range(990000,990080):
   e=random_expr(random.Random(seed),5)
   sig=semantic_signature(e,range(-5,6));nfs=normal_forms(e,'canonical')
   self.assertEqual(len(nfs),1);self.assertEqual(semantic_signature(next(iter(nfs)),range(-5,6)),sig)
 def test_witness_replay(self):
  e=Add(Var('x'),Var('x'));paths=paths_to_normal_forms(e,'buggy')
  self.assertEqual({str(replay_path(e,p,'buggy')) for p in paths.values()},set(paths))
 def test_tampered_witness_rejected(self):
  e=Add(Var('x'),Var('x'));p=next(iter(paths_to_normal_forms(e,'buggy').values()));p=[dict(x) for x in p];p[0]['rule']='not-a-rule'
  with self.assertRaises(ValueError):replay_path(e,p,'buggy')
if __name__=='__main__':unittest.main()
