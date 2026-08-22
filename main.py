# Note, do make sure every modules is installed before running.
# Use your own name for correct results.
# Before runnig this program do make sure the Whatsapp or any other messaging is ON.
# If possible use the Whatsapp Web on Chrome for best results.
# To use this program, first get the coordinates of the cursor for chrome icon on taskbar, then the upper left corner and bottom right corner for dragging the screen.
# While choosing the coordinates make sure only the chat is being copyed not the entire chrome tab.


import os
from dotenv import load_dotenv
import pyautogui
import pyperclip
import time
from google import genai

load_dotenv()

api_key = os.environ.get("API_KEY")
client = genai.Client(api_key=api_key)
def is_last_message_from_sender(chat_history):
    last_line = chat_history.strip().split("\n")[-1]
    sender = last_line.split("] ")[1].split(":")[0]
    return sender != "Priyanshu Patel" #Write your own name here and also in the contents section of models of gemini.

pyautogui.click(1209, 1052)
time.sleep(1)
while True:
    pyautogui.moveTo(696, 252)
    pyautogui.dragTo(1844, 920, duration=1.0)
    pyautogui.hotkey('ctrl', 'c')
    pyautogui.click(1344, 900)
    time.sleep(1)
    chat_history = pyperclip.paste()
    if is_last_message_from_sender(chat_history):
        response = client.models.generate_content(
            model="gemini-3.5-flash", contents=f"Act as person named Priyanshu Patel and reply Naturally and in short messages to the chat based on the converstion and the conversation history. \nHere is the conversation history:\n{chat_history}"
        )
        pyperclip.copy(response.text)
        pyautogui.click(1220, 973)
        time.sleep(1)
        pyautogui.hotkey('ctrl', 'v')
        pyautogui.click(1879, 963)
        time.sleep(1)
