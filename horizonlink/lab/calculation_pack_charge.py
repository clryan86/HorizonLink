"""Fourth analytic pack: Reissner-Nordstrom charged black-hole diagnostics."""
from __future__ import annotations
import math
from scipy.constants import G,c,hbar,k,pi,epsilon_0
from .registry import calculation,CalculationResult
from horizonlink.horizons.schwarzschild import M_SUN

def _M(i): return i.mass_solar*M_SUN

@calculation('reissner_nordstrom_geometry','geometry',description='RN horizon radii and extremality diagnostics')
def rn_geometry(i):
    q=i.charge_ratio_qm
    if abs(q)>1: raise ValueError('|charge_ratio_qm| must be <=1')
    rg=G*_M(i)/c**2
    d=math.sqrt(max(0.0,1-q*q))
    rp=rg*(1+d); rm=rg*(1-d)
    qext=math.sqrt(4*pi*epsilon_0*G)*_M(i)
    return CalculationResult('reissner_nordstrom_geometry','geometry','ok',{
      'outer_horizon_m':rp,'inner_horizon_m':rm,
      'outer_horizon_over_rg':rp/rg,'inner_horizon_over_rg':rm/rg,
      'extremality_gap_sqrt_1_minus_q2':d,
      'physical_charge_coulomb':q*qext,
      'extremal_charge_coulomb':qext,
    },('non-rotating Reissner-Nordstrom black hole',))

@calculation('reissner_nordstrom_thermodynamics','thermodynamics',description='RN area, surface gravity, Hawking temperature and entropy')
def rn_thermo(i):
    q=i.charge_ratio_qm
    if abs(q)>1: raise ValueError('|charge_ratio_qm| must be <=1')
    rg=G*_M(i)/c**2
    d=math.sqrt(max(0.0,1-q*q))
    rp=rg*(1+d); rm=rg*(1-d)
    area=4*pi*rp*rp
    kgeom=(rp-rm)/(2*rp*rp) if rp>0 else 0.0
    kacc=c*c*kgeom
    temp=hbar*c*kgeom/(2*pi*k)
    entropy=k*c**3*area/(4*G*hbar)
    return CalculationResult('reissner_nordstrom_thermodynamics','thermodynamics','ok',{
      'horizon_area_m2':area,'surface_gravity_m_s2':kacc,
      'surface_gravity_rate_s_inv':kacc/c,'hawking_temperature_k':temp,
      'entropy_j_k':entropy,
      'temperature_over_schwarzschild_same_mass':(4*rg*kgeom),
    },('semiclassical Reissner-Nordstrom thermodynamics',))

@calculation('charged_horizon_comparison','diagnostics',description='Dimensionless comparison of charged and neutral horizons')
def rn_compare(i):
    q=i.charge_ratio_qm
    if abs(q)>1: raise ValueError('|charge_ratio_qm| must be <=1')
    d=math.sqrt(max(0.0,1-q*q))
    rp_over_rs=(1+d)/2
    area_ratio=rp_over_rs**2
    temp_ratio=0.0 if d==0 else 4*d/(1+d)**2
    return CalculationResult('charged_horizon_comparison','diagnostics','ok',{
      'outer_horizon_over_schwarzschild_radius':rp_over_rs,
      'area_over_schwarzschild_area':area_ratio,
      'temperature_over_schwarzschild_temperature':temp_ratio,
      'charge_ratio_squared':q*q,
    },('same ADM mass comparison',))
