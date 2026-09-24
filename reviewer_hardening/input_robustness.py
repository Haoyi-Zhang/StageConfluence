from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from typing import Any


def _canonical(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _mutations(valid_text: str) -> list[tuple[str, str, bool]]:
    """Return (name, payload, should_accept) in a deterministic order."""
    valid=json.loads(valid_text)
    cases: list[tuple[str,str,bool]]=[("valid_baseline",valid_text,True)]
    cases.extend([
        ("empty", "", False),
        ("truncated", valid_text[:max(1,len(valid_text)//3)], False),
        ("scalar_null", "null", False),
        ("scalar_number", "17", False),
        ("array_root", "[]", False),
        ("empty_object", "{}", False),
        ("invalid_utf8_surrogate_escape", '"\\ud800"', False),
        ("duplicate_key_syntax", '{"name":"a","name":"b"}', False),
    ])
    if isinstance(valid,dict):
        for key in sorted(valid)[:8]:
            m=dict(valid); m.pop(key,None)
            cases.append((f"missing_{key}",_canonical(m),False))
        for key in sorted(valid)[:8]:
            m=dict(valid); m[key]=None
            cases.append((f"null_{key}",_canonical(m),False))
            m=dict(valid); m[key]=["wrong-type"]
            cases.append((f"wrong_type_{key}",_canonical(m),False))
    return cases


def run_campaign(root: Path, output: Path) -> dict[str, Any]:
    cases_dir=root/'staged_cases'
    candidates=sorted(cases_dir.glob('*.json'))
    if not candidates:
        raise RuntimeError('no staged_cases JSON inputs found')
    source=candidates[0]
    valid_text=source.read_text(encoding='utf-8')
    output.mkdir(parents=True,exist_ok=True)
    rows=[]
    for name,payload,should_accept in _mutations(valid_text):
        with tempfile.NamedTemporaryFile('w',suffix='.json',encoding='utf-8',delete=False) as f:
            f.write(payload); tmp=Path(f.name)
        try:
            env=dict(os.environ); env['PYTHONHASHSEED']='0'; env['PYTHONPATH']=str(root)
            try:
                p=subprocess.run([sys.executable,str(root/'staged_check.py'),'analyze',str(tmp)],cwd=root,env=env,
                                 text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=8)
                timed_out=False; returncode=p.returncode; stdout=p.stdout; stderr=p.stderr
            except subprocess.TimeoutExpired as exc:
                timed_out=True; returncode=None; stdout=exc.stdout or ''; stderr=exc.stderr or ''
            accepted=(returncode==0 and not timed_out)
            trace=('Traceback (most recent call last)' in (stdout+stderr))
            rows.append({
                'case':name,'expected_accept':should_accept,'accepted':accepted,'returncode':returncode,
                'timed_out':timed_out,'python_traceback':trace,
                'stdout_class':'nonempty' if stdout.strip() else 'empty',
                'stderr_class':'nonempty' if stderr.strip() else 'empty',
            })
        finally:
            tmp.unlink(missing_ok=True)
    failures=[r for r in rows if r['accepted']!=r['expected_accept'] or r['timed_out'] or r['python_traceback']]
    summary={
        'schema_version':1,'status':'PASS' if not failures else 'FAIL','source_case':source.name,
        'cases':len(rows),'expected_accepts':sum(r['expected_accept'] for r in rows),
        'clean_rejections':sum((not r['accepted']) and (not r['timed_out']) and (not r['python_traceback']) for r in rows),
        'failures':failures,'rows':rows,
        'scope':'Deterministic malformed-input and wrong-type campaign for the public analyze CLI; not a security proof or coverage of all hostile inputs.'
    }
    (output/'input-robustness.json').write_text(json.dumps(summary,indent=2,sort_keys=True),encoding='utf-8')
    md=['# Input robustness campaign','',f"**Status:** {summary['status']}",f"**Cases:** {summary['cases']}",
        f"**Clean rejections:** {summary['clean_rejections']}",'',summary['scope'],'']
    (output/'INPUT-ROBUSTNESS.md').write_text('\n'.join(md),encoding='utf-8')
    return summary


def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1])
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args()
    summary=run_campaign(args.root.resolve(),args.output.resolve())
    print(json.dumps({k:summary[k] for k in ['status','cases','clean_rejections']},sort_keys=True))
    return 0 if summary['status']=='PASS' else 1

if __name__=='__main__':
    raise SystemExit(main())
