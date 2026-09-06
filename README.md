# OpenAI Responses and Conversations API examples

![OpenAI SDK](https://img.shields.io/badge/OpenAI%20Python-3.8.x-412991)
![API](https://img.shields.io/badge/OpenAI_API-Responses-000000)
![API](https://img.shields.io/badge/OpenAI_API-Conversations-000000)
![Framework](https://img.shields.io/badge/Flask-3.1%2B-000000)
![Storage](https://img.shields.io/badge/Local%20session%20storage-SQLite-0A7BBC)
[![Run unit Tests | Passing](https://github.com/AlexJJAX/OpenAI_Responses_Conversation_API/actions/workflows/unit-tests.yml/badge.svg)](https://github.com/AlexJJAX/OpenAI_Responses_Conversation_API/actions/workflows/unit-tests.yml)

This repository is a progressive Python reference for the OpenAI Responses API and Conversations API. It starts with focused scripts for text, vision, files, tools, streaming, structured output, and response retrieval, then develops the same primitives into stateless and stateful Flask examples.

⚠️ Disclamer: This Demo Is Intended For Demonstartion Purposes Only. Runnable behavior and integration tests do not imply production readiness. Retention, trust, security, reproducibility, cleanup, metrics, and lifecycle choices are illustrative—not production guarantees. Production adoption requires independent security, governance, reliability, scalability, privacy, and operational design. ⚠️

## Requirements and defaults

The examples use the following runtime requirements and API defaults:

| Component                  | Value                                                               |
| -------------------------- | ------------------------------------------------------------------- |
| OpenAI Python SDK          | `openai>=3.8.0,<4`                                                  |
| OpenAi API Key             | `required`                                                          |
| Default model              | `gpt-5.6-luna` (change model if needed)                             |
| Primary Responses API      | `client.responses.create(...)`                                      |
| Primary Conversations API  | `client.conversations.create(...)`                                  |
| Durable conversation state | `client.conversations.*` plus the `conversation` response parameter |
| Dependency manager         | `uv`                                                                |
| Python                     | `3.13+`                                                             |

The examples use the SDK's default HTTP client and require no transport-specific
configuration.

## Responses API and Conversations API

The APIs solve related but different problems:

| Primitive              | What it does                                                                       | Used in this repository         |
| ---------------------- | ---------------------------------------------------------------------------------- | ------------------------------- |
| Response               | Produces model output from text, image, file, or tool-enabled input                | Every OpenAI example            |
| `previous_response_id` | Continues directly from one stored response                                        | Custom function-calling example |
| Conversation           | Provides a durable identifier whose items can be reused across turns and processes | `Conversation_API/` examples    |
| Local session          | Tracks application state such as counters, ownership, TTL, and last response       | Flask examples                  |

When a response is attached to a Conversation, the API prepends existing conversation items and appends the new input and output after completion. Do not combine `conversation` and `previous_response_id` in the same request. The weather-session examples are application sessions; only the examples under `Conversation_API/` use OpenAI Conversation objects.

## Repository map

```text
.
├── Conversation_API/
│   ├── conversation_basic_example/
│   ├── conversation_multi_user_temp_memory_app/
│   ├── conversation_persistent_memory_app/
│   └── update_conversation_metadata/
├── Responses_API/
│   ├── Basic_examples/
│   ├── stateless_weather_app/
│   ├── weather_app_with_sessions/
│   └── weather_app_advanced_sessions/
├── pyproject.toml
├── uv.lock
└── README.md
```

## Catalogue overview

### Responses API scripts

| Script                                 | Demonstrates                                                                 | External side effect                   |
| -------------------------------------- | ---------------------------------------------------------------------------- | -------------------------------------- |
| `1-basic_example.py`                   | Basic text generation and `response.output_text`                             | Creates a stored response by default   |
| `2-analyse_images.py`                  | Remote image input with `input_image`                                        | Fetches a third-party image URL        |
| `3-analyse_online_files.py`            | Remote PDF input with `input_file.file_url`                                  | Fetches a third-party PDF URL          |
| `4-upload_and_anslyse_local_file.py`   | Files API upload followed by file analysis                                   | Uploads the included PDF               |
| `5-model_with_web_search_tool.py`      | Built-in `web_search` tool                                                   | Searches the public web                |
| `6-model_w_custom_function_calling.py` | Function schema, local execution, `function_call_output`, and final response | Creates two linked responses           |
| `7-remote_sse_mcp.py`                  | Remote MCP tool over the Streamable HTTP `/mcp` endpoint                     | Sends data to a third-party MCP server |
| `8-with_server_sent_streaming.py`      | Typed streaming events                                                       | Prints the full event stream           |
| `9-structured_output.py`               | Strict JSON Schema output                                                    | Creates a structured response          |
| `10-create-and-retrieve_response.py`   | Create and retrieve a stored response by ID                                  | Reads stored response state            |

See [Responses_API/Basic_examples/README.md](Responses_API/Basic_examples/README.md) for inputs, expected output, limitations, and individual run commands.

### Conversation API

| Directory                                 | State model                                       | Local persistence                             | Guide                                                                        |
| ----------------------------------------- | ------------------------------------------------- | --------------------------------------------- | ---------------------------------------------------------------------------- |
| `conversation_basic_example`              | One OpenAI Conversation reused for two turns      | None                                          | [README](Conversation_API/conversation_basic_example/README.md)              |
| `conversation_persistent_memory_app`      | OpenAI Conversation resumed across CLI runs       | SQLite stores the ID and topic                | [README](Conversation_API/conversation_persistent_memory_app/README.md)      |
| `conversation_multi_user_temp_memory_app` | OpenAI Conversations plus local ownership and TTL | SQLite stores conversations and response logs | [README](Conversation_API/conversation_multi_user_temp_memory_app/README.md) |
| `update_conversation_metadata`            | Retrieve and update one Conversation object       | None                                          | [README](Conversation_API/update_conversation_metadata/README.md)            |

### Weather service progression

| Directory                       | Application state                                   | OpenAI conversation state | Persistence         | Guide                                                           |
| ------------------------------- | --------------------------------------------------- | ------------------------- | ------------------- | --------------------------------------------------------------- |
| `stateless_weather_app`         | None                                                | None                      | None                | [Readme](Responses_API/stateless_weather_app/Readme.md)         |
| `weather_app_with_sessions`     | In-memory request counter                           | None                      | Lost on restart     | [Readme](Responses_API/weather_app_with_sessions/Readme.md)     |
| `weather_app_advanced_sessions` | User-bound sessions, status, TTL, and last response | None                      | SQLAlchemy + SQLite | [Readme](Responses_API/weather_app_advanced_sessions/Readme.md) |

All three weather apps ask the model to invent a plausible report. They are architecture demonstrations, not weather-data integrations.

## Quick start

Run setup commands from the repository root.

### 1. Install the locked environment

```bash
uv sync
source .venv/bin/activate
```

Use UV for dependency changes so that `pyproject.toml` and `uv.lock` remain consistent.

### 2. Configure credentials

Create `.env` in the repository root:

```dotenv
OPENAI_API_KEY=your_api_key_here
```

Optional settings used by individual applications:

```dotenv
CONVERSATION_TTL_MINUTES=30
SESSION_TTL_MINUTES=30
WEATHER_APP_DB=Responses_API/weather_app_advanced_sessions/app.db
```

Every OpenAI script loads this file with `load_dotenv(override=True)`. `.env` is excluded by `.gitignore`; never commit real credentials.

### 3. Run a standalone example

```bash
uv run python Responses_API/Basic_examples/1-basic_example.py
```

API calls are billable and require network access plus access to the configured model or tool.

## Running the Flask examples

Only one app can bind to port 5000 at a time.

### Stateless weather

```bash
uv run python Responses_API/stateless_weather_app/backend.py
```

In another terminal:

```bash
uv run python Responses_API/stateless_weather_app/frontend.py
```

### In-memory weather sessions

```bash
uv run python Responses_API/weather_app_with_sessions/backend.py
```

In another terminal:

```bash
uv run python Responses_API/weather_app_with_sessions/frontend.py
```

### Advanced persisted weather sessions

The default database path is relative to `Responses_API`, so run this example from
that directory unless `WEATHER_APP_DB` is set explicitly:

```bash
cd Responses_API
uv run python weather_app_advanced_sessions/backend.py
```

In another terminal, also from `Responses_API`:

```bash
uv run python weather_app_advanced_sessions/frontend.py
uv run python weather_app_advanced_sessions/view_db.py
```

### Multi-user Conversation API

Run this one from the repository root because its SQLite path is rooted there:

```bash
uv run python Conversation_API/conversation_multi_user_temp_memory_app/app.py
```

Create a conversation:

```bash
curl -X POST http://127.0.0.1:5000/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id":"alice","message":"Remember that my preferred language is Python."}'
```

Reuse the returned `conversation_id` in a subsequent request.

## Important API behavior

- `response.output` is heterogeneous and its ordering is not guaranteed. Use `response.output_text` for aggregate text and inspect each item's `type` for tool calls.
- A function call is not the final answer. Execute the application function, return a `function_call_output` with the matching `call_id`, then request the final model response.
- The MCP example sets `require_approval` to `never` only for a harmless dice tool and restricts access with `allowed_tools`. Review and approve sensitive MCP calls in real applications.
- `responses.retrieve(...)` requires a stored response. Responses are stored by default unless `store=False` is used.
- Response objects are retained for 30 days by default. Conversation objects and their items are not subject to that 30-day response TTL; define an explicit deletion and retention policy before production use.
- Model text is nondeterministic. Exact wording, including the introductory capabilities list in the basic conversation example, can vary between runs.

## Local data and privacy

The repository includes SQLite databases and one example PDF in the [resources](./Responses_API/Basic_examples/resources) directory. Running the applications can append or update database rows. The multi-user app stores prompt text, output text, token usage, and the full serialized OpenAI response locally. The advanced weather app stores the latest model output for each session.

## Tests

Fast repository-contract tests do not call OpenAI:

```bash
uv run pytest -m "not live"
```

The optional live test makes a real, billable Responses API request and is skipped unless explicitly enabled:

```bash
RUN_LIVE_OPENAI_TESTS=1 uv run pytest -m live
```

## Troubleshooting

| Symptom                                   | Likely cause                                                | Resolution                                                                                |
| ----------------------------------------- | ----------------------------------------------------------- | ----------------------------------------------------------------------------------------- |
| `AuthenticationError`                     | Missing, invalid, or inaccessible API key                   | Check `OPENAI_API_KEY` in the root `.env`                                                 |
| `ModuleNotFoundError`                     | Environment is not synchronized                             | Run `uv sync`, then use `uv run ...`                                                      |
| `model_not_found` or permission error     | Project lacks model access                                  | Confirm access to `gpt-5.6-luna` or intentionally select another supported model          |
| MCP connection failure                    | Third-party server is unavailable or changed                | Verify `https://dmcp-server.deno.dev/mcp` before retrying                                 |
| `Invalid conversation_id`                 | ID is wrong, deleted, or belongs to another account/project | Create a new Conversation and persist its returned ID                                     |
| `409` from a session app                  | Local TTL expired or session was closed                     | Start a new session or Conversation                                                       |
| SQLite path error in the advanced app     | Process started from the wrong working directory            | Run from `Responses_API` or set `WEATHER_APP_DB`                                          |
| Very long first basic-conversation answer | The prompt asks “What can you do?”                          | This is expected model behavior; change the prompt or add concise instructions if desired |
