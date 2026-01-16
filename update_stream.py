import requests

def get_echorouk():
    # الرابط الذي يعمل في المتصفح
    url = "https://live.dzsecurity.net/live/echorouknews/playlist.m3u8"
    return url

link = get_echorouk()
with open("playlist.m3u", "w", encoding="utf-8") as f:
    f.write("#EXTM3U\n")
    f.write("#EXTINF:-1, Echorouk News HD\n")
    # إضافة علامة | مع بيانات المتصفح ضرورية جداً هنا
    f.write(f"{link}|User-Agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36&Referer=https://www.echoroukonline.com/\n")
