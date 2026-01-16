#!/usr/bin/env python3
"""
🔥 ECHOROUK SUPER EXTRACTOR V4.0 - THE ULTIMATE STREAM EXTRACTOR
🎯 Features: Multi-method extraction, Automatic validation, Smart caching
⚡ Optimized for GitHub Actions with zero dependencies issues
"""

import os
import sys
import re
import json
import time
import hashlib
import requests
import subprocess
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Tuple
from urllib.parse import urlparse, urljoin, quote

# =============== CONFIGURATION ===============
CONFIG = {
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'timeout': 20,
    'max_retries': 3,
    'cache_duration': 3600,  # 1 hour
    'target_urls': [
        "https://www.echoroukonline.com/live-news",
        "https://www.echoroukonline.com/tv",
        "https://www.echoroukonline.com/ar/tv/live",
        "https://www.echoroukonline.com/fr/tv-en-direct"
    ],
    'cdn_patterns': [
        r'echorouk.*\.m3u8',
        r'v7\.vcloud.*\.m3u8',
        r'algeriatv.*\.m3u8',
        r'dzcdn.*\.m3u8',
        r'stream\.alaan.*\.m3u8'
    ],
    'backup_streams': [
        "https://shls-echorouk-news.v7.vcloud.dz/echorouk_news/index.m3u8",
        "https://live.alaan.tv/echorouk/live.m3u8",
        "https://cdn.algeriatv.dz/live/echorouk.m3u8",
        "https://stream.dztv.dz/echorouk/live.m3u8"
    ]
}

# =============== LOGGER ===============
class Logger:
    @staticmethod
    def info(msg):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ℹ️ {msg}")
    
    @staticmethod
    def success(msg):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ {msg}")
    
    @staticmethod
    def warning(msg):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️ {msg}")
    
    @staticmethod
    def error(msg):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ {msg}")

# =============== CACHE MANAGER ===============
class CacheManager:
    def __init__(self):
        self.cache_dir = "cache"
        os.makedirs(self.cache_dir, exist_ok=True)
    
    def get_cache_key(self, url):
        return hashlib.md5(url.encode()).hexdigest()[:16]
    
    def get(self, url):
        try:
            key = self.get_cache_key(url)
            cache_file = os.path.join(self.cache_dir, f"{key}.json")
            
            if os.path.exists(cache_file):
                with open(cache_file, 'r') as f:
                    data = json.load(f)
                
                cache_time = datetime.fromisoformat(data['timestamp'])
                if datetime.now() - cache_time < timedelta(seconds=CONFIG['cache_duration']):
                    return data['content']
        except:
            pass
        return None
    
    def set(self, url, content):
        try:
            key = self.get_cache_key(url)
            cache_file = os.path.join(self.cache_dir, f"{key}.json")
            
            data = {
                'timestamp': datetime.now().isoformat(),
                'url': url,
                'content': content
            }
            
            with open(cache_file, 'w') as f:
                json.dump(data, f)
        except:
            pass

