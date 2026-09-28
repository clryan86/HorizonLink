# HorizonLink discovery standard

This file defines what must be true before HorizonLink describes a result as a scientific discovery.

## Candidate result currently under test

In the idealized exterior Schwarzschild + low-SNR AWGN model, let

- epsilon = (r-r_s)/r_s > 0
- C be the low-SNR Shannon rate after gravitational power redshift
- T = t/(r_s/c) be the dimensionless outgoing radial Schwarzschild coordinate delay
- Q = ln(C) + T

Then, after subtracting the horizon-limit constant,

    R(epsilon) = Q(epsilon)-Q(0) = -ln(1+epsilon)-epsilon

and hence

    lim epsilon->0+ R(epsilon)/epsilon = -2.

This is an exact consequence of the assumptions above. It is not presently claimed as new physics.

## Questions that must be answered

1. Correctness: Is the derivation algebraically correct and reproduced independently by symbolic and numerical implementations?
2. Coordinate dependence: Does a physically operational formulation preserve a nontrivial relation, or is the result merely a Schwarzschild-coordinate construction?
3. Model dependence: Does the relation survive exact Shannon capacity instead of the low-SNR approximation, realistic bandwidth transformations, photon counting/bosonic channels, propagation loss, and noise?
4. Observer dependence: Which clocks and frequency/power measurements are local, and which are defined at infinity?
5. Generality: Is there an analogue for generic non-extremal horizons, Reissner-Nordstrom, and Kerr, naturally expressed through surface gravity kappa?
6. Extremal limit: What happens as kappa -> 0, where ordinary non-extremal near-horizon logarithmic scaling changes?
7. Literature novelty: Has the exact relation, an equivalent theorem, or its operational content already appeared in GR/relativistic quantum information/communication literature?
8. Utility: Does the relation predict an independently measurable quantity or improve inference/design beyond rewriting known redshift and null-delay formulas?
9. Reproducibility: Can an independent implementation reproduce every figure/table from declared assumptions?
10. External scrutiny: Has a qualified researcher independently checked the derivation and novelty claim?

## Claim levels

- Level 0: numerical pattern
- Level 1: exact identity inside a stated model
- Level 2: robust cross-model scaling law
- Level 3: apparently novel theoretical result after systematic literature review
- Level 4: externally checked preprint/result
- Level 5: peer-reviewed discovery or independently observed effect

Current status: **Level 1**.

No repository text should call this an official scientific discovery until at least Level 4, and experimental discovery language requires Level 5 plus independent empirical evidence.
