from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

import requests

from pydantic import BaseModel, ConfigDict
import json

# Tool Functions
def get_todo_list():
    return [
        {
            "id": 1,
            "title": "Buy bread"
        },
        {
            "id": 2,
            "title": "Buy milk"
        }
    ]

def get_weather(latitude, longitude):
    response = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m,wind_speed_10m&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m")
    data = response.json()

    return data['current']['temperature_2m']


# Pydantic schemas
class GetTodoListParams(BaseModel):
    model_config = ConfigDict(extra="forbid")
    pass

class GetWeatherParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    latitude: float
    longitude: float

# Generate schemas
todo_list_schema = GetTodoListParams.model_json_schema()
weather_schema = GetWeatherParams.model_json_schema()


tools = [
    {
        "type": "function",
        "name": "get_todo_list",
        "description": "Get the list of todos",
        "parameters": todo_list_schema,
        "strict": True
    },
    {
        "type": "function",
        "name": "get_weather",
        "description": "Get the weather for a given latitude and longitude",
        "parameters": weather_schema,
        "strict": True
    }
]

client = OpenAI()

input_messages = [
    {
        "role": "user",
        "content": "What is the current weather in Cape Town? Also, what are my todos?"
    }
]

while True:
    response = client.responses.create(
        model="gpt-4o-mini",
        input=input_messages,
        tools=tools
    )

    response_output = response.output[0]
    response_type = response_output.type

    if response_type == "message":
        print(response.output_text)
        break

    if response_type == "function_call":
        function_name = response_output.name
        arguments = response_output.arguments
        args = json.loads(arguments)

        print(f"Function: {function_name} with args: {args}")

        tool_result = ""
        if function_name == "get_todo_list":
            tool_result = get_todo_list()

        if function_name == "get_weather":
            tool_result = get_weather(args["latitude"], args["longitude"])

        input_messages.append(response_output)
        input_messages.append({
            "type": "function_call_output",
            "call_id": response_output.call_id,
            "output": str(tool_result)
        })
