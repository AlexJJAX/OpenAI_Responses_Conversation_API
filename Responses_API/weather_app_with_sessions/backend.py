from flask import Flask, request, jsonify
from openai import OpenAI
import os
from uuid_utils import uuid4 

from dotenv import load_dotenv
load_dotenv(override=True)

app = Flask(__name__)
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

# In-memory session store
sessions = {}

@app.route("/weather", methods=["POST"])
def get_weather():
    data = request.get_json(silent=True) or {}
    city = data.get("city")
    session_id = data.get("session_id")

    if not city:
        return jsonify({"error": "City is required"}), 400

    # Create new session if none provided
    if not session_id:
        session_id = str(uuid4())  # ← changed generation method
        sessions[session_id] = {"request_count": 0}

    # Validate session
    if session_id not in sessions:
        return jsonify({"error": "Invalid session_id"}), 400

    sessions[session_id]["request_count"] += 1
    count = sessions[session_id]["request_count"]

    response = client.responses.create(
        model="gpt-5.6-luna",
        input=f"""
        Generate a short mock weather report for {city}.
        Mention that this is request number {count} for this user.
        """
    )

    return jsonify({
        "session_id": session_id,
        "city": city,
        "request_count": count,
        "report": response.output_text
    })


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True, use_reloader=False)