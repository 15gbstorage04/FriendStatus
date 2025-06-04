import time
import requests
from urllib.parse import quote

API_KEY = "701392e4-5c85-460f-95b2-835dc0ff7648"
WEBHOOK_URL = "https://discord.com/api/webhooks/1379820652772724848/TmxUw2tEp_u8b8r2M6ZzpALV593T6ezZFaYUwbpIQxV-StEvg5j4M3q8393OF5EPCmD-"

GAMERTAGS = ["lyf qpdgodysydu", "NazmulHasaNil"]

headers = {"X-Authorization": API_KEY}

# বন্ধুর Gamertag -> XUID মেপ
def get_xuid(gamertag):
    encoded_gt = quote(gamertag)
    url = f"https://xbl.io/api/v2/friends/search?gt={encoded_gt}"
    res = requests.get(url, headers=headers)
    try:
        data = res.json()
        if 'profileUsers' in data and len(data['profileUsers']) > 0:
            return data['profileUsers'][0]['id']
    except:
        pass
    return None

# XUID দিয়ে Presence পাওয়া
def get_presence(xuid):
    url = f"https://xbl.io/api/v2/users/{xuid}/presence"
    res = requests.get(url, headers=headers)
    try:
        data = res.json()
        if res.status_code == 200:
            presence = data.get("presence", {})
            state = presence.get("state", "Offline")  # Online/Offline ইত্যাদি
            title = presence.get("titleName", "")
            return state, title
    except:
        pass
    return "Offline", ""

# Discord-এ মেসেজ পাঠানোর ফাংশন
def send_to_discord(msg):
    try:
        requests.post(WEBHOOK_URL, json={"content": msg})
    except Exception as e:
        print(f"Discord message error: {e}")

# বন্ধুদের XUID সংগ্রহ
xuid_map = {}
for tag in GAMERTAGS:
    xuid = get_xuid(tag)
    if xuid:
        xuid_map[tag] = xuid
    else:
        print(f"XUID পাওয়া যায়নি: {tag}")

# Tracker state রাখবে: online কি offline
tracking = {tag: False for tag in xuid_map.keys()}  # False = offline, True = online

while True:
    for tag, xuid in xuid_map.items():
        state, game = get_presence(xuid)
        
        if tracking[tag] == False:
            # এখন offline থেকে check করছো, online হলে মেসেজ দিবে আর tracking True করবে
            if state.lower() == "online" and game.lower().startswith("minecraft"):
                send_to_discord(f"🎮 **{tag}** এখন Minecraft খেলছে!")
                tracking[tag] = True  # এখন থেকে ট্র্যাক করবে যতক্ষণ না offline হয়
        else:
            # এখন online থেকে check করছো, offline হলে মেসেজ দিবে আর tracking False করবে
            if state.lower() == "offline" or not game.lower().startswith("minecraft"):
                send_to_discord(f"👋 **{tag}** Minecraft থেকে বের হয়ে গেছে।")
                tracking[tag] = False  # আবার offline এ ফিরে গেল
                
        # এখানে চাইলে প্রতি সেকেন্ড/মিনিট স্লিপ দিতে পারো
    time.sleep(60)
