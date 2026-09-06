"""
This is a frontend for a weather app that uses the OpenAI API to get the weather for a given location and leverages the session management capabilities of the API.

How it works:
1. It sends a request to the backend to get the weather for a given location.
2. It uses the session management capabilities of the backend to maintain the state of the conversation.
3. It prints the output of the API request.
"""

import requests

BASE = "http://127.0.0.1:5000"

user_id = "user_123"
session_id = None


def safe_json(r: requests.Response) -> dict:
    """Try to parse JSON; on failure print status + raw body and re-raise."""
    try:
        return r.json()
    except Exception:
        print(f"  [ERROR] HTTP {r.status_code} – raw body: {r.text!r}")
        raise


# 1) First call — creates a new session
payload = {"city": "Paris", "user_id": user_id, "session_id": session_id}
r = requests.post(f"{BASE}/weather", json=payload, timeout=20)
data = safe_json(r)
session_id = data["session"]["session_id"]
print("First call:")
print("  session_id:", session_id)
print("  report:", data["report"])
print()

# 2) Second call — reuses the same session
payload = {"city": "London", "user_id": user_id, "session_id": session_id}
r = requests.post(f"{BASE}/weather", json=payload, timeout=20)
data = safe_json(r)
print("Second call:")
print("  request_count:", data["session"]["request_count"])
print("  last_response_id:", data["session"]["last_response_id"])
print("  report:", data["report"])
print()

# 3) Inspect session record
r = requests.get(f"{BASE}/sessions/{session_id}", timeout=10)
data = safe_json(r)
print("Session snapshot:")
print("  ", data)
print()

# 4) Close session
r = requests.post(
    f"{BASE}/sessions/{session_id}/close",
    json={"user_id": user_id},
    timeout=10,
)
data = safe_json(r)
print("Closed:")
print("  status:", data["session"]["status"])