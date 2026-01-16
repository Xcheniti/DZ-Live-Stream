# روابط بديلة تمر عبر سيرفرات عالمية (Cloudflare)
content = """#EXTM3U
#EXTINF:-1, Echorouk News
https://all-dz-news.pages.dev/streams/echorouk_news.m3u8

#EXTINF:-1, Echorouk TV
https://all-dz-news.pages.dev/streams/echorouk_tv.m3u8
"""

with open("playlist.m3u", "w", encoding="utf-8") as f:
    f.write(content)
