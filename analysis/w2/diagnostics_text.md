# W2: diagnostics of the final network

Session W2a, 2026-10-17. The final network is the He-initialised, validation-tuned network (v2 in the repository).
Everything below comes from existing predictions with the existing estimators (`analysis/w2/diagnostics.py`);
nothing was trained. The records are in `results/derived_w2/`; the tables after this summary are rendered from them
by `analysis/w2/make_docs.py`, and every number the rewrite may quote has a `\numNet...` macro
(`paper/tools/net_macros.py`). These are diagnoses for the author and for the wording of Results; none of them
replaces a result of the paper, and none is a claim until a claims-table row is added for it.

## Findings

**(a) Descriptor network at 25 and 50 hosts: a few test oxides with f-character conduction bands, not divergence.**
No D run has a non-finite prediction or a non-finite training or validation loss, and every run stopped by early
stopping at a normal validation error (one exception, r2 seed 0 at 50 hosts, whose best validation error is
126 eV: its validation set holds BaCeO3 and LaNbO4 while its training set holds no La or Ce oxide; seed 1 of the
same resample, whose validation split put those two oxides in training instead, reaches 0.672 eV). The large D errors come from a handful of test
sites, all in La- and Ce-containing oxides (LaScO3, Rb2CeO3, BaCeO3, Cs2CeO3, LaAsO3, La2Zr2O7, LaBO3 and others),
where D predicts energies of tens to hundreds of eV, far outside the 1.6 to 8.3 eV range of the targets. At every
one of these sites the descriptor furthest from the training data is the f-orbital fraction of the conduction-band
minimum (`cbm_f`): standardised with the run's own training sites, its |z| is 60 to 300 at those sites against
about 2 at the others. With 25 or 50 training oxides there are almost no f-band hosts in training, so the SD of
`cbm_f` is tiny, and a test oxide with an f-like conduction band is a large extrapolation that the network
amplifies. The extreme sites (78 at 25 hosts, 69 at 50 hosts, under 1% of the predictions) carry a third of the
absolute error at 25 hosts and half at 50 hosts. The Tukey rule flags 2 runs at 25 hosts (r0 s1, r1 s0) and 4 at
50 (r2 s0 and all three seeds of r6, a resample whose test set holds BaCeO3, Cs2CeO3, LaScO3 and LaAsO3), so the
outliers are partly one poor resample and partly single runs; but the same mechanism also inflates runs below the
fence (16 of 30 runs at 25 hosts and 12 of 30 at 50 carry extreme sites). Removing the flagged runs moves A at 50
hosts from -0.509 [-1.823, +0.277] to +0.238 [+0.096, +0.368]: the negative A at 25 and 50 hosts in the C1 table is
produced by these sites, not by S being better than D. This is behaviour of the descriptor input (training-set
standardisation of a nearly constant descriptor, as specified), not a defect in the code, so the paper's
small-budget numbers stand as computed; Results should say that D is unstable below 100 training hosts because a
few f-band oxides lie outside its training range, and quote the median or trimmed D error if a typical value is
needed.

**(b) Training limit.** In the sweep (10 x 3), S reaches the 200-epoch limit in 0 runs up to 200 hosts, 1 at 400
and 3 of 30 at 654; D in 1 of 30 at 654 and none elsewhere; P1 (the trained part of P) in 2, 10 and 20 of 30 runs
at 200, 400 and 654. At 654 in the 30 x 5 set, 14 S and 6 D runs are capped (17 of 150 cells hold a capped run).
Capped S runs are better, not worse, than uncapped ones (single-run MAE lower by 0.051 eV): they are the runs still
improving when the limit stopped them. The cells with a capped run have a smaller paired A (0.006 eV where only S
is capped, against 0.048 where neither is), so including them lowers the mean single-run A by 0.003 eV (30 x 5) and
0.0007 eV (10 x 3); removing the capped runs from the seed ensemble raises the 30 x 5 point estimate of A from
0.033 to 0.037 eV. Training S longer would therefore more likely shrink A than grow it; the effect is small next
to the interval and is descriptive only.

**(c) Crossover with the forest.** D is below RF-Kumagai with a 95% interval from 200 hosts on (-0.046
[-0.066, -0.028] at 200). S is below the forest in point estimate from 200 hosts (-0.023 at 200, -0.017 at 400) but
its interval includes zero at 200 and 400; S is clearly below only at 654 (-0.051 [-0.073, -0.030]). At 100 hosts
both networks are worse than the forest (S +0.089 [+0.027, +0.154]; D +0.006 [-0.044, +0.073]).

**(d) Why the bound passes at 200 and fails at 400.** The intervals are about equally wide at 200, 400 and 654
(bootstrap SD 0.015, 0.013, 0.011 eV; SD of A across resamples 0.034, 0.034, 0.030 eV). What changes is the point
estimate: A is 0.024 at 200, 0.054 at 400 and 0.015 at 654, so the bound is 0.047, 0.075 and 0.033. At 400 no
resample has A below zero and 6 of 10 exceed 0.05; at 200 two resamples are below zero and two above 0.05. The 30 x 5
design confirms 400 (A 0.066, U 0.079, 19 of 30 resamples above 0.05). The 200-host pass is therefore a lower point
estimate with the same resample-to-resample noise, not a more precise one: D at 200 still varies more between
resamples (SD of MAE_D 0.031 against 0.015 for S), and A at 200 sits between zero and δ. The N* rule needs the bound
below δ at every larger size, so N* stays 654; Results can say in one clause that the 200-host bound falls below δ because
the point estimate there is low, and that 400 hosts fail on both designs.

**(e) Screening.** On the 10 screened sites the final network's MAE is 0.420 eV [0.307, 0.553] with no net bias
(+0.003 eV; 5 over, 5 under). The errors are largest on the high-energy group (MgO, Al2O3 under-predicted by about
0.6 eV; ZrO2 over-predicted by 0.5 to 0.6 eV) and smallest on Ga2O3 O1 (+0.13 eV).

