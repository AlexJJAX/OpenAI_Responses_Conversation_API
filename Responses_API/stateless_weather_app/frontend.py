"""
This is a frontend for a stateless weather app.

How it works:
1. It sends a POST request to the backend.
2. The backend generates a mock weather report for a given city.
3. The frontend prints the response.
"""

import requests

url = "http://127.0.0.1:5000/weather"

headers = {
    "Content-Type": "application/json"
}

data = {
    "city": "Paris"
}

response = requests.post(url, headers=headers, json=data)

print("Status code:", response.status_code)
print("Response JSON:", response.json())
