import anthropic
from . import config
from .registry import SCHEMAS, run_tool
from . import tools  # noqa: tools register ho jate hain

SYSTEM = """Tum "Mr. Rafay" ho - owner ka personal automation agent.
Owner se asaan Roman Urdu/Hindi mix me chhota jawab do.
Owner ke clients UK, USA, Canada, Saudi Arabia aur UAE/Dubai me hain: client-facing text (email, site, messages)
us market ki zaban me likho (English; Saudi/UAE ke liye English + Arabic) aur country parameter dena na bhoolo.
Tools ko step-by-step use karo. Kaam khatam ho to notify_owner call karo.
Facebook/Instagram: sirf official Meta API (meta_send_message) aur inbound auto-reply; cold DM/scraping ke tools nahi hain.
Email me hamesha unsubscribe line rehti hai."""

client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)

def ask(user_text, history=None, max_steps=15):
    messages = list(history or []) + [{"role": "user", "content": user_text}]
    for _ in range(max_steps):
        r = client.messages.create(model=config.MODEL, max_tokens=2000,
                                   system=SYSTEM, tools=SCHEMAS, messages=messages)
        messages.append({"role": "assistant", "content": r.content})
        if r.stop_reason != "tool_use":
            return "".join(b.text for b in r.content if b.type == "text"), messages
        results = []
        for b in r.content:
            if b.type == "tool_use":
                results.append({"type": "tool_result", "tool_use_id": b.id,
                                "content": str(run_tool(b.name, b.input))[:6000]})
        messages.append({"role": "user", "content": results})
    return "Max steps poore ho gaye, kaam adhoora ho sakta hai.", messages
