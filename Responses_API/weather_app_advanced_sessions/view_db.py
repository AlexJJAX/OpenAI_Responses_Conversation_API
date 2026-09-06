"""view_db.py – Pretty-print all WeatherSession rows (including stored response
content) from the SQLite database created by backend.py.

Usage (run from the project root with the venv active):
    python weather_app_advanced_sessions/view_db.py [--db PATH] [--user USER_ID] [--status STATUS]

Defaults to the same DB path used by backend.py:
    weather_app_advanced_sessions/app.db
"""

from __future__ import annotations

import argparse
import os
import textwrap
from datetime import datetime, timezone

from dotenv import load_dotenv
from sqlalchemy import create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session as OrmSession
from sqlalchemy import String, DateTime, Integer, Text
from typing import Optional

load_dotenv(override=True)

# ---------------------------------------------------------------------------
# Re-declare the ORM model (read-only mirror of backend.py – no migration needed)
# ---------------------------------------------------------------------------

class Base(DeclarativeBase):
    pass


class WeatherSession(Base):
    __tablename__ = "weather_sessions"

    session_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(128))
    status: Mapped[str] = mapped_column(String(16))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    last_active_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    request_count: Mapped[int] = mapped_column(Integer)
    last_city: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    last_response_id: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    last_response_content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

SEP = "─" * 80


def _fmt_dt(dt: datetime | None) -> str:
    """Return a compact UTC timestamp string, or '—' when None."""
    if dt is None:
        return "—"
    # SQLite may return naive datetimes – normalise to UTC for display.
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.strftime("%Y-%m-%d %H:%M:%S UTC")


def _wrap(text: str | None, width: int = 76, indent: int = 4) -> str:
    """Wrap long text and indent continuation lines."""
    if not text:
        return "(none)"
    prefix = " " * indent
    return textwrap.fill(text, width=width, initial_indent=prefix, subsequent_indent=prefix)


def print_session(s: WeatherSession) -> None:
    """Print one session record in a human-readable block."""
    status_badge = {"active": "🟢", "expired": "🟡", "closed": "🔴"}.get(s.status, "⚪")

    print(SEP)
    print(f"  Session : {s.session_id}")
    print(f"  User    : {s.user_id}")
    print(f"  Status  : {status_badge}  {s.status}")
    print(f"  Created : {_fmt_dt(s.created_at)}")
    print(f"  Active  : {_fmt_dt(s.last_active_at)}")
    print(f"  Requests: {s.request_count}   Last city: {s.last_city or '—'}")
    print(f"  Resp ID : {s.last_response_id or '—'}")
    print("  Content :")
    print(_wrap(s.last_response_content))


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="View WeatherSession rows from the DB.")
    parser.add_argument(
        "--db",
        default=os.environ.get("WEATHER_APP_DB", "weather_app_advanced_sessions/app.db"),
        help="Path to the SQLite DB file (default: weather_app_advanced_sessions/app.db).",
    )
    parser.add_argument("--user", default=None, help="Filter by user_id.")
    parser.add_argument(
        "--status",
        default=None,
        choices=["active", "expired", "closed"],
        help="Filter by session status.",
    )
    args = parser.parse_args()

    if not os.path.exists(args.db):
        print(f"[ERROR] Database not found: {args.db}")
        print("Is the backend running (or has it run at least once to create the DB)?")
        return

    engine = create_engine(f"sqlite:///{args.db}", future=True)

    with OrmSession(engine) as db:
        stmt = select(WeatherSession).order_by(WeatherSession.last_active_at.desc())
        if args.user:
            stmt = stmt.where(WeatherSession.user_id == args.user)
        if args.status:
            stmt = stmt.where(WeatherSession.status == args.status)

        sessions = db.execute(stmt).scalars().all()

    if not sessions:
        print("No sessions found (filters applied:", args.user, args.status, ")")
        return

    print(f"\nFound {len(sessions)} session(s) in '{args.db}':\n")
    for s in sessions:
        print_session(s)

    print(SEP)
    print()


if __name__ == "__main__":
    main()
