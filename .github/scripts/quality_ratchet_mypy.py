#!/usr/bin/env python3
"""Quality ratchet script for mypy - only fails on NEW errors not in baseline."""

import sys
from pathlib import Path


def normalize_path(path):
    """Normalize file paths for cross-platform comparison."""
    return path.replace('\\', '/')


def main():
    baseline_path = Path("mypy_baseline.txt")
    current_path = Path("mypy_current.txt")

    if not baseline_path.exists():
        print("⚠ No baseline found, creating empty baseline")
        baseline = set()
    else:
        print(f"Loading baseline from {baseline_path} (size: {baseline_path.stat().st_size} bytes)")
        with open(baseline_path) as f:
            baseline = set(normalize_path(line.strip()) for line in f if line.strip())
        print(f"Baseline entries: {len(baseline)}")

    if not current_path.exists():
        print("✓ No mypy output file found")
        return

    with open(current_path) as f:
        current_lines = [normalize_path(line.strip()) for line in f if line.strip() and ': error:' in line]

    print(f"Current errors: {len(current_lines)}")

    new_errors = [line for line in current_lines if line not in baseline]

    if new_errors:
        print(f"::error::Found {len(new_errors)} NEW mypy errors not in baseline:")
        for e in new_errors[:20]:
            print(f"  {e}")
        if len(new_errors) > 20:
            print(f"  ... and {len(new_errors) - 20} more")
        sys.exit(1)
    else:
        print("✓ No new mypy errors (quality ratchet passed)")
        baseline_size = len(baseline) if Path("mypy_baseline.txt").exists() else 0
        print(f"  Total current errors: {len(current_lines)} (baseline: {baseline_size})")


if __name__ == "__main__":
    main()