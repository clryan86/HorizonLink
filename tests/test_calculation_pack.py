import math
from horizonlink.lab import LabInput,run_lab

def _by_name(report): return {x.name:x for x in report.calculations}

def test_pack_loads_and_core_results_are_finite():
    r=run_lab(LabInput())
    d=_by_name(r)
    required={'schwarzschild_thermodynamics','local_static_observer','photon_scales','wave_scales','receiver_quantum_limits','information_scales','dimensionless_state'}
    assert required.issubset(d)
    for name in required:
        assert d[name].status=='ok'
        assert all(math.isfinite(float(v)) for v in d[name].outputs.values())

def test_known_schwarzschild_radius_ratios():
    d=_by_name(run_lab(LabInput()))
    p=d['photon_scales'].outputs
    assert math.isclose(p['photon_sphere_radius_over_rs'],1.5)
    assert math.isclose(p['isco_radius_over_rs'],3.0)

def test_redshift_factor_matches_geometry():
    d=_by_name(run_lab(LabInput(emitter_radius_rs=2.0)))
    assert math.isclose(d['local_static_observer'].outputs['metric_f'],0.5,rel_tol=1e-12)
    assert math.isclose(d['dimensionless_state'].outputs['redshift_factor'],math.sqrt(0.5),rel_tol=1e-12)

def test_hawking_temperature_inverse_mass():
    a=_by_name(run_lab(LabInput(mass_solar=10)))['schwarzschild_thermodynamics'].outputs['hawking_temperature_k']
    b=_by_name(run_lab(LabInput(mass_solar=20)))['schwarzschild_thermodynamics'].outputs['hawking_temperature_k']
    assert math.isclose(a/b,2.0,rel_tol=1e-12)
