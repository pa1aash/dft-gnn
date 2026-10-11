**Figure 3. The advantage of explicit DFT descriptors over structure alone.** A = MAE_S − MAE_D (eV; positive
when the descriptors help) against the number of training hosts (logarithmic axis). (**a**) Every budget,
`payload.budgets`; the axis spans the point estimates, and intervals reaching beyond it are clipped (full
intervals in the keys below). (**b**) The budgets from 200 training hosts up, where the decision on the margin
is made; the horizontal bars are the one-sided 95% upper bounds of A, `upper_one_sided_95`, which define N*
(the smallest budget whose upper bound lies below δ at it and at every larger budget). Solid line with filled
circles: primary backbone (v2), adopted after diagnostics of the originally registered backbone; dashed line
with open circles, a hatched band and lighter bars: originally registered backbone (v1). Values:
`results/c1c2_v2.json` and
`results/c1c2_v1.json`, key `payload.A_mae.<B>` (`A`, two-sided 95% interval `ci95`, `upper_one_sided_95`);
N* and the ceiling at the largest budget in `payload.N_star` and `payload.C2` of the same files. The dashed
horizontal line is the margin δ (`payload.delta_eV`), the dotted line zero. Shaded bands are two-sided 95%
intervals from the paired hierarchical bootstrap. No extension series is drawn: the K-fold CV and precision-extension analysis records (`results/cv_g1_v1.json`, `results/cv_g1_v2.json`, `results/precision_g1_v1.json`, `results/precision_g1_v2.json`) do not exist yet. Script: `figures/code/fig3_advantage.py`.
