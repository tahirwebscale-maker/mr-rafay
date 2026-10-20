#!/data/data/com.termux/files/usr/bin/bash
# Is file ko ~/.termux/boot/ me copy karo (Termux:Boot app chahiye)
termux-wake-lock
cd ~/mr_rafay
nohup python voice/listener.py > rafay.log 2>&1 &
