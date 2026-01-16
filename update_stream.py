import requests
import re

def get_real_link():
    url = "https://www.echoroukonline.com/live-news"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    }
    try:
        response = requests.get(url, headers=headers, timeout=15)
        # البحث عن الرابط الذي ينتهي بـ m3u8 ويحتوي على التوكن الإجباري لعام 2026
        match = re.search(r'(https://[^"]+?\.m3u8[^"]*)', response.text)
        if match:
            return match.group(1).replace('\\/', '/')
    except:
        pass
    return "https://shls-echorouk-news.v7.vcloud.dz/echorouk_news/index.m3u8"

real_url = get_real_link()

with open("playlist.m3u", "w", encoding="utf-8") as f:
    f.write("#EXTM3U\n")
    f.write("#EXTINF:-1, Echorouk News HD 2026\n")
    # إضافة سطر الحماية ليتجاوز نظام المنع في التطبيقات
    f.write(f"{real_url}|User-Agent=Mozilla/5.0&Referer=https://www.echoroukonline.com/\n")
