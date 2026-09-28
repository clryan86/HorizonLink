# HorizonLink Knowledge Store

This directory is the durable research memory for the calculation laboratory.
It is intentionally separate from executable code.

## Layers

- `known/` — established equations, benchmark values, and independently sourced results.
- `candidates/` — numerical relationships produced by HorizonLink that remain provisional.
- `rejected/` — failed/falsified candidates retained so the system does not rediscover the same dead end.
- `datasets/` — compact, reproducible derived datasets or manifests. Large generated data should live in artifacts/releases rather than Git.
- `promotion/` — records showing why a knowledge item was promoted into an executable calculation function.

## Promotion rule

A candidate must not become a trusted calculation merely because it fits data. Before promotion it should have: provenance, units/dimensional checks, numerical convergence where relevant, an independent implementation or analytic derivation, falsification sweeps, and literature comparison. Assumptions and domain of validity must be recorded.

The intended loop is:

`inputs -> registered calculations -> tests -> datasets -> discovery -> falsification -> knowledge record -> review -> new/updated calculation -> regression tests -> repeat`

This store is evidence memory, not an authority database. Executable calculations remain responsible for validation and explicit assumptions.
