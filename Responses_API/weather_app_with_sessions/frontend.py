import requests

url = "http://127.0.0.1:5000/weather"

session_id = None

for i in range(3):
    payload = {
        "city": "Paris",
        "session_id": session_id
    }

    response = requests.post(url, json=payload)
    data = response.json()

    session_id = data["session_id"]

    print(f"\nRequest #{i+1}")
    print("Session ID:", session_id)
    print("Request Count:", data["request_count"])
    print("Report:", data["report"])