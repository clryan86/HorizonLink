"""Automatically stress-test one HorizonLink candidate relationship."""
from __future__ import annotations
import argparse,json
from horizonlink.lab.falsify import falsify_candidate


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--x',required=True,help='flattened numeric field name')
    p.add_argument('--y',required=True,help='flattened numeric field name')
    p.add_argument('--model',choices=['linear','power_law','logarithmic'],required=True)
    p.add_argument('--sweep-parameter',default='emitter_radius_rs',choices=['emitter_radius_rs','mass_solar','spin_chi','emitted_hz','bandwidth_hz'])
    a=p.parse_args()
    result=falsify_candidate(x=a.x,y=a.y,model=a.model,sweep_parameter=a.sweep_parameter)
    print(json.dumps(result,indent=2,sort_keys=True,allow_nan=False))

if __name__=='__main__': main()
