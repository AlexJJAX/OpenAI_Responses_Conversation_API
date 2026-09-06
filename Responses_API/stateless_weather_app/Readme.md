# Stateless Mock Weather Service

![OpenAI SDK](https://img.shields.io/badge/OpenAI%20Python-3.8.x-412991)
![API](https://img.shields.io/badge/OpenAI_API-Responses-000000)
![Model](https://img.shields.io/badge/model-gpt--5.6--luna-412991)
![Framework](https://img.shields.io/badge/Flask-3.1%2B-000000)
![State](https://img.shields.io/badge/application%20state-none-0A7BBC)

A minimal Flask service that wraps one OpenAI Responses API call behind
`POST /weather`. Every request is independent: the application stores no user,
session, Response ID, or prior message.

The model is explicitly instructed to invent plausible weather. This is a software
architecture demonstration, not a weather-data integration, and its output must not
be used for factual forecasting or safety-critical decisions.

## Architecture Overview

| Component            | Responsibility                                                 |
| -------------------- | -------------------------------------------------------------- |
| `backend.py`         | Validates a city, creates one model Response, and returns JSON |
| Flask                | Exposes `POST /weather` on the local development server        |
| OpenAI Responses API | Generates the fictional weather report                         |
| `frontend.py`        | Sends one example request for Paris and prints the result      |

Importing `backend.py` loads `.env` and initializes the OpenAI client. Running the
backend starts Flask; running the frontend immediately sends an HTTP request.

## What It Demonstrates

- Wrapping `client.responses.create(...)` in a small HTTP endpoint.
- Using one required JSON field as model input.
- Returning `response.output_text` in an application JSON response.
- Keeping application requests independent from one another.
- Separating an HTTP client process from a model-backed server process.
- Loading `OPENAI_API_KEY` with `load_dotenv(override=True)`.

## Key Design Decisions

- **No application session** — each request contains everything the backend uses.
- **No OpenAI Conversation** — neither `conversation` nor `previous_response_id` is
  supplied.
- **Plain-text model output** — the prompt requests one short report and the endpoint
  places it directly in the `report` field.
- **Fictional data by design** — the example demonstrates request flow without adding
  a real weather provider.
- **One frontend request** — the companion client shows the complete HTTP contract
  without UI or browser dependencies.

## State Model

| Property                 | Behavior                                                           |
| ------------------------ | ------------------------------------------------------------------ |
| Application memory       | None                                                               |
| Database                 | None                                                               |
| Cookie or session ID     | None                                                               |
| Prior messages supplied  | None                                                               |
| OpenAI Conversation      | Not used                                                           |
| Stored Response          | Created remotely by default, but its ID is not retained by the app |
| Cross-request continuity | None                                                               |

Application-stateless does not mean that no remote resource can exist. The Responses
API applies its configured storage and data-control behavior independently of this
Flask application's lack of local state.

## Simplified Request Flow

```text
1. frontend.py sends POST /weather with {"city": "Paris"}
2. Flask reads the JSON body
3. Missing or empty city
   └─ return HTTP 400
4. Valid city
   └─ responses.create(model="gpt-5.6-luna", input=mock-weather prompt)
5. Return {"city": city, "report": response.output_text}
6. Discard all application state after the request
```

## Files

```text
stateless_weather_app/
├── backend.py
├── frontend.py
└── Readme.md
```

## Runtime Defaults

| Setting          | Value                                           |
| ---------------- | ----------------------------------------------- |
| Model            | `gpt-5.6-luna`                                  |
| Endpoint         | `POST /weather`                                 |
| Bind address     | Flask development default, normally `127.0.0.1` |
| Port             | `5000`                                          |
| Debug mode       | Enabled                                         |
| Frontend city    | `Paris`                                         |
| Frontend timeout | None                                            |
| Weather source   | Model fabrication, not observed data            |

## Run It

Prerequisites:

- Python 3.13 or later.
- [`uv`](https://docs.astral.sh/uv/).
- An OpenAI API key with access to `gpt-5.6-luna`.
- Two terminals, or another process capable of calling the local endpoint.

From the repository root:

```bash
uv sync --locked
source .venv/bin/activate
```

Create `.env` in the repository root:

```dotenv
OPENAI_API_KEY=your_api_key_here
```

Start the backend in terminal 1:

```bash
uv run python Responses_API/stateless_weather_app/backend.py
```

Run the client in terminal 2:

```bash
uv run python Responses_API/stateless_weather_app/frontend.py
```

Only one repository example can bind to port 5000 at a time.

## HTTP Contract

### `POST /weather`

Request:

```json
{
  "city": "Paris"
}
```

Successful response shape:

```json
{
  "city": "Paris",
  "report": "A short, model-generated mock report."
}
```

If `city` is missing or empty, the endpoint returns HTTP 400:

```json
{
  "error": "City is required"
}
```

The endpoint expects a JSON object. A missing JSON content type, malformed JSON, or a
JSON `null` value is not handled consistently by the example and can fail before the
normal `city` validation response.

## Expected Behavior

The frontend prints the HTTP status and decoded response:

```text
Status code: 200
Response JSON: {'city': 'Paris', 'report': '...'}
```

The report changes between runs. It may sound realistic because the prompt asks for
a plausible temperature and conditions, but it has no provider, observation time,
source attribution, or factual guarantee.

Sending two requests for the same city does not establish continuity. The second
model call receives no output or message from the first one.

## Input and Trust Boundary

The city string is interpolated directly into the model prompt:

```python
input=f"""
You are a weather service.
Generate a short mock weather report for {city}.
...
"""
```

Treat it as untrusted input. A real service should validate length and allowed
characters, separate trusted instructions from user content, apply abuse controls,
and use an authoritative weather provider for actual conditions.

## Retention, Trust, and Limitations

1. Generated weather is fictional and unsuitable for factual or safety-sensitive
   use.
2. No authentication, authorization, rate limiting, request-size limit, or abuse
   protection is provided.
3. The backend has no OpenAI exception mapping, explicit timeout, retry policy,
   request-ID logging, or structured diagnostics.
4. The frontend has no timeout, `raise_for_status()`, or safe handling for non-JSON
   responses.
5. Flask debug mode and the development server are enabled and must not be exposed to
   untrusted networks.
6. The app does not retain the Response ID or implement remote cleanup.
7. User input is embedded directly in the instruction text without a separate policy
   or validation layer.

## Troubleshooting

| Symptom                         | What to Check                                    |
| ------------------------------- | ------------------------------------------------ |
| Connection refused              | Start `backend.py` and confirm port 5000 is free |
| Authentication error            | Confirm `OPENAI_API_KEY` in the root `.env`      |
| Model permission error          | Confirm project access to `gpt-5.6-luna`         |
| HTTP 400                        | Send a non-empty `city` inside a JSON object     |
| JSON decoding error in frontend | Inspect the raw backend response and status      |
| Reports contradict one another  | Calls are independent and weather is fabricated  |

## Test It

Fast repository checks parse both scripts without starting Flask or contacting
OpenAI:

```bash
uv run pytest -m "not live"
```

There are no dedicated route tests for this example. Running `frontend.py` against
the backend performs a real, billable model request.

## Related Examples

- [In-memory sessions](../weather_app_with_sessions/Readme.md) add a local request
  counter without model conversation memory.
- [Persisted sessions](../weather_app_advanced_sessions/Readme.md) add user labels,
  SQLite storage, status, and lazy expiry.
- [OpenAI Conversations](../../Conversation_API/conversation_basic_example/README.md)
  demonstrate model-facing multi-turn state.
