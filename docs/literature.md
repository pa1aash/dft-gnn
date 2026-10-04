# Literature: verified references and key claims

Session S01, retrieved 2026-10-05. Every DOI listed was resolved at doi.org (HTTP 302) and returned a
BibTeX record by content negotiation; every arXiv identifier was resolved through the arXiv API. No
reference was added from memory. Items that could not be fully verified are listed at the end. The
BibTeX for all items is in `paper/refs.bib` (built by `scripts/build_bib.py`, checked by
`scripts/verify_bib.py`).

**Relevance to this paper.** PREDICT-style staging (Linton, Singh & Aidhy 2026: predict the Bader
charge, then E_f) is the closest published analogue of our staged model P. Its central-atom
"mini" graph is the analogue of our site-centred readout. That work concerns metallic FCC
high-entropy alloys, so it is a methodological precedent, not a benchmark on oxides. Kiyohara et al.
2025 (CGCNN on pristine unit cells with O-site readout) is the structure-only benchmark for C0; see
`docs/provenance.md`.

Method: metadata from api.crossref.org (works/{doi} and query.bibliographic); abstracts from api.openalex.org (abstract_inverted_index), api.semanticscholar.org (batch), export.arxiv.org, or the publisher's `dc.description` meta tag (nature.com) where the APIs had none. "Resolved" = `curl -sI https://doi.org/<doi>` returned HTTP 302 (or, for arXiv, `export.arxiv.org/api/query?id_list=` returned the entry and `https://arxiv.org/abs/<id>` returned 200). "BibTeX" = `curl -sL -H "Accept: application/x-bibtex" https://doi.org/<doi>` output starts with `@` (for arXiv, tested via the DataCite DOI 10.48550/arXiv.<id>). Key claims are paraphrased from the retrieved abstract; where no abstract could be retrieved this is stated.

Columns: citation | DOI / arXiv | resolved | bibtex-via-doi | key claim | status

---

## 1. Core data papers

**1. Kumagai, Tsunoda, Takahashi, Oba**
- Citation: Y. Kumagai, N. Tsunoda, A. Takahashi, F. Oba, "Insights into oxygen vacancies from high-throughput first-principles calculations", Phys. Rev. Materials 5, 123803 (2021).
- DOI: 10.1103/physrevmaterials.5.123803 | resolved Y | bibtex Y
- Key claim: High-throughput point-defect codes applied to oxygen vacancies in 937 oxides; random-forest models predict vacancy formation energies to 0.27 to 0.44 eV depending on charge state, with the neutral-vacancy energy governed mainly by conduction-band-minimum orbital character, oxide stability and band gap. The codes and data are public.
- Status: VERIFIED

**2. Kiyohara, Shibui, Bae, Kumagai**
- arXiv: S. Kiyohara, C. Shibui, S. Bae, Y. Kumagai, "Machine Learning Prediction of Charged Defect Formation Energies from Crystal Structures", arXiv:2510.00513 (v1 posted 2025-10-01; v2 current).
- Journal version EXISTS: "Machine-Learning Prediction of Charged-Defect Formation Energies from Crystal Structures", Phys. Rev. Lett. 135, 246101 (2025). The arXiv record carries this journal_ref and DOI.
- DOI: 10.1103/h66h-y5k6 | resolved Y | bibtex Y ; arXiv:2510.00513 | resolved Y | bibtex (DataCite) Y
- Key claim: Proposes a protocol (data normalisation, Fermi-level alignment, treatment of perturbed host states) that lets a single structure-only model predict O-vacancy formation energies in q = 0, +1 and +2. It is combined with band-edge prediction to screen for 89 hole-dopable oxides. Full text (arXiv PDF): CGCNN accuracies are 0.29/0.22/0.37 eV for 0/+1/+2, and removing defects with PHS from the data improves accuracy.
- Status: VERIFIED (journal version found)

---

## 2. Graph networks

