# S site resolution: implementation check (S10b)

Question: G1 found that model S predicts nearly the same value for every O site of a host at B = 25-200
(`results/g1_diagnostics.json`). Is that (A) an implementation error in how the vacancy flag reaches the readout,
or (B) a learned outcome? This note reports read-only measurements on stored checkpoints. Nothing was trained,
rerun or changed. Numbers are from `results/s_site_resolution_forensic.json`; energies in eV.

**Verdict: B: no implementation error; flag effect is a learned outcome at small budgets.** Qualification from
the measurements: the within-host spread was absent at initialisation for every configuration (so it was never
learned at small budgets, not learned away), and it is carried by the environment of the read-out vacancy node,
not by the flag itself.

## Setup

- Checkpoints: resample 0, seed 0, S and D-state at B = 25, 50, 100, 200, 400, 654 (12 runs), loaded with
  `dftgnn.train.load_checkpoint` on the CPU in eval mode. The CPU predictions reproduce the stored GPU test
  predictions to at most 1.8e-4 eV (S at B = 200; 6.7e-7 to 9.0e-5 elsewhere).
- Hosts: 30 of the 105 resample-0 test hosts with at least two labelled sites, drawn with
  `numpy.random.default_rng(20261008)`; the same hosts for every checkpoint.
- Init control: an untrained model with each checkpoint's hyperparameters, built after `seed_everything(0)` as in
  training.
- **Scope of this pass:** the vacancy (flag and readout index) was moved over the labelled sites of each host.
  The sweep over every O atom of the supercell (`sd_all_O`) was not run: the full sweep needs several CPU-hours
  and the Mac was on battery power. It is listed as outstanding in the S10b handoff.
- SDs are sample SDs (ddof = 1) across a host's sites; tables give the median over the 30 hosts. Median
  within-host target SD of these hosts: 0.121 eV.

## Unit tests (`tests/test_flag_path.py`, untrained S, both poolings, blocks 2 and 4, hidden 64 and 128)

| check | result |
|---|---|
| zeroing the flag changes the output (> 1e-6) | passes for all 8 configurations |
| moving only the flag (readout index fixed) changes the output | passes for all 8 configurations |
| moving the vacancy between two inequivalent O sites changes the output by > 1e-6 | **fails for all 8 configurations** (kept as a strict expected failure) |

In the test host (2x2x2 MgO with one Mg replaced by Ca), the two O sites' outputs differ by about 1e-8 to 1e-7
(standardised units) at initialisation, also with the near O displaced by 0.2 or 0.5 Å. Tracing one
configuration layer by layer: a Ca/Mg difference of 0.16 in the encoded node features becomes 1.7e-3 after the
three-layer edge MLP (each Linear + SoftPlus2 layer roughly halves it), and about 6e-7 in the O node embedding
after the mean over the O atom's 56 edges and the node MLP. matgl's own MEGNet uses the same default PyTorch
initialisation, so this is a property of the backbone at initialisation, not of this project's wiring.

## (a) Flag sweep over labelled sites

| model | B | trained: SD across labelled sites | trained: SD, flag off | trained: mean abs(on - off) | init: SD across labelled sites | init: mean abs(on - off) | target SD |
|---|---:|---:|---:|---:|---:|---:|---:|
| S | 25 | 4.3e-04 | 4.3e-04 | 1.3e-02 | 2.0e-08 | 1.2e-03 | 0.121 |
| S | 50 | 2.9e-04 | 2.9e-04 | 3.8e-03 | 2.2e-08 | 1.3e-03 | 0.121 |
| S | 100 | 1.3e-04 | 1.2e-04 | 9.6e-02 | 4.2e-08 | 3.9e-04 | 0.121 |
| S | 200 | 2.8e-05 | 3.1e-05 | 5.7e-02 | 3.9e-08 | 3.6e-04 | 0.121 |
| S | 400 | 1.7e-02 | 2.8e-02 | 1.2e+00 | 1.8e-08 | 8.7e-04 | 0.121 |
| S | 654 | 6.6e-02 | 6.5e-02 | 5.0e-01 | 1.7e-08 | 8.5e-04 | 0.121 |
| D-state | 25 | 4.4e-02 | 1.8e-04 | 1.5e-01 | 5.3e-04 | 1.9e-03 | 0.121 |
| D-state | 50 | 4.7e-02 | 2.2e-04 | 1.6e-01 | 5.9e-04 | 2.3e-03 | 0.121 |
| D-state | 100 | 2.9e-02 | 4.5e-05 | 1.4e-01 | 3.5e-04 | 1.5e-03 | 0.121 |
| D-state | 200 | 5.8e-02 | 3.2e-05 | 2.1e-01 | 3.4e-04 | 1.5e-03 | 0.121 |
| D-state | 400 | 4.9e-02 | 1.2e-05 | 1.7e-01 | 5.7e-04 | 1.8e-03 | 0.121 |
| D-state | 654 | 7.6e-02 | 7.9e-05 | 2.8e-01 | 5.7e-04 | 1.8e-03 | 0.121 |

