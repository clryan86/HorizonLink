"""Fifth analytic pack: communications, integration, photon-rate, and spectral-efficiency diagnostics."""
from __future__ import annotations
import math
from scipy.constants import h
from horizonlink.horizons.schwarzschild import M_SUN,schwarzschild_radius
from horizonlink.horizons.link_budget import horizon_link_fraction
from horizonlink.detectors.radiometer import power_snr,integrated_radiometer_snr,required_integration_time,thermal_noise_power
from horizonlink.channels.gaussian import capacity_from_snr
from .registry import calculation,CalculationResult

def _received(i):
    m=i.mass_solar*M_SUN; rs=schwarzschild_radius(m); r=i.emitter_radius_rs*rs
    frac=horizon_link_fraction(m,r,i.receiver_distance_m,i.aperture_area_m2)
    return i.transmitter_power_w*frac

@calculation('communications_analysis','communications',description='Unified link/SNR/capacity and integration diagnostics')
def communications(i):
    if min(i.bandwidth_hz,i.system_temperature_k,i.integration_time_s,i.emitted_hz)<=0:
        raise ValueError('bandwidth, temperature, integration time, and carrier frequency must be positive')
    pr=_received(i)
    noise=thermal_noise_power(i.system_temperature_k,i.bandwidth_hz)
    snr=power_snr(pr,i.system_temperature_k,i.bandwidth_hz)
    isnr=integrated_radiometer_snr(pr,i.system_temperature_k,i.bandwidth_hz,i.integration_time_s)
    cap=capacity_from_snr(snr,i.bandwidth_hz)
    eta=cap/i.bandwidth_hz
    eph=h*i.emitted_hz
    photon_rate=pr/eph if eph>0 else 0.0
    eb=pr/cap if cap>0 else math.inf
    ebn0=snr/eta if eta>0 else math.inf
    req=required_integration_time(pr,i.system_temperature_k,i.bandwidth_hz,i.target_snr) if pr>0 and i.target_snr>0 else math.inf
    return CalculationResult('communications_analysis','communications','ok',{
      'received_power_w':pr,'noise_power_w':noise,'instantaneous_snr':snr,
      'integrated_snr':isnr,'shannon_capacity_bits_s':cap,'spectral_efficiency_bits_s_hz':eta,
      'received_photon_rate_s_inv':photon_rate,'received_energy_per_capacity_bit_j':eb,
      'capacity_eb_over_n0':ebn0,'required_integration_time_for_target_snr_s':req,
      'target_snr':i.target_snr,
    },('AWGN Shannon capacity','idealized radiometer integration','photon-rate comparison uses carrier photon energy',))

@calculation('communications_dimensionless','diagnostics',description='Dimensionless communication ratios for discovery sweeps')
def comm_dim(i):
    if min(i.bandwidth_hz,i.emitted_hz,i.integration_time_s)>0:
        pass
    else: raise ValueError('positive signal inputs required')
    pr=_received(i)
    snr=power_snr(pr,i.system_temperature_k,i.bandwidth_hz)
    cap=capacity_from_snr(snr,i.bandwidth_hz)
    eta=cap/i.bandwidth_hz
    return CalculationResult('communications_dimensionless','diagnostics','ok',{
      'fractional_bandwidth':i.bandwidth_hz/i.emitted_hz,
      'time_bandwidth_product':i.integration_time_s*i.bandwidth_hz,
      'spectral_efficiency':eta,'snr_per_hz_ratio':snr/i.bandwidth_hz,
      'capacity_per_carrier_hz':cap/i.emitted_hz,
      'log1p_snr':math.log1p(snr),
    },('diagnostic dimensionless combinations',))
