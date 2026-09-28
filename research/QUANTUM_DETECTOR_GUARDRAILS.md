# Quantum-detector guardrails for HorizonLink

## Why this file exists

The capacity-latency scaling program has reached a point where heuristic thermal-noise substitutions can easily overstate the physics. This note records what may and may not be treated as established before implementing a full Unruh-DeWitt (UDW) detector calculation.

## Supported statements

1. Static Schwarzschild detectors in the Hartle-Hawking state have a thermal response with the locally redshifted (Tolman) Hawking temperature. The local temperature diverges for an observer held static as the horizon is approached.
2. Horizon-crossing detector responses can remain finite for regular states/trajectories; the detailed response depends on the state, worldline, switching function, detector gap, coupling, dimension, and field.
3. A UDW response is determined by the pullback of the field Wightman function to the detector worldline, schematically

   F(Omega) = integral d tau d tau' chi(tau) chi(tau') exp[-i Omega(tau-tau')] W[x(tau),x(tau')].

   Therefore an effective communication-noise exponent must be extracted from a specified response calculation, not assigned solely from a local temperature slogan.

## Claims that HorizonLink must NOT make yet

- Do not claim that a freely falling detector has exactly b=0 in every quantum state.
- Do not identify detector excitation probability with additive Gaussian channel-noise power without an explicit receiver model.
- Do not claim that Hartle-Hawking, Unruh, and Boulware states have the same near-horizon operational noise.
- Do not claim that the previously proposed +1/2 noise correction is universal. It is a model-specific high-temperature/static-detector scaling hypothesis.
- Do not call the capacity-latency relation a new physical discovery until priority and independent derivation are established.

## Next calculation

Implement a controlled UDW benchmark before attempting full 3+1 Schwarzschild numerics:

1. Validate the detector integrator against an analytically thermal stationary trajectory.
2. Use smooth switching to avoid spurious switching divergences.
3. Compute response versus detector gap and observation duration.
4. Only after validation, insert Schwarzschild Wightman data for a specified state.
5. Convert detector response into an explicit communication receiver/noise model.
6. Fit the resulting SNR/capacity exponent blindly and compare its latency slope with the independently predicted geometric relation.

## Current status

The general asymptotic identity remains a conditional theorem: if a specified physical channel yields SNR ~ x^q with q>0 and a non-extremal horizon yields T ~ -(2 kappa)^(-1) ln x, exact Shannon capacity implies d ln C/dT -> -2 q kappa. The unresolved physics is the derivation of q for realistic transmitter/field/receiver/state combinations.
