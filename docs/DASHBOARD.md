# HorizonLink Lab dashboard

HorizonLink Lab is the interactive front end for the numerical models in the Python package. It runs locally in a browser using Streamlit; the calculations still come from the same tested `horizonlink` modules used by the CLI and experiments.

## Start the dashboard

From a terminal in the repository root:

```bash
python -m pip install -e ".[dashboard]"
python -m streamlit run horizonlink/dashboard.py
```

On Windows, Streamlit normally opens a browser tab automatically. If it does not, copy the local URL printed in the terminal (usually `http://localhost:8501`) into your browser.

## Exterior Link workspace

This workspace connects four layers:

1. **Schwarzschild exterior physics** — mass, Schwarzschild radius, emitter radius, and gravitational redshift.
2. **Geometric collection** — a deliberately simple isotropic collecting-area fraction.
3. **Receiver thermal noise** — the Rayleigh-Jeans approximation `P_noise = k T B`.
4. **Information theory** — power SNR, idealized radiometer integration improvement, and Shannon-Hartley capacity.

The controls are intentionally exposed as variables. Changing one variable lets you see which downstream quantities change and which do not.

### Important interpretation

The current link model is not an antenna design, ray tracer, plasma simulation, or full GR radiative-transfer calculation. It does not include lensing gain, beaming, orbital Doppler effects, absorption, scattering, polarization, detector efficiency, pointing error, interference, atmospheric losses, or hardware nonlinearities.

The model is most useful as a transparent baseline and as a way to identify which physical effect needs to be added next.

## Kerr Rotation workspace

The Kerr panel lets you vary:

- black-hole mass;
- dimensionless spin `chi = cJ/(GM^2)`;
- Boyer-Lindquist polar angle.

It reports:

- outer event-horizon radius;
- inner (Cauchy) horizon radius;
- static-limit radius;
- horizon angular velocity;
- a radial profile of ZAMO frame-dragging angular velocity.

This is exterior Kerr geometry, not a visual ray-traced black-hole renderer.

## Quantum Information workspace

The quantum panel runs the project's explicit NumPy implementation of standard three-qubit teleportation. It lets you vary:

- the input qubit angles `theta` and `phi`;
- Pauli noise on Bob's half of the Bell resource;
- independent bit-flip probability on Alice's two classical correction bits.

The dashboard displays output fidelity and a live resource-noise sweep.

Entanglement does not remove the need for ordinary classical communication. The simulator does not imply faster-than-light signaling or information escaping from inside a classical event horizon.

## Suggested experiments

### 1. Approach the Schwarzschild horizon

Keep every receiver setting fixed and move the emitter from `10 r_s` toward `1.0001 r_s`. Watch the received/emitted frequency ratio and received power fall.

### 2. Trade bandwidth against thermal noise

Hold received signal power approximately fixed and change receiver bandwidth. The instantaneous thermal noise power grows linearly with bandwidth. The interpretation of capacity depends on the signal/noise assumptions, so treat the result as a baseline rather than a hardware prediction.

### 3. Increase integration time

Keep all link variables fixed and increase integration time. In the idealized radiometer model, integrated SNR improves as the square root of integration time.

### 4. Spin up a Kerr black hole

Compare `chi = 0` with large positive or negative spin. Observe how the outer horizon, ergoregion, horizon angular velocity, and frame-dragging profile change.

### 5. Damage the classical side channel in teleportation

Keep Bell-resource noise at zero, then raise the classical correction-bit error probability. Fidelity falls even though the entangled resource remains perfect. This demonstrates why teleportation does not bypass ordinary communication constraints.

## Scientific levels

When interpreting HorizonLink results, keep three categories separate:

- **Established equation** — standard results such as Schwarzschild/Kerr horizon formulas, `kTB`, or Shannon capacity under its stated channel assumptions.
- **Simplified analogue** — combinations such as the isotropic exterior link budget or ideal radiometer receiver.
- **Speculative toy model** — abstractions motivated by black-hole information questions that are not literal engineering descriptions of a real black hole.

A numerical result becomes scientifically interesting only when its assumptions are explicit and independently defensible.
