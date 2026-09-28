"""Safe learned/derived calculation methods.

Validated numerical relationships may be promoted to declarative formulas.
Only a small audited model vocabulary is supported; no eval/exec is used.
"""
from __future__ import annotations
from dataclasses import dataclass,asdict
import math
from typing import Any

@dataclass(frozen=True)
class DerivedMethod:
    key:str
    x_field:str
    model:str
    parameters:dict[str,float]
    domain_min:float|None=None
    domain_max:float|None=None
    evidence:str=""
    status:str="validated"

    def predict(self,x:float)->float:
        x=float(x)
        if not math.isfinite(x): raise ValueError('x must be finite')
        if self.domain_min is not None and x<self.domain_min: raise ValueError('x below validated domain')
        if self.domain_max is not None and x>self.domain_max: raise ValueError('x above validated domain')
        p=self.parameters
        if self.model=='linear': return float(p['intercept'])+float(p['slope'])*x
        if self.model=='power_law':
            if x<=0: raise ValueError('power-law input must be positive')
            return float(p['coefficient'])*(x**float(p['exponent']))
        if self.model=='logarithmic':
            if x<=0: raise ValueError('logarithmic input must be positive')
            return float(p['intercept'])+float(p['log_slope'])*math.log(x)
        raise ValueError(f'unsupported derived model: {self.model}')

    def payload(self)->dict[str,Any]: return asdict(self)

def flatten_report(report)->dict[str,float]:
    row={}
    for k,v in report.inputs.items():
        if isinstance(v,(int,float)) and math.isfinite(float(v)): row[k]=float(v)
    for calc in report.calculations:
        if calc.status!='ok': continue
        for k,v in calc.outputs.items():
            if isinstance(v,(int,float)) and math.isfinite(float(v)):
                row[f'{calc.name}.{k}']=float(v)
    return row

def method_from_knowledge(item:dict[str,Any])->DerivedMethod:
    p=item['payload']
    return DerivedMethod(
      key=item['key'],x_field=p['x_field'],model=p['model'],
      parameters={k:float(v) for k,v in p['parameters'].items()},
      domain_min=p.get('domain_min'),domain_max=p.get('domain_max'),
      evidence=item.get('evidence',''),status=item.get('status','validated'))

def apply_methods(report,items:list[dict[str,Any]])->list[dict[str,Any]]:
    row=flatten_report(report); out=[]
    for item in items:
        if item.get('kind')!='derived_method' or item.get('status')!='validated': continue
        m=method_from_knowledge(item)
        if m.x_field not in row:
            out.append({'key':m.key,'status':'unavailable','reason':f'missing field {m.x_field}'})
            continue
        try:
            y=m.predict(row[m.x_field])
            out.append({'key':m.key,'status':'ok','x_field':m.x_field,'x':row[m.x_field],'prediction':y,
                        'model':m.model,'evidence':m.evidence})
        except ValueError as exc:
            out.append({'key':m.key,'status':'out_of_domain','reason':str(exc)})
    return out
