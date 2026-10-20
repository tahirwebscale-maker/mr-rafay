import os, subprocess, sys, time
from ..registry import tool

@tool("pc_open_app", "PC par app/file/URL kholo.", {"target": {"type": "string"}})
def pc_open_app(target):
    if sys.platform.startswith("win"): os.startfile(target)
    elif sys.platform == "darwin": subprocess.Popen(["open", target])
    else: subprocess.Popen(["xdg-open", target])
    return "opened"

@tool("pc_screenshot", "PC screenshot.", {})
def pc_screenshot():
    import pyautogui
    p = os.path.expanduser(f"~/rafay_{int(time.time())}.png")
    pyautogui.screenshot(p); return p

@tool("pc_type", "PC par text type karo.", {"text": {"type": "string"}})
def pc_type(text):
    import pyautogui; pyautogui.write(text, interval=0.02); return "typed"
