import requests

def get_live():
    # هذا الرابط المباشر الذي ظهر في صورتك أنه يعمل في المتصفح
    return "https://live.dzsecurity.net/live/echorouknews/playlist.m3u8"

url = get_live()
with open("playlist.m3u", "w", encoding="utf-8") as f:
    f.write("#EXTM3U\n")
    f.write("#EXTINF:-1, Echorouk News\n")
    f.write(f"{url}\n")
