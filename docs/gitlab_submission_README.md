# NPS-26-009 Combine/datacard review

This repository preserves the blinded counting model and compact validation
material for CMS NPS-26-009. It follows the existing GitLab submission layout.

## Model and repository layout

Each signal-mass hypothesis has eight counting channels: 2016preVFP,
2016postVFP, 2017, 2018, 2022, 2022EE, 2023 and 2023BPix. The processes are
Zprime, QCD, tt, ST, DY and Others. Production constructs each multichannel
card directly; it does not require intermediate per-era cards.

| Location | Contents |
|---|---|
| `input/` | Representative M20 Run2Run3 card and nuisance dictionary |
| `preservation/Run2Run3/` | All thirteen mass hypotheses, M12 through M70 |
| `preservation/` | Alpha conversion, internal expected limits and provenance |
| `scripts/` | Production, review and saved-toy audit/repair code |
| `review_validation/M20/`, `M70/` | Current representative results and numerical checks |
| `yaml/`, `.gitlab-ci.yml`, `.gitmodules` | CI configuration and systematics submodule |

Only M20 is placed in `input/`, so the CI does not combine different signal
mass hypotheses as additional channels. No external histogram ROOT files,
custom PDFs or custom physics model are needed to run these rate-only cards.
Temporary workspaces, toys and HybridNew grids are not included.

## Signal parameter

Combine fits internal signal strength `r`. The physical parameter is
`alpha_qZp = r * alpha_internal_unit`. The conversion depends on target and
mass and is stored in `preservation/alpha_internal_scaling.csv` and `.json`.
For Run2Run3 M20, `alpha_internal_unit = 8.005935406497654e-7`, with 25 signal
events at internal r=1.

The B-only `impacts_Run2Run3_alpha_M*.json` and PDFs use physical alpha;
the corresponding `_internal.json` retains internal r. The S+B impact JSONs
and PDFs ending in `_SB` retain internal r. Bias summaries, scan labels and
the preserved limit JSON use internal r.

## Asimov observations and blinding

Observations are unrounded prefit background-only expectations, evaluated
with r=0 and nominal nuisances. They include the absolute data-driven QCD
yield and normalised data-driven DY yield after evaluating rateParams,
as well as simulated tt, ST and Others. They are not the simple sum of the
rate row or of simulated backgrounds alone. Earlier integer observations
were rounded background expectations; current cards preserve fractional values.

For example, the M20 2022EE observation is 334.485890987 events. Its nominal
QCD yield is 3.165496852 events despite the unit QCD base rate. Reconstructing
all thirteen Run2Run3 cards and eight channels agrees with the observations
within 5e-10 events, at the precision stored in the text cards.

Blind production does not read signal-region data histograms. Expected limits
use `AsymptoticLimits --run blind`. Nominal local B-only diagnostic and full
impact fits use `-t -1 --expectSignal 0`. Additional S+B impacts intentionally
inject the expected median limit; metadata record those injections.

## Uncertainties and correlations

Luminosity uses the multiyear Lumi POG Cholesky lnN components:

| Nuisance | 2016 | 2017 | 2018 | 2022 | 2023 |
|---|---:|---:|---:|---:|---:|
| lumi_13TeV_1516_l | 1.0118 | — | — | — | — |
| lumi_13TeV_151617_l | 1.0004 | 1.0055 | — | — | — |
| lumi_13TeV_15161718_l | 1.0035 | 1.0061 | 1.0084 | — | — |
| lumi_1 | — | — | — | 1.0138 | 1.0017 |
| lumi_2 | — | — | — | — | 1.0127 |

Detector periods in the same year share coefficients and nuisance parameters.
Run 2 and Run 3 luminosity components are independent. They apply directly
to signal and simulation-normalised backgrounds, not data-driven QCD or DY.

QCD has separate transfer-modelling, functional-form and statistical terms.
The unit base rate is multiplied by a final-yield formula:

    max(0, q_shape + delta_local_stat + sigma_MC * theta_MC_Run)

