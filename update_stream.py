with open("playlist.m3u", "w", encoding="utf-8") as f:
    f.write("#EXTM3U\n\n")
    
    # رابط قناة الشروق نيوز (مصدر بديل مفتوح)
    f.write("#EXTINF:-1, Echorouk News HD\n")
    f.write("https://shls-echorouk-news.v7.vcloud.dz/echorouk_news/index.m3u8\n\n")
    
    # رابط قناة الشروق العامة (إضافية)
    f.write("#EXTINF:-1, Echorouk TV\n")
    f.write("https://shls-echorouk-tv.v7.vcloud.dz/echorouk_tv/index.m3u8\n")