**3. Linton, Singh, Aidhy (npj Comput. Mater. 2026)**
- Citation: N. Linton, P. Singh, D. S. Aidhy, "Framework to completely bypass expensive DFT calculations via graph neural networks for vacancy formation energy predictions in FCC high entropy alloys", npj Comput. Mater. 12, 175 (2026). Published online 2026-03-19. Open access.
- DOI: 10.1038/s41524-026-02037-6 | resolved Y | bibtex Y
- Key claim: A fine-tuned CHGNet relaxes FCC alloy structures. CGCNN models trained on binary and ternary alloys then predict Bader charges and vacancy formation energies in HEAs with no DFT.
- Full-text checks (nature.com HTML, fetched with curl):
  - Mini/local graph: YES. Methods, subsection "Crystal graph convolutional neural network (CGCNN) graph construction and feature representation": "rather than using the entire structure as the graph, a "mini" graph is used. That is, a graph consisting of only the central atom (the atom for which predictions are made) and its 12 NNs in FCC."
  - Bader first, then E_f: YES. Results, text around Fig. 2 ("Model framework"): "Bader charges are then predicted for these structures via Model 2. The predicted Bader charges and relaxed structure from Models 1 and 2 are then fed into Model 3 to predict E_v^f". The Fig. 6 caption repeats it: "by first predicting the Bader charges and using them as input to the E_v^f model".
- Status: CORRECTED. "PREDICT" is not the title of this paper. In the text it names the authors' earlier train-on-simple-alloys and predict-in-HEAs approach ("our previously developed PREDICT approach", ref. 15 = Linton & Aidhy, APL Mach. Learn. 1, 016109 (2023), resolved separately in S01: N. Linton, D. S. Aidhy, "A machine learning framework for elastic constants predictions in multi-principal element alloys", APL Mach. Learn. 1, 016109 (2023), DOI 10.1063/5.0129928, resolved Y). The system is also important: metallic FCC high-entropy alloys, not oxides.

**4. MEGNet**
- Citation: C. Chen, W. Ye, Y. Zuo, C. Zheng, S. P. Ong, "Graph Networks as a Universal Machine Learning Framework for Molecules and Crystals", Chem. Mater. 31, 3564-3572 (2019).
- DOI: 10.1021/acs.chemmater.9b01294 | resolved Y | bibtex Y
- Key claim: MEGNet graph-network models predict properties of molecules and crystals accurately. They beat prior models such as SchNet on 11 of 13 QM9 properties and also do well on crystal properties.
- Status: VERIFIED

**6. CGCNN**
- Citation: T. Xie, J. C. Grossman, "Crystal Graph Convolutional Neural Networks for an Accurate and Interpretable Prediction of Material Properties", Phys. Rev. Lett. 120, 145301 (2018).
- DOI: 10.1103/physrevlett.120.145301 | resolved Y | bibtex Y
- Key claim: A convolutional network learns material properties directly from the crystal graph (atomic connectivity), with no hand-built feature vectors, and the results stay interpretable.
- Status: VERIFIED

**7. ALIGNN**
- Citation: K. Choudhary, B. DeCost, "Atomistic Line Graph Neural Network for improved materials property predictions", npj Comput. Mater. 7, 185 (2021).
- DOI: 10.1038/s41524-021-00650-1 | resolved Y | bibtex Y
- Key claim: Message passing on the atomistic graph and its line graph adds bond angles explicitly, which improves property prediction over distance-only GNNs.
- Note: an Author Correction exists, npj Comput. Mater. 8, 221 (2022), DOI 10.1038/s41524-022-00913-5 (found by Crossref search only; resolution not tested).
- Status: VERIFIED

---

## 3. MLIPs / foundation potentials

**8. MACE-MP-0**
- Citation: I. Batatia, P. Benner, Y. Chiang, et al. (88 authors), "A foundation model for atomistic materials chemistry", J. Chem. Phys. 163, 184110 (2025). Preprint arXiv:2401.00096 (v1 2023-12-29).
- DOI: 10.1063/5.0297006 | resolved Y | bibtex Y ; arXiv:2401.00096 | resolved Y | bibtex (DataCite) Y
- Key claim: MACE-MP-0 is a single ML force field trained on a moderate-size public dataset. It runs stable MD across a broad range of molecules and materials and can be fine-tuned with a few data points to reach ab initio accuracy.
- Status: VERIFIED; journal version found (cite JCP 2025).

**9. CHGNet**
- Citation: B. Deng, P. Zhong, K. Jun, J. Riebesell, K. Han, C. J. Bartel, G. Ceder, "CHGNet as a pretrained universal neural network potential for charge-informed atomistic modelling", Nat. Mach. Intell. 5, 1031-1041 (2023).
- DOI: 10.1038/s42256-023-00716-3 | resolved Y | bibtex Y
- Key claim: A pretrained universal GNN potential that includes magnetic-moment (charge) information to capture coupling between electronic states and ionic rearrangement at large scale.
- Status: VERIFIED

