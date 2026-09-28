# Roadmap

## v0.2 — reproducible research core

- [x] Schwarzschild exterior helpers
- [x] Erasure, binary-symmetric, and AWGN channel baselines
- [x] Hayden–Preskill-inspired recovery toy model
- [x] Grid search utilities
- [x] Reproducible Monte Carlo trials
- [x] Exterior-horizon link-budget model
- [x] Command-line interface
- [x] CSV experiment output
- [x] Optional plotting helpers
- [x] Automated tests and GitHub Actions

## v0.3 — quantum-information track

- [x] Add auditable NumPy qubit-state helpers
- [x] Implement standard three-qubit teleportation circuit
- [x] Add Bell-resource Pauli-noise model
- [x] Add teleportation fidelity sweep
- [x] Expose teleportation from the CLI
- [x] Add entanglement entropy helpers
- [x] Add Bell-state / CHSH diagnostics
- [x] Add explicit noisy classical side-channel models
- [x] Add a 2D quantum-resource / classical-channel fidelity surface
- [ ] Add small circuit diagrams to the documentation

## v0.4 — rotating horizons, detector design, and reproducibility

- [x] Add Kerr inner/outer horizon calculations
- [x] Add Kerr static-limit / ergosphere calculations
- [x] Add Kerr horizon angular velocity
- [x] Expose Kerr quantities from the CLI
- [x] Add frame-dragging/ZAMO angular-velocity profiles outside the horizon
- [x] Add thermal detector/background-noise baseline
- [x] Add end-to-end exterior-link detectability calculations
- [x] Add inverse design for transmitter power and maximum receiver distance
- [x] Add inverse design for collecting area and integration time
- [x] Add parameter-sweep persistence and experiment metadata
- [x] Add atomic output writes that preserve prior results after failed runs
- [x] Add versioned dashboard scenario exports
- [x] Add scenario replay/regression checks in the dashboard and CLI
- [x] Add package build/install smoke testing in CI
- [ ] Add error-correcting-code comparisons
- [ ] Add notebook examples that reproduce documented experiments
- [ ] Add confidence intervals and convergence diagnostics

## v0.5 — analogue horizons

- [ ] Acoustic-horizon toy model
- [ ] Optical analogue-horizon model interface
- [ ] Compare analogue observables against channel metrics
- [ ] Add datasets or synthetic fixtures with provenance

## Long-term research questions

1. Which information-channel abstractions are useful near relativistic horizons without smuggling in impossible signaling assumptions?
2. How quickly do classical communication resources degrade as a transmitter approaches an idealized horizon from outside?
3. Which black-hole-information thought experiments can be represented as reproducible circuits or stochastic models?
4. How do entanglement fidelity and ordinary classical-channel quality jointly constrain teleportation-style recovery protocols?
5. How does rotation change the geometry and observables available to exterior communication models?
6. Can analogue-horizon systems provide experimentally accessible tests of the information-theory pieces?
7. Which saved numerical results remain stable across model revisions, and which changes can be traced to explicit assumption or implementation updates?

The roadmap favors falsifiable models and reproducible numerics over claims of exotic communication.
