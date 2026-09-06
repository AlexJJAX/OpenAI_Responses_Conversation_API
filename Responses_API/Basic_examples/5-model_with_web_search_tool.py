"""
This is an example of how to use the OpenAI API to create a response with a web search tool.

How it works:
1. It initializes the OpenAI client.
2. It creates a response using the OpenAI API.
3. It uses the web search tool to search the web for the latest news.
4. It prints the output of the API request.
"""

from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime

load_dotenv(override=True)

client = OpenAI()

today = datetime.now()

response = client.responses.create(
    model="gpt-5.6-luna",
    tools=[{"type": "web_search"}],
    input=f"What was the top positive news story in the UK from {today.date()}?"
)

print(response.output_text)