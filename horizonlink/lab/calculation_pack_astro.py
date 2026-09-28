"""Second analytic calculation pack: orbital, radiative, timescale and information diagnostics."""
from __future__ import annotations
import math
from scipy.constants import G,c,h,k,pi,sigma
from .registry import calculation,CalculationResult
from horizonlink.horizons.schwarzschild import M_SUN

def M(i): return i.mass_solar*M_SUN
def rs(i): return 2*G*M(i)/c**2
def r(i): return i.emitter_radius_rs*rs(i)

@calculation('orbital_scales','dynamics',description='Schwarzschild circular-orbit diagnostics')
def orbital(i):
    R=r(i)
    if R<=1.5*rs(i): raise ValueError('circular timelike orbit diagnostics require r>1.5 r_s')
    omega=math.sqrt(G*M(i)/R**3)
    period=2*pi/omega
    v_newton=math.sqrt(G*M(i)/R)
    return CalculationResult('orbital_scales','dynamics','ok',{
      'kepler_angular_frequency_rad_s':omega,'kepler_period_s':period,
      'newtonian_orbital_speed_m_s':v_newton,'orbital_speed_over_c':v_newton/c,
      'period_over_light_crossing':period/(rs(i)/c)},('diagnostic orbital scales; Newtonian speed is only a comparison quantity',))

@calculation('radiative_scales','thermodynamics',description='Blackbody comparison luminosity at Hawking temperature')
def radiative(i):
    MM=M(i); R=rs(i)
    T=h*c**3/(16*pi*pi*G*MM*k)  # h=2pi hbar
    A=4*pi*R**2
    L=sigma*A*T**4
    return CalculationResult('radiative_scales','thermodynamics','ok',{
      'blackbody_comparison_luminosity_w':L,'hawking_temperature_k_rederived':T,
      'mass_loss_rate_blackbody_kg_s':-L/c**2,
      'evaporation_timescale_comparison_s':MM*c**2/L},('blackbody horizon-area comparison; greybody corrections omitted',))

@calculation('signal_timescales','communications',description='Carrier, bandwidth and light-travel timescales')
def times(i):
    if min(i.emitted_hz,i.bandwidth_hz,i.receiver_distance_m)<=0: raise ValueError('positive inputs required')
    return CalculationResult('signal_timescales','communications','ok',{
      'carrier_period_s':1/i.emitted_hz,'bandwidth_coherence_time_s':1/i.bandwidth_hz,
      'receiver_light_travel_time_s':i.receiver_distance_m/c,
      'receiver_distance_light_crossings':i.receiver_distance_m/rs(i),
      'carrier_cycles_to_receiver':i.emitted_hz*i.receiver_distance_m/c},())

@calculation('entropy_information','information',description='Entropy converted to idealized information counts')
def entropy_info(i):
    A=4*pi*rs(i)**2
    S=k*c**3*A/(4*G*(h/(2*pi)))
    bits=S/(k*math.log(2))
    return CalculationResult('entropy_information','information','ok',{
      'horizon_entropy_bits':bits,'bits_per_square_meter':bits/A,
      'bits_per_solar_mass_squared':bits/(i.mass_solar**2),
      'sqrt_bits':math.sqrt(bits)},('Bekenstein-Hawking thermodynamic entropy expressed in bits',))

@calculation('frequency_redshift_diagnostics','waves',description='Local/asymptotic frequency diagnostics near Schwarzschild horizon')
def freqdiag(i):
    R=r(i); f=1-rs(i)/R
    if f<=0: raise ValueError('requires exterior radius')
    g=math.sqrt(f); ninf=i.emitted_hz*g
    return CalculationResult('frequency_redshift_diagnostics','waves','ok',{
      'g_factor':g,'frequency_at_infinity_hz':ninf,'local_to_infinity_period_ratio':1/g,
      'photon_energy_at_infinity_j':h*ninf,'fractional_energy_retained':g},('static emitter in Schwarzschild spacetime',))

@calculation('receiver_sensitivity_scales','communications',description='Receiver sensitivity and photon-count comparisons')
def sensitivity(i):
    if min(i.emitted_hz,i.bandwidth_hz,i.system_temperature_k)<=0: raise ValueError('positive receiver inputs required')
    pnoise=k*i.system_temperature_k*i.bandwidth_hz
    eph=h*i.emitted_hz
    return CalculationResult('receiver_sensitivity_scales','communications','ok',{
      'noise_equivalent_photons_per_second':pnoise/eph,
      'noise_photons_per_bandwidth_time':pnoise/eph/i.bandwidth_hz,
      'energy_per_bandwidth_interval_j':pnoise/i.bandwidth_hz,
      'photon_energy_over_kT':eph/(k*i.system_temperature_k)},('classical kTB comparison expressed in photon units',))
