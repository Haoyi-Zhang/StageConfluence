from __future__ import annotations
import argparse,json,time,random,hashlib
from pathlib import Path
from .residual_optimizer import *

def main():
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);p.add_argument('--max-size',type=int,default=7);p.add_argument('--holdout',type=int,default=300);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
 t=time.perf_counter();exprs=generate_expressions(a.max_size)
 modes=['buggy','left','right','canonical'];summary={'schema_version':1,'bounded_generator':{'max_size':a.max_size,'expressions':len(exprs),'domain':[-2,-1,0,1,2]},'modes':{},'holdout':{},'limitations':'This is a micro case study and a checker stress test, not a production-compiler benchmark.'}
 first_witness=None
 for mode in modes:
  divergent=0;sem_errors=0;max_states=0;total_states=0
  for e in exprs:
   states,_=reachable_graph(e,mode);max_states=max(max_states,len(states));total_states+=len(states)
   nfs=normal_forms(e,mode)
   if len(nfs)>1:
    divergent+=1
    if first_witness is None and mode=='buggy':first_witness={'start':e.to_json(),'start_text':str(e),'mode':mode,'normal_forms':sorted(map(str,nfs)),'paths':paths_to_normal_forms(e,mode)}
   sig=semantic_signature(e)
   if any(semantic_signature(n)!=sig for n in nfs):sem_errors+=1
  summary['modes'][mode]={'syntax_divergent_expressions':divergent,'semantic_error_expressions':sem_errors,'reachable_states_total':total_states,'reachable_states_max':max_states}
 # held-out random expressions use disjoint, declared seeds and a wider input domain
 seeds=list(range(910_000,910_000+a.holdout));h={'seeds_sha256':hashlib.sha256(','.join(map(str,seeds)).encode()).hexdigest(),'expressions':len(seeds),'domain':list(range(-7,8)),'modes':{}}
 for mode in modes:
  div=sem=0;states_total=0
  for seed in seeds:
   e=random_expr(random.Random(seed),5+(seed%2)); states,_=reachable_graph(e,mode);states_total+=len(states);nfs=normal_forms(e,mode)
   div+=len(nfs)>1;sig=semantic_signature(e,range(-7,8));sem+=any(semantic_signature(n,range(-7,8))!=sig for n in nfs)
  h['modes'][mode]={'syntax_divergent_expressions':int(div),'semantic_error_expressions':int(sem),'reachable_states_total':states_total}
 summary['holdout']=h;summary['seconds']=round(time.perf_counter()-t,6)
 if first_witness:
  (a.out/'buggy-witness.json').write_text(json.dumps(first_witness,indent=2),encoding='utf-8')
 summary['status']='PASS' if all(x['semantic_error_expressions']==0 for x in summary['modes'].values()) and all(x['semantic_error_expressions']==0 for x in h['modes'].values()) and summary['modes']['buggy']['syntax_divergent_expressions']>0 and summary['modes']['canonical']['syntax_divergent_expressions']==0 else 'FAIL'
 # Runtime is resource metadata, not deterministic scientific output.
 summary.pop('seconds', None)
 summary.pop('elapsed_seconds', None)
 summary.pop('runtime_seconds', None)
 (a.out/'case-study-summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
 print(json.dumps(summary,sort_keys=True))
 if summary['status']!='PASS':raise SystemExit(1)
if __name__=='__main__':main()
