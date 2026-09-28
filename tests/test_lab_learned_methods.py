import math
from horizonlink.lab.learned_methods import DerivedMethod

def test_linear_derived_method():
    m=DerivedMethod('k','x','linear',{'intercept':2,'slope':3})
    assert m.predict(4)==14

def test_power_law_derived_method():
    m=DerivedMethod('k','x','power_law',{'coefficient':7,'exponent':1.5})
    assert math.isclose(m.predict(4),56.0,rel_tol=1e-12)

def test_domain_guard():
    m=DerivedMethod('k','x','linear',{'intercept':0,'slope':1},domain_min=1,domain_max=2)
    try: m.predict(3)
    except ValueError: pass
    else: raise AssertionError('expected domain guard')
