from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

from playwright.sync_api import sync_playwright
import base64
import time
from PIL import Image
from io import BytesIO

# Input messages
input_messages = [
    {
        "role": "user",
        "content": "Open bing and search for images of Emma Watson. Then click on the first image that you found. Download the image."
    }
]

# Tools
tools = [{
    "type": "computer_use_preview",
    "display_width": 1024,
    "display_height": 768,
    "environment": "browser",
}]

# OpenAI client
client = OpenAI()

def show_image(base_64_image):
    image_data = base64.b64decode(base_64_image)
    image = Image.open(BytesIO(image_data))
    image.show()

def get_screenshot(page):
    """
    Take a full-page screenshot using Playwright and return the image bytes.
    """
    return page.screenshot()

def handle_model_action(browser, page, action):
    action_type = action.type

    try:
        # Check if we have a new page/tab and switch to it
        all_pages = browser.contexts[0].pages
        if len(all_pages) > 1 and all_pages[-1] != page:
            page = all_pages[-1]
            print("Switched to new page/tab")

        match action_type:
            case "click":
                x, y = action.x, action.y
                button = action.button
                print(f"Clicking at ({x}, {y}) with button {button}")
                page.mouse.click(x, y, button=button)

            case "scroll":
                x, y = action.x, action.y
                scroll_x, scroll_y = action.scroll_x, action.scroll_y
                print(f"Action: scroll at ({x}, {y}) with offsets (scroll_x={scroll_x}, scroll_y={scroll_y})")
                page.mouse.move(x, y)
                page.evaluate(f"window.scrollBy({scroll_x}, {scroll_y})")

            case "keypress":
                keys = action.keys
                for k in keys:
                    print(f"Action: keypress '{k}'")
                    # A simple mapping for common keys; expand as needed.
                    if k.lower() == "enter":
                        page.keyboard.press("Enter")
                    elif k.lower() == "space":
                        page.keyboard.press(" ")
                    else:
                        page.keyboard.press(k)

            case "type":
                text = action.text
                print(f"Action: type text: {text}")
                page.keyboard.type(text)

            case "wait":
                print(f"Action: wait")
                time.sleep(2)

            case _:
                print(f"Unrecognized action: {action}")

        return page

    except Exception as e:
        print(f"Error handling action {action}: {e}")
        return page  # Return the original page
    

def computer_use_loop(browser, page, response):
    while True:
        computer_calls = [item for item in response.output if item.type == "computer_call"]
        if not computer_calls:
            print("No more computer calls. Output from model: ")
            for item in response.output:
                print(item)
            break # Exit when no computer calls are issued.

        # We expect at most one computer call per response.
        computer_call = computer_calls[0]
        last_call_id = computer_call.call_id
        action = computer_call.action

        page = handle_model_action(browser, page, action)
        time.sleep(1)        

        screenshot_bytes = get_screenshot(page)
        screenshot_base64 = base64.b64encode(screenshot_bytes).decode("utf-8")
        show_image(screenshot_base64)

        response = client.responses.create(
            model="computer-use-preview",
            previous_response_id=response.id,
            tools=tools,
            input=[{
                "call_id": last_call_id,
                "type": "computer_call_output",
                "output": {
                    "type": "input_image",
                    "image_url": f"data:image/png;base64,{screenshot_base64}"
                }
            }],
            truncation="auto"
        )

        print("Response: ", response.output)

    return response


def main():

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            chromium_sandbox=True,
            env={},
            args=[
                "--disable-extensions",
                "--disable-file-system"
            ]
        )

        page = browser.new_page()
        page.set_viewport_size({"width": 1024, "height": 768})

        # Navigate to the initial URL
        page.goto("https://bing.com", wait_until="domcontentloaded")

        # Create initial response
        response = client.responses.create(
            model="computer-use-preview",
            input=input_messages,
            tools=tools,
            reasoning={
                "generate_summary": "concise",
            },
            truncation="auto"
        )

        print(response.output)

        final_response = computer_use_loop(browser, page, response)
        print("Final response: ", final_response.output_text)

        # Close the browser
        browser.close()


if __name__ == "__main__":
    main()

