"""
This script retrieves a conversation from the OpenAI Conversations API.
It takes the conversation ID as an argument and returns the conversation object.
It uses the client.conversations.retrieve() method to retrieve the conversation.
"""
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(override=True)

client = OpenAI()

conversation = client.conversations.retrieve("conv_69a07a0305ec8190b79d96d1e225741106d65c5307c9761b")
print(conversation)
