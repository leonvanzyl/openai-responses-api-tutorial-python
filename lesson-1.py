from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

client = OpenAI()

input_messages = [
    {
        "role": "user",
        "content": "How much wood would a woodchuck chuck?"
    }
]

# Chat
# response = client.responses.create(
#     model="gpt-4o-mini",
#     instructions="Respond like a pirate",
#     input=input_messages
# )

# Reasoning
response = client.responses.create(
    model="o3-mini",
    input=input_messages,
    reasoning={
        "effort": "medium"
    }
)

print(response.output_text)

# With Streaming
# full_response = ""

# for event in response:
#     if event.type == "response.output_text.delta":
#         print(event.delta, end="", flush=True)
#         full_response += event.delta


# print("\n\nFull Response: ", full_response)
