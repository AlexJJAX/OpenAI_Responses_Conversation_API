"""
This script updates the metadata of a conversation.
It takes the conversation ID as an argument and updates the metadata.
It uses the client.conversations.update() method to update the conversation.
"""

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(override=True)

client = OpenAI()

conv = "conv_69a07a0305ec8190b79d96d1e225741106d65c5307c9761b"

updated = client.conversations.update(
    conv,
    metadata={"topic": "About Paris"} # topic to be assigned to the conversation. Change the topic to assign another one
)

print("Updated metadata:")
print(updated)