"""Sweep one HorizonLink input and automatically rank candidate relationships."""
from __future__ import annotations
import argparse,json,math
from dataclasses import replace
from horizonlink.lab import LabInput,run_lab
from horizonlink.lab.discovery import scan_table


def flatten(report):
    row={}
    row.update(report.inputs)
    for calc in report.calculations:
        if calc.status!='ok': continue
        for k,v in calc.outputs.items():
            if isinstance(v,(int,float)) and math.isfinite(float(v)):
                row[f'{calc.name}.{k}']=float(v)
    return row


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--parameter',choices=['emitter_radius_rs','mass_solar','spin_chi','emitted_hz','bandwidth_hz'],default='emitter_radius_rs')
    p.add_argument('--start',type=float,default=1.000001)
    p.add_argument('--stop',type=float,default=1.1)
    p.add_argument('--points',type=int,default=40)
    p.add_argument('--log-offset',action='store_true',help='for radius: log-space the offset r/rs-1')
    p.add_argument('--threshold',type=float,default=0.9995)
    a=p.parse_args()
    base=LabInput()
    if a.points<6: raise SystemExit('points must be >= 6')
    if a.log_offset:
        if a.parameter!='emitter_radius_rs' or a.start<=1 or a.stop<=1: raise SystemExit('--log-offset requires radius bounds > 1')
        lo,hi=math.log10(a.start-1),math.log10(a.stop-1)
        values=[1+10**(lo+(hi-lo)*i/(a.points-1)) for i in range(a.points)]
    else:
        values=[a.start+(a.stop-a.start)*i/(a.points-1) for i in range(a.points)]
    rows=[flatten(run_lab(replace(base,**{a.parameter:v}))) for v in values]
    candidates=scan_table(rows,a.threshold)
    payload={'sweep':{'parameter':a.parameter,'start':a.start,'stop':a.stop,'points':a.points,'threshold':a.threshold},
             'candidate_count':len(candidates),'candidates':[c.as_dict() for c in candidates[:50]],
             'warning':'Candidates are numerical relationships, not discoveries. Validate against known identities, independent implementations, wider domains, dimensional analysis, and falsification sweeps.'}
    print(json.dumps(payload,indent=2,sort_keys=True,allow_nan=False))

if __name__=='__main__': main()
