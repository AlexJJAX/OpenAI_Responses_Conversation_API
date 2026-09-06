""" 
This script is a backend for a mock weather app with persisted local sessions.

How it works:
1. It initializes the OpenAI client.
2. It creates or validates application sessions stored in SQLite.
3. It creates an independent OpenAI Response for each accepted weather request.
4. It stores the latest response ID and text in the local session row.
5. It returns the session snapshot and mock report as JSON.
"""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from typing import Optional

from flask import Flask, request, jsonify
from openai import OpenAI
from sqlalchemy import (
    create_engine,
    String,
    DateTime,
    Integer,
    Text,
    select
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session as OrmSession

from uuid_utils import uuid4

from dotenv import load_dotenv
load_dotenv(override=True)

# ----------------------------
# Config
# ----------------------------
DB_PATH = os.environ.get("WEATHER_APP_DB", "weather_app_advanced_sessions/app.db")
SESSION_TTL_MINUTES = int(os.environ.get("SESSION_TTL_MINUTES", "30"))  # inactivity TTL

OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
client = OpenAI(api_key=OPENAI_API_KEY)

app = Flask(__name__)

engine = create_engine(f"sqlite:///{DB_PATH}", echo=False, future=True)


# ----------------------------
# Database models
# ----------------------------
class Base(DeclarativeBase):
    pass


class WeatherSession(Base):
    __tablename__ = "weather_sessions"

    session_id: Mapped[str] = mapped_column(String(36), primary_key=True)  # UUID string
    user_id: Mapped[str] = mapped_column(String(128), index=True)

    status: Mapped[str] = mapped_column(String(16), default="active", index=True)  # active|expired|closed

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    last_active_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    request_count: Mapped[int] = mapped_column(Integer, default=0)

    last_city: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)

    last_response_id: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    last_response_content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


def init_db() -> None:
    Base.metadata.create_all(engine)


# ----------------------------
# Helpers
# ----------------------------
def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def is_expired(last_active_at: datetime, ttl_minutes: int) -> bool:
    # SQLite stores datetimes without timezone info; normalise to UTC-aware
    # before comparing so we don't hit "can't subtract offset-naive and
    # offset-aware datetimes".
    if last_active_at.tzinfo is None:
        last_active_at = last_active_at.replace(tzinfo=timezone.utc)
    return utc_now() - last_active_at > timedelta(minutes=ttl_minutes)


def expire_if_needed(db: OrmSession, s: WeatherSession) -> WeatherSession:
    if s.status == "active" and is_expired(s.last_active_at, SESSION_TTL_MINUTES):
        s.status = "expired"
        db.add(s)
        db.commit()
        db.refresh(s)
    return s


def json_session(s: WeatherSession) -> dict:
    return {
        "session_id": s.session_id,
        "user_id": s.user_id,
        "status": s.status,
        "created_at": s.created_at.isoformat(),
        "last_active_at": s.last_active_at.isoformat(),
        "request_count": s.request_count,
        "last_city": s.last_city,
        "last_response_id": s.last_response_id,
        "last_response_content": s.last_response_content,
    }


# ----------------------------
# Routes
# ----------------------------
@app.get("/health")
def health():
    return jsonify({"ok": True, "db": DB_PATH, "session_ttl_minutes": SESSION_TTL_MINUTES})


@app.post("/weather")
def weather():
    """
    Request JSON:
      {
        "city": "Paris",
        "user_id": "user_123",
        "session_id": "optional-existing-session-id"
      }
    """
    data = request.get_json(silent=True) or {}
    city = data.get("city")
    user_id = data.get("user_id")
    session_id = data.get("session_id")

    if not city:
        return jsonify({"error": "City is required"}), 400
    if not user_id:
        return jsonify({"error": "user_id is required"}), 400

    with OrmSession(engine) as db:
        # Load or create session
        if session_id:
            s = db.get(WeatherSession, session_id)
            if not s:
                return jsonify({"error": "Invalid session_id"}), 400
            if s.user_id != user_id:
                return jsonify({"error": "session_id does not belong to user_id"}), 403

            s = expire_if_needed(db, s)
            if s.status != "active":
                return jsonify({"error": f"Session is {s.status}. Start a new session."}), 409
        else:
            session_id = str(uuid4())
            s = WeatherSession(
                session_id=session_id,
                user_id=user_id,
                status="active",
                created_at=utc_now(),
                last_active_at=utc_now(),
                request_count=0,
            )
            db.add(s)
            db.commit()
            db.refresh(s)

        # Update activity + request count
        s.request_count += 1
        s.last_active_at = utc_now()
        s.last_city = city
        db.add(s)
        db.commit()
        db.refresh(s)

        # Call OpenAI (mock weather)
        resp = client.responses.create(
            model="gpt-5.6-luna",
            input=(
                "You are a weather service.\n"
                f"Generate a short mock weather report for: {city}.\n"
                "Return plain text only, 1–2 sentences.\n"
            ),
        )

        # Persist response metadata/content
        s.last_response_id = resp.id
        s.last_response_content = resp.output_text
        db.add(s)
        db.commit()
        db.refresh(s)

        return jsonify(
            {
                "session": json_session(s),
                "city": city,
                "report": resp.output_text,
            }
        )


@app.get("/sessions/<session_id>")
def get_session(session_id: str):
    with OrmSession(engine) as db:
        s = db.get(WeatherSession, session_id)
        if not s:
            return jsonify({"error": "Not found"}), 404
        s = expire_if_needed(db, s)
        return jsonify({"session": json_session(s)})


@app.post("/sessions/<session_id>/close")
def close_session(session_id: str):
    """
    Request JSON (optional but recommended):
      { "user_id": "user_123" }
    """
    data = request.get_json(silent=True) or {}
    user_id = data.get("user_id")

    with OrmSession(engine) as db:
        s = db.get(WeatherSession, session_id)
        if not s:
            return jsonify({"error": "Not found"}), 404
        if user_id and s.user_id != user_id:
            return jsonify({"error": "session_id does not belong to user_id"}), 403

        # Expire check first, then close
        s = expire_if_needed(db, s)
        s.status = "closed"
        s.last_active_at = utc_now()
        db.add(s)
        db.commit()
        db.refresh(s)
        return jsonify({"session": json_session(s)})


@app.get("/sessions")
def list_sessions():
    """
    Optional helper to list sessions by user_id or status:
      /sessions?user_id=user_123
      /sessions?status=active
    """
    user_id = request.args.get("user_id")
    status = request.args.get("status")

    with OrmSession(engine) as db:
        stmt = select(WeatherSession).order_by(WeatherSession.last_active_at.desc())
        if user_id:
            stmt = stmt.where(WeatherSession.user_id == user_id)
        if status:
            stmt = stmt.where(WeatherSession.status == status)

        sessions = db.execute(stmt).scalars().all()

        # Expire any that need it (best-effort)
        out = []
        for s in sessions:
            s = expire_if_needed(db, s)
            out.append(json_session(s))

        return jsonify({"sessions": out})


if __name__ == "__main__":
    init_db()
    app.run(host="127.0.0.1", port=5000, debug=True, use_reloader=False)
