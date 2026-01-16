import requests
import re
import os
import json
from datetime import datetime

CONFIG = {
    'target_url': "https://www.ennaharonline.com/live/",
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'referer': 'https://www.ennaharonline.com/',
    'output_file': 'results/ennahar_live.m3u'
}

def sniper():
    os.makedirs('results', exist_ok=True)
    session = requests.Session()
    session.headers.update({'User-Agent': CONFIG['user_agent'], 'Referer': CONFIG['referer']})
    
    try:
        print("🔍 Searching for stream links...")
        response = session.get(CONFIG['target_url'], timeout=15)
        html_content = response.text

        # محاولة 1: البحث عن رابط dzsecurity (الذي وجدته أنت سابقا)
        match = re.search(r'(https?://[^\s"\']+dzsecurity\.net[^\s"\']+chunks\.m3u8[^\s"\']*)', html_content)
        
        # محاولة 2: إذا لم ينجح، ابحث عن أي رابط m3u8 آخر (مثل vcloud)
        if not match:
            match = re.search(r'(https?://[^\s"\']+\.m3u8[^\s"\']*)', html_content)

        if match:
            stream_url = match.group(1).replace('\\/', '/').split('"')[0].split("'")[0]
            final_link = f"{stream_url}|User-Agent={CONFIG['user_agent']}&Referer={CONFIG['referer']}"
            
            m3u_content = f"#EXTM3U\n#EXTINF:-1 tvg-logo=\"https://i.imgur.com/vHInyD0.png\", Ennahar TV\n{final_link}"
            
            with open(CONFIG['output_file'], "w", encoding="utf-8") as f:
                f.write(m3u_content)
            
            with open('results/status.json', 'w') as f:
                json.dump({"status": "success", "url": stream_url, "time": datetime.now().isoformat()}, f)
            print(f"✅ Found: {stream_url}")
        else:
            # إذا فشل تماما، نضع رابطا احتياطيا ليعمل الملف دائما
            backup_url = "https://shls-ennahar-tv.v7.vcloud.dz/ennahar_tv/index.m3u8"
            final_link = f"{backup_url}|User-Agent={CONFIG['user_agent']}&Referer={CONFIG['referer']}"
            with open(CONFIG['output_file'], "w", encoding="utf-8") as f:
                f.write(f"#EXTM3U\n#EXTINF:-1, Ennahar TV (Backup)\n{final_link}")
            print("⚠️ Using backup link.")

    except Exception as e:
        print(f"⚠️ Error: {e}")

if __name__ == "__main__":
    sniper()
