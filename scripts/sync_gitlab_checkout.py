#!/usr/bin/env python3
"""Install the compact review export into an existing server checkout.

Default: prepare/verify the export and print a plan. --apply installs the files
and moves the old checkout contents to a sibling backup. Git metadata, the
systematics submodule and an existing .gitignore are retained. This utility
never stages files, commits, changes branches/remotes or pushes to GitLab.
"""
import argparse
import fcntl
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

DEFAULT_CHECKOUT = "/data6/Users/joonblee/higgs_combine/nps-26-009-datacards"
PROTECTED = {".git", "systematics", ".gitignore"}


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def git(directory, *args):
    return subprocess.check_output(["git", "-C", str(directory), *map(str, args)],
                                   stderr=subprocess.PIPE).decode().strip()


def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024*1024), b""):
            h.update(block)
    return h.hexdigest()


def inventory(root, exclude=()):
    result = {}
    for current, dirs, files in os.walk(root, followlinks=False):
        relative = Path(current).relative_to(root)
        if not relative.parts:
            dirs[:] = [n for n in dirs if n not in exclude]
            files = [n for n in files if n not in exclude]
        for name in dirs:
            require(not (Path(current)/name).is_symlink(), f"Unexpected symlink: {Path(current)/name}")
        for name in files:
            p = Path(current)/name
            require(p.is_file() and not p.is_symlink(), f"Unexpected non-regular file: {p}")
            result[str(p.relative_to(root))] = digest(p)
    return result


def validate_export(package):
    value = json.loads((package/"preservation/submission_manifest.json").read_text())
    for name, info in value["files"].items():
        require(digest(package/name) == info["sha256"], f"Export checksum mismatch: {name}")
    for name, expected in value["generated_files"].items():
        require(digest(package/name) == expected, f"Generated checksum mismatch: {name}")
    desired = inventory(package)
    declared = set(value["files"]) | set(value["generated_files"]) | {"preservation/submission_manifest.json"}
    require(set(desired) == declared, "Export has undeclared or missing files")
    require(not (set(p.parts[0] for p in map(Path, desired)) & PROTECTED),
            "Export would overwrite protected Git/submodule settings")
    return value, desired


def check_checkout(target, pin):
    require(target.is_dir(), f"Existing checkout not found: {target}")
    require(Path(git(target, "rev-parse", "--show-toplevel")).resolve() == target,
            "Target must be the root of its own Git checkout")
    require(bool(git(target, "branch", "--show-current")), "Target has a detached HEAD")
    remotes = git(target, "remote", "-v")
    require("cms-analysis/nps/nps-26-009/datacards" in remotes
            or "joonblee/combine_review" in remotes, "Unexpected target repository")
    entry = git(target, "ls-files", "--stage", "--", "systematics").split()
    require(len(entry) == 4 and entry[0] == "160000" and entry[1] == pin,
            f"Expected existing systematics gitlink {pin}; preserve/resolve its pin before syncing")
    return {"head": git(target, "rev-parse", "HEAD"),
            "branch": git(target, "branch", "--show-current"),
            "status": git(target, "status", "--porcelain=v1", "--untracked-files=all")}


def plan(target, desired):
    current = inventory(target, PROTECTED)
    changed = sorted(n for n, h in desired.items() if current.get(n) != h)
    retired = sorted(set(current) - set(desired))
    return changed, retired


def install(target, package, desired, source_manifest):
    """Replace ordinary top-level contents only; original roots stay in backup."""
    backup = Path(tempfile.mkdtemp(prefix=target.name+".before-sync.", dir=target.parent))
    stage = Path(tempfile.mkdtemp(prefix=target.name+".sync-stage.", dir=target.parent))
    moved, installed = [], []
    try:
        # Stage/check all incoming files before renaming any old checkout roots.
        for name, expected in desired.items():
            dest = stage/name
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(package/name, dest)
            require(digest(dest) == expected, f"Staged copy mismatch: {name}")
        roots = sorted(p.name for p in stage.iterdir())
        for old in sorted(target.iterdir()):
            if old.name not in PROTECTED:
                old.rename(backup/old.name)
                moved.append(old.name)
        for name in roots:
            (stage/name).rename(target/name)
            installed.append(name)
        require(inventory(target, PROTECTED) == desired, "Installed checkout does not match export")
        receipt = {"checkout": str(target), "source_repository": source_manifest["source_repository"],
                   "source_commit": source_manifest["source_commit"],
                   "submodule_pin": source_manifest["systematics_submodule_commit"],
                   "old_roots": moved, "installed_roots": installed,
                   "note": "Old working files retained here; Git index/remotes/branch untouched; no push."}
        (backup/"sync_receipt.json").write_text(json.dumps(receipt, indent=2)+"\n")
    except BaseException:
        for name in reversed(installed):
            if (target/name).exists():
                (target/name).rename(stage/name)
        for name in reversed(moved):
            (backup/name).rename(target/name)
        print(f"[RESTORED] Original checkout retained/restored. Staging: {stage}", file=sys.stderr)
        raise
    else:
        shutil.rmtree(stage)
        return backup


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkout", type=Path, default=Path(DEFAULT_CHECKOUT))
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    source = Path(__file__).resolve().parents[1]
    target = args.checkout.resolve()
    require(source != target and source not in target.parents and target not in source.parents,
            "Use a separate full combine_review source clone, not the target checkout")
    # Export provenance must describe committed bytes rather than local edits.
    require(subprocess.run(["git", "-C", str(source), "diff", "--quiet", "HEAD", "--"]).returncode == 0,
            "Source clone has tracked edits; use a fresh combine_review/master clone")
    with tempfile.TemporaryDirectory(prefix="nps26009-compact-export-") as work:
        package = Path(work)/"package"
        subprocess.run([sys.executable, str(source/"scripts/export_gitlab_submission.py"),
                        "--output", str(package)], check=True)
        manifest, desired = validate_export(package)
        require(target.parent.is_dir(), f"Missing parent directory: {target.parent}")
        with (target.parent/("."+target.name+".sync.lock")).open("a") as lock:
            try:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                raise RuntimeError("Another checkout sync is already running")
            previous = check_checkout(target, manifest["systematics_submodule_commit"])
            changed, retired = plan(target, desired)
            print(f"[SOURCE] combine_review {manifest['source_commit']}")
            print(f"[TARGET] {target}; branch retained: {previous['branch']}")
            print(f"[PLAN] {len(desired)} final files; {len(changed)} added/updated; {len(retired)} obsolete paths")
            if previous["status"]:
                print("[BACKUP] Existing working-tree edits will be preserved with the old files; Git index untouched")
            if not changed and not retired:
                print("[UP TO DATE] Checkout already matches the compact export")
                return
            if not args.apply:
                print("[DRY RUN] Target unchanged; add --apply to install locally")
                return
            current = check_checkout(target, manifest["systematics_submodule_commit"])
            require(current == previous, "Target Git/working state changed during planning; retry when idle")
            backup = install(target, package, desired, manifest)
            require(git(target, "rev-parse", "HEAD") == previous["head"], "Target HEAD changed unexpectedly")
            print(f"[BACKUP] {backup}")
            print(f"[PASS] All {len(desired)} installed files match the exported snapshot")
            print("[DONE] Local checkout updated. No git add/commit/push; GitLab remote unchanged.")
            subprocess.run(["git", "-C", str(target), "status", "--short"], check=True)


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, OSError, ValueError, KeyError, subprocess.CalledProcessError) as error:
        sys.exit(f"[ERROR] {error}")
