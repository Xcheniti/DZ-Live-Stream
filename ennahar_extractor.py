import requests
import re
import os

# الهوية المستخلصة من ملف الـ HAR وصورك
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    'Accept-Language': 'fr-FR,fr;q=0.9',
    'Referer': 'https://www.ennaharonline.com/live/',
    'Origin': 'https://live.dzsecurity.net',
}

def get_ennahar_token():
    session = requests.Session()
    session.headers.update(HEADERS)
    
    try:
        # الخطوة 1: زيارة المشغل مباشرة (كما ظهر في صورتك الرابعة)
        player_url = "https://live.dzsecurity.net/live/player/ennahartv"
        print(f"🔗 جاري فحص المشغل: {player_url}")
        
        response = session.get(player_url, timeout=15)
        
        # الخطوة 2: البحث عن التوكن (session) داخل كود الصفحة
        # التوكن يظهر في صورك كـ Base64 طويل
        token_match = re.search(r'session=([A-Za-z0-9+/=]{30,})', response.text)
        
        if token_match:
            token = token_match.group(1)
            final_m3u8 = f"https://hls-distrib-eu1.dzsecurity.net/live/EnnaharTV/chunks.m3u8?session={token}"
            print(f"🎯 تم استخراج الرابط بنجاح!")
            save_m3u(final_m3u8)
            return True
            
        print("❌ لم نجد التوكن في كود المشغل، قد يكون مشفراً.")
        return False
        
    except Exception as e:
        print(f"⚠️ خطأ تقني: {e}")
        return False

def save_m3u(url):
    os.makedirs('results', exist_ok=True)
    with open('results/ennahar.m3u', 'w') as f:
        f.write(f"#EXTM3U\n#EXTINF:-1, Ennahar TV\n{url}|Referer=https://live.dzsecurity.net/")

if __name__ == "__main__":
    get_ennahar_token()
