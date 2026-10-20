"""Android control: Termux:API + wireless ADB (self-connect). Setup README me hai."""
import os, shutil, subprocess, time, shlex
from urllib.parse import quote
from ..registry import tool

HOME = os.path.expanduser("~")
SHARED = os.path.join(HOME, "storage", "shared")
SAFE_DELETE_ROOTS = [os.path.join(SHARED, d) for d in ("Download", "DCIM", "Pictures", "Movies", "Music")]
ADB_ADDR = os.getenv("ADB_ADDR", "localhost:5555")

def sh(cmd, timeout=30):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
    return (r.stdout + r.stderr).strip() or "ok"

def adb(cmd): return sh(f"adb -s {ADB_ADDR} shell {cmd}")

@tool("speak", "Phone speaker par bolo (TTS).", {"text": {"type": "string"}})
def speak(text): return sh(f"termux-tts-speak {shlex.quote(text)}")

@tool("open_app", "Android app kholo package name se (com.whatsapp, com.google.android.youtube, com.instagram.android, com.facebook.katana, com.android.chrome).",
      {"package": {"type": "string"}})
def open_app(package): return adb(f"monkey -p {shlex.quote(package)} -c android.intent.category.LAUNCHER 1")

@tool("open_url", "Browser/Google me link kholo.", {"url": {"type": "string"}})
def open_url(url): return sh(f"termux-open-url {shlex.quote(url)}")

@tool("youtube_search", "YouTube par search kholo.", {"query": {"type": "string"}})
def youtube_search(query):
    return sh(f"termux-open-url {shlex.quote('https://www.youtube.com/results?search_query=' + quote(query))}")

@tool("take_photo", "Camera se photo kheencho. camera 0=back, 1=front.",
      {"camera": {"type": "integer"}}, required=[])
def take_photo(camera=0):
    path = os.path.join(SHARED, "DCIM", f"rafay_{int(time.time())}.jpg")
    sh(f"termux-camera-photo -c {camera} {shlex.quote(path)}", 40); return path

@tool("screenshot", "Screenshot lo.", {})
def screenshot():
    path = f"/sdcard/Pictures/rafay_shot_{int(time.time())}.png"
    adb(f"screencap -p {path}"); return path

@tool("list_files", "Folder ki files dikhao (storage/shared ke andar).", {"subpath": {"type": "string"}})
def list_files(subpath):
    p = os.path.normpath(os.path.join(SHARED, subpath.lstrip("/")))
    if not p.startswith(SHARED): return "Allowed nahi"
    return "\n".join(sorted(os.listdir(p))[:200])

@tool("latest_gallery_files", "Gallery ki sab se nayi N photos/videos ke path.", {"n": {"type": "integer"}}, required=[])
def latest_gallery_files(n=5):
    files = [os.path.join(r, f) for r, _, fs in os.walk(os.path.join(SHARED, "DCIM")) for f in fs]
    files.sort(key=os.path.getmtime, reverse=True)
    return "\n".join(files[:n])

@tool("delete_path", "File/folder delete karo (sirf Download, DCIM, Pictures, Movies, Music ke andar). Approval lazmi.",
      {"path": {"type": "string"}}, sensitive=True)
def delete_path(path):
    p = os.path.realpath(path)
    if os.getenv("DELETE_ANYWHERE") == "1":
        ok = p.startswith(os.path.realpath(SHARED) + os.sep)   # poora shared storage
    else:
        ok = any(p.startswith(os.path.realpath(r) + os.sep) for r in SAFE_DELETE_ROOTS)
    if not ok:
        return "Is path par delete allowed nahi (DELETE_ANYWHERE=1 se shared storage khulta hai)."
    shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)
    return f"deleted {p}"

@tool("play_music", "Audio file play karo.", {"path": {"type": "string"}})
def play_music(path): return sh(f"termux-media-player play {shlex.quote(path)}")

@tool("music_control", "Music control: pause, play(resume), stop, info.",
      {"action": {"type": "string", "enum": ["pause", "play", "stop", "info"]}})
def music_control(action): return sh(f"termux-media-player {shlex.quote(action)}")

@tool("set_volume", "Music volume 0-15.", {"level": {"type": "integer"}})
def set_volume(level): return sh(f"termux-volume music {int(level)}")

@tool("battery", "Battery status.", {})
def battery(): return sh("termux-battery-status")

@tool("send_sms", "Local SMS bhejo. Approval lazmi.", {"number": {"type": "string"}, "text": {"type": "string"}}, sensitive=True)
def send_sms(number, text): return sh(f"termux-sms-send -n {shlex.quote(number)} {shlex.quote(text)}")

@tool("make_call", "Call milao. Approval lazmi.", {"number": {"type": "string"}}, sensitive=True)
def make_call(number): return sh(f"termux-telephony-call {shlex.quote(number)}")

@tool("whatsapp_open_chat", "WhatsApp chat khol kar message pre-fill karo (international number bina +). Approval lazmi; Send button ADB tap se ya khud dabana hoga.",
      {"number": {"type": "string"}, "text": {"type": "string"}}, sensitive=True)
def whatsapp_open_chat(number, text):
    return sh(f"termux-open-url {shlex.quote(f'https://wa.me/{number}?text=' + quote(text))}")

@tool("playstore_install", "Play Store app page kholo (package name). Android silent install allow nahi karta; install button par tap lagta hai. Approval lazmi.",
      {"package": {"type": "string"}}, sensitive=True)
def playstore_install(package):
    adb(f"am start -a android.intent.action.VIEW -d market://details?id={shlex.quote(package)}")
    return "Play Store page khul gaya. Ab ui_dump se Install button dhoondo aur ui_tap karo."

@tool("ui_tap", "Screen par x,y tap (ADB).", {"x": {"type": "integer"}, "y": {"type": "integer"}})
def ui_tap(x, y): return adb(f"input tap {int(x)} {int(y)}")

@tool("ui_type", "Focused field me text likho (ADB).", {"text": {"type": "string"}})
def ui_type(text): return adb(f"input text {shlex.quote(text.replace(' ', '%s'))}")

@tool("ui_key", "Key press: HOME, BACK, ENTER, POWER, VOLUME_UP...", {"key": {"type": "string"}})
def ui_key(key): return adb(f"input keyevent KEYCODE_{shlex.quote(key.upper())}")

@tool("ui_dump", "Screen ke buttons/text ka XML dump (tap coordinates dhoondne ke liye).", {})
def ui_dump():
    adb("uiautomator dump /sdcard/ui.xml"); return adb("cat /sdcard/ui.xml")[:5000]
