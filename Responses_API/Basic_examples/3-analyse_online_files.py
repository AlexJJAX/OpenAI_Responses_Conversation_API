"""
This is an example of how to use the OpenAI API to analyse url based files.

How it works:
1. It initializes the OpenAI client.
2. It creates a response using the OpenAI API.
3. It analyses the file based on the user's input, the file provided via file_url and prints the output.
"""

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(override=True)

client = OpenAI()

response = client.responses.create(
    model="gpt-5.6-luna",
    input=[
        {
            "role": "user",
            "content": [
                {
                    "type": "input_text",
                    "text": "Analyze the letter and provide a summary of the key points.",
                },
                {
                    "type": "input_file",
                    "file_url": "https://www.berkshirehathaway.com/letters/2024ltr.pdf",
                },
            ],
        },
    ]
)

print(response.output_text)