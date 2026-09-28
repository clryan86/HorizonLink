import math
from horizonlink.lab import LabInput,run_lab
from horizonlink.lab.knowledge_store import KnowledgeStore

def test_store_report_and_promote(tmp_path):
    db=tmp_path/'knowledge.sqlite3'
    store=KnowledgeStore(db)
    report=run_lab(LabInput())
    run_id=store.save_report(report)
    assert run_id>=1
    store.promote('test-law','known_relation',{'exponent':2.0},evidence='unit test')
    items=store.knowledge_items('validated')
    store.close()
    assert any(x['key']=='test-law' and x['payload']['exponent']==2.0 for x in items)

def test_second_pack_known_scalings():
    report=run_lab(LabInput(mass_solar=10.0,emitter_radius_rs=3.0))
    by={c.name:c for c in report.calculations}
    assert math.isclose(by['photon_scales'].outputs['isco_radius_over_rs'],3.0,rel_tol=1e-12)
    assert math.isclose(by['entropy_information'].outputs['bits_per_solar_mass_squared'],
                        run_lab(LabInput(mass_solar=20.0)).calculations[
                            [c.name for c in run_lab(LabInput(mass_solar=20.0)).calculations].index('entropy_information')
                        ].outputs['bits_per_solar_mass_squared'],rel_tol=1e-12)
