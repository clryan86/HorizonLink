"""Run one full HorizonLink research cycle and persist the report.

Cycle:
  calculate -> store -> summarize.

Discovery/falsification scripts can consume the same knowledge DB afterward.
"""
from __future__ import annotations
import argparse,json
from horizonlink.lab import LabInput,run_lab
from horizonlink.lab.knowledge_store import KnowledgeStore

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--db',default='knowledge/horizonlink.sqlite3')
    p.add_argument('--mass-solar',type=float,default=10.0)
    p.add_argument('--spin',type=float,default=0.0)
    p.add_argument('--charge-ratio',type=float,default=0.0)
    p.add_argument('--radius-rs',type=float,default=1.01)
    p.add_argument('--frequency-hz',type=float,default=1e9)
    p.add_argument('--bandwidth-hz',type=float,default=1e6)
    p.add_argument('--temperature-k',type=float,default=50.0)
    a=p.parse_args()
    inp=LabInput(mass_solar=a.mass_solar,spin_chi=a.spin,charge_ratio_qm=a.charge_ratio,emitter_radius_rs=a.radius_rs,
                 emitted_hz=a.frequency_hz,bandwidth_hz=a.bandwidth_hz,
                 system_temperature_k=a.temperature_k)
    report=run_lab(inp)
    store=KnowledgeStore(a.db)
    try: run_id=store.save_report(report)
    finally: store.close()
    print(json.dumps({'run_id':run_id,'database':a.db,'summary':report.summary},indent=2,sort_keys=True))

if __name__=='__main__': main()
