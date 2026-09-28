"""Test the mass-scaling prediction of the HorizonLink mode law.

If a Schwarzschild fixed-local-frequency scalar channel has asymptotic
capacity-latency slope

    d ln C / dT = -2(l+2) kappa,

then for Schwarzschild kappa=c^3/(4GM). Therefore the physical e-folding time
of capacity loss should be

    tau_C = 1/[2(l+2)kappa] = 2GM/[(l+2)c^3].

The dimensionless product

    (-d ln C/dT) * GM/c^3 = (l+2)/2

should collapse across black-hole masses. This script generates the predicted
physical scales and checks the dimensionless collapse. It is a prediction of
the asymptotic law, not an independent empirical validation.
"""
from __future__ import annotations
import argparse

G=6.67430e-11
C=299792458.0
M_SUN=1.98847e30

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--masses-solar',default='10,30,100,4300000,6500000000')
    ap.add_argument('--ells',default='0,1,2')
    args=ap.parse_args()
    print('mass_solar,ell,kappa_per_s,slope_per_s,tau_capacity_s,dimensionless_slope')
    for ms in [float(x) for x in args.masses_solar.split(',')]:
        M=ms*M_SUN
        tM=G*M/C**3
        kappa=1.0/(4.0*tM)
        for ell in [int(x) for x in args.ells.split(',')]:
            slope=-2.0*(ell+2)*kappa
            tau=1.0/abs(slope)
            collapsed=(-slope)*tM
            print(f'{ms:.12g},{ell},{kappa:.12e},{slope:.12e},{tau:.12e},{collapsed:.12e}')
    print('Expected dimensionless collapse: (ell+2)/2, independent of mass.')

if __name__=='__main__': main()
