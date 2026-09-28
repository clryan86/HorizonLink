# HorizonLink

[![CI](https://github.com/clryan86/HorizonLink/actions/workflows/ci.yml/badge.svg)](https://github.com/clryan86/HorizonLink/actions/workflows/ci.yml)

**HorizonLink** is an open-source Python research sandbox for turning questions about horizons, noisy channels, and information recovery into reproducible numerical experiments.

The project deliberately separates established equations from simplified analogues and speculative toy models. It does **not** claim faster-than-light communication, communication from inside a classical black-hole event horizon, or a violation of quantum no-signaling constraints.

## Why this project exists

Questions about black holes and communication often become vague very quickly. HorizonLink makes the assumptions executable: define a channel, choose a horizon model, calculate measurable quantities, sweep parameters, and compare the result with familiar information-theory baselines.

The goal is not to force an exotic result. The goal is to find out exactly where information is preserved, degraded, or lost under a stated model.

## Current capabilities

- Schwarzschild radius, gravitational redshift, and outgoing-light coordinate-delay helpers
- Exterior-horizon toy link budget using redshift plus geometric collection
- Binary erasure channel simulation
- Binary symmetric channel capacity and simulation
- AWGN Shannon-Hartley capacity calculations
- Information-theory metrics
- Hayden–Preskill-inspired recovery toy model
- Cartesian parameter search
- Reproducible Monte Carlo experiments
- JSON-producing command-line interface
- CSV horizon-profile experiment
- Optional matplotlib profile plots
- Pytest test suite
- Ruff linting and GitHub Actions CI on Python 3.10, 3.11, and 3.12

## Install

```bash
git clone https://github.com/clryan86/HorizonLink.git
cd HorizonLink
python -m venv .venv
```

Activate the environment, then install:

```bash
pip install -e ".[dev]"
```

Optional plotting support:

```bash
pip install -e ".[viz]"
```

## Command-line examples

After installation, the `horizonlink` command is available.

### Schwarzschild radius

```bash
horizonlink radius 10
```

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

### Exterior-horizon toy link budget

```bash
horizonlink link-budget 10 2.0 1000000000 1000000000 --aperture-area-m2 100
```

Here `2.0` means the transmitter is at two Schwarzschild radii. The model rejects an emitter at or inside the event horizon.

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

The original channel-search experiment is also available:

```bash
python experiments/run_channel_sweep.py
```

## Repository layout

```text
horizonlink/
  channels/       Classical noisy-channel baselines
  horizons/       Relativistic exterior-horizon calculations
  metrics/        Information-theory metrics
  protocols/      Recovery/protocol toy models
  search/         Parameter search helpers
  simulation/     Reproducible Monte Carlo experiments
  cli.py          Command-line interface
  visualization.py
experiments/       Runnable research scripts
tests/             Automated tests
docs/              Model assumptions and roadmap
.github/workflows/ Continuous integration
```

## Scientific interpretation

The Schwarzschild helpers use an idealized, non-rotating, uncharged black hole. A static emitter arbitrarily close to the horizon is itself an idealization because the required proper acceleration diverges at the horizon.

The channel models are abstractions. A high simulated recovery score means a toy model preserved information under its assumptions; it does **not** demonstrate that a real black hole can transmit a chosen message from behind its event horizon.

See [`docs/MODELS.md`](docs/MODELS.md) for model boundaries and [`docs/ROADMAP.md`](docs/ROADMAP.md) for planned extensions.

## Development

```bash
pytest
ruff check horizonlink tests experiments
```

Contributions should include reproducible tests and clearly identify established physics versus speculative assumptions. See [`CONTRIBUTING.md`](CONTRIBUTING.md).

## License

MIT
