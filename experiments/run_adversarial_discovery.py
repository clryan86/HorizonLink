"""Calculate -> sweep -> discover -> test -> falsify -> strengthen survivors."""
from __future__ import annotations
import argparse,json,math
from dataclasses import replace
from horizonlink.lab import LabInput,run_lab
from horizonlink.lab.cross_validation import validate_pair
from horizonlink.lab.discovery import scan_table
from horizonlink.lab.falsify import falsify_candidate
from horizonlink.lab.learned_methods import flatten_report
from horizonlink.lab.null_tests import permutation_significance
from horizonlink.lab.provenance import rank_candidate
from horizonlink.lab.survivor_strength import strengthen_pair

def values(start,stop,points,log_offset):
    if points<12: raise ValueError('at least 12 points required')
    if log_offset:
        if start<=1 or stop<=1: raise ValueError('log-offset radius bounds must exceed 1')
        lo,hi=math.log10(start-1),math.log10(stop-1)
        return [1+10**(lo+(hi-lo)*i/(points-1)) for i in range(points)]
    return [start+(stop-start)*i/(points-1) for i in range(points)]

def main():
    p=argparse.ArgumentParser(); p.add_argument('--parameter',default='emitter_radius_rs')
    p.add_argument('--start',type=float,default=1.000001); p.add_argument('--stop',type=float,default=1.1)
    p.add_argument('--points',type=int,default=32); p.add_argument('--threshold',type=float,default=.9995)
    p.add_argument('--top',type=int,default=12); p.add_argument('--permutations',type=int,default=100)
    p.add_argument('--log-offset',action='store_true'); a=p.parse_args()
    sweep=values(a.start,a.stop,a.points,a.log_offset); base=LabInput()
    rows=[flatten_report(run_lab(replace(base,**{a.parameter:v}))) for v in sweep]
    ranked=[rank_candidate(c.as_dict()) for c in scan_table(rows,a.threshold)]
    ranked.sort(key=lambda c:(c['interest_score'],c['score']),reverse=True)
    survivors=[]; rejected=[]
    for candidate in ranked[:a.top]:
        x,y,model=candidate['x'],candidate['y'],candidate['model']; xs=[r[x] for r in rows]; ys=[r[y] for r in rows]
        cv=next((r for r in validate_pair(x,y,xs,ys) if r['model']==model),None)
        try: null=permutation_significance(x,y,xs,ys,model=model,permutations=a.permutations,seed=17)
        except ValueError as exc: null={'error':str(exc),'empirical_p_value':1.0}
        try: fals=falsify_candidate(x=x,y=y,model=model,sweep_parameter=a.parameter,sweep_values=sweep,base=base)
        except Exception as exc: fals={'error':f'{type(exc).__name__}: {exc}'}
        try: strength=strengthen_pair(x,y,xs,ys,model)
        except Exception as exc: strength={'error':f'{type(exc).__name__}: {exc}','strengthened':False}
        fals_pass=bool(fals.get('summary',{}).get('screening_pass',False))
        passes=bool(cv and cv['passes_1pct'] and null['empirical_p_value']<=.05 and strength.get('strengthened') and fals_pass)
        record={'candidate':candidate,'cross_validation':cv,'null_test':null,'falsification':fals,
                'strengthening':strength,'survives_full_cycle':passes}
        (survivors if passes else rejected).append(record)
    print(json.dumps({'cycle':['build','calculate','sweep','discover_candidates','attack_with_tests','discard_failures','strengthen_survivors','build_next_experiment'],
      'sweep_parameter':a.parameter,'points':len(sweep),'screened':min(a.top,len(ranked)),
      'survivors':survivors,'rejected':rejected,
      'next_step':'Design the next targeted calculation pack from full-cycle survivors and repeat on wider domains.',
      'warning':'Full-cycle survival is a research lead, not proof of new physics.'},indent=2,sort_keys=True,allow_nan=False))
if __name__=='__main__': main()
