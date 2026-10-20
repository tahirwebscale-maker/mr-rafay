"""WhatsApp Business Cloud API (official). Sirf opted-in contacts / unke message ka jawab."""
import os, requests
from ..registry import tool
from .notify import push

@tool("whatsapp_send_text", "WhatsApp Cloud API se text bhejo (number international, bina +). 24h customer-window ya approved template chahiye. Approval lazmi.",
      {"to": {"type": "string"}, "text": {"type": "string"}}, sensitive=True)
def whatsapp_send_text(to, text):
    r = requests.post(f"https://graph.facebook.com/v20.0/{os.getenv('WA_PHONE_ID')}/messages",
        headers={"Authorization": f"Bearer {os.getenv('WA_TOKEN')}"},
        json={"messaging_product": "whatsapp", "to": to, "type": "text", "text": {"body": text}}, timeout=20)
    return r.text

def handle_inbound(data: dict):
    """Webhook se aaya message -> owner ko notification."""
    try:
        for e in data["entry"]:
            for c in e["changes"]:
                for m in c["value"].get("messages", []):
                    body = m.get("text", {}).get("body", f"<{m['type']}>")
                    push("Client ka reply", f"{m['from']}: {body}")
    except Exception as ex:
        print("webhook parse:", ex)
