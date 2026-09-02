# NPS-26-009 Combine/datacard review

This repository contains the statistical model and validation material for CMS analysis NPS-26-009, a search for a narrow nonisolated dimuon resonance inside a jet in a b-tagged event topology.

## Statistical model

The analysis uses a mass-dependent **counting likelihood**. For each signal-mass hypothesis, the expected event yields are integrated over a dimuon-mass counting window determined from the signal mass resolution.

The Run2Run3 model contains eight likelihood channels corresponding to the data-taking periods

* 2016preVFP
* 2016postVFP
* 2017
* 2018
* 2022
* 2022EE
* 2023
* 2023BPix

The production workflow directly constructs the multi-channel Run2, Run3, and Run2Run3 datacards. The Run2Run3 card is therefore a native eight-channel datacard and is not produced by combining eight per-era text datacards.

The processes in each channel are

* `Zprime`: signal
* `QCD`: data-driven QCD multijet background
* `tt`: top quark-antiquark background
* `ST`: single top quark background
* `DY`: data-driven Drell--Yan background
* `Others`: residual minor simulated backgrounds

The representative signal point used for the validation CI is

```text
m(Z') = 20 GeV
input/datacard_M20_Run2Run3.txt
```

Only one representative mass point is used as CI input. Additional mass points are used for dedicated statistical cross-checks.

## Counting model and ROOT inputs

This is a **rate-only counting model**, not a shape-template likelihood at the Combine stage.

The nominal yields and the effects of systematic variations are evaluated from the analysis histograms and integrated over the corresponding mass-dependent counting window when the datacard is produced. The resulting rates and nuisance responses are written directly to the text datacard.

Consequently, no ROOT histogram file is required as an input to the preserved Combine datacard. `text2workspace.py` converts the text datacard into the RooWorkspace used by Combine.

## Parameter of interest

Combine uses its standard signal-strength parameter `r` as the internal parameter of interest.

The physical parameter reported by the analysis is

```text
alpha_qZp = r * alpha_internal_unit
```

where `alpha_internal_unit` depends on the signal mass and on the Run2/Run3 combination.

For the representative Run2Run3 M20 card,

```text
alpha_internal_unit = 8.005935406497654e-07
```

and the internal signal normalization is chosen such that `r = 1` corresponds to 25 selected signal events in the combined card.

The mass- and target-dependent conversion factors are preserved in

```text
preservation/alpha_internal_scaling.csv
preservation/alpha_internal_scaling.json
```

Combine itself always fits the internal parameter `r`. Some analysis-level limit and impact outputs are subsequently rescaled from `r` to the physical `alpha_qZp` parameter for presentation.

## Blinding and limit calculation

The analysis is currently treated as blinded.

For blinded datacards, the observation in each channel is the background-only Asimov expectation constructed from the nominal background prediction. No observed signal-region result is used in the expected limit calculation.

The primary 95% CL expected limits are obtained with the Combine `AsymptoticLimits` method.

A `HybridNew` toy-based limit calculation is additionally performed at M70, where the statistical sample is smaller, as a cross-check of the asymptotic approximation.

## Combine environment

The local review validation was performed using

```text
CMSSW_16_0_0
Combine v11.0.0
CombineHarvester
```

The validation CI configuration is provided in `.gitlab-ci.yml`. The CI is restricted to the representative M20 Run2Run3 card.

## Datacard production

The nominal analysis workflow is implemented in

```text
scripts/limit_workflow.py
```

The workflow directly builds the counting datacards and runs the nominal Combine calculations.

A typical blinded production command is

```bash
python3 limit_workflow.py \
  --stage all \
  --target runs \
  --parameter alpha \
  --mode blind \
  --task all \
  --impact-parallel 12 \
  --r-max 100 \
  --strict \
  --allow-negative-r \
  --r-min -2
```

Here, `--target runs` produces the Run2, Run3, and Run2Run3 models. Per-era text datacards are not part of the nominal limit workflow.

Additional review-specific statistical tests are implemented in

```text
scripts/combine_review.py
```

This helper operates on already-produced datacards and does not modify the nominal production model.

## Systematic uncertainties

The analysis-specific systematic-uncertainty dictionary is

```text
input/systematics.yml
```

The main statistical-model choices relevant for the review are:

* luminosity and detector uncertainties follow the implemented Run2/Run3 correlation scheme;
* the b tagging uncertainties are separated into heavy-flavour and light-flavour components and into correlated and data-taking-period-specific components;
* the QCD normalization uncertainty is multiplicative, while the QCD functional-form uncertainty is propagated as an additive Gaussian uncertainty in the absolute QCD yield through a constrained `rateParam`;
* the data-driven DY prediction contains separate normalization-factor and light-jet control-sample statistical uncertainties;
* finite simulated-sample statistical uncertainties are propagated separately for the signal, top quark-antiquark, single top quark, and residual simulated-background processes.

The nuisance naming conventions have been checked with the CMS systematics checker.

## Validation

For the representative M20 card:

```text
ValidateDatacards.py : successful
text2workspace.py    : successful
check_names.py       : 148 nuisances checked, no naming issues
```

The `ValidateDatacards.py` output contains warnings for several large normalization uncertainties, primarily associated with low-statistical-yield backgrounds, but no empty-process, invalid-template, or small-signal alerts.

Additional review diagnostics include

* B-only nuisance impacts and pulls;
* S+B Asimov nuisance impacts;
* B-only likelihood scans;
* nuisance correlation matrices;
* signal-recovery/bias tests;
* an M70 `HybridNew` versus `AsymptoticLimits` comparison.

The compact validation outputs are stored under

```text
validation/M20/
validation/M70/
```

Large temporary RooWorkspace, toy, and HybridNew grid ROOT files are not preserved in this repository.

