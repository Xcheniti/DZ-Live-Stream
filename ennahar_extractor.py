import requests
import re
import os
import json
from datetime import datetime

# إعدادات الترويسة (Headers)
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://www.ennaharonline.com/',
    'Origin': 'https://www.ennaharonline.com'
}

def sniper():
    # التأكد من وجود المجلد
    os.makedirs('results', exist_ok=True)
    
    session = requests.Session()
    session.headers.update(HEADERS)
    
    stream_url = None
    
    try:
        print("🔍 جاري البحث عن رابط النهار...")
        response = session.get("https://www.ennaharonline.com/live/", timeout=20)
        html = response.text

        # 1. محاولة العثور على رابط dzsecurity (الأصلي)
        match_dz = re.search(r'(https?://[^\s"\'<>]+dzsecurity\.net[^\s"\'<>]+chunks\.m3u8[^\s"\'<>]*)', html)
        if match_dz:
            stream_url = match_dz.group(1).replace('\\/', '/')
            print("✅ تم العثور على رابط dzsecurity!")

        # 2. محاولة العثور على رابط vcloud (الاحتياطي) إذا فشل الأول
        if not stream_url:
            match_vc = re.search(r'(https?://[^\s"\'<>]+vcloud\.dz[^\s"\'<>]+index\.m3u8[^\s"\'<>]*)', html)
            if match_vc:
                stream_url = match_vc.group(1).replace('\\/', '/')
                print("⚠️ تم العثور على رابط vcloud.")

        # 3. رابط الطوارئ اليدوي (إذا فشل البحث الآلي تماماً)
        if not stream_url:
            print("❌ فشل البحث. استخدام رابط الطوارئ.")
            stream_url = "https://shls-ennahar-tv.v7.vcloud.dz/ennahar_tv/index.m3u8"

        # === الجزء الأهم: تنسيق الملف بشكل صحيح ===
        # إضافة الترويسات للرابط
        final_link = f"{stream_url}|User-Agent={HEADERS['User-Agent']}&Referer={HEADERS['Referer']}"
        
        # كتابة الملف مع فواصل الأسطر (\n) الضرورية
        with open('results/ennahar_live.m3u', "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")
            f.write('#EXTINF:-1 tvg-id="EnnaharTV" tvg-logo="https://upload.wikimedia.org/wikipedia/commons/8/8c/Ennahar_TV_Logo.png", Ennahar TV 🇩🇿\n')
            f.write(f"{final_link}\n")

        # حفظ ملف الحالة
        with open('results/status.json', 'w') as f:
            json.dump({"status": "success", "url": stream_url, "updated": datetime.now().isoformat()}, f)
            
        print("💾 تم إصلاح الملف وحفظه بنجاح.")

    except Exception as e:
        print(f"🛑 خطأ: {e}")

if __name__ == "__main__":
    sniper()
