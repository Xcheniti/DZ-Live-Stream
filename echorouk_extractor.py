import requests
import re
import os
import json
from datetime import datetime

# =============== الإعدادات الخاصة بقناة النهار ===============
CONFIG = {
    'target_url': "https://www.ennaharonline.com/live/",
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'referer': 'https://www.ennaharonline.com/',
    'output_file': 'ennahar_live.m3u'
}

class EnnaharSniper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': CONFIG['user_agent'],
            'Referer': CONFIG['referer']
        })

    def capture_stream(self):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 🎯 جاري قنص رابط النهار...")
        try:
            response = self.session.get(CONFIG['target_url'], timeout=20)
            html = response.text

            # البحث عن رابط dzsecurity الذي يحتوي على التوكن (session)
            pattern = r'(https?://[^\s"\']+dzsecurity\.net[^\s"\']+chunks\.m3u8[^\s"\']*)'
            match = re.search(pattern, html)

            if match:
                clean_url = match.group(1).replace('\\/', '/').split('"')[0].split("'")[0]
                print(f"✅ تم العثور على الرابط بنجاح!")
                return clean_url
        except Exception as e:
            print(f"❌ خطأ أثناء القنص: {e}")
        return None

    def create_m3u(self, stream_url):
        if not stream_url: return
        
        # تنسيق الرابط ليعمل في تطبيقات IPTV مع الترويسات
        final_link = f"{stream_url}|User-Agent={CONFIG['user_agent']}&Referer={CONFIG['referer']}"
        
        m3u_content = f"#EXTM3U\n#EXTINF:-1 tvg-id=\"EnnaharTV.dz\" tvg-logo=\"https://www.ennaharonline.com/wp-content/themes/ennahar/assets/images/logo.png\", Ennahar TV 🇩🇿\n{final_link}\n"
        
        os.makedirs('results', exist_ok=True)
        # حفظ ملف الـ M3U
        with open(f"results/{CONFIG['output_file']}", "w", encoding="utf-8") as f:
            f.write(m3u_content)
        
        # حفظ حالة العملية ليعرف GitHub أنها نجحت
        with open('results/extraction_status.json', 'w') as f:
            json.dump({"status": "success", "best_url": stream_url, "timestamp": datetime.now().isoformat()}, f)
        
        print(f"💾 تم تحديث ملف: results/{CONFIG['output_file']}")

if __name__ == "__main__":
    sniper = EnnaharSniper()
    url = sniper.capture_stream()
    if url: sniper.create_m3u(url)
    else: print("💔 لم يتم العثور على البث.")