**10. M3GNet**
- Citation: C. Chen, S. P. Ong, "A universal graph deep learning interatomic potential for the periodic table", Nat. Comput. Sci. 2, 718-728 (2022).
- DOI: 10.1038/s43588-022-00349-3 | resolved Y | bibtex Y
- Key claim (abstract via Semantic Scholar): A universal GNN interatomic potential with three-body interactions (M3GNet), trained on ten years of Materials Project relaxations, used for relaxation, MD and property prediction.
- Status: VERIFIED

---

## 4. Software

**5. matgl (Materials Graph Library)**
- Citation: T. W. Ko, B. Deng, M. Nassar, et al. (12 authors, last S. P. Ong), "Materials Graph Library (MatGL), an open-source graph deep learning library for materials science and chemistry", npj Comput. Mater. 11, 253 (2025).
- DOI: 10.1038/s41524-025-01742-y | resolved Y | bibtex Y
- Key claim: MatGL is an extensible graph deep-learning library built on DGL and pymatgen. It implements M3GNet, MEGNet, CHGNet, TensorNet and SO3Net, ships pretrained foundation potentials and property models, and trains through PyTorch Lightning.
- GitHub: `https://github.com/materialsvirtuallab/matgl` returns HTTP 301 to `https://github.com/materialyzeai/matgl`. The repo README (raw.githubusercontent, main branch) names this npj paper as the one to cite.
- Zenodo: no MatGL software DOI found (zenodo.org/api/records queries "matgl", "materialsvirtuallab/matgl" and title:matgl returned no MatGL record).
- Status: CORRECTED. The repo has moved to the materialyzeai organisation (old URL still redirects). No Zenodo DOI could be verified.

**11. pymatgen**
- Citation: S. P. Ong, W. D. Richards, A. Jain, G. Hautier, et al. (10 authors), "Python Materials Genomics (pymatgen): A robust, open-source python library for materials analysis", Comput. Mater. Sci. 68, 314-319 (2013).
- DOI: 10.1016/j.commatsci.2012.10.028 | resolved Y | bibtex Y
- Key claim: No abstract was retrievable from Crossref, OpenAlex or Semantic Scholar, so this is from the title only: introduces pymatgen, an open-source Python library for materials analysis.
- Status: VERIFIED (metadata); abstract not retrieved

**12. ASE**
- Citation: A. Hjorth Larsen, J. J. Mortensen, J. Blomqvist, et al. (34 authors), "The atomic simulation environment - a Python library for working with atoms", J. Phys.: Condens. Matter 29, 273002 (2017).
- DOI: 10.1088/1361-648x/aa680e | resolved Y | bibtex Y
- Key claim: ASE is a Python package for setting up, steering and analysing atomistic simulations through scripts.
- Status: VERIFIED

