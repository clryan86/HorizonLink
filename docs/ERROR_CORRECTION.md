# Error-correction benchmarks

HorizonLink includes two deliberately small, auditable classical error-correcting codes for studying reliability-versus-redundancy tradeoffs on the binary symmetric channel (BSC):

- **Repetition-3** — each payload bit is transmitted three times and decoded by majority vote.
- **Hamming(7,4)** — four payload bits are mapped to a seven-bit codeword that corrects any single flipped bit in that codeword.

These are educational baselines, not a claim that either code is optimal for a real near-horizon communication system.

## Why include coding?

A raw channel error probability does not by itself determine payload reliability. Real communication systems add redundancy, interleaving, coding, synchronization, and decoding logic. HorizonLink's first coding layer makes one part of that trade explicit without hiding the implementation behind a large communications library.

## Code rates

The **code rate** is payload bits divided by transmitted physical bits.

| Scheme | Payload bits | Transmitted bits | Code rate |
| --- | ---: | ---: | ---: |
| Uncoded | 1 | 1 | 1.0 |
| Repetition-3 | 1 | 3 | 1/3 |
| Hamming(7,4) | 4 | 7 | 4/7 |

A lower payload BER therefore does not come for free. Repetition-3 spends three transmitted bits for every one payload bit. Hamming(7,4) spends seven transmitted bits for every four payload bits.

## Channel comparison rule

The benchmark applies the **same independent BSC flip probability to every transmitted physical bit** in each scheme.

That means coded schemes experience more total bit transmissions for the same payload size. The benchmark reports both payload BER and code rate so reliability is not presented without its redundancy cost.

## Repetition-3

For source bit `b`, encoding is simply:

```text
b -> b b b
```

The decoder chooses the majority value. Any one flipped bit in the three-bit block is corrected. Two or three flips produce an incorrect payload bit.

For an independent BSC with crossover probability `p`, the exact decoded bit-error probability is:

```text
P_error = 3 p^2 (1 - p) + p^3
        = 3 p^2 - 2 p^3
```

HorizonLink's Monte Carlo benchmark should converge toward that curve as the number of trials and payload bits increases.

## Hamming(7,4)

HorizonLink uses parity positions 1, 2, and 4 and data positions 3, 5, 6, and 7.

The decoder computes the three-bit syndrome. A nonzero syndrome points to one of the seven codeword positions, which is flipped before the four payload bits are extracted.

The code therefore corrects every single-bit error within a seven-bit codeword. Two-or-more-bit errors are outside the code's guaranteed correction capability and can be miscorrected because this implementation is ordinary Hamming(7,4), not SECDED Hamming(8,4) with an additional overall parity bit.

## CLI benchmark

Run one reproducible comparison:

```bash
horizonlink ecc-benchmark 0.05 --trials 100 --bits 12000 --seed 42
```

The JSON output includes:

- uncoded mean and standard-deviation BER;
- repetition-3 mean and standard-deviation BER;
- Hamming(7,4) mean and standard-deviation BER;
- code rates for all three schemes;
- trial count, payload bits per trial, crossover probability, and RNG seed.

## Sweep experiment

Generate a provenance-backed BER sweep:

```bash
python experiments/run_ecc_sweep.py \
  --points 21 \
  --max-flip-probability 0.2 \
  --trials 50 \
  --bits 12000 \
  --seed 42 \
  --output results/ecc_sweep.csv
```

The experiment writes:

- `results/ecc_sweep.csv`
- `results/ecc_sweep.csv.metadata.json`
- an optional PNG if matplotlib is installed

The metadata records the comparison rule, tested schemes, seed, complete experiment inputs, software versions, timestamp, and Git commit when available.

## Interpretation limits

The current benchmark assumes:

- independent bit flips;
- no burst errors;
- perfect framing and synchronization;
- perfect knowledge of codeword boundaries;
- no soft-decision information;
- no latency or decoder-compute penalty;
- no modulation-specific effects;
- no energy-per-bit normalization beyond the explicit code-rate comparison.

Those simplifications are intentional. They make the first reliability comparison auditable. Future channel models can add burst noise, interleaving, soft information, energy constraints, or stronger codes without changing what these baselines mean.
