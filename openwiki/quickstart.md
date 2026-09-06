# OpenAI Responses and Conversations examples

## Overview

This repository is a progressive Python reference for the OpenAI Responses API and Conversations API. It contains standalone Responses examples, four Conversation API examples, and three Flask weather-session applications that demonstrate increasing levels of local state. The weather apps generate plausible model-written reports; they are not integrations with a weather data provider.

This is demonstration code, not a production service. The repository explicitly leaves retention, authorization, cleanup, observability, reliability, and governance decisions to adopters.

## Start here

1. Install Python 3.13+ and `uv`.
2. From the repository root, run `uv sync`.
3. Configure `OPENAI_API_KEY` in a local `.env` file. Never commit credentials.
4. Run a small example:

```bash
uv run python Responses_API/Basic_examples/1-basic_example.py
```

Calls may be billable and require network access and model access. The configured default model is `gpt-5.6-luna`; change it deliberately if that model is unavailable to the API project.

## Documentation map

- [Architecture](architecture/overview.md) — boundaries between Responses, Conversations, and local application state.
- [Responses API examples](workflows/api-examples.md) — runnable request patterns, tools, files, streaming, and retrieval.
- [Conversations and sessions](workflows/conversations-and-sessions.md) — durable Conversations, local persistence, routes, and lifecycle.
- [Operations and testing](operations.md) — configuration, data handling, tests, CI behavior, and current gaps.
- [Source map](source-map.md) — primary files by concern.

The source READMEs remain the detailed run guides: [root README](../README.md), [Responses examples](../Responses_API/Basic_examples/README.md), and the individual application READMEs under `Responses_API/` and `Conversation_API/`.

## Repository shape

- `Responses_API/Basic_examples/` contains ten focused API scripts.
- `Responses_API/stateless_weather_app/` is the no-session Flask baseline.
- `Responses_API/weather_app_with_sessions/` adds an in-memory request counter.
- `Responses_API/weather_app_advanced_sessions/` adds SQLAlchemy/SQLite persistence and lifecycle routes.
- `Conversation_API/` contains basic, persistent CLI, multi-user temporary-memory, and metadata-update examples.
- `tests/` contains static contract tests, history-retrieval tests, and an opt-in live test.

## Common run commands

```bash
# Fast tests; no OpenAI calls
uv run pytest -m "not live"

# Explicitly opt into one billable live test
RUN_LIVE_OPENAI_TESTS=1 uv run pytest -m live

# Persistent weather app (run from Responses_API)
cd Responses_API
uv run python weather_app_advanced_sessions/backend.py

# Multi-user Conversation Flask app (run from repository root)
uv run python Conversation_API/conversation_multi_user_temp_memory_app/app.py
```

Only one Flask example should bind port 5000 at a time. Several SQLite paths are relative to the process working directory; follow each app README rather than assuming root-relative behavior.

## Important distinctions

- A **Response** is one model output and can be retrieved by ID while retained.
- `previous_response_id` links a follow-up Responses request; it is used by the function-calling example.
- A **Conversation** is a durable remote item history reused with `conversation=<id>`.
- A **local session** is application state such as ownership labels, counters, TTL, status, and the latest output. It does not itself give the model memory.
- Do not send `conversation` and `previous_response_id` together.

## Backlog

- Route-level Flask authorization and transaction behavior are not comprehensively integration-tested; see [operations and testing](operations/testing.md).
- Database migration, concurrency, and cleanup policies are not implemented; the examples intentionally use simple `create_all()`/`CREATE TABLE IF NOT EXISTS` setup.
- The OpenWiki automation workflow deserves a dedicated hardening review if it is used beyond this repository's documentation refresh.
