#!/usr/bin/env python3
"""Export final review material in the compact existing CERN GitLab layout.

Run in the full combine_review GitHub checkout. This creates a new directory;
it never changes the checkout, deletes historical results or pushes a remote.
"""
import argparse
import hashlib
import json
import shutil
import subprocess
import tempfile
from pathlib import Path


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path):
    return json.loads(path.read_text())


def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="New, non-existing output directory")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    output = args.output.resolve() if args.output else Path(tempfile.mkdtemp(prefix="nps26009-gitlab."))
    if args.output:
        output.mkdir(parents=True, exist_ok=False)
    commit = subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip()
    entry = subprocess.check_output(["git", "-C", str(root), "ls-tree", "HEAD", "systematics"], text=True).split()
    if len(entry) != 4 or entry[:2] != ["160000", "commit"]:
        raise RuntimeError("Expected pinned systematics git submodule")
    manifest = {"source_repository": "https://github.com/joonblee/combine_review",
                "source_commit": commit, "systematics_submodule_commit": entry[2],
                "layout": "Existing GitLab input/, preservation/Run2Run3/, scripts/, review_validation/M20|M70/",
                "files": {}, "generated_files": {},
                "full_diagnostics": f"https://github.com/joonblee/combine_review/tree/{commit}/review_validation"}

    def copy(source, target=None):
        source = Path(source); target = Path(target) if target else source
        src, dst = root / source, output / target
        if not src.is_file():
            raise RuntimeError(f"Missing source: {src}")
        if dst.exists():
            raise RuntimeError(f"Duplicate export path: {dst}")
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        manifest["files"][str(target)] = {"source_path": str(source), "sha256": digest(dst)}

    for name in ("LICENSE", ".gitlab-ci.yml", ".gitmodules", "input/datacard_M20_Run2Run3.txt", "input/systematics.yml",
                 "preservation/alpha_internal_scaling.csv", "preservation/alpha_internal_scaling.json",
                 "yaml/run_t2w_mdf_impacts_matrix.yml"):
        copy(name)
    copy("docs/gitlab_submission_README.md", "README.md")
    # The former '*git* export-ignore' hides CI and .gitmodules from GitLab ZIPs.
    attributes = "\n".join(line for line in (root / ".gitattributes").read_text().splitlines()
                           if "export-ignore" not in line) + "\n"
    (output / ".gitattributes").write_text(attributes)
    manifest["generated_files"][".gitattributes"] = digest(output / ".gitattributes")
    cards = sorted((root / "preservation/Run2Run3").glob("*.txt"))
    if len(cards) != 13:
        raise RuntimeError("Expected thirteen preserved mass cards")
    for card in cards:
        copy(card.relative_to(root))
    if (output / "input/datacard_M20_Run2Run3.txt").read_bytes() != (output / "preservation/Run2Run3/datacard_M-20_Run2Run3.txt").read_bytes():
        raise RuntimeError("Representative M20 card differs from preserved card")
    for script in ("limit_workflow.py", "combine_review.py", "review.sh", "audit_bias_intervals.py",
                   "repair_bias_intervals.py", "validate_bias_repair.py"):
        copy("scripts/" + script)
    current = Path("review_validation/updated_blind_P2ejoE9l")
    copy(current / "limits_Run2Run3_alpha_internal.json", "preservation/limits_Run2Run3_alpha_internal.json")
    copy(current / "run_manifest.json", "preservation/additional_review_run_manifest.json")
    snapshots = {20: ("bias_M20_verified_7x_fn8sj", 32, (-50, 100)),
                 70: ("bias_M70_verified_avf0d2lz", 4, (-2, 100))}
    for mass, (snapshot, count, bounds) in snapshots.items():
        dest = Path(f"review_validation/M{mass}")
        review = current / f"Run2Run3/M{mass}"
        bonly = Path(f"review_validation/b_only_impacts/Run2Run3/M{mass}")
        if (root / bonly / f"datacard_M-{mass}_Run2Run3.txt").read_bytes() != (root / f"preservation/Run2Run3/datacard_M-{mass}_Run2Run3.txt").read_bytes():
            raise RuntimeError(f"B-only impact card differs at M{mass}")
        if (root / review / f"datacard_M-{mass}_Run2Run3.txt").read_bytes() != (root / f"preservation/Run2Run3/datacard_M-{mass}_Run2Run3.txt").read_bytes():
            raise RuntimeError(f"Additional review card differs at M{mass}")
        for suffix in (".json", ".pdf", "_internal.json"):
            name = f"impacts_Run2Run3_alpha_M{mass}{suffix}"
            copy(bonly / name, dest / name)
        validations = {str(p.relative_to(root / bonly)): load(p)
                       for p in (root / bonly).rglob("*validation.json")}
        if not validations:
            raise RuntimeError(f"Missing B-only validation at M{mass}")
        for record in validations.values():
            if record.get("passed") is False:
                raise RuntimeError(f"Failed B-only validation at M{mass}")
        name = dest / f"b_only_impact_validation_M{mass}.json"
        dump(output / name, validations); manifest["generated_files"][str(name)] = digest(output / name)
        for name in (f"impacts_Run2Run3_M{mass}_SB.json", f"impacts_Run2Run3_M{mass}_SB.pdf",
                     f"sb_impacts_metadata_M{mass}.json", f"scan_Run2Run3_M{mass}_Bonly.pdf",
                     f"scan_plot_M{mass}.log", f"correlation_Run2Run3_M{mass}.pdf", f"validation_M{mass}.json"):
            copy(review / name, dest / name)
        if not load(root / review / f"impact_repair_M{mass}/validation.json")["passed"]:
            raise RuntimeError(f"S+B impact repair failed at M{mass}")
        copy(review / f"impact_repair_M{mass}/validation.json", dest / f"sb_impact_validation_M{mass}.json")
        copy(current / f"logs/check_names_M{mass}.log", dest / f"check_names_M{mass}.log")
        bias = Path("review_validation") / snapshot
        validation = load(root / bias / "validation.json")
        summaries = load(root / bias / f"bias_summary_Run2Run3_M{mass}.json")
        merged = load(root / bias / "merged_toys.json")
        if not validation["passed"] or validation["errors"] or validation["n_verified_repairs"] != count:
            raise RuntimeError(f"Incomplete bias repair at M{mass}")
        if len(summaries) != 3 or len(merged) != 3 or any(r["n_toys"] != 500 or r["n_pulls"] != 500 for r in summaries):
            raise RuntimeError(f"Incomplete bias ensembles at M{mass}")
        for records in merged.values():
            if set(map(int, records)) != set(range(1, 501)):
                raise RuntimeError(f"Missing/duplicate toy IDs at M{mass}")
            for record in records.values():
                lo, best, hi = record["interval"]
                if not bounds[0] + 1e-5 < lo < best < hi < bounds[1] - 1e-5:
                    raise RuntimeError(f"Invalid interval at M{mass}")
        copy(bias / f"bias_summary_Run2Run3_M{mass}.json", dest / f"bias_summary_Run2Run3_M{mass}.json")
        for name in ("validation", "merged_toys", "input_manifest", "run_manifest"):
            copy(bias / (name + ".json"), dest / f"bias_{name}_M{mass}.json")
    copy(current / "Run2Run3/M70/hybrid_comparison_M70.json", "review_validation/M70/hybrid_comparison_M70.json")
    copy("review_validation/bias_M20_verified_d4jw2m6v/run_manifest.json",
         "review_validation/M20/bias_previous_run_manifest_M20.json")
    copy("review_validation/bias_M70_verified_avf0d2lz/original_interval_audit.json",
         "review_validation/M70/bias_original_interval_audit_M70.json")
    # Every copied byte is checked against its selected source.
    for target, info in manifest["files"].items():
        if digest(root / info["source_path"]) != info["sha256"] or digest(output / target) != info["sha256"]:
            raise RuntimeError(f"Export hash mismatch: {target}")
    dump(output / "preservation/submission_manifest.json", manifest)
    files = [p for p in output.rglob("*") if p.is_file()]
    print(f"[COMPLETE] {len(files)} files, {sum(p.stat().st_size for p in files)/1024**2:.2f} MiB")
    print(f"[OUTPUT] {output}")
    print(f"[SUBMODULE] systematics {entry[2]}")
    print("[SCOPE] Prepared compact files only; no repository or remote was changed.")


if __name__ == "__main__":
    main()
