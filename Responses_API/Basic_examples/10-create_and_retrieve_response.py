"""
This is an example of how to use the OpenAI API to create and retrieve a response.

How it works:
1. It initializes the OpenAI client.
2. It creates a response using the OpenAI API.
3. It retrieves the response using its ID.
4. It prints the output of the API request.
"""

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(override=True)

client = OpenAI()

print("Creating a response...")
# 1. Create a response
response = client.responses.create(
    model="gpt-5.6-luna", 
    input="Tell me a quick 1-sentence joke."
)

print(f"Created Response ID:\n {response.id}")
print("Response text:\n", response.output_text)
print("-" * 50)

print("Retrieving the response by ID...")
# 2. Retrieve the response using its ID
retrieved_response = client.responses.retrieve(response.id)

print(f"Retrieved Response ID:\n {retrieved_response.id}")
print(f"Status:\n {retrieved_response.status}")
print("Retrieved text:\n", retrieved_response.output_text)
