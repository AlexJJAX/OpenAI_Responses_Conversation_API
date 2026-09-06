import os
import json
import sqlite3
from datetime import datetime, timezone, timedelta

from flask import Flask, request, jsonify
from openai import OpenAI

from dotenv import load_dotenv
load_dotenv(override=True)

# ----------------------
# Configuration
# ----------------------
DB_FILE = "Conversation_API/conversation_multi_user_temp_memory_app/conversations.db"
TTL_MINUTES = int(os.environ.get("CONVERSATION_TTL_MINUTES", "30"))

client = OpenAI()
app = Flask(__name__)


# ----------------------
# Database Setup
# ----------------------
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS conversations (
        conversation_id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        status TEXT NOT NULL,
        created_at TEXT NOT NULL,
        last_active_at TEXT NOT NULL
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS responses (
        response_id TEXT PRIMARY KEY,
        conversation_id TEXT NOT NULL,
        user_id TEXT NOT NULL,
        created_at TEXT NOT NULL,
        model TEXT,
        input_text TEXT,
        output_text TEXT,
        usage_json TEXT,
        raw_json TEXT,
        FOREIGN KEY(conversation_id) REFERENCES conversations(conversation_id)
    )
    """)

    conn.commit()
    conn.close()


# ----------------------
# Utilities
# ----------------------
def utc_now():
    """
    Get the current time in UTC.
    """
    return datetime.now(timezone.utc)


def is_expired(last_active_at):
    """
    Check if a conversation has expired.
    """
    last = datetime.fromisoformat(last_active_at)
    return utc_now() - last > timedelta(minutes=TTL_MINUTES)


def get_conversation(conversation_id):
    """
    Get a conversation by ID.
    """
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM conversations WHERE conversation_id=?", (conversation_id,))
    row = c.fetchone()
    conn.close()
    return row


def expire_if_needed(conversation_id):
    """
    Expire a conversation if needed.
    """
    row = get_conversation(conversation_id)
    if not row:
        return None

    _, user_id, status, created_at, last_active_at = row

    if status == "active" and is_expired(last_active_at):
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute(
            "UPDATE conversations SET status=? WHERE conversation_id=?",
            ("expired", conversation_id),
        )
        conn.commit()
        conn.close()

        return "expired"

    return status


# ----------------------
# Routes
# ----------------------
@app.post("/chat")
def chat():
    """
    Chat with the OpenAI API.
    """
    data = request.json or {}
    user_id = data.get("user_id")
    message = data.get("message")
    conversation_id = data.get("conversation_id")

    if not user_id or not message:
        return jsonify({"error": "user_id and message required"}), 400

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    # Create new conversation if needed
    if not conversation_id:
        conv = client.conversations.create()
        conversation_id = conv.id

        now = utc_now().isoformat()

        c.execute("""
            INSERT INTO conversations
            VALUES (?, ?, ?, ?, ?)
        """, (conversation_id, user_id, "active", now, now))
        conn.commit()

    # Validate conversation ownership
    row = get_conversation(conversation_id)
    if not row:
        return jsonify({"error": "Invalid conversation_id"}), 400

    _, stored_user, status, created_at, last_active = row

    if stored_user != user_id:
        return jsonify({"error": "Conversation does not belong to user"}), 403

    status = expire_if_needed(conversation_id)
    if status != "active":
        return jsonify({"error": f"Conversation is {status}"}), 409

    # Send message
    response = client.responses.create(
        model="gpt-5.6-luna",
        conversation=conversation_id,
        input=[{"role": "user", "content": message}],
    )

    # Store response metadata
    now = utc_now().isoformat()

    c.execute("""
        INSERT INTO responses
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        response.id,
        conversation_id,
        user_id,
        now,
        response.model,
        message,
        response.output_text,
        response.usage.model_dump_json() if response.usage else None,
        response.model_dump_json(),
    ))

    c.execute("""
        UPDATE conversations
        SET last_active_at=?
        WHERE conversation_id=?
    """, (now, conversation_id))

    conn.commit()
    conn.close()

    return jsonify({
        "conversation_id": conversation_id,
        "response_id": response.id,
        "reply": response.output_text
    })


@app.get("/conversations")
def list_conversations():
    """
    List conversations.
    """
    user_id = request.args.get("user_id")
    status = request.args.get("status")

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    query = "SELECT * FROM conversations WHERE 1=1"
    params = []

    if user_id:
        query += " AND user_id=?"
        params.append(user_id)

    if status:
        query += " AND status=?"
        params.append(status)

    c.execute(query, params)
    rows = c.fetchall()
    conn.close()

    results = []
    for row in rows:
        results.append({
            "conversation_id": row[0],
            "user_id": row[1],
            "status": row[2],
            "created_at": row[3],
            "last_active_at": row[4],
        })

    return jsonify({"conversations": results})


@app.post("/conversations/<conversation_id>/close")
def close_conversation(conversation_id):
    """
    Close a conversation.
    """
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    c.execute("""
        UPDATE conversations
        SET status=?
        WHERE conversation_id=?
    """, ("closed", conversation_id))

    conn.commit()
    conn.close()

    return jsonify({"conversation_id": conversation_id, "status": "closed"})


@app.get("/responses/<conversation_id>")
def list_responses(conversation_id):
    """
    List responses for a conversation.
    """
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    c.execute("""
        SELECT response_id, created_at, model, input_text, output_text
        FROM responses
        WHERE conversation_id=?
        ORDER BY created_at ASC
    """, (conversation_id,))

    rows = c.fetchall()
    conn.close()

    return jsonify({
        "conversation_id": conversation_id,
        "responses": [
            {
                "response_id": r[0],
                "created_at": r[1],
                "model": r[2],
                "input": r[3],
                "output": r[4],
            }
            for r in rows
        ]
    })


# ----------------------
# Main
# ----------------------
if __name__ == "__main__":
    init_db()
    app.run(host="127.0.0.1", port=5000, debug=True, use_reloader=False)