"""Automated calculate -> discover -> falsify -> strengthen research cycle."""
from __future__ import annotations
from dataclasses import replace
import math
from .runner import LabInput,run_lab
from .learned_methods import flatten_report
from .discovery import scan_table
from .provenance import rank_candidate
from .falsify import falsify_candidate
from .survivor_strength import strengthen_pair
from .knowledge_store import KnowledgeStore

def log_radius_values(start:float=1.000001,stop:float=1.1,points:int=30):
    if start<=1 or stop<=1 or points<6: raise ValueError('exterior radius bounds >1 and >=6 points required')
    lo,hi=math.log10(start-1),math.log10(stop-1)
    return [1+10**(lo+(hi-lo)*i/(points-1)) for i in range(points)]

def run_research_cycle(*,store:KnowledgeStore,base:LabInput|None=None,
                       sweep_parameter:str='emitter_radius_rs',values=None,
                       threshold:float=.9995,min_interest:float=.5,
                       falsify_top:int=3):
    base=base or LabInput()
    values=list(values or log_radius_values())
    rows=[]; run_ids=[]
    for value in values:
        report=run_lab(replace(base,**{sweep_parameter:value}))
        run_ids.append(store.save_report(report))
        rows.append(flatten_report(report))
    raw=scan_table(rows,threshold)
    ranked=[rank_candidate(c.as_dict()) for c in raw]
    ranked.sort(key=lambda x:(x['interest_score'],x['score']),reverse=True)
    interesting=[x for x in ranked if x['interest_score']>=min_interest]
    saved=[]
    for idx,c in enumerate(interesting):
        fals=None; strength=None; survivor=False
        if idx<falsify_top and c['x'] in rows[0] and c['y'] in rows[0]:
            try:
                fals=falsify_candidate(x=c['x'],y=c['y'],model=c['model'],
                    sweep_parameter=sweep_parameter,sweep_values=values,base=base)
                if fals.get('summary',{}).get('screening_pass'):
                    strength=strengthen_pair(c['x'],c['y'],
                        [r[c['x']] for r in rows],[r[c['y']] for r in rows],c['model'])
                    survivor=bool(strength.get('strengthened'))
            except Exception as exc:
                fals={'error':f'{type(exc).__name__}: {exc}'}
        cid=store.save_candidate(c,provenance=c.get('provenance'),falsification=fals)
        saved.append({'candidate_id':cid,'x':c['x'],'y':c['y'],'model':c['model'],
                      'score':c['score'],'interest_score':c['interest_score'],
                      'falsification':fals,'strengthening':strength,'survivor':survivor})
    survivors=[c for c in saved if c['survivor']]
    return {
      'run_ids':run_ids,'sweep_parameter':sweep_parameter,'points':len(values),
      'raw_candidates':len(raw),'interesting_candidates':len(interesting),
      'saved_candidates':saved,'survivors':survivors,'survivor_count':len(survivors),
      'next_experiment':(
          'expand surviving relationships across independent mass/spin/charge sweeps'
          if survivors else
          'increase sweep diversity and search for candidates under independent controls'
      ),
      'policy':'Failed screens are not promoted; survivors require independent validation and novelty review.'
    }
