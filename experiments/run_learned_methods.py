"""Apply validated learned methods from the HorizonLink knowledge DB."""
from __future__ import annotations
import argparse,json
from horizonlink.lab import LabInput,run_lab
from horizonlink.lab.knowledge_store import KnowledgeStore
from horizonlink.lab.learned_methods import apply_methods

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--db',default='knowledge/horizonlink.sqlite3')
    p.add_argument('--mass-solar',type=float,default=10.0)
    p.add_argument('--radius-rs',type=float,default=1.01)
    a=p.parse_args()
    report=run_lab(LabInput(mass_solar=a.mass_solar,emitter_radius_rs=a.radius_rs))
    store=KnowledgeStore(a.db)
    try: items=store.knowledge_items('validated')
    finally: store.close()
    print(json.dumps({'methods':apply_methods(report,items)},indent=2,sort_keys=True,allow_nan=False))
if __name__=='__main__': main()
