"""Strengthen surviving HorizonLink candidates by attacking domain stability.

A survivor is refit over nested and shifted windows. Stable parameters across
windows are more interesting than fits that only work in one hand-picked range.
"""
from __future__ import annotations
import math
from .discovery import scan_pair

_PARAM={"linear":"slope","power_law":"exponent","logarithmic":"log_slope"}

def strengthen_pair(x_name:str,y_name:str,xs:list[float],ys:list[float],model:str)->dict:
    if len(xs)!=len(ys) or len(xs)<12: raise ValueError('at least 12 paired points required')
    n=len(xs)
    windows=[('full',0,n),('early',0,max(8,3*n//4)),('late',n//4,n),('middle',n//8,7*n//8)]
    fits=[]
    key=_PARAM[model]
    for label,a,b in windows:
        cs=scan_pair(x_name,y_name,xs[a:b],ys[a:b])
        fit=next((c for c in cs if c.model==model),None)
        if fit is not None:
            fits.append({'window':label,'start':a,'stop':b,'score':fit.score,
                         'parameter':float(fit.parameters[key]),'parameters':fit.parameters})
    params=[f['parameter'] for f in fits]
    scores=[f['score'] for f in fits]
    mean=sum(params)/len(params) if params else None
    spread=(max(params)-min(params))/max(abs(mean),1e-300) if params else None
    return {'x':x_name,'y':y_name,'model':model,'fits':fits,
            'minimum_score':min(scores) if scores else None,
            'relative_parameter_spread':spread,
            'strengthened':bool(len(fits)==len(windows) and min(scores)>=.999 and spread<=.02),
            'interpretation':'window-stability screen; survival is not proof of novelty'}
