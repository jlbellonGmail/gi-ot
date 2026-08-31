#!/usr/bin/env python3
"""Quality ratchet script for ruff - only fails on NEW errors not in baseline."""

import json
import sys
from pathlib import Path


def main():
    baseline_path = Path("ruff_baseline.json")
    current_path = Path("ruff_current.json")

    if not baseline_path.exists():
        print("⚠ No baseline found, creating empty baseline")
        baseline = set()
    else:
        with open(baseline_path) as f:
            baseline = {json.dumps(e, sort_keys=True) for e in json.load(f)}

    with open(current_path) as f:
        current = json.load(f)

    new_errors = [e for e in current if json.dumps(e, sort_keys=True) not in baseline]

    if new_errors:
        print(f"::error::Found {len(new_errors)} NEW ruff errors not in baseline:")
        for e in new_errors[:20]:
            print(f'  {e["filename"]}:{e["location"]["row"]}:{e["location"]["column"]} {e["code"]} {e["message"]}')
        if len(new_errors) > 20:
            print(f"  ... and {len(new_errors) - 20} more")
        sys.exit(1)
    else:
        print("✓ No new ruff errors (quality ratchet passed)")
        with open("ruff_current.json") as f:
            current = json.load(f)
        baseline_size = len(json.loads(Path("ruff_baseline.json").read_text())) if Path("ruff_baseline.json").exists() else 0
        print(f"  Total current errors: {len(current)} (baseline: {baseline_size})")


if __name__ == "__main__":
    main()