"flag off" zeroes the flag with the readout index kept on each site. For D-state, zeroing the flag also removes the
site descriptors (they enter as flag x descriptor).

## (f) D-state control: site descriptors held at the host mean

Median within-host SD across labelled sites:

| B | trained, own site descriptors | trained, host-mean site descriptors | init, own | init, host-mean |
|---:|---:|---:|---:|---:|
| 25 | 4.4e-02 | 1.8e-04 | 5.3e-04 | 2.2e-08 |
| 50 | 4.7e-02 | 2.2e-04 | 5.9e-04 | 2.5e-08 |
| 100 | 2.9e-02 | 4.4e-05 | 3.5e-04 | 1.6e-08 |
| 200 | 5.8e-02 | 3.2e-05 | 3.4e-04 | 1.5e-08 |
| 400 | 4.9e-02 | 8.1e-06 | 5.7e-04 | 3.0e-08 |
| 654 | 7.6e-02 | 4.7e-05 | 5.7e-04 | 3.8e-08 |

## (b) Readout decomposition (first head layer)

w = Frobenius norm of the block's weights / sqrt(block width); a = within-host activation SD across labelled
sites (mean over features, mean over hosts); w x a = rough contribution scale. Set2set pooled blocks are twice
the hidden half-width.

| model | B | state | vacancy node: w / a / w x a | pooled: w / a / w x a | global state: w / a / w x a |
|---|---:|---|---|---|---|
| S | 25 | trained | 0.30 / 1.4e-03 / 4.3e-04 | 0.36 / 9.4e-07 / 3.4e-07 | 0.29 / 7.6e-07 / 2.2e-07 |
| S | 25 | init | 0.29 / 6.4e-07 / 1.9e-07 | 0.29 / 4.5e-09 / 1.3e-09 | 0.29 / 7.7e-09 / 2.2e-09 |
| S | 50 | trained | 0.30 / 4.2e-03 / 1.2e-03 | 0.34 / 3.9e-07 / 1.3e-07 | 0.30 / 1.9e-07 / 5.6e-08 |
| S | 50 | init | 0.29 / 6.4e-07 / 1.9e-07 | 0.29 / 4.5e-09 / 1.3e-09 | 0.29 / 7.7e-09 / 2.2e-09 |
| S | 100 | trained | 0.53 / 2.7e-04 / 1.4e-04 | 0.57 / 1.7e-07 / 9.6e-08 | 0.42 / 7.5e-08 / 3.2e-08 |
| S | 100 | init | 0.41 / 6.5e-07 / 2.7e-07 | 0.41 / 6.1e-09 / 2.5e-09 | 0.41 / 9.8e-09 / 4.0e-09 |
| S | 200 | trained | 0.63 / 1.6e-04 / 1.0e-04 | 0.71 / 4.3e-07 / 3.1e-07 | 0.56 / 1.5e-06 / 8.5e-07 |
| S | 200 | init | 0.41 / 6.5e-07 / 2.7e-07 | 0.41 / 6.1e-09 / 2.5e-09 | 0.41 / 9.8e-09 / 4.0e-09 |
| S | 400 | trained | 0.84 / 1.3e-02 / 1.1e-02 | 1.18 / 2.0e-05 / 2.3e-05 | 0.78 / 1.9e-05 / 1.5e-05 |
| S | 400 | init | 0.67 / 6.0e-07 / 4.0e-07 | 0.67 / 5.3e-09 / 3.5e-09 | 0.66 / 8.5e-09 / 5.6e-09 |
| S | 654 | trained | 1.11 / 9.9e-02 / 1.1e-01 | 1.44 / 3.6e-04 / 5.2e-04 | 0.93 / 3.3e-04 / 3.1e-04 |
| S | 654 | init | 0.67 / 6.0e-07 / 4.0e-07 | 0.67 / 5.3e-09 / 3.5e-09 | 0.66 / 8.5e-09 / 5.6e-09 |
| D-state | 25 | trained | 0.61 / 2.3e-02 / 1.4e-02 | 0.59 / 7.2e-05 / 4.3e-05 | 0.62 / 3.4e-06 / 2.1e-06 |
| D-state | 25 | init | 0.58 / 1.5e-02 / 8.6e-03 | 0.58 / 4.6e-05 / 2.7e-05 | 0.57 / 3.5e-08 / 2.0e-08 |
| D-state | 50 | trained | 0.62 / 2.1e-02 / 1.3e-02 | 0.60 / 6.7e-05 / 4.0e-05 | 0.63 / 6.4e-06 / 4.0e-06 |
| D-state | 50 | init | 0.58 / 1.4e-02 / 8.3e-03 | 0.58 / 4.5e-05 / 2.6e-05 | 0.57 / 3.4e-08 / 1.9e-08 |
| D-state | 100 | trained | 0.44 / 2.6e-02 / 1.2e-02 | 0.42 / 7.5e-05 / 3.2e-05 | 0.51 / 8.6e-07 / 4.3e-07 |
| D-state | 100 | init | 0.41 / 1.3e-02 / 5.5e-03 | 0.41 / 4.1e-05 / 1.7e-05 | 0.40 / 3.1e-08 / 1.3e-08 |
| D-state | 200 | trained | 0.54 / 4.7e-02 / 2.5e-02 | 0.55 / 1.7e-04 / 9.4e-05 | 0.60 / 7.9e-06 / 4.8e-06 |
| D-state | 200 | init | 0.41 / 1.3e-02 / 5.5e-03 | 0.41 / 4.1e-05 / 1.7e-05 | 0.40 / 3.2e-08 / 1.3e-08 |
| D-state | 400 | trained | 0.79 / 9.4e-02 / 7.4e-02 | 1.15 / 4.9e-04 / 5.7e-04 | 0.77 / 6.5e-06 / 5.0e-06 |
| D-state | 400 | init | 0.47 / 1.5e-02 / 6.8e-03 | 0.47 / 7.7e-05 / 3.6e-05 | 0.48 / 3.2e-08 / 1.5e-08 |
| D-state | 654 | trained | 1.37 / 2.1e-01 / 2.9e-01 | 1.74 / 1.2e-03 / 2.0e-03 | 1.25 / 3.4e-05 / 4.3e-05 |
| D-state | 654 | init | 0.47 / 1.5e-02 / 6.9e-03 | 0.47 / 7.8e-05 / 3.7e-05 | 0.48 / 3.3e-08 / 1.6e-08 |

