"""
This is an example of using a remote MCP server from the Responses API.

How it works:
1. It initializes the OpenAI client.
2. It connects to the server's current Streamable HTTP /mcp endpoint.
3. It restricts the available MCP tools to the dice-roll operation.
4. It creates a response and prints the result of the dice roll.
"""

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(override=True)

client = OpenAI()

resp = client.responses.create(
    model="gpt-5.6-luna",
    tools=[
        {
            "type": "mcp",
            "server_label": "dmcp",
            "server_description": "A Dungeons and Dragons MCP server to assist with dice rolling.",
            "server_url": "https://dmcp-server.deno.dev/mcp",
            "allowed_tools": ["roll"],
            "require_approval": "never",
        },
    ],
    input="Roll 2d4+1",
)

print(resp.output_text)
