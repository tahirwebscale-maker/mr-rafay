"""Wake word listener: 'Mr. Rafay' / 'Rafay'.
Termux: python voice/listener.py        (termux-speech-to-text)
PC:     python voice/listener.py --pc   (SpeechRecognition + mic)"""
import re, subprocess, sys, os, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from rafay.brain import ask
from rafay import config

WAKE = re.compile(r"\b(?:mr\.?|mister|mistar)?\s*raf(?:ay|ai|ey)\b", re.I)

def say(t):
    if config.IS_TERMUX:
        subprocess.run(["termux-tts-speak", t])
    else:
        try:
            import pyttsx3; e = pyttsx3.init(); e.say(t); e.runAndWait()
        except Exception:
            print("Rafay:", t)

def listen_termux():
    r = subprocess.run(["termux-speech-to-text"], capture_output=True, text=True, timeout=40)
    return r.stdout.strip()

def listen_pc():
    import speech_recognition as sr
    r = sr.Recognizer()
    with sr.Microphone() as src:
        r.adjust_for_ambient_noise(src, 0.5)
        audio = r.listen(src, phrase_time_limit=8)
    try: return r.recognize_google(audio, language="en-IN")
    except Exception: return ""

def main():
    listen = listen_pc if "--pc" in sys.argv else listen_termux
    if config.IS_TERMUX: subprocess.run(["termux-wake-lock"])
    hist = []
    print("Listening... (wake word: Mr. Rafay)")
    while True:
        try: text = listen()
        except Exception: time.sleep(2); continue
        if not text or not WAKE.search(text): continue
        cmd = WAKE.sub("", text, count=1).strip(" ,.")
        if not cmd:
            say("Ji, boliye"); cmd = listen()
        reply, hist = ask(cmd, hist); hist = hist[-20:]
        say(reply[:400])

if __name__ == "__main__": main()
