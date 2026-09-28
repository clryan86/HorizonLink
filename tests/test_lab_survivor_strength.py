from horizonlink.lab.survivor_strength import strengthen_pair


def test_exact_power_law_is_stable_across_windows():
    xs=[float(i) for i in range(1,41)]
    ys=[11.0*x**1.25 for x in xs]
    r=strengthen_pair('x','y',xs,ys,'power_law')
    assert r['strengthened']
    assert r['relative_parameter_spread'] < 1e-10


def test_requires_enough_points():
    try: strengthen_pair('x','y',[1.0]*8,[2.0]*8,'linear')
    except ValueError: pass
    else: raise AssertionError('expected sample guard')
