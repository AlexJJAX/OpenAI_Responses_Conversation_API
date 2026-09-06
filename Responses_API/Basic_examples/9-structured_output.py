"""
This is an example of how to use the OpenAI API to create a response with structured output.

How it works:
1. It initializes the OpenAI client.
2. It creates a response using the OpenAI API.
3. It uses the structured output to get the response in a structured format.
4. It prints the output of the API request in a structured format.
"""

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(override=True)

client = OpenAI()

response = client.responses.create(
  model="gpt-5.6-luna",
  input="Bob, 54 years old", 
  text={
    "format": {
      "type": "json_schema",
      "name": "person",
      "strict": True,
      "schema": {
        "type": "object",
        "properties": {
          "name": {
            "type": "string",
            "minLength": 1
          },
          "age": {
            "type": "number",
            "minimum": 0,
            "maximum": 130
          }
        },
        "required": [
          "name",
          "age"
        ],
        "additionalProperties": False
      }
    }
  }
)

print(response.output_text)