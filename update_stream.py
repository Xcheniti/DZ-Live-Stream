# كود بسيط جداً لإنشاء قائمة تشغيل نظيفة
content = """#EXTM3U
#EXTINF:-1, Echorouk News HD
https://shls-echorouk-news.v7.vcloud.dz/echorouk_news/index.m3u8

#EXTINF:-1, Echorouk TV
https://shls-echorouk-tv.v7.vcloud.dz/echorouk_tv/index.m3u8
"""

with open("playlist.m3u", "w", encoding="utf-8") as f:
    f.write(content)
