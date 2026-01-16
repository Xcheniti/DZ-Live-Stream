import requests
import re

def get_live_url():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'https://www.echoroukonline.com/'
    }
    try:
        # الاتصال بالرابط الذي أرسلته لجلب التوكن الجديد
        response = requests.get("https://www.echoroukonline.com/live-news", headers=headers, timeout=15)
        # البحث عن روابط m3u8 التي تحتوي على توكنات حماية 2026
        matches = re.findall(r'(https?://[^\s"\'<>]+?\.m3u8[^\s"\'<>]*?)', response.text)
        for link in matches:
            if "echorouk" in link.lower():
                return link
    except:
        pass
    # رابط احتياطي رسمي في حال فشل القنص
    return "https://shls-echorouk-news.v7.vcloud.dz/echorouk_news/index.m3u8"

live_link = get_live_url()

with open("playlist.m3u", "w", encoding="utf-8") as f:
    f.write("#EXTM3U\n")
    f.write("#EXTINF:-1, Echorouk News HD [Live 2026]\n")
    # إضافة User-Agent للرابط لضمان عمله في IPTV Smarters و Televizo
    f.write(f"{live_link}|User-Agent=Mozilla/5.0\n")
