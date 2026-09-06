# OpenAI Responses API Basic Examples

![OpenAI SDK](https://img.shields.io/badge/OpenAI%20Python-3.8.x-412991)
![Model](https://img.shields.io/badge/model-gpt--5.6--luna-412991)
![API](https://img.shields.io/badge/OpenAI_API-Responses-000000)

A collection of 10 minimalistic, independent scripts covering the main input, output, tool, state, and
storage patterns of the OpenAI Responses API. Each script keeps orchestration to a
minimum so the relevant request shape and returned SDK object remain easy to inspect.

These are demonstrational working primitives, not production integrations. Several
scripts send data to remote URLs or third-party services, create stored OpenAI
resources, omit cleanup, and rely on model-generated output that varies between
runs.

## Architecture Overview

| Script                                 | Primary Input or Tool      | State Pattern              | Printed Result               | External Effect                                  |
| -------------------------------------- | -------------------------- | -------------------------- | ---------------------------- | ------------------------------------------------ |
| `1-basic_example.py`                   | Plain text                 | One independent Response   | Aggregate output text        | Creates a stored Response by default             |
| `2-analyse_images.py`                  | Remote image URL           | One independent Response   | Image description            | OpenAI fetches a third-party image               |
| `3-analyse_online_files.py`            | Remote PDF URL             | One independent Response   | Document summary             | OpenAI fetches a third-party PDF                 |
| `4-upload_and_anslyse_local_file.py`   | Files API upload           | File referenced by ID      | Answer about the PDF         | Uploads a persistent File and creates a Response |
| `5-model_with_web_search_tool.py`      | Hosted web search          | Tool-enabled Response      | Date-sensitive news answer   | Searches public web sources                      |
| `6-model_w_custom_function_calling.py` | Local function tool        | Two Responses linked by ID | Tool call and final answer   | Runs local mock code and creates two Responses   |
| `7-remote_sse_mcp.py`                  | Remote MCP tool            | Tool-enabled Response      | Dice-roll answer             | Sends tool data to a third-party MCP server      |
| `8-with_server_sent_streaming.py`      | Streaming text request     | One streamed Response      | Every typed stream event     | Holds a streaming API connection                 |
| `9-structured_output.py`               | Strict JSON Schema         | One independent Response   | JSON text                    | Creates a schema-constrained Response            |
| `10-create_and_retrieve_response.py`   | Text followed by retrieval | Stored Response ID         | Created and retrieved fields | Reads the stored Response from OpenAI            |

Each script loads `OPENAI_API_KEY` with `load_dotenv(override=True)` and uses
`gpt-5.6-luna` explicitly.

## What the Collection Demonstrates

- Plain string input and structured message-array input.
- Text, image, remote file, and uploaded file content parts.
- Hosted web search, local custom functions, and remote MCP tools.
- Typed server-sent streaming events.
- Strict JSON Schema output.
- Response storage and retrieval by `resp_...` ID.
- A complete custom function loop using `function_call_output` and the original
  `call_id`.
- Continuing a tool call with `previous_response_id` without constructing a message
  transcript manually.
- Reading user-facing text through `response.output_text`.

## Key Design Decisions

- **Keep scripts independent** — every file can be read and run without importing an
  example framework.
- **Use one explicit model** — request behavior is easy to compare across examples.
- **Use `output_text` for aggregate text** — code does not assume that the first
  output item is the assistant message.
- **Inspect heterogeneous outputs by type** — the custom function example searches
  for `function_call` items instead of indexing `response.output`.
- **Use strict schemas where shape matters** — custom function arguments and
  structured output reject undeclared properties.
- **Expose remote side effects** — uploads, stored Responses, hosted search, and MCP
  calls are documented rather than treated as local-only operations.

## Shared Request Model

```text
1. Load OPENAI_API_KEY from repository-root .env
2. Initialize OpenAI()
3. Build one Responses API request
   ├─ text, image, file, or schema input
   └─ optional hosted, local, or remote tool
4. OpenAI returns a Response or typed event stream
5. Script prints aggregate text, structured text, a tool call, or raw events
6. Some examples leave remotely stored resources for later retrieval or cleanup
```

The custom function example adds a second model call after the application executes
the requested function. The create-and-retrieve example adds a read request for the
Response it just created.

## Files

```text
Basic_examples/
├── 1-basic_example.py
├── 2-analyse_images.py
├── 3-analyse_online_files.py
├── 4-upload_and_analyse_local_file.py
├── 5-model_with_web_search_tool.py
├── 6-model_w_custom_function_calling.py
├── 7-remote_sse_mcp.py
├── 8-with_server_sent_streaming.py
├── 9-structured_output.py
├── 10-create_and_retrieve_response.py
├── resources/
│   └── Unit6Exercises.pdf *-required for script #4
└── README.md
```

## Run It

Prerequisites:

- Python 3.13 or later.
- [`uv`](https://docs.astral.sh/uv/) for the locked environment.
- An OpenAI API key with model and tool access required by the chosen script.
- Network access to OpenAI and any remote URL or MCP server used by that script.

From the repository root:

```bash
uv sync --locked
source .venv/bin/activate
```

Create `.env` in the repository root:

```dotenv
OPENAI_API_KEY=your_api_key_here
```

Run one script at a time:

```bash
uv run python Responses_API/Basic_examples/1-basic_example.py
```

Every model call consumes API quota. File upload, hosted tools, storage, and remote
services can have separate cost, retention, and availability characteristics.

## Example 1: Basic Text Response

[`1-basic_example.py`](1-basic_example.py) sends one string through `input` and
prints the aggregate assistant text.

```bash
uv run python Responses_API/Basic_examples/1-basic_example.py
```

Core request:

```python
response = client.responses.create(
    model="gpt-5.6-luna",
    input="Write a one-sentence bedtime story about a unicorn.",
)
print(response.output_text)
```

Expected behavior: one short story is printed. Wording changes between runs.

## Example 2: Analyze a Remote Image

[`2-analyse_images.py`](2-analyse_images.py) sends an `input_text` part and an
`input_image` part in the same user message.

```bash
uv run python Responses_API/Basic_examples/2-analyse_images.py
```

The image URL points to a third-party JPEG. OpenAI must be able to fetch it without
interactive authentication. Availability, redirects, content changes, and usage
rights remain outside this repository's control.

Expected behavior: the model prints a description of the referenced image. The
description is generated analysis, not verified catalog metadata.

## Example 3: Analyze a Remote PDF

[`3-analyse_online_files.py`](3-analyse_online_files.py) combines a summarization
instruction with an `input_file` containing a public `file_url`.

```bash
uv run python Responses_API/Basic_examples/3-analyse_online_files.py
```

The file URL must resolve directly to a supported document that OpenAI can fetch.
Private links, expiring URLs, anti-bot pages, or HTML landing pages can fail. The
script asks for key points and prints only the returned text.

## Example 4: Upload and Analyze a Local PDF

[`4-upload_and_analyse_local_file.py`](4-upload_and_analyse_local_file.py) first
uploads a file with `purpose="user_data"`, then references the returned `file.id` in
a Response request.

```bash
uv run python Responses_API/Basic_examples/4-upload_and_analyse_local_file.py
```

The source currently opens this literal relative path:

```text
OpenAI_Responses_Conversation_API/Basic_examples/resources/Unit6Exercises.pdf
```

The bundled PDF is located at:

```text
Responses_API/Basic_examples/resources/Unit6Exercises.pdf
```

Those paths do not resolve to the same file when the command is run from the
repository root. Until the source path is adjusted for the local checkout, the
script raises `FileNotFoundError`. A working path from the repository root is:

```python
open("Responses_API/Basic_examples/resources/Unit6Exercises.pdf", "rb")
```

The upload creates a remote File that is not deleted by the script. Record the
returned File ID and implement explicit cleanup when adapting this pattern.

## Example 5: Hosted Web Search

[`5-model_with_web_search_tool.py`](5-model_with_web_search_tool.py) enables the
hosted `web_search` tool and asks for a positive UK news story using the local date.

```bash
uv run python Responses_API/Basic_examples/5-model_with_web_search_tool.py
```

Expected behavior: the model may search public sources and return a date-sensitive
answer. Search execution, cited sources, latency, wording, and tool cost can vary.
Treat retrieved web content as untrusted external data and verify consequential
claims independently.

## Example 6: Custom Function Calling

[`6-model_w_custom_function_calling.py`](6-model_w_custom_function_calling.py)
demonstrates the complete local tool loop:

1. Define a strict `get_weather` JSON Schema tool.
2. Ask the model about weather in Paris.
3. Find every returned `function_call` item by type.
4. Parse the arguments and execute deterministic local mock code.
5. Return `function_call_output` with the matching `call_id`.
6. Link the second request with `previous_response_id`.
7. Print the final user-facing answer.

```bash
uv run python Responses_API/Basic_examples/6-model_w_custom_function_calling.py
```

```text
initial Response
   └─ function_call(name="get_weather", call_id=...)
          └─ application validates and executes local function
                 └─ function_call_output(call_id=..., output=...)
                        └─ final Response linked by previous_response_id
```

The returned temperature and conditions are hard-coded mock data. Strict function
arguments reduce shape ambiguity but do not authorize side effects or establish that
tool output is factually correct.

## Example 7: Remote MCP Tool

[`7-remote_sse_mcp.py`](7-remote_sse_mcp.py) connects to a public Dungeons &
Dragons MCP server through `https://dmcp-server.deno.dev/mcp`.

```bash
uv run python Responses_API/Basic_examples/7-remote_sse_mcp.py
```

The tool configuration exposes only `roll`:

```python
{
    "type": "mcp",
    "server_label": "dmcp",
    "server_url": "https://dmcp-server.deno.dev/mcp",
    "allowed_tools": ["roll"],
    "require_approval": "never",
}
```

Automatic approval is used because the allowed operation is a harmless dice roll.
Do not apply the same policy to tools with data access or side effects. The remote
server is an independent trust boundary and receives information needed for its tool
call.

## Example 8: Server-Sent Streaming

[`8-with_server_sent_streaming.py`](8-with_server_sent_streaming.py) passes
`stream=True` and prints every event object produced by the iterator.

```bash
uv run python Responses_API/Basic_examples/8-with_server_sent_streaming.py
```

Expected behavior: the terminal displays lifecycle events, output-item events, text
deltas, and completion data. It does not print only the reconstructed assistant
text. A user interface would normally select relevant event types, append text
deltas, handle errors, and finalize the display on completion.

## Example 9: Strict Structured Output

[`9-structured_output.py`](9-structured_output.py) supplies a strict JSON Schema for
a person object and asks the model to parse `Bob, 54 years old`.

```bash
uv run python Responses_API/Basic_examples/9-structured_output.py
```

The schema requires `name` and `age`, rejects additional properties, and constrains
age to the range 0 through 130. The script prints a JSON string through
`response.output_text`; it does not call `json.loads()` or map the result into a
typed application object.

Expected shape:

```json
{
  "name": "Bob",
  "age": 54
}
```

Validate or parse returned JSON at the application boundary before using it in
business logic.

## Example 10: Create and Retrieve a Stored Response

[`10-create_and_retrieve_response.py`](10-create_and_retrieve_response.py) creates
a Response, records its ID, retrieves it with `client.responses.retrieve(...)`, and
prints both objects' stable fields.

```bash
uv run python Responses_API/Basic_examples/10-create_and_retrieve_response.py
```

Expected output shape:

```text
Creating a response...
Created Response ID:
 resp_...
Response text:
 ...
--------------------------------------------------
Retrieving the response by ID...
Retrieved Response ID:
 resp_...
Status:
 completed
Retrieved text:
 ...
```

Retrieval depends on the Response being stored and accessible to the API project.
The script does not delete the stored Response.

## Expected Behavior

| Example | Expected Terminal Behavior                                                                                  |
| ------- | ----------------------------------------------------------------------------------------------------------- |
| 1       | Prints one model-generated bedtime-story sentence                                                           |
| 2       | Prints a generated description of the remote image                                                          |
| 3       | Prints a generated summary of the remote PDF                                                                |
| 4       | Raises `FileNotFoundError` until the documented source path is corrected; then uploads and analyzes the PDF |
| 5       | Prints a date-sensitive answer that may contain web-derived information                                     |
| 6       | Prints the requested function-call object followed by a final model answer                                  |
| 7       | Prints the result of the allowed remote dice-roll tool                                                      |
| 8       | Prints multiple typed streaming events rather than one assembled string                                     |
| 9       | Prints JSON text matching the person schema                                                                 |
| 10      | Prints matching created and retrieved Response IDs plus status and text                                     |

Model wording, tool selection, remote content, and latency can vary. IDs use example
prefixes such as `resp_...` and should not be compared to fixed values in tests.

## State and Retention Summary

| Resource              | Created By   | Stored Where                                    | Cleanup in Script       |
| --------------------- | ------------ | ----------------------------------------------- | ----------------------- |
| Response              | All examples | OpenAI by default, subject to API data controls | None                    |
| Uploaded File         | Example 4    | OpenAI Files API                                | None                    |
| Web search execution  | Example 5    | Hosted tool request                             | None                    |
| Local function result | Example 6    | Process memory, then sent as tool output        | Process exits naturally |
| MCP tool exchange     | Example 7    | OpenAI and third-party server boundaries        | None                    |

None of these examples uses the Conversations API. Example 6 uses a
`previous_response_id` chain; this links Responses but is separate from a durable
Conversation object.

## Retention, Trust, and Limitations

1. Most scripts have no explicit exception handling, retry policy, timeout policy,
   or request-ID logging.
2. Remote image, PDF, web, and MCP content can change or become unavailable.
3. Tool output, model text, and summaries are nondeterministic or unverified unless
   the local mock function explicitly fixes a value.
4. Uploaded files and stored Responses are not cleaned up by these scripts.
5. The local file example has a documented path mismatch and is not runnable from
   the repository root until its source path is adjusted.
6. `require_approval="never"` is appropriate only for the narrowly allowed dice
   operation shown here.
7. Strict schemas constrain structure but do not provide authentication,
   authorization, semantic validation, or policy enforcement.
8. Examples print results directly and do not redact sensitive data before terminal
   output or logs.

## Troubleshooting

| Symptom                            | What to Check                                                  |
| ---------------------------------- | -------------------------------------------------------------- |
| Authentication or permission error | Root `.env`, API project, model access, and tool access        |
| Remote image or PDF fails          | URL availability, direct file access, and supported media type |
| `FileNotFoundError` in example 4   | The documented difference between source and bundled PDF paths |
| No function call is returned       | Prompt/tool fit and model access; the script raises explicitly |
| MCP request fails                  | Public server availability and the `/mcp` endpoint             |
| Stream output looks verbose        | Example 8 intentionally prints every typed event               |
| Structured output is a string      | Parse the JSON text before using it as an object               |
| Response retrieval fails           | Confirm storage, ID, project access, and data controls         |

## Test It

Fast repository checks parse every example and verify model and MCP configuration
without making OpenAI requests:

```bash
uv run pytest -m "not live"
```

The opt-in live test performs one billable Responses API call. It does not exercise
remote files, web search, MCP, streaming, function calling, or upload cleanup.
