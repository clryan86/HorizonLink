# Contributing to HorizonLink

Thanks for considering a contribution. HorizonLink welcomes small, testable improvements to the physics helpers, channel models, experiments, documentation, and tooling.

## Development setup

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e ".[dev]"
pytest
ruff check horizonlink tests experiments
```

For plotting support:

```bash
pip install -e ".[viz]"
```

## Scientific expectations

Contributions should clearly distinguish among:

- standard/established equations;
- simplified numerical or information-theory analogues;
- speculative toy assumptions.

Do not present a numerical toy result as evidence for faster-than-light signaling, signaling from inside a classical event horizon, or a violation of established no-signaling results.

## Pull requests

A strong pull request includes:

1. a concise statement of the model or software change;
2. references or derivation notes when physics equations are introduced;
3. tests for new behavior and edge cases;
4. reproducible seeds for stochastic experiments;
5. documentation of assumptions and units.

Keep public APIs typed, prefer SI units in physics helpers, and avoid adding large dependencies unless they materially improve the research workflow.
