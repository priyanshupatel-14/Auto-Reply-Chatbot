import os
import re
import time
from dotenv import load_dotenv
from openai import OpenAI
import pyautogui
import pyperclip

load_dotenv()

# =====================================================================
# CONFIGURATION & SCREEN COORDINATES
# =====================================================================
USER_NAME = "Priyanshu Patel"
MODEL_NAME = "gpt-4o-mini"

# Screen coordinates (exact coordinates from your working setup)
CHROME_ICON_POS = (933, 1049)
CHAT_TOP_LEFT = (691, 271)
CHAT_BOTTOM_RIGHT = (1844, 920)
DESELECT_CLICK_POS = (1873, 897)
MESSAGE_BOX_POS = (1220, 973)
SEND_BUTTON_POS = (1879, 963)

# Timing settings:
# Drag duration MUST be ~0.8s-1.0s so Chrome highlights multiple messages
# (WhatsApp Web only copies '[time] Sender:' headers when multiple bubbles are selected)
DRAG_DURATION_SEC = 0.85
POLL_INTERVAL_SEC = 0.8
MAX_HISTORY_LINES = 35

# PyAutoGUI safety: move cursor to any screen corner to stop the bot
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.08

# =====================================================================
# OPENAI CLIENT & HUMAN PERSONA SETUP
# =====================================================================
api_key = os.environ.get("API_KEY") or os.environ.get("OPENAI_API_KEY")
if not api_key:
    raise ValueError("API_KEY not found. Please set API_KEY in your .env file.")

client = OpenAI(api_key=api_key)

SYSTEM_INSTRUCTION = f"""You are {USER_NAME} chatting with someone on WhatsApp.
Reply naturally so the other person never suspects an AI or chatbot is replying.

Strict texting rules:
1. Mirror {USER_NAME}'s exact texting style, tone, and language mix (English, Hinglish, or local slang) from the conversation history.
2. Keep replies short and casual (usually 2 to 15 words, 1-2 short sentences max).
3. Use casual texting habits: lowercase where natural, common abbreviations ('u', 'rn', 'idk', 'kk', 'haan', 'bhai', 'bro', 'kya', 'acha' as appropriate), and no trailing period on short one-liners.
4. NEVER sound like an AI assistant. No polite filler ("Sure!", "I understand", "How can I help?"), no bullet points, no markdown formatting.
5. NEVER include timestamps, dates, or sender prefixes like "[12:30, 19/10/2026] {USER_NAME}:" or "{USER_NAME}:". Output ONLY the raw message text.
"""

# Matches WhatsApp Web copy headers even with invisible Unicode marks (e.g. \u200e[20:05, 19/10/2026] Name: msg)
HEADER_REGEX = re.compile(r"\]\s*([^:\n]+):\s*(.*)")


def get_last_sender_and_message(chat_history: str) -> tuple[str | None, str]:
    """
    Finds the sender and text of the very last message in the copied chat.
    Uses the same '] ' and ':' structure as your original working code, while
    scanning upward if the last message spans multiple lines.
    """
    lines = [line.strip() for line in chat_history.strip().splitlines() if line.strip()]
    if not lines:
        return None, ""

    collected_lines = []
    for line in reversed(lines):
        # Match using regex or direct '] ' split
        if "] " in line and ":" in line.split("] ", 1)[1]:
            after_bracket = line.split("] ", 1)[1]
            sender, first_line_msg = after_bracket.split(":", 1)
            sender = sender.strip()
            if first_line_msg.strip():
                collected_lines.append(first_line_msg.strip())
            full_msg = "\n".join(reversed(collected_lines)).strip()
            return sender, full_msg

        match = HEADER_REGEX.search(line)
        if match:
            sender = match.group(1).strip()
            first_line_msg = match.group(2).strip()
            if first_line_msg:
                collected_lines.append(first_line_msg)
            full_msg = "\n".join(reversed(collected_lines)).strip()
            return sender, full_msg

        collected_lines.append(line)

    return None, lines[-1]


