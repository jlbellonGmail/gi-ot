import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).parents[1]
PWSH = "pwsh"


def run_script(name, *args):
    result = subprocess.run(
        [PWSH, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(ROOT / "scripts" / name), *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    return result.stdout


def test_mcp_and_integrity_scripts():
    assert "PASS" in run_script("mcp-tools.ps1")
    assert "PASS" in run_script("check-integrity.ps1")


def test_assess_materialize_and_contract(tmp_path):
    assessment = tmp_path / "assess.jsonl"
    sdd = tmp_path / "sdd.json"
    run = tmp_path / "run"
    run.mkdir()
    run_script("assess-work-unit.ps1", "-Slug", "test-unit", "-RequestedDepth", "LIGHT", "-OutputPath", str(assessment))
    run_script("materialize-sdd.ps1", "-AssessmentPath", str(assessment), "-OutputPath", str(sdd))
    (run / "SUMMARY.md").write_text("# Summary\n", encoding="utf-8")
    (run / "sdd.json").write_text(sdd.read_text(encoding="utf-8"), encoding="utf-8")
    result = json.loads(run_script("feature-contract.ps1", "-RunDir", str(run), "-Json"))
    assert result["valid"] is True


def test_reconcile_is_non_mutating():
    output = run_script("local-feature-reconcile.ps1", "-BaseCommit", "0" * 40)
    assert "NO_AUTOMATIC_MERGE" in output
