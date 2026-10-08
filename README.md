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

The analysis remains blinded. Each card observation is the **unrounded prefit background-only expectation**, evaluated with signal strength zero and nominal nuisance values. The expectation includes the simulated tt, ST, and Others yields and the data-driven DY and QCD yields **after applying the initial rateParam values**. It is neither a sum of MC backgrounds alone nor a simple sum of the entries in the `rate` row.

For QCD, the base `rate` is 1 and the QCD rateParam initial value is the nominal absolute yield. For a positive DY source, the base `rate` is the light-jet source yield and the DY rateParam initial value is the aMC normalisation factor. A zero-source DY channel uses its additive rateParam with nominal value zero. Multiplicative lnN modifiers are unity at their nominal nuisance values.

For example, in the M20 2016preVFP channel, DY is `831.221959608 * 0.140454398 = 116.748779941` events and QCD is `1 * 14.184085883` events. Including tt, ST, and Others gives `313.669289461` events, which is now written as the observation. Earlier snapshots rounded this value to `314`; those rounded observations were background-derived placeholders rather than exact Asimov observations.

Blind card generation does not open the signal-region `data.root` histogram. Data-driven control-region inputs remain part of the background prediction. In unblind mode, a missing signal-region data input raises an error instead of silently substituting an Asimov observation.

The expected-limit command uses `AsymptoticLimits --run blind`, which constructs a prefit background-only Asimov dataset without fitting the signal-region observation. Nominal FitDiagnostics and impact calculations use `-t -1 --expectSignal 0`. The separately documented S+B impact studies intentionally inject a nonzero signal. These execution settings are unchanged by the observation correction. Existing saved fit, limit, impact, and validation outputs have not been regenerated for the updated cards; they must be rerun in the Combine environment.

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
| Heavy-flavour b tagging, uncorrelated | `CMS_btag_fixedWP_bc_uncorrelated_ERA` | Independent by era |
| Light-flavour b tagging, uncorrelated | `CMS_btag_fixedWP_light_uncorrelated_ERA` | Independent by era |

Era-specific nominal corrections and Up/Down responses are retained. The muon ID and momentum inputs are aggregate central-calibration variations, not a separately propagated statistical/systematic covariance decomposition. Their Run-wise correlation is the **analysis prescription**, not a consequence of identical correction values or of passing the naming checker. `mu_scale` reads the existing `MuonEnDown/Up` variations; a separate independent momentum-resolution nuisance is not introduced.

