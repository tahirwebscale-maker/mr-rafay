import os, json
from fastapi import FastAPI, Header, HTTPException, Request, Response, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from rafay import config
from rafay.brain import ask
from rafay.registry import approve, PENDING
from rafay.tools.whatsapp import handle_inbound
from rafay.tools.notify import push

app = FastAPI(title="Mr. Rafay")
app.mount("/demo", StaticFiles(directory=config.SITES_DIR, html=True), name="demo")

def auth(authorization: str):
    if not config.TOKEN or authorization != f"Bearer {config.TOKEN}":
        raise HTTPException(401, "bad token")

class Q(BaseModel):
    text: str

@app.get("/health")
def health(): return {"ok": True}

@app.post("/ask")
def ask_ep(q: Q, authorization: str = Header("")):
    auth(authorization)
    reply, _ = ask(q.text)
    return {"reply": reply}

@app.post("/approve/{pid}")
def approve_ep(pid: str, authorization: str = Header("")):
    auth(authorization)
    if pid not in PENDING: raise HTTPException(404, "no such id")
    out = approve(pid); push("Mr. Rafay", f"Approved task done: {str(out)[:150]}")
    return {"result": str(out)}

@app.get("/webhook/whatsapp")
def wa_verify(request: Request):
    p = request.query_params
    if p.get("hub.verify_token") == os.getenv("WA_VERIFY_TOKEN"):
        return Response(p.get("hub.challenge"), media_type="text/plain")
    raise HTTPException(403)

@app.post("/webhook/whatsapp")
async def wa_inbound(request: Request):
    handle_inbound(await request.json()); return {"ok": True}

from rafay.tools.meta import handle_inbound as meta_inbound, verify_signature

@app.get("/webhook/meta")
def meta_verify(request: Request):
    p = request.query_params
    if p.get("hub.verify_token") == os.getenv("META_VERIFY_TOKEN"):
        return Response(p.get("hub.challenge"), media_type="text/plain")
    raise HTTPException(403)

@app.post("/webhook/meta")
async def meta_in(request: Request, bg: BackgroundTasks):
    raw = await request.body()
    if not verify_signature(raw, request.headers.get("x-hub-signature-256", "")):
        raise HTTPException(403)
    bg.add_task(meta_inbound, json.loads(raw))
    return {"ok": True}
@app.post("/api/chat")
def chat(q: Q, authorization: str = Header("")):
    """Text chat route: {"text": "..."} -> {"reply": "..."}"""
    return command(q, authorization)
