# Operations and testing

## Configuration

The project requires Python 3.13+, `uv`, and `OPENAI_API_KEY` in a local `.env`. Dependencies are declared in `pyproject.toml` and locked in `uv.lock`. Optional settings include `SESSION_TTL_MINUTES`, `CONVERSATION_TTL_MINUTES`, and `WEATHER_APP_DB`. Never commit credentials.

## Verification

```bash
uv sync
uv run pytest -m "not live"
RUN_LIVE_OPENAI_TESTS=1 uv run pytest -m live
```

The default suite is fast and offline. The live test is opt-in and billable. CI runs the non-live suite from `.github/workflows/unit-tests.yml`; it does not run linting, type checks, Flask route integration tests, migrations, or concurrency checks.

`tests/test_repository_contract.py` parses examples and enforces conventions such as the default model, MCP allowlist, documentation, and credential-ignore rules. `tests/test_retrieve_conversation_history.py` covers fake SDK history retrieval and temporary SQLite behavior. At initialization, the non-live suite has an existing disclaimer-text mismatch between the contract test and current README, so CI is currently red until intentionally reconciled.

## Operational cautions

These are local demonstrations: Flask examples run with `debug=True`, bind port 5000, accept caller-supplied IDs, and have no production authentication. SQLite paths depend on the working directory. The multi-user Conversation app stores prompts, outputs, usage, and complete serialized responses; the weather app stores the latest output. TTL is lazy and no cleanup job exists. Remote Conversations, Responses, uploaded files, and tool effects are not automatically deleted.

The daily/manual `.github/workflows/openwiki-update.yml` grants write permissions and sends repository content through an external model/tracing workflow. Review it before using the automation for sensitive repositories.

## Change checklist

1. Read the relevant README and source entrypoint.
2. Preserve stable response shapes, IDs, status values, and working-directory assumptions.
3. Run the non-live suite.
4. Run live tests only with explicit approval and credentials.
5. Update source docs and the matching wiki page when behavior changes.
