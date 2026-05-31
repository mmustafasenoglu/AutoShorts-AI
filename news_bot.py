import os
import time
import random
import requests
import subprocess
import feedparser
import textwrap
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont

from youtube_api import get_youtube_service, upload_to_youtube, add_first_comment

load_dotenv()

FREESOUND_API_KEY = os.getenv("FREESOUND_API_KEY", "")
UNSPLASH_API_KEY = os.getenv("UNSPLASH_API_KEY", "")
WORK_DIR = Path("./temp")
WORK_DIR.mkdir(exist_ok=True)

VIDEO_DURATION_MAX = 15 # Kısa can alıcı haber
TAGS = ["ainews", "artificialintelligence", "tech", "technology", "news", "shorts"]

def fetch_ai_news():
    print("[📰] Güncel AI (ChatGPT, Anthropic vb.) haberleri çekiliyor...")
    query = "ChatGPT+OR+Anthropic+OR+OpenAI+OR+Gemini+OR+Claude"
    feed = feedparser.parse(f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en")
    
    if not feed.entries:
        return "BREAKING: AI Makes Huge Leap!", "Artificial intelligence models reach a new milestone in reasoning capabilities today.", ""
    
    entry = random.choice(feed.entries[:10])
    
    full_title = entry.title
    if " - " in full_title:
        title, source = full_title.rsplit(" - ", 1)
        description = f"According to {source}, massive new developments are happening in the AI space today!"
    else:
        title = full_title
        description = "Major developments in the AI industry involving top tier AI models."
        
    return title, description, entry.link

def fetch_news_music():
    query = random.choice(["news intro", "exciting synth", "suspense electronic", "cyberpunk loop", "breaking news"])
    print(f"[🔍] Habere uygun müzik aranıyor: '{query}'")
    url = "https://freesound.org/apiv2/search/text/"
    params = {
        "query": query,
        "token": FREESOUND_API_KEY,
        "fields": "id,name,previews",
        "filter": "duration:[10 TO 60] license:\"Creative Commons 0\"",
        "page_size": 10,
        "format": "json",
    }
    resp = requests.get(url, params=params)
    results = resp.json().get("results", [])
    if not results:
        raise Exception("Haber müziği bulunamadı!")
    
    sound = random.choice(results)
    sound_id = str(sound["id"])
    download_url = sound["previews"]["preview-hq-mp3"]
    out_path = WORK_DIR / f"news_audio_{sound_id}.mp3"
    
    with requests.get(download_url, stream=True) as r:
        with open(out_path, "wb") as f:
            for chunk in r.iter_content(8192):
                f.write(chunk)
    print(f"[✅] Müzik indirildi: {out_path}")
    return out_path

def fetch_background_image():
    query = random.choice(["artificial intelligence", "cyberpunk city", "matrix code", "hacker dark", "data center", "robot cyborg"])
    print(f"[🔍] Arka plan resmi aranıyor: '{query}'")
    url = "https://api.unsplash.com/photos/random"
    headers = {"Authorization": f"Client-ID {UNSPLASH_API_KEY}"}
    params = {"query": query, "orientation": "portrait"}
    resp = requests.get(url, headers=headers, params=params)
    data = resp.json()
    img_url = data["urls"]["regular"]
    out_path = WORK_DIR / f"news_bg_{data['id']}.jpg"
    with requests.get(img_url, stream=True) as r:
        with open(out_path, "wb") as f:
            for chunk in r.iter_content(8192):
                f.write(chunk)
    print(f"[✅] Arka plan indirildi: {out_path}")
    return out_path

def create_text_overlay(title, description):
    print("[✍️] Haber metni görsele dönüştürülüyor...")
    width, height = 1080, 1920
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    try:
        font_title = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 65)
        font_desc = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 45)
    except:
        font_title = ImageFont.load_default()
        font_desc = ImageFont.load_default()

    if len(description) > 150:
        description = description[:147] + "..."

    wrapped_title = textwrap.wrap(title, width=28)
    wrapped_desc = textwrap.wrap(description, width=40)

    y_text = 600
    
    draw.text((100, y_text - 120), "AI NEWS UPDATE", font=font_title, fill=(255, 60, 60, 255))
    
    for line in wrapped_title:
        draw.text((104, y_text+4), line, font=font_title, fill=(0, 0, 0, 255))
        draw.text((100, y_text), line, font=font_title, fill=(255, 255, 255, 255))
        y_text += 80

    y_text += 60
    
    for line in wrapped_desc:
        draw.text((103, y_text+3), line, font=font_desc, fill=(0, 0, 0, 255)) 
        draw.text((100, y_text), line, font=font_desc, fill=(210, 210, 210, 255)) 
        y_text += 60

    out_path = WORK_DIR / "news_overlay.png"
    img.save(out_path)
    return out_path

def create_news_video(audio_path, image_path, overlay_path):
    output_path = WORK_DIR / f"news_video_{int(time.time())}.mp4"
    
    filter_complex = (
        "[0:v]scale=2160:3840:force_original_aspect_ratio=increase,crop=2160:3840,"
        "zoompan=z='min(zoom+0.0005,1.5)':d=3000:x='iw/2-(iw/zoom)/2':y='ih/2-(ih/zoom)/2':s=1080x1920:fps=30,"
        "colorchannelmixer=rr=0.4:gg=0.4:bb=0.4[bg];"
        "[bg][1:v]overlay=0:0[outv]"
    )
    
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", str(image_path),
        "-i", str(overlay_path),
        "-i", str(audio_path),
        "-filter_complex", filter_complex,
        "-map", "[outv]",
        "-map", "2:a",
        "-c:v", "libx264",
        "-c:a", "aac",
        "-shortest",
        "-t", str(VIDEO_DURATION_MAX),
        "-pix_fmt", "yuv420p",
        str(output_path)
    ]
    
    print("[🎬] Haber videosu render alınıyor...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"FFmpeg hatası: {result.stderr}")
        
    print(f"[✅] Video hazır: {output_path}")
    return output_path

def run():
    print(f"\n{'='*50}\n  AI News YouTube Otomasyon — {datetime.now().strftime('%Y-%m-%d %H:%M')}\n{'='*50}\n")
    try:
        title, desc, link = fetch_ai_news()
        audio_path = fetch_news_music()
        bg_path = fetch_background_image()
        overlay_path = create_text_overlay(title, desc)
        video_path = create_news_video(audio_path, bg_path, overlay_path)
        
        service = get_youtube_service()
        
        yt_title = f"🚨 {title[:60]} #ainews #shorts"
        yt_desc = f"AI News Update 🔥\n{title}\n\n📰 Read full article: {link}\n\nSubscribe for daily tech updates! 🤖\n\n#ai #artificialintelligence #tech #news #shorts"
        
        video_id = upload_to_youtube(service, video_path, yt_title, yt_desc, TAGS, "28")
        
        if link:
            add_first_comment(service, video_id, f"🔗 Kaynağı oku: {link}")
            
        print("[✨] Haber botu tamamlandı!\n")
    except Exception as e:
        print(f"\n[❌] Hata: {e}")

if __name__ == "__main__":
    run()
