#!/data/data/com.termux/files/usr/bin/bash
pkg update -y && pkg install -y python git termux-api android-tools
termux-setup-storage
pip install anthropic python-dotenv requests fastapi uvicorn
echo "Ab: cp .env.example .env  -> keys bharo -> ADB pairing (README step 4)"
