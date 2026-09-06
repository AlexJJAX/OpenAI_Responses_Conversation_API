"""Retrieve and display the items stored in an OpenAI Conversation.

What this script does?
    Loads a Conversation ID from the example's SQLite database, retrieves every
    item in that remote Conversation, and prints the history in chronological order.

Why is it needed?
    The local database stores only a Conversation ID and topic. The actual messages,
    tool calls, and other Conversation items are stored by OpenAI and must be fetched
    through the Conversation Items API.

How it works?
    The script loads environment variables from ``.env``, selects the newest local
    Conversation unless ``--conversation-id`` is supplied, and iterates the paginated
    ``client.conversations.items.list`` result. Messages are rendered for readability;
    other item types are retained as formatted JSON.
"""

from __future__ import annotations

import argparse
import json
import logging
import sqlite3
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI, OpenAIError


DB_FILE = Path(__file__).resolve().with_name("conversations.db")
LOGGER = logging.getLogger(__name__)


def configure_logging() -> None:
    """Configure concise diagnostic logging for command-line execution."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments for the history retrieval command."""
    parser = argparse.ArgumentParser(
        description="Retrieve all items stored in an OpenAI Conversation.",
    )
    parser.add_argument(
        "--conversation-id",
        help="Use this Conversation ID instead of the newest ID in conversations.db.",
    )
    return parser.parse_args(argv)


def get_latest_conversation(
    db_file: Path = DB_FILE,
) -> tuple[str, str | None]:
    """Return the newest locally stored Conversation ID and topic."""
    if not db_file.is_file():
        raise FileNotFoundError(f"Conversation database not found: {db_file}")

    try:
        with sqlite3.connect(db_file) as connection:
            row = connection.execute(
                """
                SELECT conversation_id, topic
                FROM conversations
                ORDER BY id DESC
                LIMIT 1
                """
            ).fetchone()
    except sqlite3.Error as exc:
        raise RuntimeError(f"Unable to read Conversation database: {exc}") from exc

    if row is None:
        raise LookupError(
            "No locally stored Conversation was found. Run app.py first or pass "
            "--conversation-id."
        )

    conversation_id, topic = row
    return str(conversation_id), str(topic) if topic is not None else None


def retrieve_items(client: OpenAI, conversation_id: str) -> list[Any]:
    """Retrieve every item in a Conversation in chronological order."""
    page = client.conversations.items.list(
        conversation_id,
        order="asc",
        limit=100,
    )
    # OpenAI cursor pages automatically request subsequent pages during iteration.
    return list(page)


def item_payload(item: Any) -> Any:
    """Convert an SDK item or content part into JSON-compatible data."""
    model_dump = getattr(item, "model_dump", None)
    if callable(model_dump):
        return model_dump(mode="json", exclude_none=True)
    if hasattr(item, "__dict__"):
        return vars(item)
    return str(item)


def format_item(item: Any) -> str:
    """Render a message readably and preserve other item types as JSON."""
    item_type = str(getattr(item, "type", "unknown"))
    if item_type != "message":
        payload = json.dumps(
            item_payload(item),
            indent=2,
            ensure_ascii=False,
            default=str,
        )
        return f"{item_type}:\n{payload}"

    role = str(getattr(item, "role", "unknown")).capitalize()
    rendered_parts: list[str] = []
    for part in getattr(item, "content", []):
        text = getattr(part, "text", None)
        refusal = getattr(part, "refusal", None)
        if text:
            rendered_parts.append(str(text))
        elif refusal:
            rendered_parts.append(str(refusal))
        else:
            rendered_parts.append(
                json.dumps(
                    item_payload(part),
                    indent=2,
                    ensure_ascii=False,
                    default=str,
                )
            )

    body = "\n".join(rendered_parts) or "[No printable content]"
    return f"{role}: {body}"


def print_history(
    conversation_id: str,
    topic: str | None,
    items: Sequence[Any],
) -> None:
    """Print Conversation metadata followed by its retrieved items."""
    print(f"Conversation ID: {conversation_id}")
    if topic is not None:
        print(f"Stored topic: {topic}")
    print(f"Items retrieved: {len(items)}")

    if not items:
        print("\nThe Conversation does not contain any items.")
        return

    print("\nConversation history:\n")
    for index, item in enumerate(items):
        if index:
            print()
        print(format_item(item))


def main(argv: Sequence[str] | None = None) -> int:
    """Run the history retrieval command and return a process exit status."""
    configure_logging()
    load_dotenv(override=True)
    args = parse_args(argv)

    try:
        if args.conversation_id:
            conversation_id = args.conversation_id
            topic = None
        else:
            conversation_id, topic = get_latest_conversation()

        LOGGER.info("Retrieving Conversation items conversation_id=%s", conversation_id)
        items = retrieve_items(OpenAI(), conversation_id)
    except (FileNotFoundError, LookupError, RuntimeError) as exc:
        LOGGER.error("%s", exc)
        return 1
    except OpenAIError as exc:
        LOGGER.error(
            "Unable to retrieve Conversation %s: %s",
            locals().get("conversation_id", "<unknown>"),
            exc,
        )
        return 1

    LOGGER.info("Retrieved %d Conversation item(s)", len(items))
    print_history(conversation_id, topic, items)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
