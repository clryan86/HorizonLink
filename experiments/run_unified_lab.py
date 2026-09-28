"""Run one HorizonLink scenario through the unified calculation registry.

Example:
  python experiments/run_unified_lab.py --mass-solar 10 --spin 0.9 --radius-rs 1.01

New calculation methods should register through horizonlink.lab.registry rather
than being wired directly into this script. This keeps the lab extensible.
"""
from __future__ import annotations
import argparse, json
from horizonlink.lab import LabInput, run_lab


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--mass-solar',type=float,default=10.0)
    p.add_argument('--spin',type=float,default=0.0)
    p.add_argument('--radius-rs',type=float,default=1.01)
    p.add_argument('--receiver-distance-m',type=float,default=1e9)
    p.add_argument('--emitted-hz',type=float,default=1e9)
    p.add_argument('--transmitter-power-w',type=float,default=1.0)
    p.add_argument('--aperture-area-m2',type=float,default=1.0)
    p.add_argument('--bandwidth-hz',type=float,default=1e6)
    p.add_argument('--system-temperature-k',type=float,default=50.0)
    a=p.parse_args()
    inp=LabInput(
        mass_solar=a.mass_solar, spin_chi=a.spin, emitter_radius_rs=a.radius_rs,
        receiver_distance_m=a.receiver_distance_m, emitted_hz=a.emitted_hz,
        transmitter_power_w=a.transmitter_power_w, aperture_area_m2=a.aperture_area_m2,
        bandwidth_hz=a.bandwidth_hz, system_temperature_k=a.system_temperature_k,
    )
    print(json.dumps(run_lab(inp).as_dict(),indent=2,sort_keys=True,allow_nan=False))

if __name__=='__main__': main()
