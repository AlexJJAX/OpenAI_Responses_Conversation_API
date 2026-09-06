# Retrieve and Update OpenAI Conversation Metadata

![OpenAI SDK](https://img.shields.io/badge/OpenAI%20Python-3.8.x-412991)
![API](https://img.shields.io/badge/OpenAI-Conversations-000000)
![Operation](https://img.shields.io/badge/operation-metadata-0A7BBC)
![State](https://img.shields.io/badge/state-remote%20resource-795548)

Two standalone scripts that retrieve an existing OpenAI Conversation and set its
application-defined metadata. They demonstrate resource administration rather than
model generation: neither script creates a Response or asks a model for output.

This is a direct API demonstration. The target Conversation ID and topic are
hard-coded for readability, and the scripts intentionally omit argument parsing,
access-control logic, retries, and a complete data lifecycle.

## Architecture Overview

| Component                      | Responsibility                                                                |
| ------------------------------ | ----------------------------------------------------------------------------- |
| `retrieve_conversation.py`     | Calls `client.conversations.retrieve(...)` and prints the Conversation object |
| `update_conversation_topic.py` | Calls `client.conversations.update(...)` with a `topic` metadata map          |
| OpenAI Conversations API       | Stores the Conversation object and its metadata                               |
| `OPENAI_API_KEY`               | Authenticates access to the API project that owns the target Conversation     |

The two scripts are independent. Running the update script does not automatically
run the retrieve script, and neither script creates a missing Conversation.

## What It Demonstrates

- Retrieving a Conversation by its `conv_...` identifier.
- Setting application metadata with `client.conversations.update(...)`.
- Reading the updated metadata from the returned SDK object.
- Separating metadata from model instructions and Conversation items.
- Understanding that resource IDs remain subject to project access controls.

## Key Design Decisions

- **Use separate scripts** — retrieval and update behavior can be observed without a
  menu, framework, or additional application state.
- **Keep the target explicit** — the concrete ID makes the required resource input
  visible, but users must replace it with an ID their API project can access.
- **Treat metadata as application state** — the `topic` field is useful for labels,
  filtering, ownership references, and workflow correlation; it does not instruct
  the model to discuss that topic.
- **Print the SDK object** — this exposes the ID, creation timestamp, object type,
  and metadata returned by the service.

## Metadata Contract

| Property          | Constraint or Meaning                                         |
| ----------------- | ------------------------------------------------------------- |
| Number of entries | Up to 16 key-value pairs                                      |
| Key length        | Up to 64 characters                                           |
| Value length      | Up to 512 characters                                          |
| Value type        | String                                                        |
| Model behavior    | Metadata is not automatically included as a model instruction |
| Storage           | Stored remotely with the Conversation object                  |

An application metadata map might look like:

```python
metadata={
    "topic": "About Paris",
    "tenant_ref": "tenant_123",
    "workflow": "support_demo",
}
```

Do not store API keys, passwords, access tokens, or unnecessary sensitive personal
data in metadata.

## Simplified Request Flow

```text
retrieve_conversation.py
   └── conversations.retrieve(conversation_id)
          └── print remote Conversation object

update_conversation_topic.py
   └── conversations.update(conversation_id, metadata={...})
          └── print updated remote Conversation object
```

Metadata updates do not create user or assistant messages and do not rewrite the
Conversation's item history.

## Files

```text
update_conversation_metadata/
├── retrieve_conversation.py
├── update_conversation_topic.py
└── README.md
```

## Configure the Target Conversation

Both scripts contain a concrete `conv_...` ID. Replace it with a Conversation ID
that belongs to the OpenAI project associated with your key.

In `retrieve_conversation.py`:

```python
conversation = client.conversations.retrieve("conv_your_conversation_id")
```

In `update_conversation_topic.py`:

```python
conv = "conv_your_conversation_id"
```

The update script uses this metadata by default:

```python
metadata={"topic": "About Paris"}
```

Change the value before running the script if another label is required.

## Run It

Prerequisites:

- Python 3.13 or later.
- [`uv`](https://docs.astral.sh/uv/).
- An OpenAI API key that can access the target Conversation.

From the repository root:

```bash
uv sync --locked
source .venv/bin/activate
```

Create `.env` in the repository root:

```dotenv
OPENAI_API_KEY=your_api_key_here
```

Retrieve the Conversation:

```bash
uv run python Conversation_API/update_conversation_metadata/retrieve_conversation.py
```

Set its topic metadata:

```bash
uv run python Conversation_API/update_conversation_metadata/update_conversation_topic.py
```

## Expected Behavior

Retrieval prints a Conversation object similar to:

```text
Conversation(
    id='conv_...',
    created_at=1772124675,
    metadata={'topic': 'About Paris'},
    object='conversation'
)
```

The update script prints a heading followed by the returned object:

```text
Updated metadata:
Conversation(id='conv_...', metadata={'topic': 'About Paris'}, ...)
```

The exact representation can vary with SDK serialization. A successful update is
remote and can be confirmed by running the retrieval script against the same ID.

## Identity and Access

| Scenario                                 | Expected Result                                     |
| ---------------------------------------- | --------------------------------------------------- |
| ID belongs to the API key's project      | The permitted retrieve or update operation succeeds |
| ID belongs to another project            | The resource is unavailable to the request          |
| ID was deleted or mistyped               | Retrieval or update fails                           |
| Restricted key lacks endpoint permission | The API rejects the operation                       |

A Conversation ID is a resource identifier, not an authorization credential. Do not
accept arbitrary IDs from users without mapping them to authenticated ownership in
your application.

## Retention, Trust, and Limitations

1. Both scripts rely on a hard-coded target and are easy to run against the wrong
   Conversation if the ID is not reviewed first.
2. Metadata updates can overwrite application state. A multi-writer application
   needs concurrency control and an authoritative metadata policy.
3. The scripts provide no exception handling, retries, timeouts, or structured
   request-ID logging.
4. They do not create, list, or delete Conversations.
5. They do not retrieve Conversation items; use the Conversation Items endpoint when
   message or tool history is required.
6. Metadata must follow the same access, privacy, retention, and deletion policy as
   the Conversation it describes.

## Troubleshooting

| Symptom                | What to Check                                                         |
| ---------------------- | --------------------------------------------------------------------- |
| Conversation not found | Verify the ID, API project, and whether the Conversation still exists |
| Authentication error   | Confirm `OPENAI_API_KEY` is present in the root `.env`                |
| Permission error       | Check the API key's endpoint permissions                              |
| Validation error       | Check entry count and key/value lengths                               |
| Unexpected metadata    | Confirm both scripts target exactly the same Conversation ID          |

## Test It

Fast repository checks validate Python syntax without contacting OpenAI:

```bash
uv run pytest -m "not live"
```

These scripts make real remote resource requests when run directly. Review the
hard-coded ID before executing either script.
