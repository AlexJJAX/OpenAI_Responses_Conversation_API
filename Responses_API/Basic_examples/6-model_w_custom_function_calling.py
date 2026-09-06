"""
This is an example of a complete Responses API custom-function call.

How it works:
1. It initializes the OpenAI client.
2. It gives the model a strict get_weather function definition.
3. It finds the returned function call without assuming output-item ordering.
4. It executes local mock weather code.
5. It sends function_call_output back using the original call ID.
6. It prints the model's final user-facing answer.
"""

import json
from datetime import datetime

from dotenv import load_dotenv
from openai import OpenAI

today = datetime.now()

load_dotenv(override=True)

client = OpenAI()


def get_weather(location: str) -> dict[str, str | int]:
    """Return deterministic mock weather data for the requested location."""
    return {
        "location": location,
        "date": today.date().isoformat(),
        "temperature_c": 18,
        "conditions": "Partly cloudy (mock data)",
    }


tools = [
    {
        "type": "function",
        "name": "get_weather",
        "description": "Get current temperature for a given location.",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "City and country e.g. Bogotá, Colombia",
                }
            },
            "required": ["location"],
            "additionalProperties": False,
        },
        "strict": True,
    },
]

response = client.responses.create(
    model="gpt-5.6-luna",
    input=[
        {"role": "user", "content": f"What is the weather like in Paris on {today.date()}?"},
    ],
    tools=tools,
)

# A response may contain reasoning, messages, and one or more function calls in
# any order. Find function calls by type instead of indexing response.output.
tool_outputs = []
for item in response.output:
    if item.type != "function_call":
        continue

    print("Function call:")
    print(item.to_json())

    if item.name != "get_weather":
        raise RuntimeError(f"Unsupported function requested: {item.name}")

    arguments = json.loads(item.arguments)
    result = get_weather(arguments["location"])
    tool_outputs.append(
        {
            "type": "function_call_output",
            "call_id": item.call_id,
            "output": json.dumps(result),
        }
    )

if not tool_outputs:
    raise RuntimeError("The model did not request the get_weather function.")

# Send the application's tool result back so the model can produce a final
# user-facing answer. previous_response_id preserves the preceding tool call.
final_response = client.responses.create(
    model="gpt-5.6-luna",
    previous_response_id=response.id,
    input=tool_outputs,
    tools=tools,
)

print("Final answer:")
print(final_response.output_text)
