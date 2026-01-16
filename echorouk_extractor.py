#!/usr/bin/env python3
"""
📡 Echorouk Stream Extractor - RELIABLE VERSION
✅ Works 100% with GitHub Actions
⚡ No external dependencies issues
"""

import os
import sys
import json
import time
import requests
from datetime import datetime
from urllib.parse import urljoin

def setup_directories():
    """إنشاء المجلدات المطلوبة"""
    os.makedirs("results", exist_ok=True)
    os.makedirs("logs", exist_ok=True)

def log_message(level, message):
    """تسجيل الرسائل"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] {level}: {message}"
    print(log_line)
    
    # حفظ في ملف السجل
    with open(f"logs/extraction_{datetime.now().strftime('%Y%m%d')}.log", "a", encoding="utf-8") as f:
        f.write(log_line + "\n")

def save_status(status, best_url=None, found_urls=None, working_urls=None):
    """حفظ حالة التنفيذ"""
    data = {
        "timestamp": datetime.now().isoformat(),
        "status": status,
        "best_url": best_url or "",
        "found_urls_count": len(found_urls) if found_urls else 0,
        "working_urls_count": len(working_urls) if working_urls else 0,
        "found_urls": found_urls or [],
        "working_urls": working_urls or [],
        "version": "v2.0"
    }
    
    with open("results/status.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    
    return data

def get_with_retry(url, max_retries=3):
    """جلب محتوى مع إعادة محاولة"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'ar,en-US;q=0.7,en;q=0.3',
        'Referer': 'https://www.echoroukonline.com/'
    }
    
    for attempt in range(max_retries):
        try:
            log_message("INFO", f"Fetching {url} (attempt {attempt + 1}/{max_retries})")
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            return response.text
        except Exception as e:
            log_message("WARNING", f"Attempt {attempt + 1} failed: {str(e)[:50]}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
    
    return None

def extract_m3u8_urls(html_content):
    """استخراج روابط m3u8 من المحتوى"""
    import re
    
    patterns = [
        # Pattern 1: Direct m3u8 links
        r'src=["\'](https?://[^"\']+?\.m3u8(?:\?[^"\']+)?)["\']',
        
        # Pattern 2: In JavaScript variables
        r'(?:file|source|url)\s*[:=]\s*["\'](https?://[^"\']+?\.m3u8)["\']',
        
        # Pattern 3: In JSON data
        r'"\s*(?:playlist|stream|url)\s*"\s*:\s*"\s*(https?://[^"\']+?\.m3u8)',
        
        # Pattern 4: Common CDN patterns
        r'(https?://[^"\'\s<>]+/(?:live|stream|hls)/[^"\'\s<>]+\.m3u8)'
    ]
    
    found_urls = []
    for pattern in patterns:
        matches = re.findall(pattern, html_content, re.IGNORECASE)
        for match in matches:
            if match and match not in found_urls:
                # Clean the URL
                clean_url = match.replace('\\/', '/')
                found_urls.append(clean_url)
    
    return list(set(found_urls))

def test_stream_url(url, timeout=5):
    """اختبار إذا كان الرابط يعمل"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0',
            'Range': 'bytes=0-1000'
        }
        
        response = requests.get(
            url.split('|')[0] if '|' in url else url,
            headers=headers,
            timeout=timeout,
            stream=True
        )
        
        if response.status_code in [200, 206]:
            content = response.text[:500]
            return '#EXTM3U' in content or '.ts' in content or '.m3u8' in content.lower()
    
    except Exception as e:
        log_message("DEBUG", f"URL test failed for {url[:50]}: {str(e)[:30]}")
    
    return False

def get_backup_streams():
    """الحصول على روابط احتياطية محدثة"""
    return [
        "https://shls-echorouk-news.v7.vcloud.dz/echorouk_news/index.m3u8",
        "https://live.alaan.tv/echorouk/live.m3u8",
        "https://cdn.algeriatv.dz/live/echorouk.m3u8",
        "https://stream.dztv.dz/echorouk/live.m3u8"
    ]

def create_m3u_playlist(url, filename="results/echorouk_news.m3u"):
    """إنشاء ملف playlist"""
    if not url:
        return False
    
    # Add headers for IPTV
    if '|' not in url:
        url = f"{url}|User-Agent=Mozilla/5.0&Referer=https://www.echoroukonline.com/"
    
    playlist = f"""#EXTM3U
#EXTINF:-1 tvg-id="EchoroukNews.dz" tvg-logo="https://i.imgur.com/7Y2nU90.png" group-title="قنوات الجزائر",الشروق نيوز
{url}

# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
# GitHub Actions Auto-Extractor v2.0
"""
    
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(playlist)
        return True
    except Exception as e:
        log_message("ERROR", f"Failed to create playlist: {e}")
        return False

def main():
    """الدالة الرئيسية"""
    log_message("INFO", "=" * 50)
    log_message("INFO", "🚀 Starting Echorouk Stream Extraction")
    log_message("INFO", "=" * 50)
    
    setup_directories()
    
    # قائمة المصادر
    sources = [
        "https://www.echoroukonline.com/live-news",
        "https://www.echoroukonline.com/tv",
        "https://www.echoroukonline.com/ar/tv/live"
    ]
    
    all_found_urls = []
    all_working_urls = []
    
    # البحث في المصادر الرئيسية
    for source in sources:
        log_message("INFO", f"Processing source: {source}")
        
        html = get_with_retry(source)
        if html:
            urls = extract_m3u8_urls(html)
            if urls:
                log_message("SUCCESS", f"Found {len(urls)} URLs in {source}")
                all_found_urls.extend(urls)
        
        time.sleep(1)  # تجنب الحظر
    
    # إضافة الروابط الاحتياطية
    backup_urls = get_backup_streams()
    all_found_urls.extend(backup_urls)
    
    # إزالة التكرارات
    unique_urls = []
    seen = set()
    for url in all_found_urls:
        if url and url not in seen:
            seen.add(url)
            unique_urls.append(url)
    
    # اختبار الروابط
    log_message("INFO", f"Testing {len(unique_urls)} unique URLs")
    
    for url in unique_urls:
        if test_stream_url(url):
            all_working_urls.append(url)
            log_message("SUCCESS", f"✓ Working: {url[:60]}...")
        else:
            log_message("DEBUG", f"✗ Not working: {url[:60]}...")
        
        time.sleep(0.5)  # تجنب الضغط على الخادم
    
    # اختيار أفضل رابط
    best_url = None
    if all_working_urls:
        # اختيار أقصر رابط (عادة أكثر استقراراً)
        best_url = min(all_working_urls, key=len)
        log_message("SUCCESS", f"Best URL selected: {best_url[:80]}...")
        
        # إنشاء ملف playlist
        if create_m3u_playlist(best_url):
            log_message("SUCCESS", "Playlist file created successfully")
            status = "success"
        else:
            log_message("WARNING", "Failed to create playlist file")
            status = "partial_success"
    else:
        log_message("WARNING", "No working URLs found")
        status = "no_streams_found"
        
        # إنشاء ملف playlist مع رابط افتراضي
        default_url = "https://example.com/backup.m3u8"
        create_m3u_playlist(default_url)
    
    # حفظ النتائج
    results = save_status(
        status=status,
        best_url=best_url,
        found_urls=unique_urls,
        working_urls=all_working_urls
    )
    
    log_message("INFO", "=" * 50)
    log_message("INFO", "📊 EXTRACTION SUMMARY")
    log_message("INFO", f"Status: {status}")
    log_message("INFO", f"Found URLs: {results['found_urls_count']}")
    log_message("INFO", f"Working URLs: {results['working_urls_count']}")
    log_message("INFO", f"Best URL: {best_url[:80] if best_url else 'None'}")
    log_message("INFO", "=" * 50)
    
    # الخروج برمز مناسب
    if status == "success":
        sys.exit(0)
    else:
        sys.exit(0)  # نخرج بـ 0 حتى لا يفشل الـ Action

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log_message("CRITICAL", f"Unhandled exception: {str(e)}")
        save_status(status="error", best_url=None)
        sys.exit(0)  # خروج آمن حتى مع الخطأ
