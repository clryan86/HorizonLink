"""Computational provenance and trivial-dependency filtering for HorizonLink Lab.

A numerically perfect relationship is uninteresting when both outputs are
algebraically tied to the same immediate calculation. Provenance metadata lets
the discovery pipeline distinguish shared ancestry from more independent paths.
This is a ranking heuristic, not a proof of independence or novelty.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict

@dataclass(frozen=True)
class Provenance:
    field: str
    engine: str
    family: str
    direct_inputs: tuple[str,...]=()
    parents: tuple[str,...]=()
    formula_tag: str|None=None
    def as_dict(self): return asdict(self)

# Initial catalog for outputs currently exposed by the unified runner.
CATALOG={
 'schwarzschild_geometry.radius_m':Provenance('schwarzschild_geometry.radius_m','schwarzschild_geometry','geometry',('mass_solar',),formula_tag='schwarzschild_radius'),
 'schwarzschild_geometry.emitter_radius_m':Provenance('schwarzschild_geometry.emitter_radius_m','schwarzschild_geometry','geometry',('mass_solar','emitter_radius_rs'),('schwarzschild_geometry.radius_m',),'radius_scaling'),
 'schwarzschild_geometry.redshift_factor_squared':Provenance('schwarzschild_geometry.redshift_factor_squared','schwarzschild_geometry','geometry',('emitter_radius_rs',),('schwarzschild_geometry.radius_m','schwarzschild_geometry.emitter_radius_m'),'schwarzschild_f'),
 'kerr_geometry.outer_horizon_m':Provenance('kerr_geometry.outer_horizon_m','kerr_geometry','geometry',('mass_solar','spin_chi'),formula_tag='kerr_horizon'),
 'kerr_geometry.inner_horizon_m':Provenance('kerr_geometry.inner_horizon_m','kerr_geometry','geometry',('mass_solar','spin_chi'),formula_tag='kerr_horizon'),
 'kerr_geometry.horizon_angular_velocity_rad_s':Provenance('kerr_geometry.horizon_angular_velocity_rad_s','kerr_geometry','geometry',('mass_solar','spin_chi'),('kerr_geometry.outer_horizon_m',),'kerr_omega_h'),
 'exterior_link.redshifted_frequency_hz':Provenance('exterior_link.redshifted_frequency_hz','exterior_link','communications',('mass_solar','emitter_radius_rs','emitted_hz'),formula_tag='redshift_frequency'),
 'exterior_link.received_power_fraction':Provenance('exterior_link.received_power_fraction','exterior_link','communications',('mass_solar','emitter_radius_rs','receiver_distance_m','aperture_area_m2'),formula_tag='link_fraction'),
 'exterior_link.received_power_w':Provenance('exterior_link.received_power_w','exterior_link','communications',('transmitter_power_w',),('exterior_link.received_power_fraction',),'received_power'),
 'exterior_link.thermal_noise_power_w':Provenance('exterior_link.thermal_noise_power_w','exterior_link','communications',('system_temperature_k','bandwidth_hz'),formula_tag='kTB'),
 'exterior_link.power_snr':Provenance('exterior_link.power_snr','exterior_link','communications',(),('exterior_link.received_power_w','exterior_link.thermal_noise_power_w'),'snr_ratio'),
 'exterior_link.shannon_capacity_bits_per_second':Provenance('exterior_link.shannon_capacity_bits_per_second','exterior_link','communications',('bandwidth_hz',),('exterior_link.power_snr',),'shannon_awgn'),
}

def ancestors(field:str)->set[str]:
    seen=set(); stack=[field]
    while stack:
        cur=stack.pop()
        p=CATALOG.get(cur)
        if not p: continue
        for parent in p.parents:
            if parent not in seen:
                seen.add(parent); stack.append(parent)
    return seen

def assess_pair(x:str,y:str)->dict:
    px,py=CATALOG.get(x),CATALOG.get(y)
    if not px or not py:
        return {'classification':'unknown','independence_score':0.5,'reason':'provenance not cataloged'}
    ax,ay=ancestors(x),ancestors(y)
    if x in ay or y in ax:
        return {'classification':'direct_dependency','independence_score':0.0,'reason':'one output is an ancestor of the other'}
    shared=ax & ay
    same_formula=px.formula_tag is not None and px.formula_tag==py.formula_tag
    if same_formula:
        return {'classification':'same_formula_family','independence_score':0.05,'reason':f'shared formula tag {px.formula_tag}'}
    if px.engine==py.engine:
        return {'classification':'same_engine','independence_score':0.25,'reason':'outputs produced by the same calculation engine','shared_ancestors':sorted(shared)}
    if shared:
        return {'classification':'shared_ancestry','independence_score':0.5,'reason':'different engines but shared computational ancestors','shared_ancestors':sorted(shared)}
    if px.family==py.family:
        return {'classification':'same_family_independent_engines','independence_score':0.7,'reason':'different engines in the same broad physics family'}
    return {'classification':'cross_family','independence_score':1.0,'reason':'catalog shows distinct engines/families with no shared output ancestry'}

def rank_candidate(candidate:dict)->dict:
    prov=assess_pair(candidate['x'],candidate['y'])
    numerical=float(candidate.get('score',0.0))
    independence=float(prov['independence_score'])
    # Independence gates a perfect numerical fit instead of merely adding to it.
    interest=numerical*independence
    return {**candidate,'provenance':prov,'interest_score':interest,
            'screening_label':('low_triviality_risk' if independence>=0.7 else 'dependency_review_required')}
