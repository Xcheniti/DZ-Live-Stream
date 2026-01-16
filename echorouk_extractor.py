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
    # التأكد من وجود مجلد النتائج لتجنب Exit Code 2
    os.makedirs('results', exist_ok=True)
    
    session = requests.Session()
    session.headers.update({'User-Agent': CONFIG['user_agent'], 'Referer': CONFIG['referer']})
    
    try:
        print("🔍 Searching for Ennahar stream...")
        response = session.get(CONFIG['target_url'], timeout=15)
        # البحث عن الرابط الذي استخرجته أنت يدوياً dzsecurity.net
        match = re.search(r'(https?://[^\s"\']+dzsecurity\.net[^\s"\']+chunks\.m3u8[^\s"\']*)', response.text)
        
        if match:
            stream_url = match.group(1).replace('\\/', '/')
            final_link = f"{stream_url}|User-Agent={CONFIG['user_agent']}&Referer={CONFIG['referer']}"
            
            m3u_content = f"#EXTM3U\n#EXTINF:-1 tvg-logo=\"https://i.imgur.com/vHInyD0.png\", Ennahar TV\n{final_link}"
            
            with open(CONFIG['output_file'], "w", encoding="utf-8") as f:
                f.write(m3u_content)
            
            with open('results/status.json', 'w') as f:
                json.dump({"status": "success", "time": datetime.now().isoformat()}, f)
            
            print("✅ Success! File updated.")
        else:
            print("❌ Stream link not found in HTML.")
            # إنشاء ملف فارغ أو حالة فشل لمنع تعطل الأكشن
            with open('results/status.json', 'w') as f:
                json.dump({"status": "failed"}, f)

    except Exception as e:
        print(f"⚠️ Error: {e}")

if __name__ == "__main__":
    sniper()
