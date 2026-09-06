"""
This is an example of how to use the OpenAI API to upload and analyse local files.

How it works:
1. It initializes the OpenAI client.
2. It uploads the local file to the OpenAI API.
3. It creates a response using the OpenAI API.
4. It analyses the file based on the user's input, the uploaded file and prints the output.
"""

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(override=True)

client = OpenAI()

file = client.files.create(
    file=open("OpenAI_Responses_Conversation_API/Basic_examples/resources/Unit6Exercises.pdf", "rb"),
    purpose="user_data"
)

response = client.responses.create(
    model="gpt-5.6-luna",
    input=[
        {
            "role": "user",
            "content": [
                {
                    "type": "input_file",
                    "file_id": file.id,
                },
                {
                    "type": "input_text",
                    "text": "What is Question 1 about?",
                },
            ]
        }
    ]
)

print(response.output_text)