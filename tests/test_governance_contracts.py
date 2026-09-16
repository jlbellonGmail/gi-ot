import json
from pathlib import Path


ROOT = Path(__file__).parents[1]


def test_canonical_roles_are_provider_neutral():
    data = json.loads((ROOT / ".agentic" / "agents.json").read_text())
    assert set(data["roles"]) == {"planner", "builder", "reviewer"}
    text = "\n".join((ROOT / role["prompt"]).read_text() for role in data["roles"].values())
    for forbidden in ("Luna", "Sol", "Claude", "Codex", "OpenCode", "Kimi", "Gemini", "OpenAI", "Anthropic"):
        assert forbidden not in text


def test_mcp_is_empty_and_deny_by_default():
    mcp = json.loads((ROOT / ".agentic" / "mcp.json").read_text())
    policy = json.loads((ROOT / ".agentic" / "security-policy.json").read_text())
    assert mcp["servers"] == {}
    assert policy["defaultDecision"] == "deny"


def test_legacy_runs_are_present_and_untouched_by_contract():
    assert (ROOT / "runs" / "09-comprobantes" / "spec.md").is_file()
    assert (ROOT / "runs" / "activar-ai-native" / "spec.md").is_file()
    assert "LEGACY" in (ROOT / "AGENTS.md").read_text()


def test_v2_sources_of_truth_exist():
    for path in ("CONSTITUTION.md", "AGENTS.md", "ROADMAP.md", "STATUS.md", ".audit/README.md"):
        assert (ROOT / path).is_file()


def test_sdd_profiles_are_explicit():
    text = (ROOT / ".agentic" / "circuit.md").read_text()
    for profile in ("LIGHT", "STANDARD", "FULL"):
        assert profile in text