# =============== SMART EXTRACTOR ===============
class EchoroukSuperExtractor:
    def __init__(self):
        self.session = requests.Session()
        self.cache = CacheManager()
        self.setup_session()
        self.results = {
            'start_time': datetime.now().isoformat(),
            'methods_tried': [],
            'urls_found': [],
            'urls_working': [],
            'best_url': None,
            'final_m3u': None
        }
    
    def setup_session(self):
        """إعداد جلسة HTTP متقدمة"""
        self.session.headers.update({
            'User-Agent': CONFIG['user_agent'],
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ar,en-US;q=0.9,en;q=0.8,fr;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Referer': 'https://www.echoroukonline.com/',
            'DNT': '1'
        })
    
    # =============== METHOD 1: YT-DLP (MOST POWERFUL) ===============
    def extract_with_ytdlp(self, url):
        """الطريقة الأقوى باستخدام yt-dlp"""
        Logger.info(f"المحاولة 1: استخدام yt-dlp لـ {url}")
        
        try:
            cmd = [
                'yt-dlp',
                '--no-warnings',
                '--quiet',
                '--skip-download',
                '--dump-json',
                '--user-agent', CONFIG['user_agent'],
                '--referer', 'https://www.echoroukonline.com/',
                url
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                
                # البحث في جميع التنسيقات
                urls_found = []
                
                # البحث في formats
                if 'formats' in data:
                    for fmt in data['formats']:
                        if 'url' in fmt and '.m3u8' in fmt['url']:
                            urls_found.append(fmt['url'])
                
                # البحث في requested_formats
                if 'requested_formats' in data:
                    for fmt in data['requested_formats']:
                        if 'url' in fmt and '.m3u8' in fmt['url']:
                            urls_found.append(fmt['url'])
                
                # البحث في url مباشرة
                if 'url' in data and '.m3u8' in data['url']:
                    urls_found.append(data['url'])
                
                if urls_found:
                    Logger.success(f"yt-dlp وجد {len(urls_found)} روابط")
                    self.results['methods_tried'].append('ytdlp_success')
                    return list(set(urls_found))
        
        except Exception as e:
            Logger.warning(f"yt-dlp فشل: {str(e)[:50]}")
        
        self.results['methods_tried'].append('ytdlp_failed')
        return []
    
    # =============== METHOD 2: DEEP HTML PARSING ===============
    def extract_from_html(self, url):
        """تحليل HTML بعمق للعثور على روابط مخفية"""
        Logger.info(f"المحاولة 2: تحليل HTML لـ {url}")
        
        cached = self.cache.get(url)
        if cached:
            html = cached
            Logger.info("استخدام HTML من الذاكرة المؤقتة")
        else:
            try:
                response = self.session.get(url, timeout=CONFIG['timeout'])
                response.raise_for_status()
                html = response.text
                self.cache.set(url, html)
            except Exception as e:
                Logger.warning(f"فشل جلب HTML: {e}")
                self.results['methods_tried'].append('html_fetch_failed')
                return []
        
        # أنماط بحث شاملة
        patterns = [
            # أنماط JavaScript المباشرة
            r'(?:src|file|url)\s*[=:]\s*["\'](https?://[^"\']+?\.m3u8(?:\?[^"\']+)?)["\']',
            
            # أنماط JSON
            r'["\'](?:playlist|sources|stream)["\']\s*:\s*\[?\s*{?[^}]*["\'](?:src|file|url)["\']\s*:\s*["\'](https?://[^"\']+?\.m3u8)["\']',
            
            # أنماط HTML5 video
            r'<video[^>]+data-setup=[\'"][^\'"]*["\']file["\']\s*:\s*["\'](https?://[^"\']+?\.m3u8)["\']',
            
            # روابط CDN خاصة
            r'(https?://[^"\'\s<>]+/(?:live|stream|hls)/[^"\'\s<>]+\.m3u8)',
            
            # روابط عامة تنتهي بـ m3u8
            r'(https?://[^"\'\s<>]+\.m3u8(?:\?[^"\'\s<>]*)?)',
        ]
        
        found_urls = []
        for pattern in patterns:
            try:
                matches = re.findall(pattern, html, re.IGNORECASE)
                for match in matches:
                    clean_url = self.clean_url(match)
                    if clean_url and clean_url not in found_urls:
                        found_urls.append(clean_url)
            except:
                continue
        
        if found_urls:
            Logger.success(f"HTML parsing وجد {len(found_urls)} روابط")
            self.results['methods_tried'].append('html_parse_success')
        else:
            self.results['methods_tried'].append('html_parse_failed')
        
        return found_urls
    
    # =============== METHOD 3: SMART CDN DISCOVERY ===============
    def discover_cdn_urls(self):
        """اكتشاف روابط CDN ذكية"""
        Logger.info("المحاولة 3: اكتشاف روابط CDN ذكية")
        
        cdn_urls = []
        
        # توليد روابط CDN محتملة بناءً على الأنماط
        base_domains = [
            "https://cdn.echoroukonline.com",
            "https://stream.echoroukonline.com",
            "https://live.echoroukonline.com",
            "https://tv.echorouk.tv",
            "https://v7.vcloud.dz",
            "https://cdn.algeriatv.dz"
        ]
        
        paths = [
            "/live/stream.m3u8",
            "/hls/stream.m3u8",
            "/echorouk/live.m3u8",
            "/echorouk_news/index.m3u8",
            "/live/echorouk.m3u8",
            "/stream/playlist.m3u8"
        ]
        
        for domain in base_domains:
            for path in paths:
                test_url = domain + path
                cdn_urls.append(test_url)
        
        # إضافة الروابط الاحتياطية
        cdn_urls.extend(CONFIG['backup_streams'])
        
        Logger.info(f"تم توليد {len(cdn_urls)} رابط CDN للاختبار")
        self.results['methods_tried'].append('cdn_discovery')
        
        return cdn_urls
    
    # =============== METHOD 4: NETWORK REQUEST ANALYSIS ===============
    def analyze_network_requests(self, url):
        """محاكاة طلبات الشبكة لاكتشاف روابط خفية"""
        Logger.info(f"المحاولة 4: تحليل طلبات الشبكة لـ {url}")
        
        api_endpoints = [
            f"{url}/config.json",
            f"{url}/manifest.m3u8",
            f"{url}/playlist.m3u8",
            url.replace("live-news", "api/stream"),
            url.replace("live-news", "api/v1/live"),
            "https://www.echoroukonline.com/api/stream/live",
            "https://www.echoroukonline.com/json/live.json"
        ]
        
        found_urls = []
        for api_url in api_endpoints:
            try:
                response = self.session.get(
                    api_url,
                    timeout=10,
                    headers={'X-Requested-With': 'XMLHttpRequest'}
                )
                
                if response.status_code == 200:
                    content = response.text
                    
                    # البحث عن روابط في الاستجابة
                    m3u8_matches = re.findall(
                        r'(https?://[^\s"\']+\.m3u8[^\s"\']*)',
                        content
                    )
                    
                    for match in m3u8_matches:
                        clean_url = self.clean_url(match)
                        if clean_url:
                            found_urls.append(clean_url)
                            
            except:
                continue
        
        if found_urls:
            Logger.success(f"تحليل الشبكة وجد {len(found_urls)} روابط")
            self.results['methods_tried'].append('network_analysis_success')
        else:
            self.results['methods_tried'].append('network_analysis_failed')
        
        return found_urls
    
    # =============== URL VALIDATION ===============
    def validate_stream_url(self, url):
        """التحقق الشامل من صحة الرابط"""
        if not url or not isinstance(url, str):
            return False
        
        # تنظيف الرابط
        clean_url = self.clean_url(url)
        if not clean_url:
            return False
        
        # التحقق من الشكل الأساسي
        if not clean_url.startswith('http'):
            return False
        
        if '.m3u8' not in clean_url.lower():
            return False
        
        # اختبار الاتصال بالرابط
        try:
            # طلب HEAD أولاً (أسرع)
            head_response = self.session.head(
                clean_url,
                timeout=10,
                allow_redirects=True,
                headers={'Range': 'bytes=0-0'}
            )
            
            if head_response.status_code in [200, 206, 302, 307]:
                # إذا نجح HEAD، اختبر جزء صغير من المحتوى
                response = self.session.get(
                    clean_url,
                    timeout=10,
                    stream=True,
                    headers={'Range': 'bytes=0-500'}
                )
                
                if response.status_code in [200, 206]:
                    content = response.text[:500]
                    
                    # التحقق من أن المحتوى هو m3u8 حقيقي
                    is_valid = any([
                        '#EXTM3U' in content,
                        '#EXTINF' in content,
                        '.ts' in content,
                        '.m3u8' in content.lower()
                    ])
                    
                    if is_valid:
                        return clean_url
        
        except Exception as e:
            Logger.warning(f"فشل التحقق من {clean_url[:50]}: {str(e)[:30]}")
        
        return False
    
    # =============== URL CLEANING ===============
    def clean_url(self, url):
        """تنظيف الرابط من جميع الشوائب"""
        if not url:
            return ""
        
        # تحويل إلى string إذا لم يكن
        url_str = str(url)
        
        # إزالة الأحرف غير المرغوبة
        bad_chars = ['\\', '"', "'", '<', '>', '\n', '\r', '\t', ' ']
        for char in bad_chars:
            url_str = url_str.replace(char, '')
        
        # إصلاح الترميز
        url_str = url_str.replace('\\/', '/')
        url_str = url_str.replace('\\u002F', '/')
        url_str = url_str.replace('%2F', '/')
        url_str = url_str.replace('%3A', ':')
        
        # إصلاح الروابط النسبية
        if url_str.startswith('//'):
            url_str = 'https:' + url_str
        elif url_str.startswith('/'):
            url_str = 'https://www.echoroukonline.com' + url_str
        
        # إزالة parameters غير ضرورية
        if '|' in url_str:
            url_str = url_str.split('|')[0]
        
        return url_str.strip()
    
    # =============== MAIN EXTRACTION LOGIC ===============
    def extract_all_urls(self):
        """الجمع بين جميع طرق الاستخراج"""
        all_urls = []
        
        Logger.info("=" * 60)
        Logger.info("بدء عملية الاستخراج الشاملة")
        Logger.info("=" * 60)
        
        # الطريقة 1: yt-dlp (الأقوى)
        for target_url in CONFIG['target_urls']:
            urls = self.extract_with_ytdlp(target_url)
            all_urls.extend(urls)
            time.sleep(1)  # تجنب الحظر
        
        # الطريقة 2: تحليل HTML
        for target_url in CONFIG['target_urls'][:2]:  # أول رابطين فقط
            urls = self.extract_from_html(target_url)
            all_urls.extend(urls)
            time.sleep(1)
        
        # الطريقة 3: اكتشاف CDN
        cdn_urls = self.discover_cdn_urls()
        all_urls.extend(cdn_urls)
        
        # الطريقة 4: تحليل الشبكة
        urls = self.analyze_network_requests(CONFIG['target_urls'][0])
        all_urls.extend(urls)
        
        # إزالة التكرارات
        unique_urls = []
        seen = set()
        for url in all_urls:
            if url and url not in seen:
                seen.add(url)
                unique_urls.append(url)
        
        self.results['urls_found'] = unique_urls
        Logger.success(f"إجمالي الروابط المجمعة: {len(unique_urls)}")
        
        return unique_urls
    
    def validate_all_urls(self, urls):
        """التحقق من جميع الروابط"""
        Logger.info(f"التحقق من {len(urls)} رابط...")
        
        working_urls = []
        
        for i, url in enumerate(urls[:20]):  # اختبر أول 20 رابط فقط
            Logger.info(f"التحقق {i+1}/{min(20, len(urls))}: {url[:60]}...")
            
            validated_url = self.validate_stream_url(url)
            if validated_url:
                working_urls.append(validated_url)
                Logger.success(f"✅ يعمل!")
            
            # وقفة قصيرة بين الاختبارات
            if (i + 1) % 5 == 0:
                time.sleep(1)
        
        self.results['urls_working'] = working_urls
        Logger.success(f"الروابط العاملة: {len(working_urls)}")
        
        return working_urls
    
    def select_best_url(self, urls):
        """اختيار أفضل رابط"""
        if not urls:
            return None
        
        # نظام تقييم ذكي
        def score_url(url):
            score = 0
            url_lower = url.lower()
            
            # الكلمات المفتاحية المهمة
            keywords = {
                'echorouk': 20,
                'news': 15,
                'live': 10,
                'stream': 10,
                'hls': 5,
                'v7.vcloud': 25,  # CDN موثوق
                'algeriatv': 20,
                'alaan': 15
            }
            
            for keyword, points in keywords.items():
                if keyword in url_lower:
                    score += points
            
            # HTTPS أفضل
            if url.startswith('https://'):
                score += 10
            
            # الروابط القصيرة أفضل
            if len(url) < 150:
                score += 5
            
            # الروابط بدون parameters كثيرة أفضل
            if '?' not in url:
                score += 3
            
            return score
        
        # اختيار الرابط بأعلى تقييم
        best_url = max(urls, key=score_url)
        self.results['best_url'] = best_url
        
        Logger.success(f"أفضل رابط مختار: {best_url[:80]}...")
        
        return best_url
    
    def create_m3u_file(self, url):
        """إنشاء ملف M3U احترافي"""
        if not url:
            return None
        
        # تنسيق الرابط لـ IPTV
        headers_part = f"|User-Agent={CONFIG['user_agent']}&Referer=https://www.echoroukonline.com/"
        final_url = url + headers_part
        
        # معلومات القناة
        now = datetime.now()
        m3u_content = f"""#EXTM3U x-tvg-url="http://epg.51zmt.top:8000/e.xml" url-tvg="http://epg.51zmt.top:8000/e.xml"
#EXTINF:-1 tvg-id="EchoroukNews.dz" tvg-name="الشروق نيوز" tvg-logo="https://www.echoroukonline.com/images/logo.png" group-title="🇩🇿 قنوات الجزائر",الشروق نيوز - البث الحي
{final_url}

# 🎥 Echorouk News Live Stream
# 🔄 تم التحديث آلياً: {now.strftime('%Y-%m-%d %H:%M:%S')}
# 📡 الرابط الأصلي: {url}
# ⚡ الإصدار: Super Extractor v4.0
# 📊 الروابط المجربة: {len(self.results['urls_found'])}
# ✅ الروابط العاملة: {len(self.results['urls_working'])}
"""
        
        # حفظ الملف
        os.makedirs('results', exist_ok=True)
        m3u_path = 'results/echorouk_news.m3u'
        
        with open(m3u_path, 'w', encoding='utf-8') as f:
            f.write(m3u_content)
        
        self.results['final_m3u'] = m3u_path
        Logger.success(f"تم إنشاء ملف M3U: {m3u_path}")
        
        return m3u_path
    
    def save_results(self):
        """حفظ جميع النتائج"""
        os.makedirs('results', exist_ok=True)
        os.makedirs('logs', exist_ok=True)
        
        # حالة التنفيذ
        self.results['end_time'] = datetime.now().isoformat()
        self.results['status'] = 'success' if self.results['best_url'] else 'failed'
        self.results['execution_time'] = str(
            datetime.fromisoformat(self.results['end_time']) - 
            datetime.fromisoformat(self.results['start_time'])
        )
        
        # حفظ النتائج التفصيلية
        with open('results/extraction_results.json', 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        # حفظ حالة مبسطة
        status_data = {
            'status': self.results['status'],
            'best_url': self.results['best_url'],
            'working_urls_count': len(self.results['urls_working']),
            'last_update': datetime.now().isoformat(),
            'version': 'v4.0'
        }
        
        with open('results/extraction_status.json', 'w', encoding='utf-8') as f:
            json.dump(status_data, f, indent=2)
        
        # حفظ السجل
        log_file = f"logs/extraction_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write(json.dumps(self.results, indent=2, ensure_ascii=False))
        
        Logger.success(f"تم حفظ النتائج في مجلد results/")
        
        return self.results['status']
    
    def run(self):
        """تشغيل العملية الكاملة"""
        try:
            # 1. استخراج جميع الروابط
            all_urls = self.extract_all_urls()
            
            # 2. التحقق من الروابط
            working_urls = self.validate_all_urls(all_urls)
            
            # 3. اختيار أفضل رابط
            best_url = self.select_best_url(working_urls)
            
            if best_url:
                # 4. إنشاء ملف M3U
                self.create_m3u_file(best_url)
                
                # 5. حفظ النتائج
                status = self.save_results()
                
                Logger.success("=" * 60)
                Logger.success("🎉 عملية الاستخراج اكتملت بنجاح!")
                Logger.success(f"📊 الروابط العاملة: {len(working_urls)}")
                Logger.success(f"🏆 أفضل رابط: {best_url[:80]}...")
                Logger.success("=" * 60)
                
                return True, best_url
            else:
                Logger.error("❌ لم يتم العثور على أي رابط يعمل")
                self.save_results()
                return False, None
                
        except Exception as e:
            Logger.error(f"خطأ غير متوقع: {e}")
            import traceback
            traceback.print_exc()
            return False, None

# =============== MAIN EXECUTION ===============
def main():
    """الدالة الرئيسية"""
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║   🎥 ECHOROUK SUPER EXTRACTOR v4.0 - GITHUB ACTIONS EDITION  ║
    ║   🔄 تحديث آلي لرابط بث الشروق نيوز                       ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    
    extractor = EchoroukSuperExtractor()
    success, best_url = extractor.run()
    
    # إخراج للـ GitHub Actions
    if success:
        print(f"::set-output name=status::success")
        print(f"::set-output name=stream_url::{best_url}")
        print(f"::set-output name=timestamp::{datetime.now().isoformat()}")
        sys.exit(0)
    else:
        print(f"::set-output name=status::failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
