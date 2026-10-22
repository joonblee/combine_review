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

## Optional resolution-based mass scan

`scripts/limit_workflow.py` still defaults to the available simulated masses.
Add `--interpolate-signal` to build and fit each intermediate hypothesis. The
limits themselves are never interpolated. Run from the production directory
with the existing ROOT inputs, `sigfit_inputs/` and Combine environment:

```bash
# Use the path to your GitHub checkout; keep mass_scan_grid.json beside the script.
workflow=/path/to/combine_review/scripts/limit_workflow.py

python3 "$workflow" --stage all --task limits --target runs \
  --parameter alpha --mode blind --interpolate-signal \
  --sigfit-dir ./sigfit_inputs --backend condor --r-max 100 \
  --condor-dir condor_jobs/interpolated_blind \
  --plot-limits-py "$PWD/python/plotLimits.py" --strict

# After every Condor job has finished, collect and plot the results.
python3 condor_jobs/interpolated_blind/limit_workflow.py \
  --stage collect --condor-dir condor_jobs/interpolated_blind
```

For one era, replace `--target runs` with e.g. `--target 2016preVFP`.
`--mode` retains its existing behaviour; the scan option does not unblind data.
Execution defaults to Condor, matching the current production workflow.
`--stage all` builds cards and submits jobs; it does not wait for their completion.
Use the printed collect command after the jobs finish. A single-era full scan
submits 229 mass jobs; each unblind mass job performs the observed fit and a
separate blind-expected fit. There is no default workflow concurrency cap;
`--condor-nmax 40` optionally applies the existing site concurrency limit.
For local execution instead, use `--local --jobs 40`. `--jobs` is local-only.
Omit `--masses` to use the complete shared grid. With interpolation enabled,
`--masses 12,12.5,15,20` instead selects exactly those hypotheses (including
off-grid points inside the supported interval). Without interpolation, the
existing simulated-mass selection is unchanged.

The frozen `scripts/mass_scan_grid.json` contains **229 hypotheses from 12 to
70 GeV**, including all 13 original sample masses. It is common to every era,
Run 2, Run 3 and Run 2+3. The reference curve is the equal-era arithmetic mean
of the eight stored fits to `sigma_m/m = a*m+b`, with
`a=0.0001331148680501898 /GeV`, `b=0.012312862256709963`. This is a sampling
reference, not a fit to the combined signal distribution. Successive scan
steps are at most half this reference sigma, rounded down to 0.001 GeV; the
additional original sample masses can shorten a step. Before those insertions,
the spacing grows from about 0.083 GeV to 0.75 GeV. The JSON pins the source
fit commit and all eight coefficient pairs. The grid is not regenerated from
the requested era or from new local fits. To deliberately replace it, provide
`--mass-grid-file FILE` with `{"schema_version":1,"masses":[12,12.5,15,20,70]}`.
These values are **mass hypotheses, not histogram bin edges**. Per-era fitted
resolution, `--n-sigma`, source histogram bin integration and window truncation
remain unchanged.

At an existing sample mass, signal inputs are read directly as before. Between
samples, the selected signal yield and each requested Up/Down yield are
interpolated log-linearly in mass, separately for each era. Each anchor is
integrated in its own original counting window. This is the counting-yield
prescription implemented in `SKPlotMaker/sigFit_v2.py`; it does not require
regenerating `signal_interpolation.json`. Applying the same log interpolation
to nominal and varied yields also interpolates their multiplicative ratios
log-linearly. Independent anchor Sumw2 errors are propagated through the
interpolation and used for the existing signal MC-stat nuisance. They are not
an interpolation-model uncertainty. Luminosity and nuisance correlations are
unchanged. Optional signal generator variations are included if requested.
In xsec mode, a supplied mass-dependent reference cross-section map is also
log-interpolated; alpha mode retains its per-card internal scaling.

Background yields, QCD fit derivatives/covariance and transfer statistics, DY
light-jet statistics/NF terms, and other background variations are read at
**each new window**. They are not interpolated from the old cards. No new
background fit is required solely to add scan points, provided the current
producer ROOT files contain their full templates and QCDStat/DYAux inputs.
The original nominal and systematic signal ROOT files at bracketing masses
are also required. Missing/non-positive signal inputs and extrapolation fail
before existing cards are removed. The supplied grid starts at 12 GeV; it
does not infer an 11 GeV signal from samples starting at 12 GeV.

Default outputs are `datacards_NIsoMuon_interpolated/` and
`limit_outputs_interpolated/`. Explicit non-default `--card-base` and
`--output-base` are honoured. To separate generation from fitting, first use
`--stage cards`; later use `--stage run --interpolate-signal` with the same
grid/masses and card base. The run stage requires no histogram/sigfit inputs
but checks that all requested cards exist and match the grid fingerprint.
The grid JSON must remain alongside the standalone script if it is copied.
Condor submissions snapshot the grid beside the worker script and save its
fingerprint in the manifest. Workers, collection and resume use that snapshot,
so later checkout/custom-grid changes do not change submitted hypotheses.

`signal_interpolation_audit.json` beside `card_summary.json` records the grid,
resolution inputs, anchor yields/errors/windows, per-point anchor choices and
leave-one-out residuals for yields and systematic ratios. Review these
residuals before adopting the interpolated scan as a final analysis result;
no new interpolation nuisance is added automatically. The same checks can be
reproduced with the upstream signal fitter. A small `--masses` subset can
have too few native anchors for a leave-one-out check; use the full scan to
obtain closure over the full mass range.

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

## Apply the compact snapshot to the existing server checkout

Run from a fresh, separate `combine_review` GitHub clone:

```bash
python3 scripts/sync_gitlab_checkout.py \
  --checkout /data6/Users/joonblee/higgs_combine/nps-26-009-datacards \
  --apply
```

Without `--apply`, this prepares the export and prints a read-only plan. With
the flag it installs the 71-file compact package, checks every installed hash,
and moves the old ordinary checkout contents to a reported sibling backup.
Existing edits are retained there. The Git directory, branch, remotes, index,
existing `.gitignore` and `systematics` working tree are retained. The existing
submodule gitlink must match the snapshot's pinned version before installation.
It does not stage, commit or push anything, and it does not modify NIsoMuon or
the AN. Review `git status` and the resulting diff before the later GitLab push.

The compact checkout keeps the existing GitLab format: thirteen mass cards,
the representative M20 CI card, and M20/M70 validation results. All 39 production
impact sets and historical diagnostics remain in the full GitHub repository.