def clean_reply(raw_text: str) -> str:
    """Removes any accidental '[time] Name:' prefixes, quotes, or markdown symbols."""
    text = raw_text.strip()
    if "] " in text and ":" in text.split("] ", 1)[1]:
        text = text.split("] ", 1)[1].split(":", 1)[1].strip()
    prefix_pattern = re.compile(rf"^{re.escape(USER_NAME)}\s*:\s*", re.IGNORECASE)
    text = prefix_pattern.sub("", text).strip()
    text = text.replace("**", "").replace("__", "").replace("`", "")
    if len(text) >= 2 and text[0] == text[-1] and text[0] in ('"', "'"):
        text = text[1:-1].strip()
    return text


def copy_chat_from_screen() -> str:
    """
    Selects the full chat area from top-left to bottom-right and copies it.
    Waits briefly before deselecting so Chrome finishes writing to clipboard.
    """
    pyautogui.moveTo(*CHAT_TOP_LEFT)
    time.sleep(0.1)
    pyautogui.dragTo(*CHAT_BOTTOM_RIGHT, duration=DRAG_DURATION_SEC, button="left")
    time.sleep(0.15)
    pyautogui.hotkey("ctrl", "c")
    time.sleep(0.35)  # Crucial: wait for Chrome to copy before clicking to deselect
    pyautogui.click(*DESELECT_CLICK_POS)
    return pyperclip.paste()


def generate_reply(chat_history: str) -> str:
    """Generates a fast, human-like reply using OpenAI."""
    lines = [line for line in chat_history.strip().splitlines() if line.strip()]
    recent_chat = "\n".join(lines[-MAX_HISTORY_LINES:])

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": SYSTEM_INSTRUCTION},
            {
                "role": "user",
                "content": (
                    f"Act as {USER_NAME} and reply naturally in a short message to the latest "
                    f"message in this WhatsApp conversation:\n\n{recent_chat}"
                ),
            },
        ],
        temperature=0.7,
        max_tokens=100,
    )
    return clean_reply(response.choices[0].message.content or "")


def paste_and_send(reply_text: str) -> None:
    """Clicks the WhatsApp message box, pastes the reply, and clicks send."""
    pyperclip.copy(reply_text)
    pyautogui.click(*MESSAGE_BOX_POS)
    time.sleep(0.2)
    pyautogui.hotkey("ctrl", "v")
    time.sleep(0.15)
    pyautogui.click(*SEND_BUTTON_POS)
    time.sleep(0.3)


def main() -> None:
    print(f"Starting WhatsApp Auto-Reply Bot as '{USER_NAME}'...")
    print("Move your mouse to any screen corner to abort (PyAutoGUI Fail-Safe).")

    # Click Chrome icon on taskbar to bring WhatsApp Web into focus
    pyautogui.click(*CHROME_ICON_POS)
    time.sleep(1.0)

    last_replied_message = None
    last_logged_state = None

    try:
        while True:
            chat_history = copy_chat_from_screen()
            if not chat_history.strip():
                time.sleep(POLL_INTERVAL_SEC)
                continue

            sender, last_message = get_last_sender_and_message(chat_history)
            current_state = (sender, last_message)

            if sender is None:
                if current_state != last_logged_state:
                    print("[Scan] No '[time] Sender:' header found in selection. Make sure multiple messages are visible.")
                    last_logged_state = current_state
                time.sleep(POLL_INTERVAL_SEC)
                continue

            # Log whenever the latest detected message changes
            if current_state != last_logged_state:
                print(f"[Scan] Latest message from '{sender}': {last_message}")
                last_logged_state = current_state

            # Reply only if the last sender is NOT Priyanshu Patel and we haven't replied to this exact message yet
            if sender.lower() != USER_NAME.lower() and current_state != last_replied_message:
                print(f"--> Generating reply to {sender}...")
                try:
                    reply = generate_reply(chat_history)
                    if reply:
                        print(f"--> Sending reply: {reply}")
                        paste_and_send(reply)
                        last_replied_message = current_state
                except Exception as e:
                    print(f"[Error] OpenAI API call failed: {e}")

            time.sleep(POLL_INTERVAL_SEC)

    except pyautogui.FailSafeException:
        print("\nBot stopped via mouse corner fail-safe.")
    except KeyboardInterrupt:
        print("\nBot stopped by user (Ctrl+C).")


if __name__ == "__main__":
    main()