import math
from horizonlink.lab import LabInput,run_lab

def by_name(report): return {c.name:c for c in report.calculations}

def test_neutral_rn_matches_schwarzschild():
    r=by_name(run_lab(LabInput(mass_solar=10.0,charge_ratio_qm=0.0)))
    rn=r['reissner_nordstrom_thermodynamics'].outputs
    ss=r['schwarzschild_thermodynamics'].outputs
    assert math.isclose(rn['hawking_temperature_k'],ss['hawking_temperature_k'],rel_tol=1e-12)
    assert math.isclose(rn['horizon_area_m2'],ss['horizon_area_m2'],rel_tol=1e-12)

def test_extremal_rn_temperature_zero():
    r=by_name(run_lab(LabInput(charge_ratio_qm=1.0)))
    x=r['reissner_nordstrom_thermodynamics'].outputs
    assert math.isclose(x['hawking_temperature_k'],0.0,abs_tol=1e-18)
    assert math.isclose(x['surface_gravity_m_s2'],0.0,abs_tol=1e-18)

def test_charge_shrinks_outer_horizon_at_fixed_mass():
    n=by_name(run_lab(LabInput(charge_ratio_qm=0.0)))['reissner_nordstrom_geometry'].outputs
    q=by_name(run_lab(LabInput(charge_ratio_qm=0.9)))['reissner_nordstrom_geometry'].outputs
    assert q['outer_horizon_m']<n['outer_horizon_m']

def test_rn_temperature_ratio_formula():
    r=by_name(run_lab(LabInput(charge_ratio_qm=0.6)))
    a=r['reissner_nordstrom_thermodynamics'].outputs['temperature_over_schwarzschild_same_mass']
    b=r['charged_horizon_comparison'].outputs['temperature_over_schwarzschild_temperature']
    assert math.isclose(a,b,rel_tol=1e-12)
