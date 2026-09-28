import math
from horizonlink.lab import LabInput,run_lab

def by_name(report):
    return {c.name:c for c in report.calculations}

def test_kerr_zero_spin_matches_schwarzschild_temperature_and_area():
    r=by_name(run_lab(LabInput(mass_solar=10.0,spin_chi=0.0)))
    ks=r['kerr_thermodynamics'].outputs
    ss=r['schwarzschild_thermodynamics'].outputs
    assert math.isclose(ks['hawking_temperature_k'],ss['hawking_temperature_k'],rel_tol=1e-12)
    assert math.isclose(ks['horizon_area_m2'],ss['horizon_area_m2'],rel_tol=1e-12)

def test_extremal_kerr_surface_gravity_goes_to_zero():
    r=by_name(run_lab(LabInput(mass_solar=10.0,spin_chi=1.0)))
    assert math.isclose(r['kerr_thermodynamics'].outputs['surface_gravity_m_s2'],0.0,abs_tol=1e-18)
    assert math.isclose(r['kerr_thermodynamics'].outputs['hawking_temperature_k'],0.0,abs_tol=1e-18)

def test_surface_gravity_natural_times_are_consistent():
    r=by_name(run_lab(LabInput(mass_solar=10.0)))
    x=r['surface_gravity_timescales'].outputs
    assert math.isclose(x['inverse_surface_gravity_time_s'],2*x['rs_over_c_s'],rel_tol=1e-12)
    assert math.isclose(x['p1_capacity_efold_time_s'],x['rs_over_c_s'],rel_tol=1e-12)

def test_proper_distance_shrinks_toward_horizon():
    far=by_name(run_lab(LabInput(emitter_radius_rs=1.1)))['near_horizon_geometry'].outputs
    near=by_name(run_lab(LabInput(emitter_radius_rs=1.0001)))['near_horizon_geometry'].outputs
    assert near['proper_distance_from_horizon_m'] < far['proper_distance_from_horizon_m']

def test_bosonic_entropy_nonnegative():
    r=by_name(run_lab(LabInput()))
    x=r['bosonic_mode_information'].outputs
    assert x['mean_thermal_occupation']>=0
    assert x['thermal_entropy_bits_per_mode']>=0
