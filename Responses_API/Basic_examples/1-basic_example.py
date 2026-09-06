"""
This is a basic example of how to use the OpenAI API to create a response.

How it works:
1. It initializes the OpenAI client.
2. It creates a response using the OpenAI API.
3. It prints the output of the API request.
"""

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(override=True)

# Initialize the OpenAI client
client = OpenAI()

# Create a response
response = client.responses.create(
    model="gpt-5.6-luna", 
    input="Write a one-sentence bedtime story about a unicorn."
)

# Print the output of the API request known as "response"
print(response.output_text)