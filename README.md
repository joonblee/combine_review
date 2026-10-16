# NPS-26-009 Combine/datacard review

## Current snapshot

This is a blinded, mass-dependent counting analysis with eight era channels.
The representative CI input is input/datacard_M20_Run2Run3.txt.
All thirteen Run2Run3 mass points are under preservation/Run2Run3/.
The production commit, card hashes and impact provenance are recorded in
preservation/snapshot_manifest.json.

The snapshot metadata is synchronised with the organised production layout at
[higgs_combine 7722b21](https://github.com/joonblee/higgs_combine/commit/7722b2145278644b88fed0e8f54d5781897e39c1).
Final B-only impacts are in `NIsoMuon/limit_outputs/alpha/blind/<target>/`;
final verified bias records are in
`NIsoMuon/review_outputs/Run2Run3/M<mass>/bias/verified/`.
Path and checksum metadata were updated after directory consolidation; fitted
values, toy intervals and PDFs are unchanged. Historical diagnostics retain
their original directory labels and command logs.

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
  repaired S+B impacts and the original bias results.
- Final M20 bias intervals and summaries:
  [review_validation/bias_M20_verified_7x_fn8sj/](review_validation/bias_M20_verified_7x_fn8sj/).
- Final M70 bias intervals and summaries:
  [review_validation/bias_M70_verified_avf0d2lz/](review_validation/bias_M70_verified_avf0d2lz/).
- Other review snapshots are historical.

Production impact files ending in _internal.json use internal r.
Other production impact JSONs and PDFs use physical alpha.
The additional-review S+B impacts retain internal r.

The final bias snapshots contain 500 distinct toys with finite, ordered,
interior 68% profile intervals per injection at both masses. They replace
32 problematic M20 toy fits and four problematic M70 toy fits using the
original saved datasets and workspaces. Each repaired fit passes saved-fit
quality screening and independent endpoint profile checks. The original
results and failure logs remain as provenance; use the final snapshots above
for the repaired summaries.

The final JSON summaries report mean bias, its Monte Carlo standard error,
and directional pull mean and width. Numerical repair is not a coverage test
or a demonstration of zero bias. Original per-toy fit status is unavailable
for the unrepaired ensemble fits; those intervals received structural checks.

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
The updated M20/M70 naming checks passed; their logs are preserved under
review_validation/updated_blind_P2ejoE9l/logs/check_names_M*.log.
Rerun the check if the submitted cards or dictionaries change.

## Execution and CI

Production and review helpers are preserved in scripts/.
Production requires the original ROOT inputs and sigfit_inputs.
review.sh is server-specific and initialises CMSSW_16_0_0.

The GitLab CI configuration is .gitlab-ci.yml.
CI approximate impacts differ from the preserved full local impacts.
Local validation does not establish CERN GitLab pipeline success.

docs/README_before_snapshot_sync.md preserves the previous documentation.
Its snapshot-status statements and numerical validation results are historical.

## Compact GitLab submission

The full GitHub checkout retains detailed diagnostics and all production impacts.
For the existing compact CERN GitLab layout, run:

    python3 scripts/export_gitlab_submission.py

This creates a new directory containing the representative M20 input, all
Run2Run3 cards and current M20/M70 results. It does not modify this checkout
or push GitLab. The submission README is maintained in
[docs/gitlab_submission_README.md](docs/gitlab_submission_README.md).
The export manifest pins source hashes and the systematics submodule commit.