The functional-form parameter has a Gaussian constraint centred on the nominal
absolute yield. The local statistical Gaussian combines low-mass OS/SS data
ratio statistics and full SS-fit covariance propagation using their conservative
linear bound, because those estimates share SS data. The finite-MC transport
shift is shared within each Run and independent between Runs. It is excluded
from the local bound. The separate QCD_norm lnN factor multiplies this yield.
No extra independent statistical error is assigned to smooth fitted-template bins.

DY uses a background-subtracted light-jet data source and aMC@NLO b/light
normalisation factor. LightJetStat and NFStat are independent by era; NFModel
is shared within a Run. Zero-source channels retain additive LightJetStat and
do not attach multiplicative NFStat/NFModel responses.

Pileup, muon ID and muon momentum nuisances are shared within each Run.
Muon trigger, JES/JER and L1 prefiring nuisances are independent by era.
B-tagging terms separate Run-correlated and era-uncorrelated components.
Finite-simulation statistics are independent by process and era. Full nuisance
definitions are in `input/systematics.yml` and the datacards.

## Environment and reproduction

The validated runtime is CMSSW_16_0_0, Combine v11.0.0, ROOT 6.36.07 and
el9_amd64_gcc13, with CombineHarvester for naming checks. The production
directory under CMSSW_14_1_0_pre4 identifies the checkout, not the active runtime.

After initialising Combine, the representative expected limit can be rerun with:

```bash
mkdir -p work
text2workspace.py input/datacard_M20_Run2Run3.txt -m 20 -o work/workspace_M20.root
(
  cd work
  combine -M AsymptoticLimits workspace_M20.root -m 20 --run blind \
    --rMin 0 --rMax 100 --cminDefaultMinimizerStrategy 1 -n .NPS26009_M20
)
```

Multiply internal results by the corresponding alpha conversion. Production
`limit_workflow.py` implements the full adaptive-range workflow and physical
conversion. Regenerating analysis cards requires the original histogram and
signal-resolution inputs. `review.sh` is a server-specific production driver.
Bias repair helpers require the original saved workspace and toys, whose
fingerprints and original server paths are retained in their input manifests.

From the repository root, after initialising CombineHarvester:

```bash
git submodule update --init --recursive
python3 systematics/check_names.py \
  --input input/datacard_M20_Run2Run3.txt \
  --systematics-dict input/systematics.yml \
  --global-dict systematics/systematics_master.yml --analysis NPS26009
```

## Current validation results

The M20/M70 naming checks report 150/148 checked names, including eight
derived QCD-yield modifiers. Full impacts contain 142/140 constrained nuisances.
Repaired B-only and S+B impacts, their validations, B-only scans and correlation
plots are preserved in the respective mass directories. Both scans bracket
the lower and upper 68% and 95% crossings. S+B metadata record injections
r=15.5625 at M20 and r=0.94921875 at M70.

Bias repairs replaced 32 M20 toy fits and four M70 toy fits, using the original
saved datasets and workspaces. The final merged results contain exactly 500
distinct toys and valid 68% intervals at each of three injections per mass.
Repaired profiles passed fit-quality screening and independent endpoint checks.
Unrepaired intervals received structural checks; their per-toy saved fit statuses
are unavailable. Numerical validation is not a coverage test or proof of zero bias.
Final summaries include mean bias, its Monte Carlo standard error, and directional
pull mean and width. Detailed validation JSONs and command manifests are retained.

At M70, HybridNew on the prefit B-only Asimov dataset gives r95=0.9468495544,
versus 0.94921875 from AsymptoticLimits: a ratio of 0.9975040573. This comparison
is not the median of toy limits or a coverage test.

Intermediate retry/probe snapshots and verbose debugging logs are retained in
the full GitHub history, linked at the exact source commit in
`preservation/submission_manifest.json`. That manifest also maps every selected
file to its source path and SHA256 and records the systematics submodule commit.

The CI uses the representative M20 card and approximate robust impacts;
these differ from the preserved full local impacts. Local validation does not
establish successful CERN GitLab CI execution. Check the pipeline and artifacts
after pushing. The publication stage is not required for this review update.
