import re
import os
from playwright.sync_api import sync_playwright

def hunt_ennahar():
    with sync_playwright() as p:
        # تشغيل متصفح خفي
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # قائمة لتخزين الروابط المكتشفة
        found_links = []

        # مراقبة جميع طلبات الشبكة (مثل الـ Network Tab)
        page.on("request", lambda request: found_links.append(request.url) 
                if "chunks.m3u8?session=" in request.url else None)

        try:
            print("🚀 جاري فتح صفحة البث...")
            page.goto("https://www.ennaharonline.com/live/", wait_until="networkidle", timeout=60000)
            
            # الانتظار قليلاً للتأكد من توليد الرابط
            page.wait_for_timeout(10000) 

            if found_links:
                final_link = found_links[-1] # أحدث رابط
                print(f"🎯 تم القنص بنجاح: {final_link[:50]}...")
                
                # حفظ النتيجة في ملف M3U
                os.makedirs('results', exist_ok=True)
                with open('results/ennahar.m3u', 'w', encoding='utf-8') as f:
                    f.write("#EXTM3U\n#EXTINF:-1, Ennahar TV\n")
                    f.write(f"{final_link}|User-Agent=Mozilla/5.0&Referer=https://live.dzsecurity.net/\n")
                return True
            else:
                print("❌ لم يتم العثور على رابط التوكن.")
                return False
        except Exception as e:
            print(f"⚠️ خطأ أثناء التشغيل: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    hunt_ennahar()
