# Updated blind review: M20 and M70

This snapshot uses CMSSW_16_0_0, Combine v11.0.0 and ROOT 6.36.07.
The producing code and input fingerprints are recorded in run_manifest.json.
The original uploaded snapshot is commit 9c0c17b928db3a515fb37bf58d4286f4359b1177.

## Retained material

- Matching datacards and internal-r expected limits.
- Impact, scan and correlation PDFs; impact and validation JSONs.
- Signal-injection metadata, bias summaries and the HybridNew comparison.
- Nuisance naming-check logs and detailed fit/scan/collection logs.
- Bias-fit logs, including failed toy fits and interval warnings.

Duplicate top-level command logs, successful toy-generation logs, individual
HybridNew grid-point logs and empty text2workspace logs were removed. Their
contents remain recoverable from the original upload commit.

## Findings from the uploaded JSONs and logs

Naming checks report 150 entries at M20 and 148 at M70; these counts include
formula rateParams. The constrained nuisance counts used by impacts are
142 and 140 respectively.

Both likelihood scans have bracketed lower and upper 68% and 95% crossings.
At M70, HybridNew/AsymptoticLimits = 0.9975040573 for the background-only
Asimov comparison stored in hybrid_comparison_M70.json.

## Repaired S+B impacts

The repaired JSON/PDF snapshot is commit f50f080c237193af84a2bf2f10334e33296b011e.
Independent checks against the preserved cards give:

| Mass [GeV] | Expected/present nuisances | Original injected r | Conditional QCD endpoints |
|---|---:|---:|---:|
| 20 | 142/142 | 15.5625 | 1 |
| 70 | 140/140 | 0.94921875 | 8 |

There are no missing nuisance entries or unresolved intervals under the repair
contract. All impact values are finite and equal to the maximum displacement
from their nuisance-specific central r. The initial POI fit is unchanged.
Only the reported repair parameters changed: one at M20 and seventeen at M70.

The M70 PDF and top-mass nuisance entries have been restored with finite,
non-collapsed intervals. QCD lower endpoints are conditional fits at zero,
with their actual profiled r and deltaNLL recorded in boundary_endpoints.
The signal injection, card hashes and alpha_internal_unit match the original
production metadata. These review impacts retain internal r; the PDFs also
label their POI as r.

Use impact_repair_M20/validation.json, impact_repair_M70/validation.json
and logs/sb_impacts_repair_M*.log for the current repair status. Original
scan/collection logs describe the pre-repair run and remain as provenance.

The plotting log still reports six normalised-pull calculation warnings at
M70. The corresponding nuisance fit intervals and r impacts are present and
finite in the repaired JSON.

## Existing bias results

For injections of 0, 1 and 2 times the expected limit, the M20 summaries read
493/500, 491/500 and 493/500 best-fit entries; M70 reads 500/500 for each.
The detailed bias-fit logs retain the failed-fit/interval warnings.
The S+B impact repair did not rerun the bias tests.
