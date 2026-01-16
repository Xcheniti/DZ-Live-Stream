import requests
import re
import os
from datetime import datetime

# الهوية الكاملة لمحاكاة المتصفح الذي استخدمته أنت
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://www.ennaharonline.com/',
    'Origin': 'https://www.ennaharonline.com',
    'Accept': '*/*',
    'Accept-Language': 'ar-DZ,ar;q=0.9,en-US;q=0.8,en;q=0.7',
}

def real_stream_hunter():
    os.makedirs('results', exist_ok=True)
    session = requests.Session()
    session.headers.update(HEADERS)
    
    target_page = "https://www.ennaharonline.com/live/"
    
    try:
        print(f"🔍 جاري فحص صفحة النهار للبحث عن رابط dzsecurity...")
        response = session.get(target_page, timeout=20)
        content = response.text

        # النمط الذي يبحث حصرياً عن الروابط التي رأيتها أنت (dzsecurity + chunks.m3u8)
        # تم تحسين النمط ليتعرف على التوكن الطويل جداً
        pattern = r'(https?://[^\s"\'<>]+dzsecurity\.net[^\s"\'<>]+chunks\.m3u8\?session=[^\s"\'<>]+)'
        
        match = re.search(pattern, content)
        
        if not match:
            # محاولة ثانية: البحث عن الرابط حتى لو كان بترميز يونيكود (مخفي في JS)
            pattern_unicode = r'(https?:\\/\\/[^\s"\'<>]+dzsecurity\.net[^\s"\'<>]+chunks\.m3u8[^\s"\'<>]*)'
            match = re.search(pattern_unicode, content)

        if match:
            # تنظيف الرابط المستخرج
            raw_url = match.group(0).replace('\\/', '/')
            # إزالة أي علامات اقتباس قد تعلق في نهاية الرابط
            clean_url = raw_url.split('"')[0].split("'")[0]
            
            print(f"✅ تم قنص الرابط المضمون: {clean_url[:60]}...")
            
            # تنسيق الملف النهائي للعمل في التطبيقات
            # نضع الرابط مع ترويسات المتصفح لضمان عدم الحظر
            final_entry = f"{clean_url}|User-Agent={HEADERS['User-Agent']}&Referer={HEADERS['Referer']}"
            
            m3u_content = f"#EXTM3U\n#EXTINF:-1, Ennahar TV (Official Stream)\n{final_entry}\n"
            
            with open('results/ennahar_live.m3u', 'w', encoding='utf-8') as f:
                f.write(m3u_content)
            
            print("💾 تم حفظ الرابط في: results/ennahar_live.m3u")
        else:
            print("❌ فشل القنص: الرابط الأساسي غير موجود في كود الصفحة حالياً.")
            # لن نكتب أي رابط احتياطي هنا بناءً على طلبك
            if os.path.exists('results/ennahar_live.m3u'):
                print("ℹ️ سيتم الاحتفاظ بالنسخة السابقة من الملف.")

    except Exception as e:
        print(f"🛑 خطأ أثناء القنص: {e}")

if __name__ == "__main__":
    real_stream_hunter()
