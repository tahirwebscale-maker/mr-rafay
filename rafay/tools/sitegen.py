import re, os
import anthropic
from .. import config
from ..locales import market
from ..registry import tool

client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)

PROMPT = """Write a single-file HTML landing page (inline CSS + small inline JS, no external libraries).
Business: {name} | Niche: {niche} | City: {city} | Country: {country} | Details: {notes}
Language: {lang}. Currency for any prices: {currency}. Text direction for Arabic parts: RTL (add a language toggle if bilingual).
Requirements: responsive, subtle CSS 3D effect in the hero (transform/perspective), services section,
3 testimonial placeholders clearly labelled 'DEMO' (never pose as real reviews), contact/CTA button,
footer note 'Demo design'. Output HTML only, no markdown fences."""

@tool("generate_site", "Client ke liye demo landing page banao (country ke hisab se zaban/currency) aur demo link do.",
      {"business_name": {"type": "string"}, "niche": {"type": "string"}, "city": {"type": "string"},
       "country": {"type": "string", "enum": ["UK", "US", "CA", "SA", "AE"]}, "notes": {"type": "string"}},
      required=["business_name", "niche"])
def generate_site(business_name, niche, city="", country="US", notes=""):
    m = market(country)
    r = client.messages.create(model=config.MODEL, max_tokens=6000, messages=[{"role": "user", "content": PROMPT.format(
        name=business_name, niche=niche, city=city, country=m["name"], notes=notes,
        lang=m["lang"], currency=m["currency"])}])
    html = "".join(b.text for b in r.content if b.type == "text").strip()
    html = re.sub(r"^```(?:html)?\s*|\s*```$", "", html)
    slug = re.sub(r"[^a-z0-9]+", "-", business_name.lower()).strip("-")[:40] or "demo"
    d = os.path.join(config.SITES_DIR, slug); os.makedirs(d, exist_ok=True)
    open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(html)
    base = (config.SERVER_URL or "http://localhost:8000").rstrip("/")
    return f"{base}/demo/{slug}/"
