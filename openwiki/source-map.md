# Source map

## Entry points and guidance

- `README.md` — canonical repository setup, catalogue, run commands, API distinctions, privacy notes, troubleshooting.
- `pyproject.toml` / `uv.lock` — Python/dependency/test configuration.
- `openwiki/INSTRUCTIONS.md` — repository-specific documentation brief; control metadata, not generated content.

## Responses API

- `Responses_API/Basic_examples/README.md` — detailed catalogue and limitations.
- `Responses_API/Basic_examples/1-basic_example.py` — smallest request.
- `Responses_API/Basic_examples/6-model_w_custom_function_calling.py` — tool loop and response chaining.
- `Responses_API/Basic_examples/7-remote_sse_mcp.py` — remote MCP boundary.
- `Responses_API/Basic_examples/8-with_server_sent_streaming.py` — raw events.
- `Responses_API/Basic_examples/9-structured_output.py` — strict schema.
- `Responses_API/Basic_examples/10-create_and_retrieve_response.py` — response retrieval.

## Conversations and local state

- `Conversation_API/conversation_basic_example/` — in-memory two-turn Conversation.
- `Conversation_API/conversation_persistent_memory_app/app.py` — SQLite pointer to a remote Conversation.
- `Conversation_API/conversation_persistent_memory_app/retrieve_conversation_history.py` — remote item history retrieval.
- `Conversation_API/conversation_multi_user_temp_memory_app/app.py` — Flask control plane, TTL, ownership label, response audit log.
- `Conversation_API/update_conversation_metadata/` — retrieve/update Conversation metadata without adding messages.
- `Responses_API/weather_app_with_sessions/backend.py` — in-memory local sessions.
- `Responses_API/weather_app_advanced_sessions/backend.py` — SQLAlchemy/SQLite local sessions and lifecycle routes.

## Verification and automation

- `tests/test_repository_contract.py` — AST/source contract checks.
- `tests/test_retrieve_conversation_history.py` — history helper unit tests.
- `tests/live/test_openai_responses.py` — opt-in billable integration test.
- `.github/workflows/unit-tests.yml` — fast CI.
- `.github/workflows/openwiki-update.yml` — scheduled documentation refresh.
