from horizonlink.lab import LabInput
from horizonlink.lab.knowledge_store import KnowledgeStore
from horizonlink.lab.research_cycle import run_research_cycle

def test_small_research_cycle_persists_runs(tmp_path):
    store=KnowledgeStore(tmp_path/'r.sqlite3')
    try:
        result=run_research_cycle(store=store,base=LabInput(),
            values=[1.0001,1.0003,1.001,1.003,1.01,1.03],threshold=.99,falsify_top=0)
    finally: store.close()
    assert len(result['run_ids'])==6
    assert result['raw_candidates']>=0
    assert result['policy'].startswith('Candidates are stored')
