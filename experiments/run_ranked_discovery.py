"""Run discovery, then downgrade candidates explained by computational ancestry."""
from __future__ import annotations
import argparse,json,math
from dataclasses import replace
from horizonlink.lab import LabInput,run_lab
from horizonlink.lab.discovery import scan_table
from horizonlink.lab.provenance import rank_candidate

def flatten(report):
    row=dict(report.inputs)
    for calc in report.calculations:
        if calc.status!='ok': continue
        for k,v in calc.outputs.items():
            if isinstance(v,(int,float)) and math.isfinite(float(v)):
                row[f'{calc.name}.{k}']=float(v)
    return row

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--points',type=int,default=40)
    p.add_argument('--threshold',type=float,default=.9995)
    p.add_argument('--min-interest',type=float,default=.5)
    a=p.parse_args()
    base=LabInput(); lo,hi=-6.0,-1.0
    vals=[1+10**(lo+(hi-lo)*i/(a.points-1)) for i in range(a.points)]
    rows=[flatten(run_lab(replace(base,emitter_radius_rs=v))) for v in vals]
    raw=scan_table(rows,a.threshold)
    ranked=[rank_candidate(c.as_dict()) for c in raw]
    ranked.sort(key=lambda x:(x['interest_score'],x['score']),reverse=True)
    interesting=[r for r in ranked if r['interest_score']>=a.min_interest]
    print(json.dumps({
      'raw_candidate_count':len(raw),
      'post_provenance_candidate_count':len(interesting),
      'candidates':interesting[:50],
      'downgraded_examples':[r for r in ranked if r['interest_score']<a.min_interest][:20],
      'warning':'Provenance filtering removes obvious computational circularity only. Surviving candidates still require dimensional analysis, independent implementations, convergence checks, literature review, and physical falsification.'
    },indent=2,sort_keys=True,allow_nan=False))
if __name__=='__main__': main()