Luminosity uses the multiyear `lnN` prescriptions in the [Run 2](https://twiki.cern.ch/twiki/bin/view/CMS/LumiRecommendationsRun2) and [Run 3](https://twiki.cern.ch/twiki/bin/view/CMS/LumiRecommendationsRun3) Lumi POG recommendations. The coefficients already encode the Cholesky decomposition:

| Nuisance (`lnN`) | 2016 | 2017 | 2018 | 2022 | 2023 |
|---|---:|---:|---:|---:|---:|
| `lumi_13TeV_1516_l` | 1.0118 | - | - | - | - |
| `lumi_13TeV_151617_l` | 1.0004 | 1.0055 | - | - | - |
| `lumi_13TeV_15161718_l` | 1.0035 | 1.0061 | 1.0084 | - | - |
| `lumi_1` | - | - | - | 1.0138 | 1.0017 |
| `lumi_2` | - | - | - | - | 1.0127 |

The same 2016 coefficients apply to preVFP/postVFP, the same 2022 coefficients to 2022/2022EE, and the same 2023 coefficients to 2023/2023BPix. Each row is one shared parameter across all affected processes and channels. Run 2 and Run 3 luminosity parameters are treated as independent. Luminosity is applied to simulation-normalised signal, top pair, single top, and Others; QCD or DY also receive it only when their MC mode is selected. The data-driven QCD and DY predictions receive no direct luminosity response. All prescribed coefficients are retained even when `--ignore-rel-below` is used for other variations. Analysis-specific integrated luminosities and nominal yields are unchanged.

The luminosity update changes the generator and checked-in datacards. Existing limit, fit, impact, and validation outputs predate this update and must be regenerated from the updated cards before being quoted for the new model.

L1 prefiring remains independent between the Run2 eras. The existing generator-theory and top-mass correlations are unchanged.

For data-driven QCD, the updated generator retains normalisation modelling as
`CMS_NPS26009_bckgNorm_QCD_BJetOS_ERA` (`lnN`) and the functional-form width as
`CMS_NPS26009_bckgShape_QCD_BJetOS_ERA` (Gaussian `param`). It adds
`CMS_NPS26009_stat_QCD_BJetOS_ERA`, a zero-centred additive Gaussian statistical
shift. These three era-local QCD nuisance families remain independent between eras.
For the default run-common MC transport there is also one
`CMS_NPS26009_QCD_MCTransferStat_Run2` or `Run3` standard Gaussian, shared
within that Run with a producer-derived yield coefficient.

All NF/SS-fit statistical derivatives are calculated within SKPlotMaker's
`qcd_bkg_estimation.py` during normal ROOT production. Each regenerated
`NIsoMuon_SS_fit.root` contains `QCDStat/metadata` (`NPS26009_QCDStat_v3` for
run-common transport, v2 for legacy methods) with
the full SS-fit covariance and transfer-factor variances, plus `CentralYield`,
`FitGradient_0` through `FitGradient_4`, and two `NFGradient_*` histograms under
`QCDStat/`. The workflow sums these yield derivatives over the actual native-bin
counting window before propagating covariance. It does not reconstruct or refit
the SS function; fitted-template TH1 bin errors remain zero. NF-stat
includes finite control-data and MC statistics, plus the shared DY NF-stat in the
low-mass OS subtraction. SS-fit-stat is `sqrt(g^T C g)` with the transfer fixed.
Covariance status 2 or 3 is accepted, including boundary solutions such as
`n = 0`. Where needed, Minuit2 regularises the covariance to be positive definite.
The saved matrix is used directly; its status, regularisation flag and boundary
parameters are retained in ROOT metadata and reported by the workflow.
Their SS-data cross-covariance is unknown, so common transport uses the
era-local bound `sigma_lowNFstat + sigma_SSfitStat`, plus an independent common
MC component shared within each Run. The local width excludes that MC component
to avoid counting it twice. Legacy methods retain the full
`sigma_NFstat + sigma_SSfitStat` bound. This is a
Gaussian approximation, not a coverage test or a simultaneous control-region fit.

The QCD base rate is 1. A single formula modifier computes
`max(0, shape-yield parameter + local statistical shift + common MC shift)`; norm modelling multiplies
this yield. The shape parameter has the original nominal yield and envelope
width. The separate statistical parameter has mean zero. Nominal yields and
unrounded background-only Asimov observations therefore remain unchanged for
unchanged ROOT inputs. Both workflow and review helpers evaluate the formula at
Gaussian parameter means when reconstructing nominal yields.

Common-transfer cards use `max(0.0,@0+@1+sigmaMC*@2)`, while legacy cards use
`max(0.0,@0+@1)`, to avoid an ambiguous `TMath::Max` overload
in ROOT. Rebuild cards containing `max(0,@0+@1)` with `--stage cards` or
`--stage all`; the QCD ROOT inputs need no rerun. The nominal-yield reader also
supports the older formula for reviewing historical cards. Combine command
failures stop immediately; adaptive rMax expansion uses collected limit output.

Update SKPlotMaker, validate with
`qcd_bkg_estimation.py --mode ss-data --year Run2+3 --validate-qcd-double-ratio`,
and regenerate all affected era ROOT templates before rebuilding cards for the
new common transport. The validation tests weighted-MC statistical compatibility,
not equality or detector/generator modelling. The workflow rejects mixed/stale
common-fit fingerprints within a Run and older card contracts. ROOT-free card
tests run with `python3 -m unittest discover -s scripts/tests -v`.

**Regeneration status:** the checked-in cards under `input/` and `preservation/`,
and the saved validation/limit outputs, still precede this statistical update.
New uncertainties cannot be reconstructed for those cards without the original
per-era ROOT inputs and SS covariance. Do not relabel those snapshots as the new
model. The updated `scripts/limit_workflow.py` rejects older background contracts;
regenerate per-era QCD ROOT files, rebuild cards, then rerun limits and reviews.
No separate statistical module or execution is required. Older metadata-only
ROOT files are rejected, so rerun the producer for this derivative storage format.
The naming dictionary includes the statistical parameter and formula modifier.

For a first check in the production NIsoMuon directory, rebuild cards only:

```bash
python3 limit_workflow.py --stage cards --target runs --parameter alpha \
    --mode blind --sigfit-dir ./sigfit_inputs --strict
```

Then use the existing full-production command above to rerun the statistical
outputs. Actual ROOT/Combine production is performed on the analysis server.

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

The saved `review_validation/M20/check_names_M20.log` reports

```text
132 nuisances checked, no issues related to nuisance parameter names found.
```

The former 150-name model had independent era nuisances for pileup, muon ID, and muon momentum. Replacing each set of eight by two Run-level parameters reduces the M20 count by 18. Counts can vary with mass because some terms are inactive; the M70 card contains 130 constrained nuisance parameters. Naming validation is not a validation of fit convergence or a prescription for physical correlations.

## Validation status

The preserved model and review material are snapshots of the blinded
production used for the analysis note, before the new QCD statistical nuisance.
The statements below describe those saved snapshots; updated-model validation
requires regenerated inputs, cards and fits.

The CMS nuisance-name checker reports no naming issues for the representative
M20 card (132 active nuisances) or the M70 card (130 active nuisances).

The previously zero-width intervals of the very small additive DY
`LightJetStat` nuisances were traced to numerical interval-crossing precision.
Using tighter crossing and minimizer tolerances gives finite intervals, while
dedicated checks show no change in the affected expected limits at the stored
numerical precision. The nominal likelihood is therefore unchanged.

The additive QCD functional-form nuisance has finite fitted intervals and shows
no analogous numerical problem.

Bias tests were performed at M20 and M70, including background-only and
signal-injected pseudo-experiments. No material signal-recovery bias is
observed.

Background-only 1D likelihood scans at M20 and M70 have bracketed 68% and 95%
crossings after extending the scan ranges.

At M70, the HybridNew limit evaluated on a background-only Asimov dataset is
about 7.1% higher than the corresponding AsymptoticLimits result.

The analysis remains blinded throughout these validation studies. Compact
validation outputs are stored under `review_validation/M20/` and
`review_validation/M70/`.
