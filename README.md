# NPS-26-009 Combine/datacard review

This repository contains the statistical model and validation material for CMS analysis NPS-26-009, a search for a narrow nonisolated dimuon resonance inside a jet in a b-tagged event topology.

## Statistical model

The analysis uses a mass-dependent **counting likelihood**. For each signal-mass hypothesis, the expected event yields are integrated over an era-dependent dimuon-mass counting window determined from the signal mass resolution.

The Run2Run3 model contains eight likelihood channels: `2016preVFP`, `2016postVFP`, `2017`, `2018`, `2022`, `2022EE`, `2023`, and `2023BPix`. The production workflow directly constructs the Run2, Run3, and Run2Run3 multichannel datacards; the full card is not assembled from eight intermediate per-era text cards.

Each channel contains `Zprime` (signal), `QCD` (data-driven multijet), `tt` (top-quark pair), `ST` (single top quark), `DY` (data-driven Drell--Yan), and `Others` (minor simulated backgrounds).

The representative CI input is

```text
m(Z') = 20 GeV
input/datacard_M20_Run2Run3.txt
```

The thirteen full-combination mass points, 12, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, and 70 GeV, are preserved under `preservation/Run2Run3/`. M70 is used for additional low-yield diagnostics; its card is not duplicated in a separate preservation directory.

## Counting model and ROOT inputs

This is a **rate-only counting model**, not a shape-template likelihood at the Combine stage. Analysis histograms are integrated when the datacards are produced. Nominal rates and nuisance responses are encoded in the text cards, including the Gaussian-constrained rate parameters described below.

No external ROOT histogram file or custom physics model is required to run a preserved card. `text2workspace.py` produces the RooWorkspace used by Combine. Temporary workspaces, toy files, and HybridNew grids are not preserved here.

## Parameter of interest

Combine fits its standard internal signal-strength parameter `r`. The physical parameter is

```text
alpha_qZp = r * alpha_internal_unit
```

The conversion depends on the mass and target combination. For the representative Run2Run3 M20 card, `alpha_internal_unit = 8.005935406497654e-07`; the nominal internal signal normalisation is 25 selected events at `r = 1`.

The conversion factors are in `preservation/alpha_internal_scaling.csv` and `preservation/alpha_internal_scaling.json`. Nominal analysis-level limit and impact outputs are rescaled to physical `alpha_qZp`; the review S+B impact JSON files retain internal `r`. The parameter key alone should not be used to infer the units of an analysis-rescaled output.

## Blinding and limit calculation

The analysis remains blinded. Card observations are the nominal background-only Asimov expectations; no observed signal-region result is used for the expected limits.

The primary expected 95% CL upper limits use `AsymptoticLimits`. The additional M70 `HybridNew` test constructs toy test-statistic distributions and evaluates CLs on a **prefit background-only Asimov dataset**. It is not a calculation of the median of an ensemble of background-only toy limits and is not a coverage test.

## Combine environment

The saved local review logs identify

```text
CMSSW_16_0_0
Combine v11.0.0
SCRAM_ARCH=el9_amd64_gcc13
CombineHarvester
```

The analysis checkout used to produce the inputs is located at

```text
/data6/Users/joonblee/higgs_combine/CMSSW_14_1_0_pre4/src/NIsoMuon
```

The directory name does not identify the active runtime: the validation uses the separately initialised CMSSW_16_0_0 environment. `.gitlab-ci.yml` defines the CERN CI configuration for M20. This repository audit does not establish the status of a CERN GitLab pipeline.

## Datacard production and reproduction

The nominal workflow is preserved in `scripts/limit_workflow.py`. In the production `NIsoMuon` directory, with the original ROOT inputs and signal-fit inputs available, the regeneration command is

```bash
python3 limit_workflow.py \
  --stage all \
  --target runs \
  --parameter alpha \
  --mode blind \
  --task all \
  --sigfit-dir ./sigfit_inputs \
  --impact-parallel 12 \
  --r-max 100 \
  --strict \
  --allow-negative-r \
  --r-min -2
```

`--target runs` builds Run2, Run3, and Run2Run3. The upstream histogram production is not reproduced by this review repository alone. `scripts/combine_review.py` operates on existing production cards, and `scripts/review.sh` is a server-specific driver, not a portable entry point for this repository layout.

