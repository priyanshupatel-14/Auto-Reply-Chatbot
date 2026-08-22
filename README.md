# AI Auto-Reply ChatBot

A Python automation project that reads the visible chat history, detects whether the latest message was sent by someone else, generates a short natural reply using Google Gemini, and sends the reply through the selected messaging app.

## Features

- Automates mouse and keyboard interaction with selected messaging app using `PyAutoGUI`
- Copies the visible chat history from the screen
- Uses `Pyperclip` to read and paste clipboard content
- Detects whether the latest message is from the configured user
- Generates a short conversational reply using Google Gemini
- Sends the generated response back through the selected messaging app
- Uses an environment variable for the Gemini API key

## Requirements

- Python 3.x
- Google Gemini API key
- Any messaging app
- Google Chrome is recommended
- A desktop environment where PyAutoGUI can control the mouse and keyboard

## Installation

Clone the repository:

```bash
git clone <your-repository-url>
cd <your-repository-folder>
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

## API Key Setup

The program reads the Gemini API key from the `API_KEY` environment variable.

Create a `.env` file in the project directory:

```env
API_KEY=your_gemini_api_key
```

Do not commit the `.env` file or expose your API key.

## Before Running

The program uses fixed screen coordinates, so the coordinates must match your own desktop setup.

According to the program instructions:

1. Make sure WhatsApp or the target messaging application is open.
2. any messaging app on Chrome is recommended.
3. Determine the cursor coordinates for the Chrome icon on the taskbar.
4. Determine the upper-left and bottom-right coordinates used to select the chat.
5. Make sure the selected area contains only the chat and not the entire Chrome tab.
6. Replace the example personal name in the sender-detection logic with your own name.

## Running the Program

Run:

```bash
python main.py
```

The program continuously selects the configured chat area, copies the visible conversation, and checks the latest message.

When the latest message is not from the configured sender, Gemini generates a reply and the program pastes and sends it.

## Configuration

The sender-detection function currently checks for:

```python
return sender != "Priyanshu Patel"
```

Replace `"Priyanshu Patel"` with your own name.

The program also contains hard-coded screen coordinates for mouse actions. These values must be adjusted to your screen and the messaging app layout.

## How It Works

1. `PyAutoGUI` interacts with the selected messaging app interface.
2. The configured chat area is selected.
3. The selected content is copied to the clipboard.
4. `Pyperclip` retrieves the copied chat history.
5. The program extracts the sender of the latest message.
6. If the latest message is not from the configured user, the conversation history is sent to Google Gemini.
7. Gemini generates a short natural-language response.
8. The response is copied to the clipboard.
9. `PyAutoGUI` pastes and sends the response.

## Important Notes

This project depends on screen coordinates and the current selected messaging app interface, so changes in window position, screen resolution, browser layout, zoom level, or the messaging app UI can affect the automation.

The current implementation is designed for a specific local desktop setup and should be treated as a learning/automation project rather than a general-purpose WhatsApp bot.
