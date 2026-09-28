from horizonlink.lab.discovery import scan_pair
from horizonlink.lab.survivor_strength import strengthen_pair


def test_exact_power_law_survives_window_attack():
    xs=[float(i) for i in range(1,41)]
    ys=[3.0*x**2 for x in xs]
    result=strengthen_pair('x','y',xs,ys,'power_law')
    assert result['strengthened'] is True
    assert result['minimum_score'] > 0.999999999
    assert result['relative_parameter_spread'] < 1e-10


def test_broken_power_law_is_rejected_by_window_attack():
    xs=[float(i) for i in range(1,41)]
    ys=[x**2 if i < 20 else 0.05*x**3 for i,x in enumerate(xs)]
    result=strengthen_pair('x','y',xs,ys,'power_law')
    assert result['strengthened'] is False


def test_discovery_recovers_exact_power_exponent():
    xs=[float(i) for i in range(1,31)]
    ys=[7.0*x**1.5 for x in xs]
    candidates=scan_pair('x','y',xs,ys)
    power=next(c for c in candidates if c.model=='power_law')
    assert power.score > 0.999999999
    assert abs(power.parameters['exponent']-1.5) < 1e-10
