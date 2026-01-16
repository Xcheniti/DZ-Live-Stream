import requests
import re

def get_live_url():
    source_page = "https://www.echoroukonline.com/live-news"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://www.echoroukonline.com/'
    }
    
    try:
        response = requests.get(source_page, headers=headers, timeout=15)
        response.raise_for_status()
        
        patterns = [
            r'src=["\'](https?://[^"\']+\.m3u8[^"\']*)["\']',
            r'"(https?://[^"\']+\.m3u8[^"\']*)"',
            r'file["\']?\s*:\s*["\'](https?://[^"\']+\.m3u8[^"\']*)["\']'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, response.text)
            if match:
                url = match.group(1)
                url = url.replace('\\/', '/').replace('\\u002F', '/')
                return url
                
    except:
        pass
    
    return "https://shls-echorouk-news.v7.vcloud.dz/echorouk_news/index.m3u8"

if __name__ == "__main__":
    final_link = get_live_url()
    
    # اسم الملف يجب أن يكون playlist.m3u ليتوافق مع الروابط التي وضعتها سابقاً
    with open("playlist.m3u", "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        f.write("#EXTINF:-1, Echorouk News HD\n")
        # التعديل الهام: إضافة الترويسات للرابط مباشرة ليعمل في تطبيقات IPTV
        f.write(f"{final_link}|User-Agent=Mozilla/5.0&Referer=https://www.echoroukonline.com/\n")
