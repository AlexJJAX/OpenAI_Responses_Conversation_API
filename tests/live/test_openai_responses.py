"""Opt-in live check for the configured OpenAI Responses API project."""

from __future__ import annotations

import os
from pathlib import Path

import pytest
from dotenv import load_dotenv
from openai import OpenAI


pytestmark = pytest.mark.live
ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.skipif(
    os.environ.get("RUN_LIVE_OPENAI_TESTS") != "1",
    reason="Set RUN_LIVE_OPENAI_TESTS=1 to allow a real, billable API request.",
)
def test_create_live_response() -> None:
    """Create one live response and validate its stable SDK-level fields."""
    load_dotenv(ROOT / ".env", override=True)
    client = OpenAI()

    response = client.responses.create(
        model="gpt-5.6-luna",
        input="Reply briefly with a greeting.",
    )

    assert response.id.startswith("resp_")
    assert response.output_text.strip()
