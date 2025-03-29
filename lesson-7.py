from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

client = OpenAI()

input_messages = [
    {
        "role": "user",
        "content": "What are the current specials?"
    }
]

tools = [
    {
        "type": "file_search",
        "vector_store_ids": ["vs_67e7a75bbee88191881d571e17999868"],
        "max_num_results": 2
    }
]

response = client.responses.create(
    model="gpt-4o-mini",
    instructions="You are a helpful assistant.",
    input=input_messages,
    tools=tools,
    include=["file_search_call.results"]
)

print("Agent Answer: ", response.output_text)


for output_item in response.output:

    if output_item.type == "file_search_call":
        print("Search Results:")
        for i, result in enumerate(output_item.results, 1):
            print(f"Results {i}")
            print(f"Filename: {result.filename}")
            print(f"Score: {result.score}")
            print(f"Text snippet: {result.text[:150]}..." if len(result.text) > 150 else f"Text snippet: {result.text}" )

    if output_item.type == "message":
        for content_item in output_item.content:
            if content_item.type == "output_text":
                print("Annotation: ")
                for annotation in content_item.annotations:
                    if annotation.type == "file_citation":
                        print(f"- Citation from File: {annotation.filename}")


# print(response.model_dump_json(indent=4))
