# HorizonLink model notes

HorizonLink is a research sandbox, not evidence that information can be sent out of a classical black-hole event horizon. Models are classified explicitly as one of three levels:

| Level | Meaning |
|---|---|
| **Established** | Standard equation used within its stated domain and assumptions |
| **Analogue / simplified** | Useful abstraction that does not reproduce the full physical system |
| **Speculative toy** | Deliberately uncalibrated hypothesis/proxy requiring separate validation |

## Schwarzschild exterior model — Established

`horizonlink.horizons.schwarzschild` implements standard equations for an idealized non-rotating, uncharged black hole:

- Schwarzschild radius: `r_s = 2GM/c^2`;
- static gravitational frequency factor outside the horizon: `sqrt((r-r_s)/r)`;
- exact Schwarzschild coordinate-time interval for an outgoing radial null ray.

The coordinate-time result includes the flat-space propagation term. It is not a local observer's proper time and it is not only the excess gravitational delay. The helpers reject radii at or below the event horizon. The static-emitter idealization also becomes physically extreme as `r -> r_s`; an observer cannot remain static at the horizon with finite proper acceleration.

Reference: Sean Carroll, *Lecture Notes on General Relativity*, Schwarzschild geometry discussion: https://arxiv.org/abs/gr-qc/9712019

## Kerr rotating-horizon model — Established

`horizonlink.horizons.kerr` implements standard idealized Kerr geometry for an uncharged rotating black hole. It uses

`chi = cJ/(GM^2)`, with `|chi| <= 1`.

Current helpers calculate:

- gravitational radius `r_g = GM/c^2`;
- outer and algebraic inner Boyer-Lindquist roots `r_+` and `r_-`;
- outer static-limit radius as a function of polar angle;
- horizon angular velocity;
- ZAMO frame-dragging angular velocity outside the outer horizon.

At `chi=0`, the algebraic inner root is zero and should not be interpreted as a regular Schwarzschild inner Cauchy horizon. The ZAMO angular velocity evaluated at `r_+` is a limiting horizon value; it does not describe a timelike observer remaining on the horizon.

Reference: Matt Visser, *The Kerr spacetime: A brief introduction*: https://arxiv.org/abs/0706.0622

## Exterior link budget — Simplified analogue

`horizonlink.horizons.link_budget` combines two deliberately separable effects:

1. a receiver-at-infinity redshift power factor `(1-r_s/r)`;
2. an isotropic Euclidean collecting fraction `A/(4*pi*d^2)`.

`distance_m` is an independent spreading distance used only by the geometric toy term; it is not a Schwarzschild receiver radius. Emitted power is interpreted per unit proper time of a static emitter. The model omits photon capture/escape cones, lensing, aperture orientation, detector efficiency, pointing, plasma, orbital dynamics, polarization, and finite-receiver gravitational frequency shifts.

This helper is therefore a deliberately simplified detectability model, not a complete near-horizon radiative-transfer calculation.

## Classical channel baselines — Established information theory

The erasure, binary-symmetric, and additive-white-Gaussian-noise helpers are reference channels. They provide known capacities and error behavior against which toy mappings can be compared.

- Binary erasure capacity: `1-p` bits/use.
- Binary symmetric capacity: `1-H2(p)` bits/use for the full interval `0 <= p <= 1`.
- AWGN Shannon-Hartley capacity: `B log2(1+SNR)` bits/s.

Reference: Claude Shannon, *A Mathematical Theory of Communication*: https://people.math.harvard.edu/~ctm/home/text/others/shannon/entropy/entropy.pdf

## Quantum-information models — Established protocol + explicit noise models

`horizonlink.quantum` and `horizonlink.protocols.teleportation` implement small, auditable NumPy models for standard quantum-information concepts:

- pure qubit and Bell states;
- validated density matrices and pure-state fidelity;
- Pauli depolarizing noise;
- a standard three-qubit teleportation protocol;
- noisy Bell-resource experiments;
- noisy two-bit classical correction channels;
- purity, von Neumann entropy, partial trace, and one fixed-setting CHSH diagnostic.

For the implemented Pauli-error convention,

`D_p(rho) = (1-p)rho + p/3 (XrhoX + YrhoY + ZrhoZ)`.

Complete depolarization occurs at `p = 3/4`, not `p = 1`. At `p = 1` a non-identity Pauli is always applied uniformly.

Teleportation does not permit faster-than-light communication. Alice's two classical measurement bits are still required before Bob can select the correct Pauli operation. Failure to violate the single fixed CHSH setting implemented by HorizonLink does not prove that a state is separable.

Reference: John Preskill, quantum information / teleportation lecture material: https://www.preskill.caltech.edu/ph219/

## Hayden–Preskill-inspired recovery proxy — Speculative toy

`horizonlink.protocols.hayden_preskill.recovery_proxy_score` is an intentionally uncalibrated sigmoid proxy. The threshold `2 * message_qubits`, sigmoid shape, and `scrambling_strength` are modeling choices, not quantitative predictions of the Hayden–Preskill protocol.

The compatibility function name `recovery_probability` returns the same proxy but should not be interpreted as a calibrated physical probability.

A future genuine small-system recovery experiment should explicitly model a reference system, scrambling unitary, radiation partition, access to early radiation, decoder assumptions, and a recovery/decoupling metric.

Reference: Patrick Hayden and John Preskill, *Black holes as mirrors*: https://arxiv.org/abs/0708.4025

## What would count as useful progress?

Useful results include:

- a numerical implementation reproducing a known analytical limit;
- a documented no-go region where recoverable information vanishes;
- an analogue-system experiment whose assumptions are measurable;
- a robust numerical discrepancy traceable to a specific physical assumption;
- a testable prediction that differs between two clearly specified models.

A surprising numerical output alone is not evidence of new physics.
