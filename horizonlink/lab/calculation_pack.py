"""Broad, dependency-light calculation pack for the unified HorizonLink Lab.

These are established analytic calculations and diagnostic transforms. More
expensive numerical/QFT engines remain separate until individually validated.
"""
from __future__ import annotations
import math
from scipy.constants import G,c,hbar,k,pi
from .registry import calculation,CalculationResult
from horizonlink.horizons.schwarzschild import M_SUN

def _mass(i): return i.mass_solar*M_SUN

def _rs(i): return 2*G*_mass(i)/c**2

def _r(i): return i.emitter_radius_rs*_rs(i)

@calculation('schwarzschild_thermodynamics','thermodynamics',description='Surface gravity, Hawking temperature, area and entropy')
def schwarzschild_thermo(i):
    M=_mass(i); rs=_rs(i); kap=c**4/(4*G*M); T=hbar*c**3/(8*pi*G*M*k); A=4*pi*rs**2; S=k*c**3*A/(4*G*hbar)
    return CalculationResult('schwarzschild_thermodynamics','thermodynamics','ok',{
      'surface_gravity_m_s2':kap,'hawking_temperature_k':T,'horizon_area_m2':A,'bekenstein_hawking_entropy_j_k':S,
      'light_crossing_time_s':rs/c,'mass_energy_j':M*c**2},('Schwarzschild black hole','semiclassical Hawking/Bekenstein relations'))

@calculation('local_static_observer','observers',description='Static-observer redshift, acceleration and Tolman temperature')
def static_observer(i):
    rs=_rs(i); r=_r(i); f=1-rs/r
    if f<=0: raise ValueError('static observer requires r>r_s')
    z=1/math.sqrt(f)-1; aproper=G*_mass(i)/(r*r*math.sqrt(f)); TH=hbar*c**3/(8*pi*G*_mass(i)*k)
    return CalculationResult('local_static_observer','observers','ok',{
      'metric_f':f,'redshift_z':z,'clock_rate_dtaudt':math.sqrt(f),'proper_acceleration_m_s2':aproper,
      'tolman_temperature_k':TH/math.sqrt(f)},('static Schwarzschild observer',))

@calculation('photon_scales','geometry',description='Photon sphere, critical impact parameter and ISCO scales')
def photon_scales(i):
    rs=_rs(i); Mgeom=rs/2
    return CalculationResult('photon_scales','geometry','ok',{
      'photon_sphere_radius_m':1.5*rs,'isco_radius_m':3*rs,'critical_impact_parameter_m':3*math.sqrt(3)*Mgeom,
      'photon_sphere_radius_over_rs':1.5,'isco_radius_over_rs':3.0},('Schwarzschild geodesics',))

@calculation('wave_scales','waves',description='Wavelength, angular frequency and dimensionless black-hole frequency')
def wave_scales(i):
    nu=i.emitted_hz
    if nu<=0: raise ValueError('frequency must be positive')
    rs=_rs(i); omega=2*pi*nu
    return CalculationResult('wave_scales','waves','ok',{
      'wavelength_m':c/nu,'angular_frequency_rad_s':omega,'omega_rs_over_c':omega*rs/c,
      'cycles_per_light_crossing':nu*rs/c,'photon_energy_j':6.62607015e-34*nu},())

@calculation('receiver_quantum_limits','communications',description='Classical/quantum receiver noise diagnostics')
def receiver_quantum(i):
    nu=i.emitted_hz; B=i.bandwidth_hz; T=i.system_temperature_k
    if min(nu,B,T)<=0: raise ValueError('frequency, bandwidth and temperature must be positive')
    x=6.62607015e-34*nu/(k*T); nth=1/math.expm1(x) if x<700 else 0.0
    return CalculationResult('receiver_quantum_limits','communications','ok',{
      'hf_over_kT':x,'thermal_photon_occupation':nth,'quantum_noise_temperature_k':6.62607015e-34*nu/k,
      'classical_kTB_w':k*T*B,'one_photon_per_mode_power_w':6.62607015e-34*nu*B},('single-frequency bosonic occupation diagnostic',))

@calculation('information_scales','information',description='Bit energy and thermal information scales')
def info_scales(i):
    T=i.system_temperature_k; B=i.bandwidth_hz
    if min(T,B)<=0: raise ValueError('temperature and bandwidth must be positive')
    landauer=k*T*math.log(2)
    return CalculationResult('information_scales','information','ok',{
      'landauer_energy_per_bit_j':landauer,'thermal_energy_j':k*T,'thermal_rate_scale_bits_s':k*T/(6.62607015e-34),
      'bandwidth_time_product_per_second':B},('Landauer bound is a thermodynamic lower bound, not receiver consumption',))

@calculation('dimensionless_state','diagnostics',description='Dimensionless groups useful for cross-scale discovery')
def dimensionless(i):
    rs=_rs(i); r=_r(i); f=1-rs/r; M=_mass(i); TH=hbar*c**3/(8*pi*G*M*k)
    return CalculationResult('dimensionless_state','diagnostics','ok',{
      'radius_over_rs':r/rs,'horizon_offset_over_rs':(r-rs)/rs,'compactness_rs_over_r':rs/r,
      'redshift_factor':math.sqrt(f) if f>=0 else float('nan'),'hawking_to_receiver_temperature':TH/i.system_temperature_k,
      'receiver_distance_over_rs':i.receiver_distance_m/rs,'aperture_over_rs_squared':i.aperture_area_m2/(rs*rs),
      'bandwidth_over_carrier':i.bandwidth_hz/i.emitted_hz},('dimensionless diagnostics only',))
