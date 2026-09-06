"""
This script is a backend for a stateless weather app.

How it works:
1. It receives a POST request with a city name.
2. It uses the OpenAI API to generate a mock weather report for the given city.
3. It returns the weather report as a JSON response.
"""

from flask import Flask, request, jsonify
from openai import OpenAI
import os

from dotenv import load_dotenv
load_dotenv(override=True)

app = Flask(__name__)
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])


@app.route("/weather", methods=["POST"])
def get_weather():
    data = request.json
    city = data.get("city")

    if not city:
        return jsonify({"error": "City is required"}), 400

    # Stateless call: no memory, no session
    response = client.responses.create(
        model="gpt-5.6-luna",
        input=f"""
        You are a weather service.
        Generate a short mock weather report for {city}.
        Make up realistic temperature and conditions.
        Return plain text only.
        """
    )

    return jsonify({
        "city": city,
        "report": response.output_text
    })


if __name__ == "__main__":
    app.run(debug=True)
