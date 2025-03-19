from openai import OpenAI
import base64

from dotenv import load_dotenv
load_dotenv()

def encode_image(image_path):
    with open(image_path, 'rb') as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")
    
base64_image = encode_image("./image.png")    

client = OpenAI()

input_messages = [
    {
        "role": "user",
        "content": [
            {
                "type": "input_text",
                "text": "Please describe these images"
            },
            {
                "type": "input_image",
                "image_url": f"data:image/jpeg;base64,{base64_image}"
            },
            {
                "type": "input_image",
                "image_url": "https://upload.wikimedia.org/wikipedia/commons/3/3b/LeBron_James_Layup_%28Cleveland_vs_Brooklyn_2018%29.jpg"
            },
        ]
    }
]

response = client.responses.create(
    model="gpt-4o-mini",
    input=input_messages 
)

print(response.output_text)