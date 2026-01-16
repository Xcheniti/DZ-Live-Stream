import requests
import re
import os
import json
from datetime import datetime

# الإعدادات المستخلصة من تجربتك اليدوية الناجحة
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
    session.headers.update({
        'User-Agent': CONFIG['user_agent'],
        'Referer': CONFIG['referer']
    })
    
    try:
        print("🔍 جاري قنص رابط النهار من سيرفرات dzsecurity...")
        response = session.get(CONFIG['target_url'], timeout=15)
        
        # البحث عن نمط الرابط الذي وجدته أنت في صورتك (chunks.m3u8)
        match = re.search(r'(https?://[^\s"\']+dzsecurity\.net[^\s"\']+chunks\.m3u8[^\s"\']*)', response.text)
        
        if match:
            stream_url = match.group(1).replace('\\/', '/')
            # تنسيق الرابط للعمل في تطبيقات IPTV
            final_link = f"{stream_url}|User-Agent={CONFIG['user_agent']}&Referer={CONFIG['referer']}"
            
            m3u_content = f"#EXTM3U\n#EXTINF:-1 tvg-logo=\"https://www.ennaharonline.com/wp-content/themes/ennahar/assets/images/logo.png\", Ennahar TV 🇩🇿\n{final_link}"
            
            with open(CONFIG['output_file'], "w", encoding="utf-8") as f:
                f.write(m3u_content)
            
            with open('results/status.json', 'w') as f:
                json.dump({"status": "success", "time": datetime.now().isoformat(), "url": stream_url}, f)
            
            print("✅ نجاح! تم تحديث الملف بنجاح.")
        else:
            print("❌ لم يتم العثور على الرابط في كود الصفحة.")
            # إنشاء ملف حالة لتجنب فشل الأكشن بالكامل
            with open('results/status.json', 'w') as f:
                json.dump({"status": "failed", "reason": "link_not_found"}, f)

    except Exception as e:
        print(f"⚠️ خطأ: {e}")

if __name__ == "__main__":
    sniper()
