#!/usr/bin/env python3
"""
IT Automation Toolkit (ITAT) - Distribution Build and Validation Script.

Cleans prior artifacts, builds standard PEP 517 sdist and wheel packages,
verifies archive integrity, and inspects package contents.
"""

import os
import sys
import shutil
import zipfile
import tarfile
import subprocess
from pathlib import Path


def log_step(msg: str) -> None:
    print(f"\n[+] {msg}")


def log_sub(msg: str) -> None:
    print(f"    - {msg}")


def log_error(msg: str) -> None:
    print(f"[!] ERROR: {msg}", file=sys.stderr)


def clean_artifacts(repo_root: Path) -> None:
    """Remove previous build outputs."""
    log_step("Cleaning prior build artifacts...")
    dirs_to_remove = ["dist", "build", "src/it_automation_toolkit.egg-info", "src/itat.egg-info"]
    for d in dirs_to_remove:
        path = repo_root / d
        if path.exists():
            shutil.rmtree(path, ignore_errors=True)
            log_sub(f"Removed {d}/")


def build_distributions(repo_root: Path, no_isolation: bool = True) -> bool:
    """Execute python -m build to create sdist and wheel."""
    log_step("Building distribution packages via 'build'...")
    cmd = [sys.executable, "-m", "build"]
    if no_isolation:
        cmd.append("--no-isolation")
    try:
        proc = subprocess.run(cmd, cwd=str(repo_root), capture_output=True, text=True)
        if proc.returncode != 0:
            log_error("Build failed:")
            print(proc.stdout)
            print(proc.stderr, file=sys.stderr)
            return False
        log_sub("Build succeeded.")
        return True
    except FileNotFoundError:
        log_error("Module 'build' not found. Install it via: pip install build")
        return False


def verify_package_contents(dist_dir: Path) -> bool:
    """Inspect contents of generated sdist and wheel archives."""
    log_step("Inspecting built package archives...")

    wheels = list(dist_dir.glob("*.whl"))
    sdists = list(dist_dir.glob("*.tar.gz"))

    if not wheels:
        log_error("No .whl package found in dist/")
        return False
    if not sdists:
        log_error("No .tar.gz package found in dist/")
        return False

    wheel_path = wheels[0]
    sdist_path = sdists[0]

    log_sub(f"Found Wheel: {wheel_path.name} ({wheel_path.stat().st_size:,} bytes)")
    log_sub(f"Found Source: {sdist_path.name} ({sdist_path.stat().st_size:,} bytes)")

    # Verify wheel internal files
    expected_modules = [
        "itat/__init__.py",
        "itat/cli.py",
        "itat/core/application.py",
        "itat/core/config.py",
        "itat/commands/audit.py",
        "itat/commands/inventory.py",
        "itat/reports/pdf.py",
        "itat/reports/html.py",
        "itat/connectors/telegram.py",
        "itat/connectors/email.py",
        "itat/skills/system_update.py",
        "itat/skills/ssl_cert.py",
    ]

    missing = []
    with zipfile.ZipFile(wheel_path, "r") as zf:
        namelist = set(zf.namelist())
        for exp in expected_modules:
            if exp not in namelist:
                missing.append(exp)

        # Check for entry points
        has_entry_points = any("entry_points.txt" in name for name in namelist)
        if not has_entry_points:
            log_error("No entry_points.txt found in wheel metadata!")
            return False

    if missing:
        log_error(f"Wheel archive is missing required files: {missing}")
        return False

    log_sub("Wheel contains all required modules and CLI entry points.")

    # Verify sdist archive
    with tarfile.open(sdist_path, "r:gz") as tf:
        names = set(tf.getnames())
        # Check license and readme
        has_license = any("LICENSE" in n for n in names)
        has_readme = any("README.md" in n for n in names)
        if not (has_license and has_readme):
            log_error("sdist archive is missing LICENSE or README.md!")
            return False

    log_sub("Source archive contains valid LICENSE and README.md.")
    return True


def run_twine_check(dist_dir: Path) -> bool:
    """Run twine check --strict to validate package metadata."""
    log_step("Validating package metadata with twine...")
    cmd = [sys.executable, "-m", "twine", "check", "--strict"] + [str(p) for p in dist_dir.glob("*")]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True)
        if proc.returncode != 0:
            log_error("twine check failed:")
            print(proc.stdout)
            print(proc.stderr, file=sys.stderr)
            return False
        log_sub("twine check passed: PASSED")
        return True
    except FileNotFoundError:
        print("    [!] Warning: 'twine' is not installed. Skipping twine check (install via: pip install twine)")
        return True


def main() -> int:
    repo_root = Path(__file__).resolve().parent.parent
    dist_dir = repo_root / "dist"

    print("=" * 65)
    print("IT Automation Toolkit (ITAT) - Distribution Packaging")
    print("=" * 65)

    clean_artifacts(repo_root)

    if not build_distributions(repo_root):
        return 1

    if not verify_package_contents(dist_dir):
        return 1

    if not run_twine_check(dist_dir):
        return 1

    print("\n" + "=" * 65)
    print("[✓] Packaging complete and verified successfully!")
    print(f"Artifacts ready in: {dist_dir}")
    for f in dist_dir.glob("*"):
        print(f"  • {f.name} ({f.stat().st_size:,} bytes)")
    print("=" * 65)
    return 0


if __name__ == "__main__":
    sys.exit(main())
