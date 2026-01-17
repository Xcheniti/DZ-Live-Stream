import os
import time
from playwright.sync_api import sync_playwright

def hunt_stream():
    with sync_playwright() as p:
        # تشغيل المتصفح مع إعدادات إضافية لتجنب الكشف
        browser = p.chromium.launch(headless=True, args=[
            '--disable-blink-features=AutomationControlled',
            '--no-sandbox',
            '--disable-setuid-sandbox'
        ])
        
        # إنشاء سياق (Context) بهوية متصفح كاملة
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={'width': 1920, 'height': 1080},
            extra_http_headers={
                "Accept-Language": "ar,en-US;q=0.9,en;q=0.8"
            }
        )
        
        # إضافة سكريبت لإزالة علامة "webdriver" التي تكشف البوتات
        page = context.new_page()
        page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        target_link = None

        # مراقبة طلبات الشبكة (Sniffing)
        def handle_request(request):
            nonlocal target_link
            if "chunks.m3u8?session=" in request.url:
                target_link = request.url
                print(f"🎯 تم صيد الرابط الجديد بنجاح!")

        page.on("request", handle_request)

        try:
            print("🌐 جاري محاكاة التصفح البشري للوصول للرابط...")
            # التوجه لصفحة البث
            page.goto("https://www.ennaharonline.com/live/", wait_until="networkidle", timeout=60000)
            
            # محاكاة حركة بسيطة داخل الصفحة لخداع الحماية
            page.mouse.move(100, 100)
            time.sleep(15) # انتظار توليد التوكن

            if target_link:
                os.makedirs('results', exist_ok=True)
                with open('results/ennahar.m3u', 'w', encoding='utf-8') as f:
                    f.write("#EXTM3U\n")
                    f.write('#EXTINF:-1 tvg-logo="https://i.imgur.com/vHInyD0.png", Ennahar TV\n')
                    # الرابط مع ترويسة Referer لضمان استمرار البث
                    f.write(f"{target_link}|User-Agent=Mozilla/5.0&Referer=https://live.dzsecurity.net/\n")
                print("✅ تم تحديث الرابط في ملف results/ennahar.m3u")
                return True
            else:
                print("❌ لم يظهر الرابط، قد يكون هناك تحدٍ أمني (Captcha).")
                return False
        except Exception as e:
            print(f"⚠️ خطأ: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    hunt_stream()
