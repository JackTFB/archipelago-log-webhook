import os
import json
from datetime import datetime
import requests
import time

WEBHOOK_URL = os.environ["DISCORD_WEBHOOK_URL"]
LOG_URL = "https://archipelago.gg/room/mFEH6skzTma_51-Rbe-TUA"
CACHE_FILE = "cache.json"

if os.path.exists(CACHE_FILE):
    try:
        with open(CACHE_FILE, "r") as f:
            data = json.load(f)
            last_timestamp = data.get("last_timestamp")
    except Exception:
        last_timestamp = None

else:
    last_timestamp = None
    with open(CACHE_FILE, "w") as f:
        json.dump({"last_timestamp": None}, f)

def parse_timestamp(line):
    import re
    match = re.match(r"\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\]", line)
    if match:
        return datetime.strptime(match.group(1), "%Y-%m-%d %H:%M:%S")
    return None

def format_line(line):
    lower = line.lower()
    if "joined" in lower:
        return f"✅ Player joined: {line}"
    if "left" in lower:
        return f"❌ Player left: {line}"
    return f"📝 {line}"

def post_to_discord(line):
    payload = {"content": format_line(line)}
    response = requests.post(WEBHOOK_URL, json=payload)
    response.raise_for_status()

def main():
    global last_timestamp
    try:
        r = requests.get(LOG_URL)
        r.raise_for_status()
        lines = [l.strip() for l in r.text.splitlines() if l.strip()]
        new_last = last_timestamp

        for line in lines:
            ts = parse_timestamp(line)
            if not ts:
                continue
            if last_timestamp is None or ts > datetime.fromisoformat(last_timestamp):
                post_to_discord(line)
                new_last = ts.fromisoformat()

    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    main()