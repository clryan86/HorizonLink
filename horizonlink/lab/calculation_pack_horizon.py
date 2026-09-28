"""Third analytic pack: near-horizon distances, delays, Kerr thermodynamics, and bosonic information."""
from __future__ import annotations
import math
from scipy.constants import G,c,h,hbar,k,pi
from .registry import calculation,CalculationResult
from horizonlink.horizons.schwarzschild import M_SUN

def _M(i): return i.mass_solar*M_SUN
def _rs(i): return 2*G*_M(i)/c**2
def _r(i): return i.emitter_radius_rs*_rs(i)

def _rstar(r,rs):
    if r<=rs: raise ValueError('tortoise coordinate requires r>r_s')
    return r+rs*math.log(r/rs-1.0)

@calculation('near_horizon_geometry','geometry',description='Proper radial distance and tortoise-coordinate delay')
def near_horizon(i):
    rs=_rs(i); r=_r(i)
    if r<=rs: raise ValueError('requires exterior emitter')
    u=math.sqrt(r-rs)
    proper=u*math.sqrt(u*u+rs)+rs*math.asinh(u/math.sqrt(rs))
    recv=i.receiver_distance_m
    if recv<=r:
        delay=None
    else:
        delay=(_rstar(recv,rs)-_rstar(r,rs))/c
    return CalculationResult('near_horizon_geometry','geometry','ok',{
      'proper_distance_from_horizon_m':proper,
      'proper_distance_over_rs':proper/rs,
      'tortoise_coordinate_m':_rstar(r,rs),
      'outgoing_coordinate_delay_to_receiver_s':delay,
      'near_horizon_sqrt_offset':math.sqrt((r-rs)/rs),
    },('Schwarzschild t=constant proper radial distance','Boyer-Lindquist/Schwarzschild coordinate delay is observer-coordinate dependent'))

@calculation('surface_gravity_timescales','thermodynamics',description='Surface-gravity rates and natural horizon timescales')
def surface_times(i):
    M=_M(i); rs=_rs(i)
    kappa_acc=c**4/(4*G*M)
    kappa_rate=kappa_acc/c
    return CalculationResult('surface_gravity_timescales','thermodynamics','ok',{
      'surface_gravity_acceleration_m_s2':kappa_acc,
      'surface_gravity_rate_s_inv':kappa_rate,
      'inverse_surface_gravity_time_s':1/kappa_rate,
      'rs_over_c_s':rs/c,
      'two_rs_over_c_s':2*rs/c,
      'p1_capacity_efold_time_s':1/(2*kappa_rate),
    },('p1 capacity e-fold time is a HorizonLink diagnostic conditional on q=1',))

@calculation('kerr_thermodynamics','thermodynamics',description='Kerr horizon area, surface gravity and Hawking temperature')
def kerr_thermo(i):
    chi=i.spin_chi
    if abs(chi)>1: raise ValueError('|spin_chi| must be <=1')
    rg=G*_M(i)/c**2
    d=math.sqrt(max(0.0,1-chi*chi))
    rp=rg*(1+d); rm=rg*(1-d); a=chi*rg
    area=4*pi*(rp*rp+a*a)
    kappa_geom=(rp-rm)/(2*(rp*rp+a*a)) if area>0 else 0.0
    kappa_acc=c*c*kappa_geom
    temp=hbar*c*kappa_geom/(2*pi*k)
    entropy=k*c**3*area/(4*G*hbar)
    return CalculationResult('kerr_thermodynamics','thermodynamics','ok',{
      'outer_horizon_over_rg':rp/rg,'inner_horizon_over_rg':rm/rg,
      'horizon_area_m2':area,'surface_gravity_m_s2':kappa_acc,
      'hawking_temperature_k':temp,'entropy_j_k':entropy,
      'extremality_gap_sqrt_1_minus_chi2':d,
    },('uncharged Kerr black hole','semiclassical Hawking/Bekenstein relations'))

def _g_boson(n):
    if n<=0: return 0.0
    return (n+1)*math.log2(n+1)-n*math.log2(n)

@calculation('bosonic_mode_information','information',description='Thermal bosonic mode entropy diagnostics')
def boson_info(i):
    if min(i.emitted_hz,i.system_temperature_k)>0:
        x=h*i.emitted_hz/(k*i.system_temperature_k)
    else:
        raise ValueError('frequency and temperature must be positive')
    n=1/math.expm1(x) if x<700 else 0.0
    return CalculationResult('bosonic_mode_information','information','ok',{
      'mean_thermal_occupation':n,
      'thermal_entropy_bits_per_mode':_g_boson(n),
      'vacuum_plus_thermal_quanta':n+0.5,
      'dimensionless_hf_over_kT':x,
    },('single ideal bosonic mode in thermal equilibrium',))

@calculation('planck_scale_ratios','diagnostics',description='Dimensionless separation from Planck scales')
def planck_ratios(i):
    lp=math.sqrt(hbar*G/c**3); tp=lp/c; mp=math.sqrt(hbar*c/G)
    M=_M(i); rs=_rs(i)
    return CalculationResult('planck_scale_ratios','diagnostics','ok',{
      'schwarzschild_radius_over_planck_length':rs/lp,
      'mass_over_planck_mass':M/mp,
      'light_crossing_over_planck_time':(rs/c)/tp,
      'planck_length_m':lp,'planck_time_s':tp,'planck_mass_kg':mp,
    },('CODATA constants via scipy.constants',))
