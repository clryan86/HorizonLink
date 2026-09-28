# HorizonLink model notes

HorizonLink is a research sandbox, not evidence that information can be sent out of a classical black-hole event horizon. Every model is tagged mentally as one of three levels: established equation, simplified analogue, or speculative toy model.

## Schwarzschild exterior model

`horizonlink.horizons.schwarzschild` implements standard equations for an idealized non-rotating, uncharged black hole:

- Schwarzschild radius: `r_s = 2GM/c^2`
- Static gravitational frequency factor outside the horizon: `sqrt(1-r_s/r)`
- An outgoing radial-light coordinate-time expression in Schwarzschild coordinates

The helpers reject radii at or below the event horizon. The static-emitter idealization also becomes physically extreme as `r -> r_s`; an observer cannot remain static at the horizon with finite proper acceleration.

## Kerr rotating-horizon model

`horizonlink.horizons.kerr` adds standard idealized Kerr geometry for an uncharged rotating black hole. It uses the dimensionless spin parameter

`chi = cJ/(GM^2)`, with `|chi| <= 1`.

Current helpers calculate:

- gravitational radius `r_g = GM/c^2`;
- outer and inner Boyer-Lindquist horizon radii `r_+` and `r_-`;
- outer static-limit radius as a function of polar angle;
- horizon angular velocity.

The region between the outer horizon and outer static limit is the ergoregion. These helpers describe geometry only. They do not yet integrate photon geodesics, calculate lensing, model locally non-rotating observers, or provide a full Kerr radiative-transfer calculation.

## Exterior link budget

`horizonlink.horizons.link_budget` multiplies two deliberately separable effects:

1. a distant-observer redshift power factor `(1-r_s/r)`;
2. an isotropic geometric collecting fraction `A/(4*pi*d^2)`.

The collecting-area form is intentional. It avoids hiding wavelength-dependent antenna assumptions inside the gravitational calculation. Real links require detector efficiency, background noise, lensing, orbital dynamics, pointing, bandwidth, polarization, plasma, and relativistic transfer calculations.

## Classical channel baselines

The erasure, binary-symmetric, and additive-white-Gaussian-noise helpers are information-theory reference channels. They let experiments compare a speculative mapping against well-understood capacities and error rates.

## Quantum-information models

`horizonlink.quantum` and `horizonlink.protocols.teleportation` implement small, auditable NumPy models for standard quantum-information concepts:

- pure qubit and Bell states;
- density matrices and pure-state fidelity;
- Pauli depolarizing noise;
- a standard three-qubit teleportation protocol;
- noisy Bell-resource experiments;
- noisy two-bit classical correction channels;
- purity, von Neumann entropy, partial trace, and a standard CHSH diagnostic.

Teleportation does not permit faster-than-light communication. Alice's two classical measurement bits are still required before Bob can select the correct Pauli operation. HorizonLink models those classical bits explicitly so that a quantum-resource advantage cannot silently bypass an ordinary communication constraint.

## Hayden–Preskill-inspired recovery

The recovery model in `horizonlink.protocols` is an information-recovery analogue inspired by black-hole information thought experiments. It is not a literal engineering protocol for transmitting a chosen message from behind an event horizon.

## What would count as useful progress?

Useful results include:

- a toy model reproducing a known analytical limit;
- a clear no-go region where recoverable information vanishes;
- an analogue-system experiment whose assumptions are measurable;
- a robust numerical discrepancy that can be traced to a specific physical assumption;
- a testable prediction that differs between two models.

A surprising numerical output alone is not evidence of new physics.
