"""Run the full persisted HorizonLink research cycle."""
from __future__ import annotations
import argparse,json
from horizonlink.lab import LabInput
from horizonlink.lab.knowledge_store import KnowledgeStore
from horizonlink.lab.research_cycle import run_research_cycle,log_radius_values

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--db',default='knowledge/horizonlink.sqlite3')
    p.add_argument('--points',type=int,default=30)
    p.add_argument('--mass-solar',type=float,default=10.0)
    p.add_argument('--spin',type=float,default=0.0)
    p.add_argument('--charge-ratio',type=float,default=0.0)
    p.add_argument('--falsify-top',type=int,default=3)
    a=p.parse_args()
    store=KnowledgeStore(a.db)
    try:
        result=run_research_cycle(store=store,
          base=LabInput(mass_solar=a.mass_solar,spin_chi=a.spin,charge_ratio_qm=a.charge_ratio),
          values=log_radius_values(points=a.points),falsify_top=a.falsify_top)
    finally: store.close()
    print(json.dumps(result,indent=2,sort_keys=True,allow_nan=False))
if __name__=='__main__': main()
