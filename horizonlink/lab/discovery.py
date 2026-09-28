"""Conservative numerical relationship discovery for HorizonLink sweeps.

This module does not label correlations as physics discoveries. It proposes
candidate relationships that must survive independent validation and
falsification tests.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
import math
from typing import Iterable


@dataclass(frozen=True)
class Candidate:
    x: str
    y: str
    model: str
    score: float
    parameters: dict[str, float]
    points: int
    interpretation: str

    def as_dict(self):
        return asdict(self)


def _linear_fit(xs: list[float], ys: list[float]):
    n=len(xs); xm=sum(xs)/n; ym=sum(ys)/n
    sxx=sum((x-xm)**2 for x in xs)
    if sxx == 0: return None
    slope=sum((x-xm)*(y-ym) for x,y in zip(xs,ys))/sxx
    intercept=ym-slope*xm
    pred=[intercept+slope*x for x in xs]
    sse=sum((y-p)**2 for y,p in zip(ys,pred))
    sst=sum((y-ym)**2 for y in ys)
    r2=1.0-sse/sst if sst>0 else 1.0
    return intercept,slope,max(-1.0,min(1.0,r2))


def scan_pair(x_name: str, y_name: str, xs: Iterable[float], ys: Iterable[float], min_points: int=6):
    pairs=[(float(x),float(y)) for x,y in zip(xs,ys) if math.isfinite(float(x)) and math.isfinite(float(y))]
    if len(pairs)<min_points: return []
    x=[p[0] for p in pairs]; y=[p[1] for p in pairs]
    out=[]
    fit=_linear_fit(x,y)
    if fit:
        a,b,r2=fit
        out.append(Candidate(x_name,y_name,'linear',r2,{'intercept':a,'slope':b},len(x),'candidate affine relationship'))
    if all(v>0 for v in x) and all(v>0 for v in y):
        fit=_linear_fit([math.log(v) for v in x],[math.log(v) for v in y])
        if fit:
            la,p,r2=fit
            # A statistically good log-log fit can have an intercept too large
            # to represent as a finite coefficient. Skip that parameterization
            # rather than crashing an entire research sweep.
            if -745.0 <= la <= 709.0:
                coefficient=math.exp(la)
                if math.isfinite(coefficient):
                    out.append(Candidate(x_name,y_name,'power_law',r2,{'coefficient':coefficient,'exponent':p},len(x),'candidate scale-free power law'))
    if all(v>0 for v in x):
        fit=_linear_fit([math.log(v) for v in x],y)
        if fit:
            a,b,r2=fit
            out.append(Candidate(x_name,y_name,'logarithmic',r2,{'intercept':a,'log_slope':b},len(x),'candidate logarithmic relationship'))
    return sorted(out,key=lambda c:c.score,reverse=True)


def scan_table(rows: list[dict[str,float]], threshold: float=0.999):
    """Scan numeric columns pairwise and return only strong candidate fits."""
    if not rows: return []
    keys=sorted(set.intersection(*(set(r) for r in rows)))
    numeric=[]
    for k in keys:
        try:
            vals=[float(r[k]) for r in rows]
            if all(math.isfinite(v) for v in vals) and len(set(vals))>1: numeric.append(k)
        except (TypeError,ValueError): pass
    candidates=[]
    for i,x in enumerate(numeric):
        for y in numeric[i+1:]:
            candidates.extend(c for c in scan_pair(x,y,[r[x] for r in rows],[r[y] for r in rows]) if c.score>=threshold)
    candidates.sort(key=lambda c:(c.score,c.points),reverse=True)
    return candidates
