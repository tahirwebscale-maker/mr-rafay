"""Tool registry + approval gate.
Sensitive tools (delete, send, call, install) bina approval ke nahi chalte."""
import json, subprocess, uuid
from . import config

TOOLS, SCHEMAS = {}, []
PENDING = {}  # id -> (name, args)

def tool(name, description, props, required=None, sensitive=False):
    def deco(fn):
        TOOLS[name] = (fn, sensitive)
        SCHEMAS.append({
            "name": name, "description": description,
            "input_schema": {"type": "object", "properties": props,
                             "required": list(props.keys()) if required is None else required},
        })
        return fn
    return deco

def _confirm(name, args) -> bool:
    mode = config.APPROVAL_MODE
    if mode == "off":
        return True
    text = f"{name}: {json.dumps(args, ensure_ascii=False)[:300]}"
    if mode == "cli":
        return input(f"\n[APPROVAL] {text}\nChalaun? (y/n): ").strip().lower() == "y"
    if mode == "termux":
        r = subprocess.run(["termux-dialog", "confirm", "-t", "Mr. Rafay approval",
                            "-i", text], capture_output=True, text=True)
        return '"text": "yes"' in r.stdout
    return False

def run_tool(name, args):
    if name not in TOOLS:
        return f"Unknown tool: {name}"
    fn, sensitive = TOOLS[name]
    try:
        if sensitive and config.APPROVAL_MODE == "queue":
            pid = uuid.uuid4().hex[:8]
            PENDING[pid] = (name, args)
            from .tools.notify import push
            push("Approval chahiye", f"{name} {json.dumps(args, ensure_ascii=False)[:200]}\nID: {pid}")
            return f"PENDING_APPROVAL id={pid}. Owner ke approve karne ka intezar hai."
        if sensitive and not _confirm(name, args):
            return "Owner ne mana kar diya (approval denied)."
        return fn(**args)
    except Exception as e:
        return f"Error in {name}: {e}"

def approve(pid):
    name, args = PENDING.pop(pid)
    fn, _ = TOOLS[name]
    return fn(**args)