D-state site descriptors are not separable in the readout: they enter as flag x descriptor at the vacancy node
input and are mixed by the node encoder. First node-encoder layer column norms (flag column; per-sqrt-width for
the site-descriptor and element-embedding columns), trained / init:

| B | flag column | site-descriptor columns | element-embedding columns |
|---:|---|---|---|
| 25 | 0.94 / 0.93 | 0.88 / 0.85 | 0.89 / 0.87 |
| 50 | 0.94 / 0.93 | 0.89 / 0.85 | 0.88 / 0.87 |
| 100 | 0.92 / 0.93 | 0.93 / 0.85 | 0.88 / 0.87 |
| 200 | 0.87 / 0.93 | 1.12 / 0.85 | 1.03 / 0.87 |
| 400 | 1.80 / 1.29 | 1.78 / 1.23 | 1.78 / 1.24 |
| 654 | 2.17 / 1.29 | 2.59 / 1.23 | 2.21 / 1.24 |

## (c) Node level, one host

SD across the host's O atoms of the vacancy-node embedding after the last block (mean over features), with the
flag on that atom versus the flag off. For D-state the host-mean site descriptors are used.

| model | B | host | trained: flag on | trained: flag off | init: flag on | init: flag off |
|---|---:|---|---:|---:|---:|---:|
| S | 25 | mp-1189528 (216 O) | 3.2e-04 | 3.2e-04 | 1.5e-07 | 1.5e-07 |
| S | 50 | mp-1189528 (216 O) | 6.2e-04 | 6.2e-04 | 1.5e-07 | 1.5e-07 |
| S | 100 | mp-1189528 (216 O) | 1.0e-04 | 1.0e-04 | 1.5e-07 | 1.6e-07 |
| S | 200 | mp-1189528 (216 O) | 4.9e-05 | 4.9e-05 | 1.5e-07 | 1.6e-07 |
| S | 400 | mp-1189528 (216 O) | 4.8e-03 | 6.0e-03 | 2.0e-07 | 1.9e-07 |
| S | 654 | mp-1189528 (216 O) | 1.1e-02 | 1.1e-02 | 2.0e-07 | 1.9e-07 |
| D-state | 25 | mp-1189528 (216 O) | 1.5e-05 | 1.4e-05 | 1.7e-07 | 1.6e-07 |
| D-state | 50 | mp-1189528 (216 O) | 1.1e-05 | 1.1e-05 | 1.7e-07 | 1.7e-07 |
| D-state | 100 | mp-1189528 (216 O) | 1.2e-06 | 1.1e-06 | 1.7e-07 | 1.7e-07 |
| D-state | 200 | mp-1189528 (216 O) | 4.1e-06 | 4.1e-06 | 1.8e-07 | 1.7e-07 |
| D-state | 400 | mp-1189528 (216 O) | 1.7e-05 | 1.7e-05 | 1.6e-07 | 1.6e-07 |
| D-state | 654 | mp-1189528 (216 O) | 1.7e-04 | 1.7e-04 | 1.6e-07 | 1.5e-07 |

