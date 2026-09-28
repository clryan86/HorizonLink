import math
from horizonlink.lab.discovery import scan_pair,scan_table


def test_power_law_recovery():
    xs=[1,2,3,4,5,6,8,10]
    ys=[7*x**1.5 for x in xs]
    fits=scan_pair('x','y',xs,ys)
    power=next(f for f in fits if f.model=='power_law')
    assert power.score>0.999999999
    assert math.isclose(power.parameters['coefficient'],7.0,rel_tol=1e-10)
    assert math.isclose(power.parameters['exponent'],1.5,rel_tol=1e-10)


def test_log_recovery():
    xs=[1,2,3,5,8,13,21]
    ys=[2+4*math.log(x) for x in xs]
    fits=scan_pair('x','y',xs,ys)
    logfit=next(f for f in fits if f.model=='logarithmic')
    assert logfit.score>0.999999999
    assert math.isclose(logfit.parameters['log_slope'],4.0,rel_tol=1e-10)


def test_table_threshold():
    rows=[{'x':float(x),'y':3.0*x+2.0,'junk':(-1.0)**x*x} for x in range(1,10)]
    found=scan_table(rows,0.999999)
    assert any(c.x=='x' and c.y=='y' and c.model=='linear' for c in found)
