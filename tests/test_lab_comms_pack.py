import math
from horizonlink.lab import LabInput,run_lab

def by_name(r): return {c.name:c for c in r.calculations}

def test_shannon_spectral_efficiency_identity():
    r=by_name(run_lab(LabInput(emitter_radius_rs=2.0)))
    x=r['communications_analysis'].outputs
    assert math.isclose(x['spectral_efficiency_bits_s_hz'],
                        math.log2(1+x['instantaneous_snr']),rel_tol=1e-12)

def test_integration_snr_scales_as_sqrt_time():
    a=by_name(run_lab(LabInput(emitter_radius_rs=2.0,integration_time_s=1.0)))['communications_analysis'].outputs
    b=by_name(run_lab(LabInput(emitter_radius_rs=2.0,integration_time_s=4.0)))['communications_analysis'].outputs
    assert math.isclose(b['integrated_snr']/a['integrated_snr'],2.0,rel_tol=1e-12)

def test_required_time_hits_target_scaling():
    r=by_name(run_lab(LabInput(emitter_radius_rs=2.0,target_snr=5.0)))['communications_analysis'].outputs
    assert r['required_integration_time_for_target_snr_s']>0
