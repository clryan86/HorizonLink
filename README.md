# HorizonLink

[![CI](https://github.com/clryan86/HorizonLink/actions/workflows/ci.yml/badge.svg)](https://github.com/clryan86/HorizonLink/actions/workflows/ci.yml)

**HorizonLink** is an open-source Python laboratory for turning questions about black-hole horizons, communication links, detector sensitivity, noisy channels, and quantum-information analogues into reproducible numerical experiments.

The project deliberately separates established equations from simplified analogues and speculative toy models. It does **not** claim faster-than-light communication, communication from inside a classical black-hole event horizon, or a violation of quantum no-signaling constraints.

## HorizonLink Lab dashboard

HorizonLink includes an interactive local browser dashboard. You can change black-hole mass, spin, emitter radius, transmitter power, frequency, receiver distance, collecting area, bandwidth, system temperature, integration time, target SNR, and quantum-channel errors and watch the calculated outputs update immediately.

Install the dashboard dependencies:

```bash
pip install -e ".[dashboard]"
```

Launch it:

```bash
horizonlink dashboard
```

Streamlit will open **HorizonLink Lab** in your browser. The current workspaces are:

- **Exterior Link** — redshift, geometric collection, received signal power, thermal noise, SNR, integration gain, Shannon capacity, required transmitter power, and maximum receiver distance
- **Kerr Rotation** — outer/inner horizons, static limit, horizon rotation, and frame-dragging profiles
- **Quantum Information** — noisy three-qubit teleportation with live fidelity sweeps

See [`docs/DASHBOARD.md`](docs/DASHBOARD.md) for a guided walkthrough.

## Why this project exists

Questions about black holes and communication often become vague very quickly. HorizonLink makes the assumptions executable: define a channel, choose a horizon model, calculate measurable quantities, sweep parameters, and compare the result with familiar information-theory baselines.

The goal is not to force an exotic result. The goal is to find out exactly where information is preserved, degraded, or lost under a stated model.

## Current capabilities

- Schwarzschild radius, gravitational redshift, and outgoing-light coordinate-delay helpers
- Kerr outer/inner horizon radii, ergosphere static limit, horizon angular velocity, and ZAMO frame dragging
- Exterior-horizon toy link budget using redshift plus geometric collection
- Idealized thermal detector model using `kTB` noise and radiometer integration scaling
- End-to-end link detectability calculation from transmitter power to SNR and Shannon capacity
- Inverse link design for required transmitter power and maximum receiver distance at a target SNR
- Binary erasure channel simulation
- Binary symmetric channel capacity and simulation over the full `0 <= p <= 1` domain
- AWGN Shannon-Hartley capacity calculations
- Information-theory metrics
- Explicitly uncalibrated Hayden-Preskill-inspired recovery proxy
- Three-qubit quantum teleportation simulator implemented directly with NumPy
- Bell-resource noise and noisy classical correction-bit models
- Entanglement entropy, purity, partial-trace, and CHSH diagnostics
- Cartesian parameter search with non-finite objective rejection
- Reproducible Monte Carlo experiments
- Strict JSON-producing command-line interface
- CSV horizon, Kerr, detectability, and teleportation experiments
- Experiment provenance metadata with package/Python/NumPy versions and Git commit when available
- Atomic experiment output writes that protect existing results from failed runs
- Interactive Streamlit browser dashboard
- Optional matplotlib plots
- Pytest test suite
- Ruff linting and GitHub Actions CI on Python 3.10, 3.11, and 3.12
- CI wheel/sdist build plus installed-package smoke test

## Install

```bash
git clone https://github.com/clryan86/HorizonLink.git
cd HorizonLink
python -m venv .venv
```

On Windows PowerShell, activate the environment with:

```powershell
.\.venv\Scripts\Activate.ps1
```

Then install the development package:

```bash
pip install -e ".[dev]"
```

Optional plotting support:

```bash
pip install -e ".[viz]"
```

Optional browser dashboard:

```bash
pip install -e ".[dashboard]"
```

## Command-line examples

After installation, the `horizonlink` command is available.

### Schwarzschild radius

```bash
horizonlink radius 10
```

### Kerr black hole

```bash
horizonlink kerr 10 0.9 --frame-radius-rg 5
```

### Exterior-horizon toy link budget

```bash
horizonlink link-budget 10 2.0 1000000000 1000000000 --aperture-area-m2 100
```

Here `2.0` means the transmitter is at two Schwarzschild radii. The model rejects an emitter at or inside the event horizon.

### End-to-end detectability

```bash
horizonlink link-detect 10 2.0 1e9 1e9 100 50 1e6 10 --aperture-area-m2 100
```

This combines the exterior link fraction with transmitter power, receiver system temperature, bandwidth, and integration time. It reports received power, thermal noise, instantaneous power SNR, idealized integrated radiometer SNR, and Shannon capacity.

### Inverse link design

```bash
horizonlink link-design 10 2.0 1e9 1e8 50 1e6 10 \
  --aperture-area-m2 100 \
  --target-snr 5
```

This asks two inverse questions under the same simplified model: how much transmitter power is required to reach the target integrated SNR at the requested distance, and how far the supplied transmitter power can reach at that target SNR. It also reports the SNR of the supplied scenario.

### Binary symmetric channel capacity

```bash
horizonlink bsc-capacity 0.1
```

### AWGN capacity

```bash
horizonlink awgn-capacity 12 1000000
```

### Monte Carlo error-rate experiment

```bash
horizonlink monte-carlo 0.1 --trials 200 --bits 20000 --seed 42
```

### Quantum teleportation toy model

```bash
horizonlink teleport 1.57079632679 --phi 0.5 --resource-error 0.1 --classical-bit-error 0.02
```

This runs a standard three-qubit teleportation circuit with optional Pauli noise on Bob's half of the shared Bell pair and independent noise on Alice's two ordinary classical correction bits.

## Reproducible experiments

Generate a radius/redshift/link profile as CSV:

```bash
python experiments/run_horizon_profile.py \
  --mass-solar 10 \
  --emitted-hz 1e9 \
  --receiver-distance-m 1e9 \
  --aperture-area-m2 100 \
  --output horizon_profile.csv
```

Generate a full detectability sweep with a provenance sidecar:

```bash
python experiments/run_detectability_sweep.py \
  --mass-solar 10 \
  --output results/detectability.csv
```

The detectability experiment writes the CSV only after the full calculation succeeds and also creates `detectability.csv.metadata.json` with the model classification, complete inputs, HorizonLink/Python/NumPy versions, timestamp, and Git commit when available.

Generate a Kerr frame-dragging profile:

```bash
python experiments/run_kerr_frame_dragging.py --mass-solar 10 --spin 0.9
```

Sweep Bell-resource noise versus teleportation fidelity:

```bash
python experiments/run_teleportation_sweep.py
```

Generate a two-dimensional teleportation noise surface:

```bash
python experiments/run_teleportation_surface.py
```

The original channel-search experiment is also available:

```bash
python experiments/run_channel_sweep.py
```

## Repository layout

```text
horizonlink/
  channels/       Classical noisy-channel baselines
  detectors/      Thermal noise and receiver sensitivity models
  horizons/       Schwarzschild and Kerr exterior calculations
  metrics/        Classical and quantum information metrics
  protocols/      Recovery and teleportation protocol models
  quantum/        Small auditable quantum-state utilities
  search/         Parameter search helpers
  simulation/     Reproducible Monte Carlo experiments
  cli.py          Command-line interface
  dashboard.py    Interactive HorizonLink Lab
  provenance.py   Reproducible output metadata and atomic writes
  visualization.py
experiments/       Runnable research scripts
tests/             Automated tests
docs/              Model assumptions, dashboard guide, and roadmap
.github/workflows/ Continuous integration
```

## Scientific interpretation

The Schwarzschild helpers use an idealized, non-rotating, uncharged black hole. A static emitter arbitrarily close to the horizon is itself an idealization because the required proper acceleration diverges at the horizon.

The Kerr helpers implement standard exterior geometry in Boyer-Lindquist coordinates. They are not a complete ray tracer, orbital integrator, plasma model, or general-relativistic radiative-transfer package.

The detector layer starts with the Rayleigh-Jeans thermal-noise approximation `P_noise = kTB` and an idealized radiometer integration improvement proportional to `sqrt(B tau)`. Real hardware can be limited by receiver gain, aperture efficiency, sky background, atmosphere, polarization, interference, quantization, calibration, and systematic noise.

The channel and quantum models are abstractions. A high simulated recovery or teleportation fidelity means the stated toy model preserved information under its assumptions; it does **not** demonstrate that a real black hole can transmit a chosen message from behind its event horizon.

The teleportation simulator is standard quantum information: Alice's measurement outcomes still require ordinary classical communication. Entanglement alone does not provide faster-than-light signaling.

See [`docs/MODELS.md`](docs/MODELS.md) for model boundaries and [`docs/ROADMAP.md`](docs/ROADMAP.md) for planned extensions.

## Development

```bash
pytest
ruff check horizonlink tests experiments
```

Contributions should include reproducible tests and clearly identify established physics versus speculative assumptions. See [`CONTRIBUTING.md`](CONTRIBUTING.md).

## License

MIT
