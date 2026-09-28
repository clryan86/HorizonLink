"""Automatic falsification helpers for numerical relationship candidates."""
from __future__ import annotations
from dataclasses import dataclass, asdict, replace
import math
from .runner import LabInput, run_lab
from .discovery import scan_pair

@dataclass(frozen=True)
class Trial:
    control: str
    value: float
    score: float | None
    parameter: float | None
    status: str
    reason: str = ""
    def as_dict(self): return asdict(self)


def _flatten(report):
    row={}
    row.update(report.inputs)
    for c in report.calculations:
        if c.status!='ok': continue
        for k,v in c.outputs.items():
            if isinstance(v,(int,float)) and math.isfinite(float(v)):
                row[f'{c.name}.{k}']=float(v)
    return row


def _fit(rows,x,y,model):
    if not rows or x not in rows[0] or y not in rows[0]: return None
    fits=scan_pair(x,y,[r[x] for r in rows],[r[y] for r in rows])
    return next((f for f in fits if f.model==model),None)


def falsify_candidate(*, x:str, y:str, model:str, sweep_parameter:str='emitter_radius_rs',
                       sweep_values=None, controls=None, base:LabInput|None=None):
    """Refit one candidate while perturbing independent controls.

    A robust candidate should keep high fit quality and stable defining parameter
    (slope, exponent, or log_slope). This is a screening test, not proof.
    """
    base=base or LabInput()
    sweep_values=sweep_values or [1+10**e for e in (-6,-5.5,-5,-4.5,-4,-3.5,-3,-2.5,-2)]
    controls=controls or {
        'mass_solar':[5.0,10.0,30.0,100.0,1e6],
        'spin_chi':[0.0,0.3,0.7,0.95],
        'emitted_hz':[1e6,1e9,1e12],
        'bandwidth_hz':[1e3,1e6,1e9],
        'system_temperature_k':[3.0,50.0,300.0],
    }
    pname={'linear':'slope','power_law':'exponent','logarithmic':'log_slope'}[model]
    trials=[]
    for control,values in controls.items():
        if control==sweep_parameter: continue
        for value in values:
            b=replace(base,**{control:value})
            rows=[]
            for sv in sweep_values:
                try: rows.append(_flatten(run_lab(replace(b,**{sweep_parameter:sv}))))
                except Exception: pass
            fit=_fit(rows,x,y,model)
            if fit is None:
                trials.append(Trial(control,float(value),None,None,'fail','fit unavailable'))
            else:
                trials.append(Trial(control,float(value),fit.score,float(fit.parameters[pname]),'ok'))
    params=[t.parameter for t in trials if t.status=='ok' and t.parameter is not None]
    scores=[t.score for t in trials if t.status=='ok' and t.score is not None]
    mean=sum(params)/len(params) if params else None
    spread=(max(params)-min(params))/max(abs(mean),1e-300) if params and mean is not None else None
    return {
        'candidate':{'x':x,'y':y,'model':model,'sweep_parameter':sweep_parameter},
        'trials':[t.as_dict() for t in trials],
        'summary':{
            'trial_count':len(trials),'successful_fits':len(params),
            'minimum_r2':min(scores) if scores else None,
            'mean_defining_parameter':mean,
            'relative_parameter_spread':spread,
            'screening_pass':bool(scores and min(scores)>=0.999 and spread is not None and spread<=0.02),
        },
        'warning':'A screening pass is not evidence of novelty or a physical law. Check algebraic dependence, units, numerical convergence, independent implementations, literature, and out-of-domain counterexamples.'
    }
