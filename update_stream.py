import requests
import re

def get_live_url():
    # الرابط الذي أكدت وجود البث فيه
    target = "https://www.echoroukonline.com/live-news"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'https://www.echoroukonline.com/'
    }
    
    try:
        response = requests.get(target, headers=headers, timeout=15)
        # محاولة اقتناص الرابط حتى لو كان خلف جافا سكريبت بسيط
        match = re.search(r'(https?://[^\s"\'<>]+?\.m3u8)', response.text)
        if match:
            return match.group(1)
        # رابط احتياطي (Guess) في حال فشل الاقتناص اللحظي
        return "https://live.dzsecurity.net/live/echorouknews/playlist.m3u8"
    except:
        return "https://live.dzsecurity.net/live/echorouknews/playlist.m3u8"

url = get_live_url()
with open("playlist.m3u", "w", encoding="utf-8") as f:
    f.write("#EXTM3U\n")
    f.write("#EXTINF:-1, Echorouk News\n")
    # إضافة الرؤوس التي تجعل IPTV Smarters يعمل
    f.write(f"{url}|Referer=https://www.echoroukonline.com/&User-Agent=Mozilla/5.0\n")
