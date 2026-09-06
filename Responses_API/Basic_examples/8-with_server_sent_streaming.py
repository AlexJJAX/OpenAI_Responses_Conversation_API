"""
This is an example of how to use the OpenAI API to create a response with server-sent streaming.

How it works:
1. It initializes the OpenAI client.
2. It creates a response using the OpenAI API.
3. It uses the server-sent streaming to get the response in real-time.
4. It streams the output.
"""

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(override=True)

client = OpenAI()

stream = client.responses.create(
    model="gpt-5.6-luna",
    input=[
        {
            "role": "user",
            "content": "Say 'double bubble bath' ten times fast.",
        },
    ],
    stream=True,
)

for event in stream:
    print(event)