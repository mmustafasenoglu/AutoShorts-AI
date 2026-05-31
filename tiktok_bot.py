import os
import json
import time
import random
import requests
import subprocess
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

from tiktok_api import upload_to_tiktok

load_dotenv()

FREESOUND_API_KEY = os.getenv("FREESOUND_API_KEY", "")
UNSPLASH_API_KEY = os.getenv("UNSPLASH_API_KEY", "")
HISTORY_FILE = "history.txt"

WORK_DIR = Path("./temp")
WORK_DIR.mkdir(exist_ok=True)

SLOW_FACTOR = 0.85
REVERB_ROOM = 0.6
VIDEO_DURATION_MAX = 58

# En etkili TikTok lofi/slowed hashtagleri!
TIKTOK_TAGS = ["#lofi", "#slowed", "#reverbed", "#aesthetic", "#chillvibes", "#fyp", "#foryoupage", "#viral", "#slowedandreverbed", "#midnightvibes", "#music"]

SEARCH_QUERIES = [
    "ambient dreamy",
    "lofi chill",
    "ethereal piano",
    "soft guitar melody",
    "atmospheric synth",
    "melancholic instrumental",
]

IMAGE_QUERIES = [
    "aesthetic landscape",
    "lofi chill",
    "night city",
    "neon",
    "dreamy sky",
    "synthwave",
    "anime background"
]

def fetch_free_music():
    query = random.choice(SEARCH_QUERIES)
    print(f"[🔍] Freesound'da aranıyor: '{query}'")

    url = "https://freesound.org/apiv2/search/text/"
    params = {
        "query": query,
        "token": FREESOUND_API_KEY,
        "fields": "id,name,duration,previews,license",
        "filter": "duration:[15 TO 45] license:\"Creative Commons 0\"",
        "page_size": 20,
        "format": "json",
    }

    resp = requests.get(url, params=params)
    resp.raise_for_status()
    results = resp.json().get("results", [])

    if not results:
        raise Exception("Müzik bulunamadı!")

    history = set()
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            history = set(line.strip() for line in f)
            
    available_sounds = [s for s in results if str(s["id"]) not in history]
    if not available_sounds:
        raise Exception("Bu arama kelimesindeki tüm müzikler zaten kullanılmış! Bir sonraki çalışmada yeni terim denenecek.")

    sound = random.choice(available_sounds)
    sound_id = str(sound["id"])
    sound_name = sound["name"]
    print(f"[🎵] Seçilen: {sound_name} (ID: {sound_id})")
    
    with open(HISTORY_FILE, "a") as f:
        f.write(f"{sound_id}\n")

    detail_url = f"https://freesound.org/apiv2/sounds/{sound_id}/"
    detail = requests.get(detail_url, params={"token": FREESOUND_API_KEY}).json()
    download_url = detail["previews"]["preview-hq-mp3"]

    out_path = WORK_DIR / f"source_{sound_id}.mp3"
    with requests.get(download_url, stream=True) as r:
        r.raise_for_status()
        with open(out_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

    print(f"[✅] İndirildi: {out_path}")
    return out_path, sound_name

def fetch_background_image() -> Path:
    query = random.choice(IMAGE_QUERIES)
    print(f"[🔍] Unsplash'tan arka plan aranıyor: '{query}'")

    url = "https://api.unsplash.com/photos/random"
    headers = {"Authorization": f"Client-ID {UNSPLASH_API_KEY}"}
    params = {"query": query, "orientation": "portrait"}

    resp = requests.get(url, headers=headers, params=params)
    resp.raise_for_status()
    data = resp.json()

    img_url = data["urls"]["regular"]
    img_id = data["id"]
    
    print(f"[🖼️] Resim bulundu: {data['user']['name']} (ID: {img_id})")

    out_path = WORK_DIR / f"bg_{img_id}.jpg"
    with requests.get(img_url, stream=True) as r:
        r.raise_for_status()
        with open(out_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

    print(f"[✅] Arka plan indirildi: {out_path}")
    return out_path

def apply_slowed_reverbed(input_path: Path) -> Path:
    output_path = WORK_DIR / f"slowed_{input_path.stem}.mp3"

    tempo = SLOW_FACTOR
    if tempo < 0.5:
        atempo = f"atempo=0.707,atempo={tempo/0.707:.3f}"
    else:
        atempo = f"atempo={tempo}"

    aecho = f"aecho=0.8:{REVERB_ROOM}:60|80:0.4|0.3"
    filter_chain = f"{atempo},{aecho}"

    cmd = [
        "ffmpeg", "-y",
        "-i", str(input_path),
        "-af", filter_chain,
        "-q:a", "2",
        str(output_path)
    ]

    print(f"[🎚️] Slowed + reverbed uygulanıyor...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"FFmpeg hatası: {result.stderr}")

    print(f"[✅] Ses efekti tamamlandı: {output_path}")
    return output_path

def create_video(audio_path: Path, image_path: Path, title: str) -> Path:
    output_path = WORK_DIR / f"video_{audio_path.stem}.mp4"

    filter_complex = (
        "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920[bg];"
        "[1:a]showwaves=s=1080x360:mode=cline:rate=30:colors=0xFF69B4|0x9B59B6,colorkey=0x000000:0.1:0.1[wave];"
        "[bg][wave]overlay=0:780[outv]"
    )

    cmd = [
        "ffmpeg", "-y",
        "-loop", "1",
        "-i", str(image_path),
        "-i", str(audio_path),
        "-filter_complex", filter_complex,
        "-map", "[outv]",
        "-map", "1:a",
        "-c:v", "libx264",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        "-t", str(VIDEO_DURATION_MAX),
        "-pix_fmt", "yuv420p",
        str(output_path)
    ]

    print(f"[🎬] Video oluşturuluyor (Arka planlı)...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"FFmpeg video hatası: {result.stderr}")

    print(f"[✅] Video hazır: {output_path}")
    return output_path

def cleanup(files: list):
    for f in files:
        try:
            Path(f).unlink()
        except Exception:
            pass

def run():
    print(f"\n{'='*50}")
    print(f"  TikTok (Sadece) Müzik Botu — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*50}\n")

    temp_files = []

    try:
        source_path, sound_name = fetch_free_music()
        temp_files.append(source_path)

        bg_path = fetch_background_image()
        temp_files.append(bg_path)

        processed_path = apply_slowed_reverbed(source_path)
        temp_files.append(processed_path)

        video_path = create_video(processed_path, bg_path, sound_name)
        temp_files.append(video_path)

        clean_name = sound_name.replace(".wav", "").replace(".mp3", "").replace(".ogg", "")
        if len(clean_name) > 60:
            clean_name = clean_name[:60] + "..."
            
        title = f"{clean_name} (slowed) 🎧"
        
        # SADECE TIKTOK YÜKLEMESİ
        tiktok_desc = f"🎵 {title}\nUse headphones for best experience 🎧\n\n{' '.join(TIKTOK_TAGS)}"
        upload_to_tiktok(video_path, tiktok_desc)

        cleanup(temp_files)
        print("\n[🧹] Geçici dosyalar temizlendi.")
        print("[✨] Video TikTok'a yüklendi!\n")

    except Exception as e:
        print(f"\n[❌] Hata: {e}")
        cleanup(temp_files)
        raise

if __name__ == "__main__":
    run()
