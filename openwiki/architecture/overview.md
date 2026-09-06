# Architecture overview

There is no shared application package. Each example creates its own OpenAI client, loads `.env`, calls the SDK, and prints or returns the result. The repository is a progression of reference implementations rather than one deployable service.

```text
CLI or HTTP client → example validation/state → OpenAI Responses API
  → direct output, tools, or Conversation-backed history → console/JSON
```

## State layers

- **Responses:** `client.responses.create(...)` produces one output. Output is heterogeneous; use `response.output_text` for aggregate text and inspect item types for tools. `10-create_and_retrieve_response.py` retrieves a stored response by ID.
- **OpenAI Conversations:** only `Conversation_API/` creates durable remote Conversations and passes `conversation=...`. The remote service owns accumulated items. `previous_response_id` is a separate continuation mechanism and must not be combined with `conversation`.
- **Local application state:** weather apps keep counters, user labels, TTLs, statuses, and/or latest output without attaching a Conversation. The multi-user Conversation app uses SQLite as a control plane around remote history. Local close/expiry does not delete remote data.

## Progression

| Area | State | Persistence | Entrypoint |
|---|---|---|---|
| Responses scripts | One request or explicit chain | OpenAI-managed where applicable | `Responses_API/Basic_examples/` |
| Stateless weather | None | None | `Responses_API/stateless_weather_app/backend.py` |
| In-memory weather | UUID + counter | Process memory | `Responses_API/weather_app_with_sessions/backend.py` |
| Advanced weather | User/status/TTL/latest result | SQLAlchemy + SQLite | `Responses_API/weather_app_advanced_sessions/backend.py` |
| Basic Conversation | Remote ID | Process memory | `Conversation_API/conversation_basic_example/conversation_api_basic.py` |
| Persistent Conversation | Remote ID + topic pointer | SQLite + remote Conversation | `Conversation_API/conversation_persistent_memory_app/app.py` |
| Multi-user Conversation | Ownership/status/audit log | SQLite + remote Conversation | `Conversation_API/conversation_multi_user_temp_memory_app/app.py` |

The latest refactor added remote Conversation history retrieval and reorganized example documentation. Earlier commits standardized `gpt-5.6-luna` and added contract tests/CI.