"""Fast tests for the persistent-memory history retrieval CLI."""

from __future__ import annotations

import importlib.util
import sqlite3
from pathlib import Path
from types import ModuleType, SimpleNamespace
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = (
    ROOT
    / "Conversation_API"
    / "conversation_persistent_memory_app"
    / "retrieve_conversation_history.py"
)


def load_script() -> ModuleType:
    """Load the standalone script without invoking its command-line entry point."""
    spec = importlib.util.spec_from_file_location(
        "retrieve_conversation_history",
        SCRIPT_PATH,
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_get_latest_conversation_returns_newest_row(tmp_path: Path) -> None:
    """Select the latest local Conversation pointer by its database ID."""
    module = load_script()
    database = tmp_path / "conversations.db"

    with sqlite3.connect(database) as connection:
        connection.execute(
            """
            CREATE TABLE conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id TEXT NOT NULL,
                topic TEXT
            )
            """
        )
        connection.executemany(
            "INSERT INTO conversations (conversation_id, topic) VALUES (?, ?)",
            [("conv_older", "Old Topic"), ("conv_newer", "New Topic")],
        )

    assert module.get_latest_conversation(database) == (
        "conv_newer",
        "New Topic",
    )


def test_retrieve_items_requests_all_items_in_chronological_order() -> None:
    """Use ascending order and the largest supported page size."""
    module = load_script()
    expected_items = [SimpleNamespace(type="message")]

    class FakeItems:
        def __init__(self) -> None:
            self.call: tuple[str, dict[str, Any]] | None = None

        def list(self, conversation_id: str, **kwargs: Any) -> list[Any]:
            self.call = (conversation_id, kwargs)
            return expected_items

    fake_items = FakeItems()
    fake_client = SimpleNamespace(
        conversations=SimpleNamespace(items=fake_items),
    )

    assert module.retrieve_items(fake_client, "conv_example") == expected_items
    assert fake_items.call == (
        "conv_example",
        {"order": "asc", "limit": 100},
    )


def test_format_item_renders_message_role_and_text() -> None:
    """Render message items as readable role-prefixed text."""
    module = load_script()
    message = SimpleNamespace(
        type="message",
        role="assistant",
        content=[SimpleNamespace(text="Hello from the stored history.")],
    )

    assert (
        module.format_item(message)
        == "Assistant: Hello from the stored history."
    )
