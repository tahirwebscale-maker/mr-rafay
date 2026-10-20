"""Terminal chat: python cli.py   (Termux ya PC)"""
from rafay.brain import ask
hist = []
print("Mr. Rafay hazir. 'exit' likh kar band karo.")
while True:
    t = input("\nAap: ").strip()
    if t.lower() in ("exit", "quit"): break
    reply, hist = ask(t, hist)
    hist = hist[-20:]
    print("Rafay:", reply)
