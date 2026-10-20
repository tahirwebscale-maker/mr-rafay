# Mr. Rafay - Personal Automation Agent

## Folder structure
```
mr_rafay/
├── rafay/
│   ├── config.py        # .env settings
│   ├── registry.py      # tools + approval gate (delete/send/call par permission)
│   ├── brain.py         # Claude tool-use loop (dimaag)
│   └── tools/
│       ├── android.py   # Termux:API + ADB (camera, SMS, call, music, apps, screenshot, tap)
│       ├── pc.py        # PC control (app open, screenshot, type)
│       ├── notify.py    # ntfy.sh push notifications (free)
│       ├── sitegen.py   # client ke liye HTML/CSS 3D landing page
│       ├── outreach.py  # Google Places leads, email (unsubscribe + limit), DM drafts
│       └── whatsapp.py  # WhatsApp Business Cloud API + client reply alerts
├── voice/listener.py    # "Mr. Rafay" wake word (phone + PC)
├── server.py            # FastAPI cloud backend (Render/Replit)
├── cli.py               # terminal chat
├── termux/setup.sh, boot_start.sh
├── render.yaml, requirements.txt, .env.example
```

## Architecture (2 hisse)
- **Phone (Termux)**: voice, camera, SMS, calls, music, apps, screenshot. Ye sab sirf phone par chal sakta hai.
- **Cloud (Render)**: sitegen, email outreach, WhatsApp webhook, notifications. 24/7 online.
Dono ek hi codebase hain; `IS_TERMUX` se khud decide hota hai kaunse tools load hon.

## Step-by-step: Phone
1. F-Droid se install karo: **Termux**, **Termux:API**, **Termux:Boot**. (Play Store wale Termux purane hain.)
2. Termux me: `pkg install git` phir project copy karo `~/mr_rafay` me, phir `bash termux/setup.sh`
3. `cp .env.example .env` aur keys bharo. Phone par **ntfy** app install karo, wahi topic subscribe karo jo `.env` me hai.
4. **ADB self-connect** (tap, screenshot, app launch ke liye):
   - Settings > About phone > Build number 7 baar tap > Developer options > **Wireless debugging** ON (WiFi zaroori)
   - "Pair device with pairing code" dabao. Termux me: `adb pair localhost:PAIRPORT` (code dalo)
   - Phir `adb connect localhost:PORT` (wireless debugging screen wala port). `.env` me `ADB_ADDR=localhost:PORT` likho.
   - Note: WiFi band ho to dobara connect karna parta hai.
5. Termux:API ko Android settings me camera, mic, SMS, phone, storage permissions do. Battery optimization "Unrestricted" karo.
6. Test: `python cli.py` -> "battery batao", "YouTube par nasheed search karo"
7. Voice: `python voice/listener.py`. Auto-start ke liye `cp termux/boot_start.sh ~/.termux/boot/`

## Step-by-step: Cloud (Render free)
1. Code GitHub (private repo) par daalo. `.env` kabhi push na karo.
2. render.com > New > Blueprint (render.yaml) ya Web Service: start command `uvicorn server:app --host 0.0.0.0 --port $PORT`
3. Environment variables dalo (.env wali). `APPROVAL_MODE=queue`, `SERVER_URL=https://<app>.onrender.com`
4. Free plan 15 min idle par so jata hai: uptimerobot.com se `/health` har 5 min ping karo.
   Render free disk **ephemeral** hai - leads/sites restart par ud sakti hain (stable ke liye paid disk ya DB).
5. WhatsApp: Meta for Developers > WhatsApp Cloud API > webhook URL `https://<app>.onrender.com/webhook/whatsapp`, verify token = `WA_VERIFY_TOKEN`. Client reply aate hi phone par notification aayegi.
6. Cloud approval: sensitive kaam ki notification me ID aati hai. `curl -X POST -H "Authorization: Bearer $RAFAY_TOKEN" https://<app>/approve/<ID>`

## Misal commands
- "Mr. Rafay, Karachi ke 5 dentists dhoondo aur har ke liye demo site banao"
- "Mr. Rafay, Downloads ki latest file delete karo" (approval dialog aayega)
- "Mr. Rafay, front camera se photo lo"

## Zaroori limitations (sach)
- **Screen off + hamesha sunna**: Android 10+ background mic restrict karta hai. `termux-speech-to-text` Google ka dialog use karta hai aur screen off par aksar nahi chalta. Behtar tareeqa: Google Assistant Routine / Tasker / HTTP Shortcuts se custom phrase "Mr. Rafay" ko `curl SERVER_URL/ask` ya Termux script se jodo.
- **Play Store install**: Android silent install allow nahi karta. Agent page kholta hai aur ADB se Install tap try karta hai.
- **Facebook/Instagram**: scraping aur auto mass-DM Meta ToS ke khilaf hai (account ban). Isliye sirf DM *draft* banta hai, aap manually bhejte hain. Inbound/opted-in chats ke liye official WhatsApp Cloud API hai.
- **Email**: har mail me sender address + unsubscribe, daily limit, duplicate/suppression check. Sirf public business email par bhejein; PECR/GDPR/CAN-SPAM ka khayal rakhein.
- **"100% autonomous"**: delete/send/call/install jaisi cheezon par approval jaan-boojh kar rakhi hai. `APPROVAL_MODE=off` na karein - AI ghalti kar sakta hai.
- Public demo sites par real client ke naam se fake reviews na lagayein (template me DEMO label hai).

---
# UPDATE v2

## Autonomous mode (koi approval nahi)
`.env` me `APPROVAL_MODE=off` (ab default hai) = delete/SMS/call/send bina poochhe chalte hain.
`DELETE_ANYWHERE=1` = poore shared storage me delete allowed. Ye aap ka phone hai, aap ki marzi - lekin AI ghalti kar sakta hai,
to backup rakhein. render.yaml me cloud ke liye `queue` rakha hai; wahan bhi `off` kar sakte hain.

## Multi-country (UK / US / CA / SA / AE)
`rafay/locales.py` me har market ki zaban, currency, timezone aur email footer hai. Saudi/UAE ke liye English + Arabic (RTL) pages.
Agent ko bolein: "Dubai ke 5 gyms dhoondo, Arabic+English demo site banao". `country` parameter khud use hota hai.

## Facebook / Instagram - fully automatic (official API)
`rafay/tools/meta.py` + `/webhook/meta`: jo bhi aap ke Page / IG Business account ko DM karta hai, bot bina manual step ke
khud jawab deta hai (English/Arabic, user ki zaban me), conversation yaad rakhta hai, STOP likhne par band, aur aap ko notification.
Setup: Meta for Developers > App > Messenger + Instagram products > webhook `https://<app>/webhook/meta`
(verify token = META_VERIFY_TOKEN, fields: messages) > Page access token `META_PAGE_TOKEN`, App Secret `META_APP_SECRET`. IG Business ko Facebook Page se link karein.
Naye logon tak pahunchne ka sahi tareeqa: **Click-to-Message ads** (Meta Ads Manager) UK/US/CA/SA/AE ke target audience par - click karte hi DM khulta hai aur bot jawab de deta hai.
Cold DM / scraping ka code isme nahi hai.
