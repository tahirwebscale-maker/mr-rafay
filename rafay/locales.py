"""Target markets: UK, US, CA, SA (Saudi), AE (UAE/Dubai). Zaban, currency, compliance footer."""
EN_FOOT = "If you'd rather not receive further emails, just reply 'UNSUBSCRIBE' and you won't hear from us again."
AR_FOOT = "\nإذا لم ترغب في تلقي رسائل أخرى، يرجى الرد بكلمة «إلغاء الاشتراك»."

MARKETS = {
    "UK": {"name": "United Kingdom", "lang": "English (British spelling)", "currency": "GBP (£)", "dir": "ltr",
           "tz": "Europe/London", "cc": "44", "footer": EN_FOOT,
           "law": "PECR/UK GDPR: limited companies ko B2B email ok, sole traders ko consent chahiye; sender identity + opt-out lazmi."},
    "US": {"name": "United States", "lang": "English (American spelling)", "currency": "USD ($)", "dir": "ltr",
           "tz": "America/New_York", "cc": "1", "footer": EN_FOOT,
           "law": "CAN-SPAM: sahi subject, physical address, opt-out 10 din me honor."},
    "CA": {"name": "Canada", "lang": "English (Canadian spelling)", "currency": "CAD ($)", "dir": "ltr",
           "tz": "America/Toronto", "cc": "1", "footer": EN_FOOT,
           "law": "CASL bohat sakht: consent (express/implied), sender identification, mailing address, working unsubscribe; jurmane bare."},
    "SA": {"name": "Saudi Arabia", "lang": "Arabic + English (bilingual, Arabic RTL)", "currency": "SAR (ر.س)", "dir": "rtl",
           "tz": "Asia/Riyadh", "cc": "966", "footer": EN_FOOT + AR_FOOT,
           "law": "PDPL + spam rules: consent aur opt-out; Arabic content behtar convert karta hai."},
    "AE": {"name": "UAE / Dubai", "lang": "English + Arabic (bilingual)", "currency": "AED (د.إ)", "dir": "ltr",
           "tz": "Asia/Dubai", "cc": "971", "footer": EN_FOOT + AR_FOOT,
           "law": "UAE PDPL + TDRA anti-spam: consent aur opt-out lazmi."},
}

def market(code):
    return MARKETS.get((code or "US").upper(), MARKETS["US"])
