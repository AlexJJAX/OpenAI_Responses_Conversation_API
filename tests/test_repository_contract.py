"""Fast checks for the repository's documented OpenAI API contract."""

from __future__ import annotations

import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXAMPLE_ROOTS = (ROOT / "Conversation_API", ROOT / "Responses_API")
DEFAULT_MODEL = "gpt-5.6-luna"
REQUIRED_DISCLAIMER = (
    "⚠️ Disclamer: This Demo Is Intended For Demonstartion Purposes Only. "
    "Runnable behavior and integration tests do not imply production readiness. "
    "Retention, trust, security, reproducibility, cleanup, metrics, and lifecycle "
    "choices are illustrative—not production guarantees. Production adoption "
    "requires independent security, governance, reliability, scalability, privacy, "
    "and operational design. ⚠️"
)


def example_scripts() -> list[Path]:
    """Return every Python example and shared helper in stable path order."""
    return sorted(path for root in EXAMPLE_ROOTS for path in root.rglob("*.py"))


def is_responses_call(node: ast.Call) -> bool:
    """Return whether a call targets client.responses.create or parse."""
    function = node.func
    return (
        isinstance(function, ast.Attribute)
        and function.attr in {"create", "parse"}
        and isinstance(function.value, ast.Attribute)
        and function.value.attr == "responses"
    )


def test_all_example_scripts_parse() -> None:
    """Ensure every example remains syntactically valid without executing it."""
    scripts = example_scripts()
    assert scripts, "No example scripts were discovered."

    for script in scripts:
        ast.parse(script.read_text(encoding="utf-8"), filename=str(script))


def test_all_responses_calls_use_the_default_model() -> None:
    """Require an explicit gpt-5.6-luna model on every Responses API call."""
    checked_calls = 0

    for script in example_scripts():
        tree = ast.parse(script.read_text(encoding="utf-8"), filename=str(script))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call) or not is_responses_call(node):
                continue

            checked_calls += 1
            model_keyword = next(
                (keyword for keyword in node.keywords if keyword.arg == "model"),
                None,
            )
            assert model_keyword is not None, f"Missing model in {script}"
            assert isinstance(model_keyword.value, ast.Constant), (
                f"Model must be a literal in {script}"
            )
            assert model_keyword.value.value == DEFAULT_MODEL, (
                f"Unexpected model in {script}: {model_keyword.value.value!r}"
            )

    assert checked_calls > 0, "No Responses API calls were discovered."


def test_mcp_example_uses_current_endpoint_and_tool_allowlist() -> None:
    """Protect the current MCP transport endpoint and least-privilege tool list."""
    script = ROOT / "Responses_API/Basic_examples/7-remote_sse_mcp.py"
    source = script.read_text(encoding="utf-8")

    assert '"server_url": "https://dmcp-server.deno.dev/mcp"' in source
    assert '"allowed_tools": ["roll"]' in source
    assert "dmcp-server.deno.dev/sse" not in source


def test_required_documentation_and_secret_ignore_rules_exist() -> None:
    """Check the documentation entry points and local secret exclusion rule."""
    required_readmes = [
        ROOT / "README.md",
        ROOT / "Responses_API/Basic_examples/README.md",
        ROOT / "Responses_API/stateless_weather_app/Readme.md",
        ROOT / "Responses_API/weather_app_with_sessions/Readme.md",
        ROOT / "Responses_API/weather_app_advanced_sessions/Readme.md",
        ROOT / "Conversation_API/conversation_basic_example/README.md",
        ROOT / "Conversation_API/conversation_multi_user_temp_memory_app/README.md",
        ROOT / "Conversation_API/conversation_persistent_memory_app/README.md",
        ROOT / "Conversation_API/update_conversation_metadata/README.md",
    ]

    assert all(path.is_file() for path in required_readmes)
    root_readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert REQUIRED_DISCLAIMER in root_readme
    assert "Run unit Tests | Passing" in root_readme
    assert ".env" in (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
