#!/usr/bin/env python3
"""
🔥 مستخرج بث الشروق نيوز الخارق - إصدار GitHub Actions
🔄 يقوم بتحديث الرابط تلقائياً كل 6 ساعات
"""

import os
import re
import sys
import json
import time
import hashlib
import requests
import yt_dlp
from datetime import datetime
from typing import Optional, Dict, List, Tuple
from urllib.parse import urlparse, parse_qs

class EchoroukSuperExtractor:
    """فئة خارقة لاستخراج البث المباشر بقوة"""
    
    def __init__(self):
        self.session = requests.Session()
        self.setup_session()
        self.results = {
            'found_urls': [],
            'working_urls': [],
            'best_url': None,
            'timestamp': datetime.now().isoformat()
        }
        
    def setup_session(self):
        """إعداد جلسة HTTP متقدمة"""
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ar,en-US;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
            'Referer': 'https://www.echoroukonline.com/'
        })
        
    def smart_proxy_rotation(self):
        """تدوير وكيل ذكي (يمكن إضافة proxies حقيقية هنا)"""
        proxies = {
            'http': os.getenv('HTTP_PROXY', ''),
            'https': os.getenv('HTTPS_PROXY', '')
        }
        if any(proxies.values()):
            self.session.proxies.update(proxies)
            
    def extract_with_ytdlp(self, url: str) -> List[str]:
        """استخراج باستخدام yt-dlp (الأقوى)"""
        print("🔍 استخدام yt-dlp للاستخراج المتقدم...")
        
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,
            'force_generic_extractor': False,
            'user_agent': self.session.headers['User-Agent'],
            'referer': 'https://www.echoroukonline.com/',
        }
        
        found_urls = []
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                # البحث في كل الأشكال الممكنة
                if 'formats' in info:
                    for fmt in info['formats']:
                        if fmt.get('protocol') in ['m3u8', 'm3u8_native']:
                            video_url = fmt.get('url')
                            if video_url and '.m3u8' in video_url:
                                found_urls.append(video_url)
                                
                # البحث في URLs مباشرة
                if 'url' in info and '.m3u8' in info['url']:
                    found_urls.append(info['url'])
                    
        except Exception as e:
            print(f"⚠️ yt-dlp خطأ: {e}")
            
        return list(set(found_urls))
    
    def deep_html_analysis(self, html: str) -> List[str]:
        """تحليل HTML عميق باحثاً عن روابط مخفية"""
        patterns = [
            # أنماط JavaScript
            r'(?i)(?:var|let|const)\s+\w+\s*=\s*["\'](https?://[^"\']+\.m3u8[^"\']*)["\']',
            r'(?i)\.setup\({\s*[^}]*file\s*:\s*["\'](https?://[^"\']+\.m3u8)["\']',
            r'(?i)src:\s*["\'](https?://[^"\']+\.m3u8(?:\?[^"\']+)?)["\']',
            
            # أنماط JSON
            r'"playlist"\s*:\s*\[\s*{[^}]+"file"\s*:\s*"([^"]+\.m3u8[^"]*)"',
            r'"sources"\s*:\s*\[\s*{[^}]+"src"\s*:\s*"([^"]+\.m3u8[^"]*)"',
            
            # أنماط HTML5 Video
            r'<video[^>]+data-setup=\'[^\']*"file"\s*:\s*"([^"]+\.m3u8)"',
            
            # روابط CDN مخصصة للجزائر
            r'(https?://(?:[^/]+\.)?(?:algeriatv|echorouk|v7\.vcloud|dzcdn)[^/]+/.*?\.m3u8)',
        ]
        
        found = []
        for pattern in patterns:
            try:
                matches = re.findall(pattern, html, re.DOTALL)
                for match in matches:
                    if isinstance(match, tuple):
                        match = match[0]
                    clean_url = self.clean_url(match)
                    if clean_url and clean_url not in found:
                        found.append(clean_url)
            except:
                continue
                
        return found
    
    def clean_url(self, url: str) -> str:
        """تنظيف الرابط من الشوائب"""
        if not url or not isinstance(url, str):
            return ""
            
        # إصلاح الترميز
        url = url.replace('\\/', '/').replace('\\u002F', '/')
        url = url.replace('\\/', '/').replace('\\/', '/')
        
        # إزالة أحرف غير مرغوبة
        bad_chars = ['\\', '"', "'", '<', '>', '\n', '\r', '\t']
        for char in bad_chars:
            url = url.replace(char, '')
            
        # التأكد من أن الرابط يبدأ بـ http
        if not url.startswith('http'):
            # محاولة إصلاح الروابط النسبية
            if url.startswith('//'):
                url = 'https:' + url
            elif '.m3u8' in url:
                # قد يكون رابطاً بدون بروتوكول
                url = 'https://' + url.lstrip('/')
                
        return url.strip()
    
    def test_stream_url(self, url: str, timeout: int = 10) -> bool:
        """اختبار إذا كان الرابط يعمل"""
        try:
            # إزالة الـ headers المرفقة لـ IPTV
            clean_url = url.split('|')[0] if '|' in url else url
            
            # طلب HEAD أولاً للسرعة
            head_response = self.session.head(
                clean_url, 
                timeout=timeout,
                allow_redirects=True
            )
            
            if head_response.status_code == 200:
                # إذا نجح HEAD، اختبر جزء من المحتوى
                response = self.session.get(
                    clean_url, 
                    timeout=timeout,
                    stream=True,
                    headers={'Range': 'bytes=0-1000'}  # أول 1000 بايت فقط
                )
                
                if response.status_code in [200, 206]:
                    content = response.text[:500]
                    return '#EXTM3U' in content or '.m3u8' in content.lower()
                    
        except Exception as e:
            print(f"⚠️ فشل اختبار {url[:50]}...: {str(e)[:50]}")
            
        return False
    
    def fetch_all_possible_sources(self) -> List[str]:
        """جمع جميع المصادر المحتملة"""
        sources = []
        
        # المصادر الأساسية
        base_sources = [
            "https://www.echoroukonline.com/live-news",
            "https://www.echoroukonline.com/tv/live",
            "https://www.echoroukonline.com/en/live",
            "https://www.echoroukonline.com/ar/tv",
        ]
        
        # روابط API محتملة
        api_sources = [
            "https://api.echoroukonline.com/live/stream",
            "https://www.echoroukonline.com/api/v1/stream",
            "https://player.echoroukonline.com/config.json",
        ]
        
        # روابط CDN محتملة (تم تحديثها)
        cdn_sources = [
            "https://streaming.echoroukonline.com/live.m3u8",
            "https://cdn.echoroukonline.com/hls/stream.m3u8",
            "https://live.echoroukonline.com/stream/playlist.m3u8",
            "https://tv.echorouk.tv/live/echorouk_news/index.m3u8",
        ]
        
        all_sources = base_sources + api_sources + cdn_sources
        
        for source in all_sources:
            try:
                print(f"🔎 فحص: {source}")
                
                if source.endswith('.m3u8'):
                    # إذا كان الرابط مباشراً لـ m3u8
                    if self.test_stream_url(source):
                        sources.append(source)
                else:
                    # جلب وتحليل HTML
                    response = self.session.get(source, timeout=15)
                    
                    # الطريقة 1: yt-dlp
                    yt_urls = self.extract_with_ytdlp(source)
                    sources.extend(yt_urls)
                    
                    # الطريقة 2: تحليل HTML
                    html_urls = self.deep_html_analysis(response.text)
                    sources.extend(html_urls)
                    
            except Exception as e:
                print(f"❌ خطأ في {source}: {str(e)[:50]}")
                continue
                
        return list(set(filter(None, sources)))
    
    def select_best_url(self, urls: List[str]) -> Optional[str]:
        """اختيار أفضل رابط يعمل"""
        working_urls = []
        
        print(f"🧪 اختبار {len(urls)} رابط...")
        
        for i, url in enumerate(urls, 1):
            print(f"  {i}/{len(urls)}: اختبار {url[:60]}...")
            
            if self.test_stream_url(url):
                working_urls.append(url)
                print(f"    ✅ يعمل!")
            else:
                print(f"    ❌ لا يعمل")
                
            # وقفة قصيرة لتجنب الحظر
            if i % 3 == 0:
                time.sleep(1)
        
        self.results['working_urls'] = working_urls
        
        if not working_urls:
            return None
            
        # معايير اختيار أفضل رابط
        def url_score(test_url: str) -> int:
            score = 0
            url_lower = test_url.lower()
            
            # أولوية للروابط التي تحتوي على كلمات معينة
            keywords = ['echorouk', 'news', 'live', 'stream', 'hls']
            for keyword in keywords:
                if keyword in url_lower:
                    score += 10
            
            # أولوية للروابط الآمنة (HTTPS)
            if test_url.startswith('https://'):
                score += 5
                
            # أولوية للروابط القصيرة (أقل احتمالية للانتهاء)
            if len(test_url) < 150:
                score += 3
                
            return score
        
        # اختيار الرابط بأعلى درجة
        best_url = max(working_urls, key=url_score)
        self.results['best_url'] = best_url
        
        return best_url
    
    def format_for_iptv(self, url: str) -> str:
        """تنسيق الرابط لملفات IPTV"""
        if not url:
            return ""
            
        # إضافة الـ headers الضرورية
        headers = {
            'User-Agent': self.session.headers['User-Agent'],
            'Referer': 'https://www.echoroukonline.com/'
        }
        
        # بناء سطر الـ headers
        header_parts = []
        for key, value in headers.items():
            header_parts.append(f'{key}={value}')
        
        return f"{url}|{'&'.join(header_parts)}"
    
    def create_playlist_file(self, stream_url: str) -> bool:
        """إنشاء ملف M3U احترافي"""
        if not stream_url:
            return False
            
        try:
            # تنسيق الرابط
            iptv_url = self.format_for_iptv(stream_url)
            
            # معلومات القناة
            channel_info = {
                'name': 'الشروق نيوز',
                'logo': 'https://www.echoroukonline.com/images/logo.png',
                'group': 'قنوات الجزائر 🇩🇿',
                'id': 'EchoroukNews.dz'
            }
            
            # محتوى ملف M3U
            m3u_content = f"""#EXTM3U x-tvg-url="http://epg.51zmt.top:8000/e.xml.gz"
#EXTINF:-1 tvg-id="{channel_info['id']}" tvg-name="{channel_info['name']}" tvg-logo="{channel_info['logo']}" group-title="{channel_info['group']}",{channel_info['name']} [آلي التحديث: {datetime.now().strftime('%Y-%m-%d %H:%M')}]
{iptv_url}

# تاريخ التحديث: {datetime.now().isoformat()}
# الروابط المجربة: {len(self.results['found_urls'])}
# الروابط العاملة: {len(self.results['working_urls'])}
# أفضل رابط: {self.results['best_url']}
"""
            
            # حفظ الملف
            with open('echorouk_news.m3u', 'w', encoding='utf-8') as f:
                f.write(m3u_content)
            
            # حفظ النتائج كـ JSON للتحليل
            with open('extraction_results.json', 'w', encoding='utf-8') as f:
                json.dump(self.results, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            print(f"❌ خطأ في إنشاء الملف: {e}")
            return False
    
    def run_extraction(self) -> Tuple[bool, str]:
        """تشغيل عملية الاستخراج الكاملة"""
        print("=" * 70)
        print("🚀 بدء استخراج بث الشروق نيوز - GitHub Actions Edition")
        print("=" * 70)
        
        # 1. جمع جميع المصادر المحتملة
        print("\n📡 مرحلة 1: جمع المصادر...")
        all_urls = self.fetch_all_possible_sources()
        self.results['found_urls'] = all_urls
        
        if not all_urls:
            print("❌ لم يتم العثور على أي روابط")
            return False, ""
        
        print(f"✅ تم جمع {len(all_urls)} رابط محتمل")
        
        # 2. اختيار أفضل رابط
        print("\n🏆 مرحلة 2: اختيار أفضل رابط...")
        best_url = self.select_best_url(all_urls)
        
        if not best_url:
            print("❌ لا توجد روابط تعمل")
            return False, ""
        
        print(f"🎯 أفضل رابط: {best_url}")
        
        # 3. إنشاء ملف التشغيل
        print("\n💾 مرحلة 3: إنشاء ملف التشغيل...")
        success = self.create_playlist_file(best_url)
        
        if success:
            print("✅ تم إنشاء ملف echorouk_news.m3u بنجاح")
            
            # عرض ملخص
            print("\n" + "=" * 70)
            print("📊 ملخص النتائج:")
            print(f"   • الروابط المجربة: {len(all_urls)}")
            print(f"   • الروابط العاملة: {len(self.results['working_urls'])}")
            print(f"   • وقت التنفيذ: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"   • رابط التشغيل: {best_url[:80]}...")
            print("=" * 70)
            
            return True, best_url
        else:
            print("❌ فشل في إنشاء ملف التشغيل")
            return False, ""

def main():
    """الدالة الرئيسية"""
    extractor = EchoroukSuperExtractor()
    success, url = extractor.run_extraction()
    
    # إعداد الخرج لـ GitHub Actions
    if success:
        print(f"::set-output name=stream_url::{url}")
        print(f"::set-output name=status::success")
        print(f"::set-output name=timestamp::{datetime.now().isoformat()}")
        sys.exit(0)
    else:
        print("::set-output name=status::failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
