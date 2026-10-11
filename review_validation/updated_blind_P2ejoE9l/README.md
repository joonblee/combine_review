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

The S+B impacts require further repair; process exit status alone is not a
completeness check:

### M20

Impact JSON contains 142/142 expected nuisances.

Collapsed nuisance intervals (before distinguishing boundary endpoints from
failed interval searches):

- `CMS_NPS26009_bckgShape_QCD_BJetOS_2022EE`

Bias summaries read 493/500, 491/500, 493/500 best-fit entries for injections of 0, 1 and 2 times the expected limit.
These counts do not certify convergence or interval quality for every toy;
the corresponding bias-fit logs are retained.

### M70

Impact JSON contains 138/140 expected nuisances.
Missing entries:

- `CMS_NPS26009_topmass_ttbar_BJetOS`
- `CMS_NPS26009_pdf_NNPDF31`

Collapsed nuisance intervals (before distinguishing boundary endpoints from
failed interval searches):

- `CMS_NPS26009_MCstat_other_BJetOS_2022EE`
- `CMS_NPS26009_MCstat_signal_BJetOS_2016preVFP`
- `CMS_NPS26009_MCstat_ttbar_BJetOS_2022EE`
- `CMS_NPS26009_NFStat_DY_BJetOS_2018`
- `CMS_NPS26009_bckgShape_QCD_BJetOS_2016postVFP`
- `CMS_NPS26009_bckgShape_QCD_BJetOS_2016preVFP`
- `CMS_NPS26009_bckgShape_QCD_BJetOS_2017`
- `CMS_NPS26009_bckgShape_QCD_BJetOS_2018`
- `CMS_NPS26009_bckgShape_QCD_BJetOS_2022`
- `CMS_NPS26009_bckgShape_QCD_BJetOS_2022EE`
- `CMS_NPS26009_bckgShape_QCD_BJetOS_2023`
- `CMS_NPS26009_bckgShape_QCD_BJetOS_2023BPix`
- `CMS_NPS26009_eff_m_trigger_2016preVFP`
- `CMS_NPS26009_stat_QCD_BJetOS_2016preVFP`
- `CMS_btag_fixedWP_bc_uncorrelated_2023BPix`

Bias summaries read 500/500, 500/500, 500/500 best-fit entries for injections of 0, 1 and 2 times the expected limit.
These counts do not certify convergence or interval quality for every toy;
the corresponding bias-fit logs are retained.