**13. Optuna**
- Citation: T. Akiba, S. Sano, T. Yanase, T. Ohta, M. Koyama, "Optuna: A Next-generation Hyperparameter Optimization Framework", Proc. 25th ACM SIGKDD Int. Conf. Knowledge Discovery & Data Mining (KDD '19), pp. 2623-2631 (2019). (The Crossref title field holds only "Optuna".)
- DOI: 10.1145/3292500.3330701 | resolved Y | bibtex Y
- Key claim: Sets out design criteria for hyperparameter-optimisation software: a define-by-run search space, efficient search and pruning, and an easily deployed, versatile architecture.
- Status: VERIFIED

**14. scikit-learn**
- Citation: F. Pedregosa, G. Varoquaux, A. Gramfort, et al. (16 authors), "Scikit-learn: Machine Learning in Python", J. Mach. Learn. Res. 12(85), 2825-2830 (2011).
- URL: https://jmlr.org/papers/v12/pedregosa11a.html | HTTP 200 (curl -L), page title and author list confirmed | no DOI (bibtex-via-doi N/A)
- Key claim: A Python module that integrates many state-of-the-art ML algorithms for medium-scale supervised and unsupervised problems, with emphasis on ease of use, performance, documentation and API consistency.
- Status: VERIFIED

---

## 5. Defect theory

**15. Freysoldt et al.**
- Citation: C. Freysoldt, B. Grabowski, T. Hickel, J. Neugebauer, G. Kresse, A. Janotti, C. G. Van de Walle, "First-principles calculations for point defects in solids", Rev. Mod. Phys. 86, 253-305 (2014).
- DOI: 10.1103/revmodphys.86.253 | resolved Y | bibtex Y
- Key claim: A review of electronic-structure (supercell) methods for modelling point defects and impurities, and of their predictive value alongside experiment.
- Status: VERIFIED

**16. Zhang & Northrup**
- Citation: S. B. Zhang, J. E. Northrup, "Chemical potential dependence of defect formation energies in GaAs: Application to Ga self-diffusion", Phys. Rev. Lett. 67, 2339-2342 (1991).
- DOI: 10.1103/physrevlett.67.2339 | resolved Y | bibtex Y
- Key claim: Absolute formation energies (and so equilibrium concentrations) of native GaAs defects depend strongly on the atomic (As, Ga) and electron chemical potentials. The Ga-vacancy concentration changes by more than ten orders of magnitude across the allowed range.
- Status: VERIFIED (the full title includes the subtitle "Application to Ga self-diffusion")

**17. Zhang, Wei & Zunger (doping-limit / formalism papers)**
- 17a. S. B. Zhang, S.-H. Wei, A. Zunger, "A phenomenological model for systematization and prediction of doping limits in II-VI and I-III-VI2 compounds", J. Appl. Phys. 83, 3192-3196 (1998). DOI 10.1063/1.367120 | resolved Y | bibtex Y | Key claim: wide-gap semiconductors are often dopable only n or p type, and this asymmetry follows a phenomenological "doping pinning rule". | VERIFIED
- 17b. S. B. Zhang, S.-H. Wei, A. Zunger, "Microscopic Origin of the Phenomenological Equilibrium "Doping Limit Rule" in n-Type III-V Semiconductors", Phys. Rev. Lett. 84, 1232-1235 (2000). DOI 10.1103/physrevlett.84.1232 | resolved Y | bibtex Y | Key claim: first-principles energetics show that equilibrium n-type doping is limited by spontaneous formation of closed-shell compensating acceptors (e.g. 3- cation vacancies), which explains the universal pinning energy. | VERIFIED
- 17c (the "PRB 2001" in the request). S. B. Zhang, S.-H. Wei, A. Zunger, "Intrinsic n-type versus p-type doping asymmetry and the defect physics of ZnO", Phys. Rev. B 63, 075205 (2001). DOI 10.1103/physrevb.63.075205 | resolved Y | bibtex Y | Key claim: a native-defect study of ZnO (Zn_O, Zn_i, V_O, O_i, V_Zn and Al/F dopants) explains why ZnO is n type under Zn-rich conditions. Most directly relevant to V_O. | VERIFIED
- Supplementary formalism review: C. G. Van de Walle, J. Neugebauer, "First-principles calculations for defects and impurities: Applications to III-nitrides", J. Appl. Phys. 95, 3851-3879 (2004). DOI 10.1063/1.1682673 | resolved Y | bibtex Y | Key claim: a review of state-of-the-art methods for defect and impurity structure and energetics, including charge states and transition levels. | VERIFIED
- Recommendation: for the formation-energy formalism, cite Zhang & Northrup 1991 together with Van de Walle & Neugebauer 2004 and/or Freysoldt 2014. Cite Zhang-Wei-Zunger 2000/2001 for doping limits and ZnO V_O physics.

**18. Lany & Zunger 2008**
- Citation: S. Lany, A. Zunger, "Assessment of correction methods for the band-gap problem and for finite-size effects in supercell defect calculations: Case studies for ZnO and GaAs", Phys. Rev. B 78, 235104 (2008).
- DOI: 10.1103/physrevb.78.235104 | resolved Y | bibtex Y
- Key claim: Finds no universal band-gap correction for defects and offers a classification of defect behaviour instead. Using up to 1728-atom supercells, it shows that a Makov-Payne first-order image-charge term scaled by about 2/3 gives size-independent formation energies.
- Status: VERIFIED (the full title includes the subtitle "Case studies for ZnO and GaAs")

**19. Perturbed-host-state (PHS) literature**
- 19a. S. Lany, A. Zunger, "Anion vacancies as a source of persistent photoconductivity in II-VI and chalcopyrite semiconductors", Phys. Rev. B 72, 035215 (2005). DOI 10.1103/physrevb.72.035215 | resolved Y | bibtex Y | Key claim: defines the type-alpha (defect-localised state in the gap) vs type-beta (resonant state in the host band, carriers relax into a perturbed host state) classification, with the neutral O vacancy in ZnO as type alpha and V_O^2+ as type beta. | VERIFIED
- 19b. Y. Zhang, A. Mascarenhas, L.-W. Wang, "Systematic approach to distinguishing a perturbed host state from an impurity state in a supercell calculation for a doped semiconductor: Using GaP:N as an example", Phys. Rev. B 74, 041201 (2006). DOI 10.1103/physrevb.74.041201 | resolved Y | bibtex Y | Key claim: a supercell procedure (charge patching) to tell perturbed host states from true impurity states, shown for GaP:N. | VERIFIED
- 19c. N. Tsunoda, Y. Kumagai, A. Takahashi, F. Oba, "Electrically Benign Defect Behavior in Zinc Tin Nitride Revealed from First Principles", Phys. Rev. Applied 10, 011001 (2018). DOI 10.1103/physrevapplied.10.011001 | resolved Y | bibtex Y | Key claim: all deep-level defects in ZnSnN2 are energetically unfavourable. Kiyohara et al. 2025 cite it (with 19b and 19d) for the definition and behaviour of PHS. | VERIFIED
- 19d. Y. Kumagai, M. Choi, Y. Nose, F. Oba, "First-principles study of point defects in chalcopyrite ZnSnP2", Phys. Rev. B 90, 125202 (2014). DOI 10.1103/physrevb.90.125202 | resolved Y | bibtex Y | Key claim: an HSE study of native defects in ZnSnP2 with image-charge corrections. Cation antisites dominate and pin the Fermi level. Cited by Kiyohara et al. as a PHS reference. | VERIFIED
- Context: in the arXiv PDF of Kiyohara et al. (2510.00513), the "Perturbed host states" paragraph defines PHS as donor electrons that "drop into the CBM and become loosely trapped by defect centers electrostatically", citing refs [17-19] = 19b, 19c, 19d. Kumagai et al. PRM 2021 (item 1) is the dataset in which PHS flags are assigned. Its abstract does not define PHS, and no arXiv full text was found to give a locator.
- No separate journal paper titled "pydefect" was found; pydefect is introduced as the code in item 1.

---

## 6. Defect ML

**20. Witman et al.**
- Citation: M. D. Witman, A. Goyal, T. Ogitsu, A. H. McDaniel, S. Lany, "Defect graph neural networks for materials discovery in high-temperature clean-energy applications", Nat. Comput. Sci. 3, 675-686 (2023).
- DOI: 10.1038/s43588-023-00495-2 | resolved Y | bibtex Y
- Key claim (abstract from nature.com dc.description): a defect GNN (dGNN) trained on DFT oxide-vacancy data predicts site-resolved defect formation enthalpies from the ideal (undefected) crystal structure, replacing per-site DFT supercell relaxations. It is coupled to reduction thermodynamics to screen oxides.
- Status: VERIFIED

**21. Frey et al. ACS Nano 2020**
- Citation: N. C. Frey, D. Akinwande, D. Jariwala, V. B. Shenoy, "Machine Learning-Enabled Design of Point Defects in 2D Materials for Quantum and Neuromorphic Information Processing", ACS Nano 14, 13406-13417 (2020).
- DOI: 10.1021/acsnano.0c05267 | resolved Y | bibtex Y
- Key claim: Deep transfer learning, ML and first-principles calculations, with physics-informed featurisation, rapidly predict point-defect properties in 2D materials. This identifies over 100 promising dopant defects for quantum emission and neuromorphic or resistive-switching uses.
- Status: CORRECTED. The authors are Frey, Akinwande, Jariwala, Shenoy, not "Frey, Ren, Chen, ... Shenoy". The title is not "High-throughput search of 2D ... point defects". (A different Frey/Shenoy 2020 paper, "High-throughput search for magnetic and topological order in transition metal oxides", Sci. Adv., DOI 10.1126/sciadv.abd1076, came up in the Crossref search. It is not a defect paper and was not resolved.)

**22. Deml et al. 2015**: see Physics floor (Section 9).

**23. Mannodi-Kanakkithodi et al. 2022**
- Citation: A. Mannodi-Kanakkithodi, X. Xiang, L. Jacoby, R. Biegaj, S. T. Dunham, D. R. Gamelin, M. K. Y. Chan, "Universal machine learning framework for defect predictions in zinc blende semiconductors", Patterns 3, 100450 (2022).
- DOI: 10.1016/j.patter.2022.100450 | resolved Y | bibtex Y
- Key claim: ML plus high-throughput DFT predicts and screens functional impurities (cation, anion and interstitial sites, elements across the periodic table) in 34 group IV, III-V and II-VI zinc-blende semiconductors.
- Status: VERIFIED (journal is Patterns)

---

## 7. Statistics / ML methodology

**24a. Roberts et al. 2017 (grouped/blocked CV)**
- Citation: D. R. Roberts, V. Bahn, S. Ciuti, et al. (14 authors), "Cross-validation strategies for data with temporal, spatial, hierarchical, or phylogenetic structure", Ecography 40, 913-929 (2017).
- DOI: 10.1111/ecog.02881 | resolved Y | bibtex Y
- Key claim: Random CV that ignores dependence structure in data seriously underestimates predictive error, so blocked CV strategies matched to that structure are recommended.
- Status: VERIFIED

**24b. Meredig et al. 2018 (leave-one-cluster-out CV)**
- Citation: B. Meredig, E. Antono, C. Church, et al. (12 authors), "Can machine learning identify the next high-temperature superconductor? Examining extrapolation performance for materials discovery", Mol. Syst. Des. Eng. 3, 819-825 (2018).
- DOI: 10.1039/c8me00012c | resolved Y | bibtex Y
- Key claim (the OpenAlex abstract is one sentence): conventional ML metrics overestimate model performance for materials discovery. (The leave-one-cluster-out CV detail is not in the retrieved abstract.)
- Status: VERIFIED

**25. Deep ensembles**
- Citation: B. Lakshminarayanan, A. Pritzel, C. Blundell, "Simple and Scalable Predictive Uncertainty Estimation using Deep Ensembles", Advances in Neural Information Processing Systems 30 (NIPS 2017). arXiv:1612.01474.
- arXiv:1612.01474 | resolved Y | bibtex (DataCite 10.48550/arXiv.1612.01474) Y. NeurIPS proceedings page https://papers.nips.cc/paper_files/paper/2017/hash/9ef2ed4b7fd2c810847ffa5fa85bce38-Abstract.html returned HTTP 200, with the title, authors and "Advances in Neural Information Processing Systems 30 (NIPS 2017)" confirmed. No publisher DOI. Page numbers not verified.
- Key claim: Ensembles of independently trained (non-Bayesian) networks are simple, parallelisable and need little tuning, yet give well-calibrated predictive uncertainty as good as or better than approximate Bayesian NNs.
- Status: VERIFIED

**26a. Efron 1979**
- Citation: B. Efron, "Bootstrap Methods: Another Look at the Jackknife", Ann. Statist. 7(1), (1979).
- DOI: 10.1214/aos/1176344552 | resolved Y | bibtex Y
- Key claim: Introduces the bootstrap, which estimates the sampling distribution of a statistic by resampling the observed data, as a more general alternative to the jackknife.
- Status: VERIFIED. Page range NOT verified: Crossref, OpenAlex and the BibTeX record carry no pages, and the Project Euclid fetch returned nothing. Check the pages before printing.

**26b. Efron & Tibshirani, An Introduction to the Bootstrap**
- DOI 10.1201/9780429246593 (Chapman and Hall/CRC). Resolved Y, bibtex Y. Crossref issued date is 1994-05-15 (the CRC e-book record of the 1993 monograph).
- Alternative DOI 10.1007/978-1-4899-4541-9 (Springer US record, issued 1993). Resolved Y, bibtex Y.
- Key claim (OpenAlex abstract of the CRC record): an introduction to the bootstrap as a computer-based inference method for estimating variance, bias and coverage without analytic formulas.
- Status: VERIFIED. The year in the CRC DOI's metadata (1994) differs from the 1993 publication year, so pick one record and keep the year consistent.

**27. Schuirmann 1987 (TOST)**
- Citation: D. J. Schuirmann, "A comparison of the Two One-Sided Tests Procedure and the Power Approach for assessing the equivalence of average bioavailability", J. Pharmacokinet. Biopharm. 15, 657-680 (1987).
- DOI: 10.1007/bf01068419 | resolved Y | bibtex Y
- Key claim (abstract via Semantic Scholar): compares the common "power approach" to bioequivalence (testing for no difference plus a post hoc power requirement) with the two one-sided tests procedure, and supports TOST.
- Status: VERIFIED

**28. Lakens 2017**
- Citation: D. Lakens, "Equivalence Tests: A Practical Primer for t Tests, Correlations, and Meta-Analyses", Soc. Psychol. Personal. Sci. 8, 355-362 (2017). (The Crossref title field holds only "Equivalence Tests". The full title is confirmed by the PsyArXiv preprint record 10.31234/osf.io/97gpc, found by Crossref search only.)
- DOI: 10.1177/1948550617697177 | resolved Y | bibtex Y
- Key claim: A nonsignificant result does not show that an effect is absent. Equivalence tests such as TOST, with prespecified upper and lower bounds, can support the absence of a meaningful effect.
- Status: VERIFIED

**29. Alain & Bengio linear probes**
- Citation: G. Alain, Y. Bengio, "Understanding intermediate layers using linear classifier probes", arXiv:1610.01644 (2016; v4 current). No journal_ref on the arXiv record.
- arXiv:1610.01644 | resolved Y | bibtex (DataCite) Y
- Key claim: Linear classifiers ("probes") trained separately on each layer's features monitor how linearly separable the representations are. In Inception v3 and ResNet-50, separability increases monotonically with depth.
- Status: VERIFIED

---

## 8. Oxide motivation

**Transparent conducting oxides**
- S. Lany, A. Zunger, "Dopability, Intrinsic Conductivity, and Nonstoichiometry of Transparent Conducting Oxides", Phys. Rev. Lett. 98, 045501 (2007). DOI 10.1103/physrevlett.98.045501 | resolved Y | bibtex Y | Key claim: corrected first-principles defect energetics for In2O3 and ZnO, validated against measured defect and carrier densities, explain high n-dopability (intrinsic "electron killers" are costly) and the origins of conductivity, nonstoichiometry and coloration. | VERIFIED
- K. Ellmer, "Past achievements and future challenges in the development of optically transparent electrodes", Nat. Photonics 6, 809-817 (2012). DOI 10.1038/nphoton.2012.282 | resolved Y | bibtex Y | Key claim (nature.com description): a review comparing transparent conductive oxides with alternatives (carbon nanotubes, metal nanowires, metal grids, graphene) for transparent electrodes. | VERIFIED

**Ceria redox catalysis**
- F. Esch, S. Fabris, L. Zhou, T. Montini, C. Africh, P. Fornasiero, G. Comelli, R. Rosei, "Electron Localization Determines Defect Formation on Ceria Substrates", Science 309, 752-755 (2005). DOI 10.1126/science.1111568 | resolved Y | bibtex Y | Key claim: STM plus DFT on CeO2(111) shows that ceria's oxygen-buffer and catalytic role rests on oxygen-vacancy formation, with the excess electrons localising on cerium ions and controlling vacancy structure. | VERIFIED
- J. Paier, C. Penschke, J. Sauer, "Oxygen Defects and Surface Chemistry of Ceria: Quantum Chemical Studies Compared to Experiment", Chem. Rev. 113, 3949-3985 (2013). DOI 10.1021/cr3004949 | resolved Y | bibtex Y | Key claim: from the title only, since OpenAlex returned page boilerplate rather than an abstract: a review of quantum-chemical studies of ceria oxygen defects and surface chemistry against experiment. | VERIFIED (metadata)

**Resistive switching / memristors**
- R. Waser, M. Aono, "Nanoionics-based resistive switching memories", Nat. Mater. 6, 833-840 (2007). DOI 10.1038/nmat2023 | resolved Y | bibtex Y | Key claim (nature.com description): classifies resistive switching as thermal, electrical or ion-migration-driven. In anion-migration cells (typically transition-metal oxides), conducting sub-oxide paths form and dissolve through local redox. | VERIFIED
- J. J. Yang, M. D. Pickett, X. Li, D. A. A. Ohlberg, D. R. Stewart, R. S. Williams, "Memristive switching mechanism for metal/oxide/metal nanodevices", Nat. Nanotechnol. 3, 429-433 (2008). DOI 10.1038/nnano.2008.160 | resolved Y | bibtex Y | Key claim (nature.com description): in Pt/TiO2 devices, bipolar switching comes from drift of positively charged oxygen vacancies that create or remove conducting channels across the Pt/TiO2 interface barrier. | VERIFIED

**Vacancy-induced coloration**
- X. Chen, L. Liu, P. Y. Yu, S. S. Mao, "Increasing Solar Absorption for Photocatalysis with Black Hydrogenated Titanium Dioxide Nanocrystals", Science 331, 746-750 (2011). DOI 10.1126/science.1200448 | resolved Y | bibtex Y | Key claim: hydrogenation adds surface disorder to nanophase TiO2, extending its absorption from the UV into the visible and infrared ("black titania") for photocatalysis. Note: the abstract attributes this to disorder engineering, not explicitly to oxygen vacancies. | VERIFIED
- C. G. Granqvist, "Electrochromic tungsten oxide films: Review of progress 1993-1998", Sol. Energy Mater. Sol. Cells 60, 201-262 (2000). DOI 10.1016/s0927-0248(99)00088-4 | resolved Y | bibtex Y | Key claim: from the title only, since no abstract was retrievable from any API: a review of electrochromic WO3 film research, 1993-1998. | VERIFIED (metadata)

**Solid-oxide ion conduction**
- J. A. Kilner, M. Burriel, "Materials for Intermediate-Temperature Solid-Oxide Fuel Cells", Annu. Rev. Mater. Res. 44, 365-393 (2014). DOI 10.1146/annurev-matsci-070813-113426 | resolved Y | bibtex Y | Key claim: reviews the stringent materials requirements for SOFCs operating near 600 °C, including mechanical and chemical compatibility and electrochemical performance. | VERIFIED
- J. B. Goodenough, "Oxide-Ion Electrolytes", Annu. Rev. Mater. Res. 33, 91-128 (2003). DOI 10.1146/annurev.matsci.33.022802.091651 | resolved Y | bibtex Y | Key claim: electrolyte performance is critical for intermediate-temperature SOFCs. The review covers YSZ and the leading alternative oxide-ion conductors. | VERIFIED

---

## 9. Physics floor (E_V(neutral) vs formation enthalpy and band gap)

**22/31a. Deml et al. 2015**
- Citation: A. M. Deml, A. M. Holder, R. P. O'Hayre, C. B. Musgrave, V. Stevanović, "Intrinsic Material Properties Dictating Oxygen Vacancy Formation Energetics in Metal Oxides", J. Phys. Chem. Lett. 6, 1948-1953 (2015).
- DOI: 10.1021/acs.jpclett.5b00710 | resolved Y | bibtex Y
- Key claim: For 45 binary and ternary oxides, a simple model combining oxide formation enthalpy, the midgap energy relative to the O 2p band centre (E_O2p + Eg/2) and atomic electronegativities reproduces the neutral O-vacancy formation energy within about 0.2 eV. It is then applied to about 1800 oxides and validated on 18.
- Status: VERIFIED

**31b. Deml et al. 2014 (direct two-descriptor precedent)**
- Citation: A. M. Deml, V. Stevanović, C. L. Muhich, C. B. Musgrave, R. O'Hayre, "Oxide enthalpy of formation and band gap energy as accurate descriptors of oxygen vacancy formation energetics", Energy Environ. Sci. 7, 1996 (2014) (Crossref gives first page only).
- DOI: 10.1039/c3ee43874k | resolved Y | bibtex Y
- Key claim: In La1-xSrxBO3 perovskites (B = Cr, Mn, Fe, Co, Ni), oxide formation enthalpy and minimum band gap together correlate accurately with the neutral O-vacancy formation energy. The energy falls as either descriptor decreases, which links to metal-O bond strength and to redistribution of the vacancy electrons.
- Status: VERIFIED. This is the closest precedent for a two-parameter (enthalpy + gap) floor.

**31c. Wexler, Sai Gautam, Stechel, Carter 2021**
- Citation: R. B. Wexler, G. Sai Gautam, E. B. Stechel, E. A. Carter, "Factors Governing Oxygen Vacancy Formation in Oxide Perovskites", J. Am. Chem. Soc. 143, 13212-13227 (2021).
- DOI: 10.1021/jacs.1c05570 | resolved Y | bibtex Y
- Key claim: A compact linear model for neutral V_O formation energy in ABO3 perovskites (A = Ca, Sr, Ba, La, Ce; B = 3d TM) reproduces SCAN+U DFT with a 0.45 eV MAE. Its key inputs are crystal bond-dissociation energies and solid-phase reduction potentials.
- Status: VERIFIED. The author list includes E. B. Stechel. Note that this model's descriptors are bond-dissociation energy and reduction potential, not band gap directly.
- Other Wexler 2019-2023 work: Crossref returned only a book chapter, R. B. Wexler, E. B. Stechel, E. A. Carter, "Materials Design Directions for Solar Thermochemical Water Splitting", in Solar Fuels (Wiley, 2023), DOI 10.1002/9781119752097.ch1. This came from search only and was not resolved or checked, so it is UNVERIFIED. No other Wexler et al. vacancy-descriptor paper was found.

---

## Removed during verification
- One candidate DOI tested in the batch (10.1063/5.0124102) resolved to an unrelated paper on essential-oil compounds. It is not in this list.

## Unverifiable / open items
- Efron 1979 page range (not in any API record).
- Lakshminarayanan et al. NeurIPS 2017 page numbers (proceedings page confirmed; pages not checked).
- A MatGL Zenodo software DOI (none found).
- Abstracts not retrievable (claims paraphrased from titles): pymatgen 2013, Paier 2013, Granqvist 2000, Efron & Tibshirani (Springer record).
