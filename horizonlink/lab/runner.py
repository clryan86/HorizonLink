"""One-input / many-calculation HorizonLink research runner."""
from __future__ import annotations
from dataclasses import asdict,dataclass
from typing import Any
from horizonlink.horizons.kerr import horizon_angular_velocity,horizon_radii
from horizonlink.horizons.link_budget import horizon_link_fraction,redshifted_frequency
from horizonlink.horizons.schwarzschild import M_SUN,schwarzschild_radius
from horizonlink.channels.gaussian import capacity_from_snr
from horizonlink.detectors.radiometer import power_snr,thermal_noise_power
from .registry import CalculationResult,calculation,registry

@dataclass(frozen=True)
class LabInput:
    mass_solar:float=10.0; spin_chi:float=0.0; charge_ratio_qm:float=0.0; emitter_radius_rs:float=1.01
    receiver_distance_m:float=1e9; emitted_hz:float=1e9; transmitter_power_w:float=1.0
    aperture_area_m2:float=1.0; bandwidth_hz:float=1e6; system_temperature_k:float=50.0; integration_time_s:float=1.0; target_snr:float=5.0

@dataclass(frozen=True)
class LabReport:
    inputs:dict[str,Any]; summary:dict[str,Any]; calculations:tuple[CalculationResult,...]
    def as_dict(self): return {'inputs':self.inputs,'summary':self.summary,'calculations':[asdict(x) for x in self.calculations]}

@calculation('schwarzschild_geometry','geometry',description='Basic Schwarzschild horizon geometry')
def _schwarzschild(inp):
    m=inp.mass_solar*M_SUN; rs=schwarzschild_radius(m); r=inp.emitter_radius_rs*rs; f=1-rs/r
    return CalculationResult('schwarzschild_geometry','geometry','ok',{'radius_m':rs,'emitter_radius_m':r,'redshift_factor_squared':f},('non-rotating Schwarzschild comparison model',))

@calculation('kerr_geometry','geometry',description='Kerr horizon radii and rotation')
def _kerr(inp):
    m=inp.mass_solar*M_SUN; rp,rm=horizon_radii(m,inp.spin_chi)
    return CalculationResult('kerr_geometry','geometry','ok',{'outer_horizon_m':rp,'inner_horizon_m':rm,'horizon_angular_velocity_rad_s':horizon_angular_velocity(m,inp.spin_chi)},('uncharged Kerr exterior',))

@calculation('exterior_link','communications',description='Exterior redshift/geometric link budget')
def _link(inp):
    m=inp.mass_solar*M_SUN; rs=schwarzschild_radius(m); r=inp.emitter_radius_rs*rs
    frac=horizon_link_fraction(m,r,inp.receiver_distance_m,inp.aperture_area_m2); pr=inp.transmitter_power_w*frac
    snr=power_snr(pr,inp.system_temperature_k,inp.bandwidth_hz)
    return CalculationResult('exterior_link','communications','ok',{'redshifted_frequency_hz':redshifted_frequency(m,r,inp.emitted_hz),'received_power_fraction':frac,'received_power_w':pr,'thermal_noise_power_w':thermal_noise_power(inp.system_temperature_k,inp.bandwidth_hz),'power_snr':snr,'shannon_capacity_bits_per_second':capacity_from_snr(snr,inp.bandwidth_hz)},('toy exterior link','Rayleigh-Jeans kTB receiver noise','AWGN Shannon capacity'))

def _load_packs():
    # Import for registration. Keeping this explicit prevents hidden plugin magic
    # and makes a failed optional pack easy to diagnose.
    from . import calculation_pack  # noqa:F401
    from . import calculation_pack_astro  # noqa:F401
    from . import calculation_pack_horizon  # noqa:F401
    from . import calculation_pack_charge  # noqa:F401

def run_lab(inp:LabInput)->LabReport:
    _load_packs(); results=[]
    for item in registry.all():
        try: results.append(item.run(inp))
        except Exception as exc: results.append(CalculationResult(item.name,item.category,'error',error=f'{type(exc).__name__}: {exc}'))
    ok=sum(r.status=='ok' for r in results)
    summary={'calculations_registered':len(results),'calculations_succeeded':ok,'calculations_failed':len(results)-ok,'categories':sorted({r.category for r in results}),'purpose':'single scenario evaluated by every compatible registered calculation'}
    return LabReport(asdict(inp),summary,tuple(results))
