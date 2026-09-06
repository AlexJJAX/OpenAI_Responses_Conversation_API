from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(override=True)

client = OpenAI()

# 1) Create a new conversation
conversation = client.conversations.create()

conversation_id = conversation.id
print("Conversation ID:", conversation_id)

# 2) Send the first message in the conversation
response1 = client.responses.create(
    model="gpt-5.6-luna",
    conversation=conversation_id,
    input=[{"role": "user", "content": "Hello! What can you do?"}]
)

print("Assistant 1:", response1.output_text)

# 3) Send a follow-up question using the same conversation
response2 = client.responses.create(
    model="gpt-5.6-luna",
    conversation=conversation_id,
    input=[{"role": "user", "content": "Can you tell me a short joke?"}]
)

print("Assistant 2:", response2.output_text)