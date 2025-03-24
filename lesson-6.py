from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

client = OpenAI()

input_messages = [
    {
        "role": "user",
        "content": "What is the latest news from OpenAI?"
    }
]

tools=[
    {
        "type": "web_search_preview",
        "user_location": {
            "type": "approximate",
            "country": "GB",
            "city": "London",
            "region": "London",
        }
    }
]

response = client.responses.create(
    model="gpt-4o-mini",
    instructions="When looking up real time data using web search, do not ask for the user's location. It will be provided by the web search tool itself.",
    input=input_messages,
    tools=tools
)

# print(response.model_dump_json(indent=4))

print("AI Response: ", response.output_text)

print("\nCitations:")

for block in response.output:
    if not hasattr(block, 'content'):
        continue

    for content_item in block.content:
        if not hasattr(content_item, 'annotations'):
            continue

        for annotation in content_item.annotations:
            if annotation.type == 'url_citation':
                print(f"- {annotation.title}: {annotation.url}")