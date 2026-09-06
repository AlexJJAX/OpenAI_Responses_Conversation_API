import os
import sqlite3
from openai import OpenAI
from dotenv import load_dotenv

DB_FILE = "Conversation_API/conversation_persistent_memory_app/conversations.db"

load_dotenv(override=True)

client = OpenAI()


# -----------------------------
# Database Setup
# -----------------------------
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id TEXT NOT NULL,
            topic TEXT
        )
    """)
    conn.commit()
    conn.close()


def get_saved_conversation():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT conversation_id, topic FROM conversations ORDER BY id DESC LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    return row if row else None


def save_conversation(conversation_id, topic):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO conversations (conversation_id, topic) VALUES (?, ?)",
        (conversation_id, topic),
    )
    conn.commit()
    conn.close()


# -----------------------------
# Conversation Logic
# -----------------------------
def get_or_create_conversation():
    saved = get_saved_conversation()

    if saved:
        conversation_id, topic = saved
        print("Loaded existing conversation:", conversation_id)
        print("Stored topic:", topic)
        return conversation_id

    # 🔥 Assign topic at creation time
    topic = "My Topic"  # Default value; change it to set your own topic.

    conversation = client.conversations.create(
        metadata={"topic": topic}
    )

    conversation_id = conversation.id
    save_conversation(conversation_id, topic)

    print("Created new conversation:/n", conversation_id)
    print("Assigned topic:/n", topic)

    return conversation_id


def send_message(conversation_id, message):
    response = client.responses.create(
        model="gpt-5.6-luna",
        conversation=conversation_id,
        input=[
            {"role": "user", "content": message}
        ]
    )

    return response.output_text


# -----------------------------
# Main
# -----------------------------
if __name__ == "__main__":
    init_db()

    conversation_id = get_or_create_conversation()

    while True:
        user_input = input("\nYou: ")
        if user_input.lower() in ["exit", "quit"]:
            break

        reply = send_message(conversation_id, user_input)
        print("\nAssistant:", reply)
