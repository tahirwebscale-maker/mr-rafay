"""Facebook Messenger + Instagram DM - OFFICIAL Meta Graph API.
Fully autonomous: jo log aap ke Page/IG ko message karte hain (ads, bio link, comments se)
unhein ye bot khud, bina kisi manual step ke, jawab deta hai. 24h window ke andar followups bhi.
Security: inbound text untrusted hai, isliye auto-reply ke paas phone/PC tools NAHI hote."""
import os, hmac, hashlib, requests
import anthropic
from .. import config
from ..registry import tool
from .notify import push

GRAPH = "https://graph.facebook.com/v20.0"
client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
CONV = {}   # sender_id -> history (memory me; restart par reset)
STOP = {"stop", "unsubscribe", "cancel", "no thanks", "إلغاء", "ايقاف", "إيقاف"}

BIZ_PROMPT = os.getenv("META_BIZ_PROMPT") or (
    "You are the friendly sales assistant of a web-design & digital-marketing studio. "
    "Reply in the SAME language as the customer (English or Arabic). Be short (max 4 sentences). "
    "Answer questions about demo websites, pricing ranges and next steps, and offer to book a call. "
    "Never invent prices or guarantees; if unsure, say the owner will follow up. "
    "If the customer says stop/unsubscribe, confirm politely and stop selling.")

def verify_signature(raw: bytes, header: str) -> bool:
    secret = os.getenv("META_APP_SECRET", "")
    if not secret: return False
    exp = "sha256=" + hmac.new(secret.encode(), raw, hashlib.sha256).hexdigest()
    return hmac.compare_digest(exp, header or "")

def _send(recipient_id, text):
    # Instagram DMs bhi Page token + /me/messages se jate hain (IG account Page se linked ho).
    r = requests.post(f"{GRAPH}/me/messages", params={"access_token": os.getenv("META_PAGE_TOKEN")},
        json={"recipient": {"id": recipient_id}, "messaging_type": "RESPONSE",
              "message": {"text": text[:1900]}}, timeout=20)
    return r.text

def auto_reply(platform, sender, text):
    if text.strip().lower() in STOP:
        _send(sender, "Understood - you won't receive further messages. / تم، لن نرسل لك رسائل أخرى.")
        push("Opt-out", f"{platform} {sender} ne stop kaha"); return
    hist = CONV.setdefault(sender, [])
    hist.append({"role": "user", "content": text})
    r = client.messages.create(model=config.MODEL, max_tokens=500, system=BIZ_PROMPT, messages=hist[-11:])
    out = "".join(b.text for b in r.content if b.type == "text") or "Thanks! We'll get back to you shortly."
    hist.append({"role": "assistant", "content": out})
    _send(sender, out)
    push(f"{platform} client reply", f"{sender}: {text[:120]}\nRafay: {out[:120]}")

def handle_inbound(data: dict):
    platform = "instagram" if data.get("object") == "instagram" else "messenger"
    for e in data.get("entry", []):
        for m in e.get("messaging", []):
            msg = m.get("message")
            if not msg or msg.get("is_echo"): continue
            if msg.get("text"):
                try: auto_reply(platform, m["sender"]["id"], msg["text"])
                except Exception as ex: push("Meta auto-reply error", str(ex)[:200])
            else:
                push(f"{platform} media/attachment", f"{m['sender']['id']} ne attachment bheja")

@tool("meta_send_message", "Messenger/Instagram par us user ko message bhejo jis ne pichle 24h me aap ko message kiya (official API).",
      {"recipient_id": {"type": "string"}, "text": {"type": "string"}}, sensitive=True)
def meta_send_message(recipient_id, text): return _send(recipient_id, text)
