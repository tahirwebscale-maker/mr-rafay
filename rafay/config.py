import os
from dotenv import load_dotenv
load_dotenv()

def env(k, d=""): return os.getenv(k, d)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ANTHROPIC_API_KEY = env("ANTHROPIC_API_KEY")
MODEL = env("RAFAY_MODEL", "claude-sonnet-5-5")
TOKEN = env("RAFAY_TOKEN")
NTFY_TOPIC = env("NTFY_TOPIC", "mr-rafay-change-me")
APPROVAL_MODE = env("APPROVAL_MODE", "termux")
SERVER_URL = env("SERVER_URL")
IS_TERMUX = os.path.exists("/data/data/com.termux")
DATA_DIR = os.path.join(ROOT, "data")
SITES_DIR = os.path.join(ROOT, "sites")
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(SITES_DIR, exist_ok=True)