A minimal M20 expected-limit calculation from the preserved card, after initialising Combine, is

```bash
mkdir -p work
text2workspace.py input/datacard_M20_Run2Run3.txt \
  -m 20 -o work/workspace_M20.root
(
  cd work
  combine -M AsymptoticLimits workspace_M20.root \
    -m 20 --run blind --rMin 0 --rMax 100 \
    --cminDefaultMinimizerStrategy 1 -n .NPS26009_M20
)
```

The physical limit is the internal result multiplied by the conversion factor above. The production helper, rather than this minimal example, defines the complete nominal command and adaptive-range bookkeeping.

## Systematic uncertainties and correlations

The nuisance dictionary is `input/systematics.yml`. In the table below, `ENERGY` means `13TeV` or `13p6TeV`, `RUN` means `Run2` or `Run3`, and `ERA` denotes one of the eight detector periods.

| Source | Datacard naming | Correlation |
|---|---|---|
| Pileup | `CMS_pileup_ENERGY` | Shared within a Run; independent between Runs |
| Muon ID | `CMS_NPS26009_eff_m_id_RUN` | Shared within a Run; independent between Runs |
| Muon trigger | `CMS_NPS26009_eff_m_trigger_ERA` | Independent by era, including 2016preVFP/postVFP |
| Muon momentum | `CMS_scale_m_ENERGY` | Shared within a Run; independent between Runs |
| JES/JER | `CMS_scale_j_ERA`, `CMS_res_j_ERA` | Independent by era |
| Heavy-flavour b tagging, correlated | `CMS_NPS26009_btag_fixedWP_comb_bc_correlated_ENERGY` | Shared within a Run; independent between Runs |
| Light-flavour b tagging, correlated | `CMS_NPS26009_btag_fixedWP_incl_light_correlated_ENERGY` | Shared within a Run; independent between Runs |
| Heavy-flavour b tagging, uncorrelated | `CMS_btag_fixedWP_comb_bc_uncorrelated_ERA` | Independent by era |
| Light-flavour b tagging, uncorrelated | `CMS_btag_fixedWP_incl_light_uncorrelated_ERA` | Independent by era |

Era-specific nominal corrections and Up/Down responses are retained. The muon ID and momentum inputs are aggregate central-calibration variations, not a separately propagated statistical/systematic covariance decomposition. Their Run-wise correlation is the **analysis prescription**, not a consequence of identical correction values or of passing the naming checker. `mu_scale` reads the existing `MuonEnDown/Up` variations; a separate independent momentum-resolution nuisance is not introduced.

Luminosity remains grouped by calendar year, with pre/post detector periods within a year sharing the corresponding aggregate nuisance. L1 prefiring remains independent between the Run2 eras. The existing generator-theory and top-mass correlations are unchanged.

For data-driven QCD, the normalisation uncertainty is multiplicative (`lnN`), while the functional-form envelope is propagated as an additive Gaussian uncertainty on the absolute QCD yield through a constrained `rateParam`. Both families are independent by era.

The data-driven DY prediction is the background-subtracted light-jet control source multiplied by an aMC@NLO normalisation factor. For a positive source, `LightJetStat` is multiplicative, `NFStat` is a Gaussian-constrained normalisation-factor `rateParam`, and `NFModel` is a multiplicative aMC@NLO-versus-MadGraph modelling response. `LightJetStat` and `NFStat` are independent by era; `NFModel` is shared within a Run and independent between Runs. A zero-source channel uses the dedicated additive `LightJetStat` yield parameter, without multiplicative `NFStat` or `NFModel` effects.

Finite simulated-sample statistical terms are independent by process and era for signal, top pair, single top, and Others; data-driven DY and QCD use their dedicated terms instead.

## Nuisance naming validation

Use the **repository's `systematics` submodule**, not a sibling checkout. From this repository root, after initialising the required CombineHarvester environment:

```bash
git submodule update --init --recursive
python3 systematics/check_names.py \
  --input input/datacard_M20_Run2Run3.txt \
  --systematics-dict input/systematics.yml \
  --global-dict systematics/systematics_master.yml \
  --analysis NPS26009
```

The saved `validation/M20/check_names_M20.log` reports