## (d) Hyperparameters of each checkpoint (from the result JSONs)

Budget, pooling, width, depth and optimiser settings change together (anchor mapping), so no causal attribution
is drawn from this table.

| model | B | pooling | hidden | blocks | dropout | lr | weight decay | batch | epochs run | best epoch (from 1) | trained within-host SD (eV) |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| S | 25 | set2set | 128 | 3 | 0.209 | 1.66e-03 | 1.1e-06 | 32 | 62 | 32 | 4.3e-04 |
| S | 50 | set2set | 128 | 3 | 0.209 | 1.66e-03 | 1.1e-06 | 32 | 41 | 11 | 2.9e-04 |
| S | 100 | set2set | 128 | 4 | 0.014 | 2.23e-03 | 5.8e-04 | 16 | 54 | 24 | 1.3e-04 |
| S | 200 | set2set | 128 | 4 | 0.014 | 2.23e-03 | 5.8e-04 | 16 | 66 | 36 | 2.8e-05 |
| S | 400 | mean | 64 | 3 | 0.141 | 1.42e-03 | 1.8e-06 | 16 | 75 | 45 | 1.7e-02 |
| S | 654 | mean | 64 | 3 | 0.141 | 1.42e-03 | 1.8e-06 | 16 | 200 | 174 | 6.6e-02 |
| D-state | 25 | set2set | 64 | 3 | 0.063 | 1.14e-04 | 6.4e-05 | 64 | 155 | 125 | 4.4e-02 |
| D-state | 50 | set2set | 64 | 3 | 0.063 | 1.14e-04 | 6.4e-05 | 64 | 122 | 92 | 4.7e-02 |
| D-state | 100 | set2set | 64 | 3 | 0.238 | 1.46e-03 | 4.9e-04 | 32 | 39 | 9 | 2.9e-02 |
| D-state | 200 | set2set | 64 | 3 | 0.238 | 1.46e-03 | 4.9e-04 | 32 | 97 | 67 | 5.8e-02 |
| D-state | 400 | mean | 128 | 3 | 0.162 | 1.67e-03 | 1.7e-06 | 16 | 108 | 78 | 4.9e-02 |
| D-state | 654 | mean | 128 | 3 | 0.162 | 1.67e-03 | 1.7e-06 | 16 | 151 | 121 | 7.6e-02 |

## Facts

1. The flag reaches the output in every checkpoint and in every untrained configuration of both poolings.
2. For S, the within-host SD is the same with the flag on and off at every budget; the node-level SD across O
   atoms is also the same with the flag on and off. The site-to-site spread of S comes from the read-out node's
   embedding, which differs between O atoms through message passing, not from the flag.
3. At initialisation that spread is about 2e-8 eV for every checkpoint's hyperparameters; the vacancy-node
   embedding differs between O atoms by about 1.5e-7 to 2e-7.
4. After training, S's within-host SD is 4.3e-4, 2.9e-4, 1.3e-4 and 2.8e-5 eV at B = 25, 50, 100 and 200, and
   1.7e-2 and 6.6e-2 eV at B = 400 and 654. The within-host activation SD of the vacancy-node readout block grew
   from about 6e-7 at init to 1.6e-4 to 4.2e-3 at B <= 200 and to 1.3e-2 and 9.9e-2 at B = 400 and 654.
5. D-state's within-host SD (2.9e-2 to 7.6e-2 eV) collapses to 8.1e-6 to 2.2e-4 eV when every site carries the
   host-mean site descriptors, at every budget including 654.

Hypothesis (not tested here): at initialisation the backbone's output is nearly insensitive to the local
environment of the read-out site, so site resolution must be built during training; with 22 to 180 training
hosts and the 50- and 200-host anchor hyperparameters, S did not build it to a measurable level, while D obtained
site resolution from its site descriptors. Separating budget from hyperparameters would need runs not in the
pre-registered design.
