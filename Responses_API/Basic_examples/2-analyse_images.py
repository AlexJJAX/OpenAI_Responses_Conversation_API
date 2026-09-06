"""
This is an example of how to use the OpenAI API to analyse url based images.

How it works:
1. It initializes the OpenAI client.
2. It creates a response using the OpenAI API.
3. It analyses the image as per the specified url and prints the output.
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
                    "text": "Describe this image",
                },
                {
                    "type": "input_image",
                    "image_url": "https://nyss.org/wp-content/uploads/2025/12/John-Constable-Scene-of-Flatford-Mill.jpeg"
                }
            ]
        }
    ]
)

print(response.output_text)