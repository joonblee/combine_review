# NPS-26-009 Combine/datacard review

## Current snapshot

This is a blinded, mass-dependent counting analysis with eight era channels.
The representative CI input is input/datacard_M20_Run2Run3.txt.
All thirteen Run2Run3 mass points are under preservation/Run2Run3/.
The production commit, card hashes and impact provenance are recorded in
preservation/snapshot_manifest.json.

Completed cards require no external histogram ROOT files or custom physics
model. Combine fits internal r. Physical alpha equals r multiplied by the
mass- and target-dependent alpha_internal_unit stored in
preservation/alpha_internal_scaling.json.

Blind observations are fractional nominal background-only expectations
after evaluating rateParams. Expected limits use AsymptoticLimits --run blind.

## Results

- Current B-only impacts for three targets and thirteen masses:
  review_validation/b_only_impacts/.
- Current M20/M70 additional review:
  review_validation/updated_blind_P2ejoE9l/.
  Its README documents validation, scans, correlations, HybridNew,
  repaired S+B impacts and bias-study limitations.
- Other review snapshots are historical.

Production impact files ending in _internal.json use internal r.
Other production impact JSONs and PDFs use physical alpha.
The additional-review S+B impacts retain internal r.

The M20 bias studies contain fewer than 500 readable best fits per injection.
Their summaries and logs retain the failures. Not every toy fit converged.

## Minimal expected-limit reproduction

After initialising Combine:

    text2workspace.py input/datacard_M20_Run2Run3.txt -m 20 -o workspace_M20.root
    combine -M AsymptoticLimits workspace_M20.root -m 20 --run blind --rMin 0 --rMax 100 --cminDefaultMinimizerStrategy 1

Multiply the internal result by the corresponding alpha_internal_unit.
Production code in scripts/limit_workflow.py additionally implements
adaptive ranges, collection, conversion and plotting.

## Naming validation

After initialising CombineHarvester:

    git submodule update --init --recursive
    python3 systematics/check_names.py --input input/datacard_M20_Run2Run3.txt --systematics-dict input/systematics.yml --global-dict systematics/systematics_master.yml --analysis NPS26009

The nuisance dictionary is input/systematics.yml.
Run this check on the updated snapshot before submitting the review.

## Execution and CI

Production and review helpers are preserved in scripts/.
Production requires the original ROOT inputs and sigfit_inputs.
review.sh is server-specific and initialises CMSSW_16_0_0.

The GitLab CI configuration is .gitlab-ci.yml.
CI approximate impacts differ from the preserved full local impacts.
Local validation does not establish CERN GitLab pipeline success.

docs/README_before_snapshot_sync.md preserves the previous documentation.
Its snapshot-status statements and numerical validation results are historical.
