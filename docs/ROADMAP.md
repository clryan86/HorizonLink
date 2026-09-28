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
- [ ] Add entanglement entropy helpers
- [ ] Add Bell-state / CHSH diagnostics
- [ ] Add explicit noisy classical side-channel models
- [ ] Add small circuit diagrams to the documentation

## v0.4 — deeper numerical experiments

- [ ] Add Kerr exterior calculations and frame-dragging examples
- [ ] Add detector/background-noise models
- [ ] Add error-correcting-code comparisons
- [ ] Add parameter-sweep persistence and experiment metadata
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
5. Can analogue-horizon systems provide experimentally accessible tests of the information-theory pieces?

The roadmap favors falsifiable models and reproducible numerics over claims of exotic communication.
