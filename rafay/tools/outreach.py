"""Compliant outreach: leads Google Places API se, email sirf public business email par,
unsubscribe + daily cap + duplicate/suppression check. Social DMs sirf draft."""
import json, os, smtplib, ssl, time, requests
from email.message import EmailMessage
from .. import config
from ..registry import tool
from ..locales import market

LEADS = os.path.join(config.DATA_DIR, "leads.json")
SUPPRESS = os.path.join(config.DATA_DIR, "suppressed.txt")
SENT_LOG = os.path.join(config.DATA_DIR, "sent_log.json")

def _load(p, d):
    return json.load(open(p)) if os.path.exists(p) else d

@tool("find_leads", "Google Places API se business dhoondo (name, phone, website). niche e.g. 'dentist', city e.g. 'Karachi'.",
      {"niche": {"type": "string"}, "city": {"type": "string"}})
def find_leads(niche, city):
    key = os.getenv("GOOGLE_PLACES_KEY")
    if not key: return "GOOGLE_PLACES_KEY set karo"
    r = requests.post("https://places.googleapis.com/v1/places:searchText",
        headers={"X-Goog-Api-Key": key, "X-Goog-FieldMask":
                 "places.displayName,places.websiteUri,places.nationalPhoneNumber,places.googleMapsUri"},
        json={"textQuery": f"{niche} in {city}"}, timeout=20).json()
    out = [{"name": p["displayName"]["text"], "website": p.get("websiteUri", ""),
            "phone": p.get("nationalPhoneNumber", ""), "maps": p.get("googleMapsUri", ""),
            "niche": niche, "city": city, "email": ""} for p in r.get("places", [])]
    json.dump(_load(LEADS, []) + out, open(LEADS, "w"), indent=1)
    return json.dumps(out, ensure_ascii=False)[:5000]

@tool("add_lead_email", "Lead ka public business email save karo (jo unki website/Google profile par diya ho).",
      {"name": {"type": "string"}, "email": {"type": "string"}})
def add_lead_email(name, email):
    leads = _load(LEADS, [])
    for l in leads:
        if l["name"].lower() == name.lower(): l["email"] = email
    json.dump(leads, open(LEADS, "w"), indent=1); return "saved"

@tool("draft_dm", "Facebook/Instagram DM ka draft likho (owner khud manually bhejta hai).",
      {"business": {"type": "string"}, "demo_link": {"type": "string"}}, required=["business", "demo_link"])
def draft_dm(business, demo_link):
    return (f"[DRAFT - manually bhejo] Hi {business}! Maine aap ke liye ek free demo website banayi hai: "
            f"{demo_link} . Pasand aaye to reply kijiye. Interest na ho to bata dein, dobara message nahi karunga.")

@tool("send_outreach_email", "Business ko demo link ke sath email bhejo (approval lazmi, unsubscribe line auto, daily limit).",
      {"to": {"type": "string"}, "business": {"type": "string"}, "subject": {"type": "string"},
       "body": {"type": "string"}, "demo_link": {"type": "string"},
       "country": {"type": "string", "enum": ["UK", "US", "CA", "SA", "AE"]}},
      required=["to", "business", "subject", "body", "demo_link"], sensitive=True)
def send_outreach_email(to, business, subject, body, demo_link, country="US"):
    sup = open(SUPPRESS).read().split() if os.path.exists(SUPPRESS) else []
    if to.lower() in sup: return "Ye address unsubscribed hai - nahi bheja."
    log = _load(SENT_LOG, [])
    today = time.strftime("%Y-%m-%d")
    if sum(1 for x in log if x["date"] == today) >= int(os.getenv("DAILY_EMAIL_LIMIT", 20)):
        return "Daily limit poori."
    if any(x["to"] == to.lower() for x in log): return "Is ko pehle email ja chuki hai (duplicate roka)."
    footer = f"\n\n--\n{os.getenv('SENDER_NAME')} | {os.getenv('SENDER_ADDRESS')}\n{market(country)['footer']}"
    m = EmailMessage(); m["From"] = os.getenv("SMTP_USER"); m["To"] = to; m["Subject"] = subject
    m["List-Unsubscribe"] = f"<mailto:{os.getenv('SMTP_USER')}?subject=unsubscribe>"
    m.set_content(f"{body}\n\nDemo: {demo_link}{footer}")
    with smtplib.SMTP(os.getenv("SMTP_HOST"), int(os.getenv("SMTP_PORT", 587))) as s:
        s.starttls(context=ssl.create_default_context())
        s.login(os.getenv("SMTP_USER"), os.getenv("SMTP_PASS")); s.send_message(m)
    log.append({"to": to.lower(), "date": today, "business": business})
    json.dump(log, open(SENT_LOG, "w"))
    return "email bhej di"

@tool("unsubscribe", "Email ko hamesha ke liye suppression list me daalo.", {"email": {"type": "string"}})
def unsubscribe(email):
    open(SUPPRESS, "a").write(email.lower() + "\n"); return "suppressed"
