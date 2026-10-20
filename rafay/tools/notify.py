import requests
from .. import config
from ..registry import tool

def push(title, message):
    """ntfy.sh - free push notification. Phone par 'ntfy' app me topic subscribe karo."""
    try:
        requests.post(f"https://ntfy.sh/{config.NTFY_TOPIC}", data=message.encode("utf-8"),
                      headers={"Title": title.encode("utf-8")}, timeout=10)
    except Exception as e:
        print("notify fail:", e)

@tool("notify_owner", "Owner ke mobile par push notification bhejo.",
      {"title": {"type": "string"}, "message": {"type": "string"}})
def notify_owner(title, message):
    push(title, message); return "notification bhej di"
