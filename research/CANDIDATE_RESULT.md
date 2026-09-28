# HorizonLink candidate result: near-horizon capacity-delay exponent law

Status: candidate mathematical/communications result; **not yet a claimed new law of physics**.

## Statement
Let x be a regular radial distance parameter that vanishes linearly at a non-extremal stationary horizon, with surface gravity kappa > 0 and asymptotic outgoing delay

T(x) = -(1/(2 kappa)) ln x + T0 + o(1).

For a specified physical emitter/receiver/mode family, suppose the operational information rate or low-SNR capacity has leading behavior

C(x) = A x^p (1 + o(1)), A>0, p>0.

Then

I_p(x) = ln C(x) + 2 p kappa T(x)

has a finite x -> 0+ limit. Equivalently,

d ln C / dT -> -2 p kappa.

The differential form is preferred because additive time origins and multiplicative capacity normalizations drop out.

## What is nontrivial / what is not
The cancellation follows mathematically once the two asymptotic scalings are assumed; that part alone is not a new physical law. The potentially useful research content is operational: determine p from a fully specified relativistic communication channel, classify how p changes with observer motion, Kerr mode parameters, greybody transmission, detector model and near-criticality, and test whether the measured capacity-vs-latency slope is predicted by -2 p kappa.

## Known boundaries exposed by HorizonLink
1. Static/ZAMO-like low-SNR power scaling gives p approximately 1.
2. Radially freely falling Schwarzschild emitter sending outward can give p approximately 2, so the old p=1 expression is not observer universal.
3. In Kerr, generic modes are controlled by the horizon-frame frequency E - Omega_H L (or omega - m Omega_H for waves). Near the critical value, the redshift scaling changes and the generic p=1 class need not apply.
4. Extremal horizons have kappa=0 and a different delay singularity, so this non-extremal logarithmic universality class does not extend by naive substitution.

## Publication threshold
Before claiming novelty:
- derive p from a wave equation / transfer function rather than assuming it;
- include greybody/transmission factors and Kerr angular modes;
- demonstrate coordinate/time-normalization robustness of the differential statement;
- compare explicitly against black-hole channel-capacity, redshift, near-horizon critical-mode and communication-bound literature;
- produce independent numerical reproduction and error/convergence tests;
- state counterexamples and domain of validity;
- obtain external expert/peer scrutiny.

## Falsifiable prediction
For any non-extremal channel family whose independently calculated capacity obeys C ~ x^p, a fit of ln C versus asymptotic delay T sufficiently near the horizon should approach slope -2 p kappa. Failure after controlling numerical and model errors falsifies this formulation for that channel family.
