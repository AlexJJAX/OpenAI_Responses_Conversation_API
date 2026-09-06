# Persisted Mock Weather Sessions with SQLAlchemy

![OpenAI SDK](https://img.shields.io/badge/OpenAI%20Python-3.8.x-412991)
![API](https://img.shields.io/badge/OpenAI_API-Responses-000000)
![Model](https://img.shields.io/badge/model-gpt--5.6--luna-412991)
![Framework](https://img.shields.io/badge/Flask%20%2B%20SQLAlchemy-000000)
![Storage](https://img.shields.io/badge/session%20storage-SQLite-0A7BBC)

A Flask API that persists application sessions in SQLite through SQLAlchemy. Each
session belongs to a caller-supplied `user_id`, tracks activity and status, counts
accepted requests, and stores the most recent OpenAI Response ID and output text.

Every weather request creates an independent Response with
`gpt-5.6-luna`. The generated reports are intentionally fictional and must not be
used as factual weather data.

This is a session-lifecycle demonstration, not a production identity, persistence,
or forecasting service. Several routes deliberately expose authorization and
transactional gaps that must be addressed before deployment.

## Architecture Overview

| Component            | Responsibility                                                          |
| -------------------- | ----------------------------------------------------------------------- |
| `backend.py`         | Defines the ORM model, session helpers, HTTP routes, and OpenAI call    |
| Flask                | Serves health, weather, session retrieval, listing, and close endpoints |
| SQLAlchemy           | Maps `WeatherSession` objects and manages SQLite reads and writes       |
| `app.db`             | Persists local session state and the most recent model result           |
| OpenAI Responses API | Produces one independent mock weather report per accepted request       |
| `frontend.py`        | Exercises create, reuse, inspect, and close operations                  |
| `view_db.py`         | Displays persisted session rows without calling OpenAI                  |

Importing `backend.py` loads configuration, initializes an OpenAI client, and creates
the SQLAlchemy engine. Tables are created when the backend runs its main block.

## Application State vs Model State

| Concern            | Local Weather Session             | OpenAI Model Request                        |
| ------------------ | --------------------------------- | ------------------------------------------- |
| Session continuity | Stored by `session_id` in SQLite  | Not used                                    |
| User label         | Stored in `user_id`               | Not sent to the model                       |
| Request count      | Incremented locally               | Not included in the weather prompt          |
| Prior city         | Stored as `last_city`             | Not supplied to later Responses             |
| Prior report       | Stored as `last_response_content` | Not supplied to later Responses             |
| Conversation ID    | None                              | Conversations API is not used               |
| Response ID        | Most recent ID only               | A new independent ID is created per request |

Persistence of the session row does not imply that the model remembers previous
requests. SQLite state supports the application's lifecycle and inspection needs.

## What It Demonstrates

- Defining a typed SQLAlchemy 2 declarative model.
- Creating a UUID-backed application session when no ID is supplied.
- Reusing a persisted session after the backend process restarts.
- Comparing a supplied user label with a stored session owner.
- Applying a configurable inactivity TTL through lazy checks.
- Representing `active`, `expired`, and `closed` local states.
- Saving the latest Response ID, output text, city, and activity timestamp.
- Filtering sessions by user label or status.
- Inspecting SQLite through a separate read-only command-line utility.

## Key Design Decisions

- **Use SQLite for cross-process persistence** — session state survives backend
  restarts without adding a separate database service.
- **Store only the most recent model result** — the schema demonstrates a session
  snapshot rather than a complete request ledger.
- **Evaluate expiry lazily** — reads and uses can change a session to `expired`; no
  scheduler scans the database.
- **Normalize SQLite timestamps** — helper logic treats naive datetimes read from
  SQLite as UTC before calculating elapsed inactivity.
- **Separate session close from remote data** — closing a local session does not
  delete its stored OpenAI Response.
- **Provide a database viewer** — operators can inspect session rows without making
  model requests or importing the backend module.

## Persisted Model

The `weather_sessions` table contains one row per local session:

| Column                  | Type and Purpose                          |
| ----------------------- | ----------------------------------------- |
| `session_id`            | UUID string primary key                   |
| `user_id`               | Caller-supplied owner label; indexed      |
| `status`                | `active`, `expired`, or `closed`; indexed |
| `created_at`            | Session creation timestamp                |
| `last_active_at`        | Most recent tracked activity timestamp    |
| `request_count`         | Number of accepted weather requests       |
| `last_city`             | Most recently requested city              |
| `last_response_id`      | Most recent OpenAI Response ID            |
| `last_response_content` | Most recent aggregate model output text   |

Earlier Response IDs and reports are overwritten. The schema is a snapshot, not a
per-request history table.

## Session Lifecycle

| Status    | Entered When                                     | Weather Request Allowed?      | Remote Response Deleted? |
| --------- | ------------------------------------------------ | ----------------------------- | ------------------------ |
| `active`  | A request creates the session                    | Yes, until a lazy check fails | No                       |
| `expired` | A read or use observes inactivity beyond the TTL | No                            | No                       |
| `closed`  | The close route updates the row                  | No                            | No                       |

Expiry is lazy. A row can remain stored as `active` beyond the configured duration
until `POST /weather`, `GET /sessions/<id>`, or `GET /sessions` evaluates it. There is
no scheduled cleanup and expired rows are not deleted.

The close route first evaluates expiry and then sets the row to `closed`, so it can
replace an `expired` status with `closed`.

## Runtime Defaults

| Setting               | Value                                  |
| --------------------- | -------------------------------------- |
| Model                 | `gpt-5.6-luna`                         |
| Bind address          | `127.0.0.1`                            |
| Port                  | `5000`                                 |
| Flask debug mode      | Enabled                                |
| Session TTL           | `30` minutes                           |
| TTL variable          | `SESSION_TTL_MINUTES`                  |
| Database variable     | `WEATHER_APP_DB`                       |
| Default database path | `weather_app_advanced_sessions/app.db` |
| SQL logging           | Disabled with `echo=False`             |

## Simplified Request Flow

```text
1. POST /weather receives city, user_id, and optional session_id
2. Validate required fields
3. Session ID supplied
   ├─ load row and compare user_id
   ├─ apply lazy expiry check
   └─ reject missing, mismatched, expired, or closed session
4. No session ID
   └─ create and commit a new active row
5. Increment count, update activity and city, then commit
6. responses.create() generates independent mock weather
7. Store latest Response ID and text, then commit
8. Return city, report, and full session snapshot
```

The three commits make intermediate state visible but do not form one atomic unit.
If the model call fails after step 5, the request count and activity update remain
persisted without a corresponding Response value.

## Files

```text
weather_app_advanced_sessions/
├── backend.py
├── frontend.py
├── view_db.py
├── app.db
└── Readme.md
```

## Working Directory and Database Path

The default is relative to the process working directory:

```text
weather_app_advanced_sessions/app.db
```

To resolve it to the included database, start the backend from `Responses_API`:

```bash
cd Responses_API
uv run python weather_app_advanced_sessions/backend.py
```

To run from the repository root, set an explicit path in `.env`:

```dotenv
WEATHER_APP_DB=Responses_API/weather_app_advanced_sessions/app.db
```

The viewer accepts its own `--db` argument, which takes precedence over its default.

## Run It

Prerequisites:

- Python 3.13 or later.
- [`uv`](https://docs.astral.sh/uv/).
- An OpenAI API key with access to `gpt-5.6-luna`.
- Two terminals, or another HTTP client.

From the repository root:

```bash
uv sync --locked
source .venv/bin/activate
```

Create `.env`:

```dotenv
OPENAI_API_KEY=your_api_key_here
SESSION_TTL_MINUTES=30
WEATHER_APP_DB=Responses_API/weather_app_advanced_sessions/app.db
```

With the explicit database path above, start the backend from the repository root:

```bash
uv run python Responses_API/weather_app_advanced_sessions/backend.py
```

Run the lifecycle client in another terminal:

```bash
uv run python Responses_API/weather_app_advanced_sessions/frontend.py
```

Only one repository example can bind to port 5000 at a time.

## HTTP API

### Endpoint Summary

| Method and Path                     | Purpose                                         | Ownership Check                              |
| ----------------------------------- | ----------------------------------------------- | -------------------------------------------- |
| `GET /health`                       | Return database path and TTL configuration      | None                                         |
| `POST /weather`                     | Create or reuse a session and generate a report | Enforced only when reusing an ID             |
| `GET /sessions/<session_id>`        | Retrieve one session and apply expiry           | None                                         |
| `POST /sessions/<session_id>/close` | Set local status to `closed`                    | Optional; bypassed when body omits `user_id` |
| `GET /sessions`                     | List and filter sessions, applying lazy expiry  | None                                         |

### `GET /health`

```bash
curl http://127.0.0.1:5000/health
```

```json
{
  "ok": true,
  "db": "Responses_API/weather_app_advanced_sessions/app.db",
  "session_ttl_minutes": 30
}
```

The `db` value reflects the configured string and can reveal a local path.

### `POST /weather`

Create a session by omitting `session_id`:

```bash
curl -X POST http://127.0.0.1:5000/weather \
  -H "Content-Type: application/json" \
  -d '{"city":"Paris","user_id":"user_123"}'
```

Continue with the returned ID:

```bash
curl -X POST http://127.0.0.1:5000/weather \
  -H "Content-Type: application/json" \
  -d '{"city":"London","user_id":"user_123","session_id":"session-uuid"}'
```

Success returns `city`, `report`, and a full `session` object. Errors include:

| Status | Condition                                               |
| ------ | ------------------------------------------------------- |
| `400`  | Missing city, missing user label, or unknown session ID |
| `403`  | Supplied user label differs from the stored row         |
| `409`  | Session is locally expired or closed                    |

### `GET /sessions/<session_id>`

```bash
curl http://127.0.0.1:5000/sessions/session-uuid
```

Returns one session or HTTP 404. It applies the inactivity check but does not require
or verify a user label.

### `POST /sessions/<session_id>/close`

```bash
curl -X POST http://127.0.0.1:5000/sessions/session-uuid/close \
  -H "Content-Type: application/json" \
  -d '{"user_id":"user_123"}'
```

Supplying a mismatched `user_id` returns HTTP 403. Omitting `user_id` bypasses the
comparison and still closes the session.

### `GET /sessions`

```bash
curl "http://127.0.0.1:5000/sessions?user_id=user_123&status=active"
```

Filters are optional. Results are ordered by descending `last_active_at`. The route
has no authenticated access check and can update rows through lazy expiry.

## Expected Behavior

`frontend.py` performs this sequence:

1. Create a session for `user_123` and request Paris.
2. Reuse the ID and request London.
3. retrieve the persisted session snapshot.
4. close the session.

Output follows this shape:

```text
First call:
  session_id: <UUID>
  report: ...

Second call:
  request_count: 2
  last_response_id: resp_...
  report: ...

Session snapshot:
  {'session': {...}}

Closed:
  status: closed
```

The two reports can be unrelated because no earlier model message is supplied. The
session counter and last-result fields are persistent application data, not model
memory.

## Inspect the Database

The viewer does not call OpenAI:

```bash
uv run python Responses_API/weather_app_advanced_sessions/view_db.py \
  --db Responses_API/weather_app_advanced_sessions/app.db
```

Optional filters:

```bash
uv run python Responses_API/weather_app_advanced_sessions/view_db.py \
  --db Responses_API/weather_app_advanced_sessions/app.db \
  --user user_123

uv run python Responses_API/weather_app_advanced_sessions/view_db.py \
  --db Responses_API/weather_app_advanced_sessions/app.db \
  --status active
```

The viewer prints each session's identifiers, status, timestamps, request count,
latest city, latest Response ID, and stored output text. It mirrors the ORM schema
for reads and does not initialize missing tables.

## Retention, Trust, and Limitations

1. `user_id` is caller-controlled text, not authenticated identity.
2. Session retrieval and listing expose stored data without authorization.
3. The close route's ownership comparison is optional and can be bypassed by
   omitting its JSON field.
4. Session output is stored in plaintext, and no retention or deletion scheduler is
   provided.
5. Only the most recent Response ID and content survive; earlier values are
   overwritten.
6. Local expiry and closure do not delete stored OpenAI Responses.
7. Multi-commit request processing can preserve partial changes after a model or
   database failure.
8. No explicit OpenAI error mapping, retry policy, request-ID logging, idempotency,
   rate limiting, input bound, or database change-management process is implemented.
9. SQLite and Flask's debug development server are not production deployment
   choices.
10. Generated weather has no authoritative source and is intentionally fictional.

Production use requires authenticated identity, consistent authorization,
transactional design, data minimization, explicit retention and deletion rules,
observability, resilient error handling, and an authoritative weather provider.

## Troubleshooting

| Symptom                            | What to Check                                             |
| ---------------------------------- | --------------------------------------------------------- |
| SQLite cannot open the database    | Verify `WEATHER_APP_DB` relative to the process directory |
| HTTP 403                           | Supplied user label differs from the stored session       |
| HTTP 409                           | Session has expired or was closed                         |
| Counter changed without new report | The pre-model commit succeeded before a later failure     |
| Viewer reports database missing    | Pass the same path used by the backend through `--db`     |
| Port already in use                | Stop another Flask example using port 5000                |
| Reports lack continuity            | The service creates independent model Responses           |

## Test It

Fast repository checks parse the scripts without starting Flask, opening the
database through the backend, or contacting OpenAI:

```bash
uv run pytest -m "not live"
```

There are no dedicated route, persistence, expiry, or authorization tests for this
example. Running `frontend.py` performs two real, billable model calls and modifies
the configured SQLite database.

## Related Examples

- [Stateless weather](../stateless_weather_app/Readme.md) removes all application
  session state.
- [In-memory weather sessions](../weather_app_with_sessions/Readme.md) keep only a
  process-local counter.
- [OpenAI Conversations](../../Conversation_API/conversation_basic_example/README.md)
  demonstrate model-facing multi-turn context.
