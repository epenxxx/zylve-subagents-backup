import os
import sys
import json
import requests

# Load API key from environment variable (set in ~/.hermes/.env)
API_KEY = os.getenv("HERMES_CUSTOM_40_50_60_2_20128_API_KEY")
if not API_KEY:
    print("Error: API key not found in environment. Make sure ~/.hermes/.env is sourced.", file=sys.stderr)
    sys.exit(1)

BASE_URL = "http://40.50.60.2:20128/v1/chat/completions"
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}

MODEL = "antigravity/gpt-oss-120b-medium"  # user‑selected model

def chat_loop():
    print("Simple Antigravity chat (type 'exit' or Ctrl‑D to quit).")
    conversation = []
    while True:
        try:
            user_input = input("You: ")
        except EOFError:
            break
        if user_input.strip().lower() in {"exit", "quit"}:
            break
        # Append user message to conversation history
        conversation.append({"role": "user", "content": user_input})
        payload = {
            "model": MODEL,
            "messages": conversation,
            "stream": False
        }
        try:
            response = requests.post(BASE_URL, headers=HEADERS, json=payload, timeout=120)
            response.raise_for_status()
        except Exception as e:
            print(f"[Error] request failed: {e}", file=sys.stderr)
            continue
        try:
            data = response.json()
            # Assuming a standard OpenAI‑compatible response
            assistant_msg = data.get("choices", [{}])[0].get("message", {})
            content = assistant_msg.get("content", "")
        except Exception as e:
            print(f"[Error] could not parse response: {e}", file=sys.stderr)
            continue
        print(f"Assistant: {content}")
        # Append assistant reply to conversation for context
        conversation.append({"role": "assistant", "content": content})

if __name__ == "__main__":
    chat_loop()
