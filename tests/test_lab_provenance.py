from horizonlink.lab.provenance import assess_pair,rank_candidate

def test_direct_dependency_is_downgraded():
    p=assess_pair('exterior_link.received_power_fraction','exterior_link.received_power_w')
    assert p['classification']=='direct_dependency'
    assert p['independence_score']==0.0

def test_cross_family_gets_higher_independence():
    p=assess_pair('kerr_geometry.outer_horizon_m','exterior_link.power_snr')
    assert p['independence_score']>=0.7

def test_perfect_trivial_fit_has_zero_interest():
    c={'x':'exterior_link.received_power_fraction','y':'exterior_link.received_power_w','model':'linear','score':1.0,'parameters':{},'points':40,'interpretation':'test'}
    r=rank_candidate(c)
    assert r['interest_score']==0.0