```text
132 nuisances checked, no issues related to nuisance parameter names found.
```

The former 150-name model had independent era nuisances for pileup, muon ID, and muon momentum. Replacing each set of eight by two Run-level parameters reduces the M20 count by 18. Counts can vary with mass because some terms are inactive; the M70 card contains 130 constrained nuisance parameters. Naming validation is not a validation of fit convergence or a prescription for physical correlations.

## Validation status: audit of the 9 September 2026 outputs

The audited production snapshot is [`higgs_combine@331f9c3`](https://github.com/joonblee/higgs_combine/commit/331f9c3cdfd0f3d6832889dde9da8c4323ca3f17), and the corresponding review-input snapshot is [`combine_review@3b738ff`](https://github.com/joonblee/combine_review/commit/3b738ffb18ab72b7f9162b641be814259b0a0caf). The M20 input, all thirteen preserved cards, dictionary, scripts, conversion factors, and copied diagnostics match their production counterparts by Git blob SHA. **Matching files do not imply that every diagnostic was regenerated or converged.**

The M20/M70 `ValidateDatacards.py` reports contain only `largeNormEff`: 29 process/channel entries involving 24 nuisance names at M20, and 65 entries involving 44 names at M70. There are no other alert categories in these reports. These warnings are distinct from the resolved nuisance-name issues.

The nominal limit JSON files cover all thirteen masses for each of the three targets, with finite, ordered expected quantiles. All 39 nominal impact JSON nuisance-name sets match their current cards. The full-combination median expected limits range from `5.725732054751335e-06` at M12 to `3.910017938680879e-04` at M70. Central B-only FitDiagnostics values are near zero at M20/M70; the S+B initial fits recover the injections `r=15.5` and `r=0.94921875`.

The M70 HybridNew Asimov comparison is

```text
AsymptoticLimits exp0 (internal r) : 0.94921875
HybridNew on B-only Asimov        : 1.016489031336746
HybridNew / AsymptoticLimits      : 1.0708691029720452
HybridNew grid                   : 29 points, 500 toys per point
```

The difference is **7.1%, not the previous approximately 3%**. The physical limits are `3.910017938680879e-04` and `4.187117402599798e-04`. No toy-statistical uncertainty on their ratio is stored, and this comparison does not establish ensemble coverage.

### Outstanding diagnostics

**Cached bias toys.** Both production `review_logs/bias_M20.log` and `bias_M70.log` explicitly report `[BIAS] reuse completed fit` for every injection. The unchanged bias summaries are retained as existing outputs, but do not validate signal recovery after the correlation revision. The helper reuses matching toy-fit filenames unless `--force` is supplied; the saved `review.sh` does not force the bias tasks. Rerun these tasks with `--force`, inspect fit counts and pulls, and replace the two preserved summaries before marking this check complete.

**Zero-width nuisance intervals.** The nominal Run3 and Run2Run3 impact files contain `fit: [0, 0, 0]` for `CMS_NPS26009_LightJetStat_DY_BJetOS_2023BPix` at M55 and `CMS_NPS26009_LightJetStat_DY_BJetOS_2023` at M70. Their nonzero Gaussian widths are approximately `4.30e-05` and `7.79e-05` events, respectively; both are additive parameters with a lower bound at zero. The M70 S+B nuisance-fit log also reports `[ERROR] Closed range without finding crossing!`. A zero stored impact must not be interpreted as proof that this uncertainty is absent. These interval fits need a dedicated boundary and numerical-precision check; the cause and the effect on inference have not been established by this file audit.

**Scan-plot export.** Both `scan_plot_M20.log` and `scan_plot_M70.log` report failures to write their PDF/PNG outputs. The helper passes an absolute output prefix to `plot1DScan.py`, which produces a malformed `.//data6/...` output path. Replot the saved scan ROOT files using a relative output basename and verify the files exist. The stored interval summaries also contain unbracketed lower crossings (M20 at 68%/95%, M70 at 95%); do not report those endpoints as measured two-sided intervals.

The compact diagnostics are under `validation/M20/` and `validation/M70/`; detailed logs reside in the pinned production snapshot. **The review package is synchronised, but the validation record is not yet complete.** This audit did not rerun Combine or inspect the transient ROOT toy ensembles.
