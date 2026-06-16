#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════╗
║         🎵  Lyrics Video Uploader  🎵            ║
║  Hazır lyrics videonu arka planı değiştirerek    ║
║  ya da direkt YouTube'a yükle.                   ║
╚══════════════════════════════════════════════════╝

Kullanım:
  python upload_lyrics.py                  ← interaktif mod (en kolay)
  python upload_lyrics.py --help           ← tüm seçenekler
"""

import os
import sys
import time
import shutil
import argparse
import subprocess
import requests
import asyncio
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

from youtube_auth import get_youtube_service, upload_video

load_dotenv()

UNSPLASH_API_KEY = os.getenv("UNSPLASH_API_KEY", "")
OUTPUT_DIR       = Path("./output")
OUTPUT_DIR.mkdir(exist_ok=True)

MUSIC_TAGS = [
    "lyrics", "lyricsvideo", "music", "song",
    "nowplaying", "viral", "trending", "spotify",
]

# ─────────────────────────────────────────────────────────────────────────────
# 1. Arka Plan: Unsplash'tan indir
# ─────────────────────────────────────────────────────────────────────────────
def download_background(query: str) -> Path:
    print(f"[🌅] Unsplash'tan arka plan indiriliyor: '{query}' ...")
    if not UNSPLASH_API_KEY:
        raise ValueError("UNSPLASH_API_KEY .env içinde tanımlı değil!")

    resp = requests.get(
        "https://api.unsplash.com/photos/random",
        headers={"Authorization": f"Client-ID {UNSPLASH_API_KEY}"},
        params={"query": query, "orientation": "landscape"},
        timeout=15,
    )
    resp.raise_for_status()
    img_url = resp.json()["urls"]["full"]
    img_id  = resp.json()["id"]

    out_path = OUTPUT_DIR / f"bg_{img_id}.jpg"
    with requests.get(img_url, stream=True, timeout=30) as r:
        r.raise_for_status()
        with open(out_path, "wb") as f:
            for chunk in r.iter_content(8192):
                f.write(chunk)
    print(f"[✅] Arka plan indirildi: {out_path.name}")
    return out_path


# ─────────────────────────────────────────────────────────────────────────────
# 2. Arka Plan Değiştirme (FFmpeg overlay)
#    Mevcut lyrics videosunun arka planını yeni bir görsel/videoyla değiştirir.
#    Yöntem: mevcut videonun parlaklık maskesini kullanarak foreground'u (metin)
#    yeni bg üzerine blend eder.
# ─────────────────────────────────────────────────────────────────────────────
def replace_background(src_video: Path, new_bg: Path, out_name: str, hide_logo_start: int = 0, hide_logo_end: int = 0, custom_text: str = "") -> Path:
    out_path = OUTPUT_DIR / f"{out_name}_new_bg.mp4"
    ext = new_bg.suffix.lower()

    if ext == ".mp4":
        bg_input = ["-stream_loop", "-1", "-i", str(new_bg)]
        bg_idx   = 1
    else:
        bg_input = ["-loop", "1", "-i", str(new_bg)]
        bg_idx   = 1

    fg_filter = "scale=1920:1080,setsar=1"
    if hide_logo_start > 0 or hide_logo_end > 0:
        box = f"drawbox=x=300:y=600:w=1320:h=350:color=black:t=fill:enable='between(t,{hide_logo_start},{hide_logo_end})'"
        fg_filter += f",{box}"
        
        if custom_text:
            # Siyah kutunun uzerine beyaz yazi ekle (lighten blend'de beyaz yazi gozukur)
            font_path = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
            text_filter = f"drawtext=fontfile='{font_path}':text='{custom_text}':fontcolor=white:fontsize=70:x=(w-text_w)/2:y=720:enable='between(t,{hide_logo_start},{hide_logo_end})'"
            fg_filter += f",{text_filter}"

    filter_complex = (
        f"[{bg_idx}:v]scale=1920:1080:force_original_aspect_ratio=increase,"
        f"crop=1920:1080,setsar=1[bg_scaled];"
        f"[0:v]{fg_filter}[fg];"
        f"[bg_scaled][fg]blend=all_mode=lighten[out]"
    )

    cmd = [
        "ffmpeg", "-y",
        "-i", str(src_video),
        *bg_input,
        "-filter_complex", filter_complex,
        "-map", "[out]",
        "-map", "0:a",
        "-c:v", "libx264",
        "-c:a", "aac",
        "-b:a", "320k",
        "-pix_fmt", "yuv420p",
        "-shortest",
        str(out_path),
    ]

    print("[🎬] Arka plan değiştiriliyor (FFmpeg)...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print("[⚠️] Blend modunda hata, fallback overlay deneniyor...")
        # Fallback: düz overlay (şeffaflık %60)
        filter_fallback = (
            f"[{bg_idx}:v]scale=1920:1080:force_original_aspect_ratio=increase,"
            f"crop=1920:1080,setsar=1[bg_scaled];"
            f"[0:v]scale=1920:1080,format=rgba,colorchannelmixer=aa=0.85[fg_alpha];"
            f"[bg_scaled][fg_alpha]overlay=0:0[out]"
        )
        cmd2 = [
            "ffmpeg", "-y",
            "-i", str(src_video),
            *bg_input,
            "-filter_complex", filter_fallback,
            "-map", "[out]",
            "-map", "0:a",
            "-c:v", "libx264",
            "-c:a", "aac",
            "-b:a", "320k",
            "-pix_fmt", "yuv420p",
            "-shortest",
            str(out_path),
        ]
        result2 = subprocess.run(cmd2, capture_output=True, text=True)
        if result2.returncode != 0:
            raise Exception(f"FFmpeg Hatası:\n{result2.stderr[-1000:]}")

    print(f"[✅] Yeni video hazır: {out_path}")
    return out_path


# ─────────────────────────────────────────────────────────────────────────────
# 3. Sadece mevcut videoyu kopyala (arka plan değişikliği yok)
# ─────────────────────────────────────────────────────────────────────────────
def prepare_video_no_change(src_video: Path, out_name: str) -> Path:
    out_path = OUTPUT_DIR / f"{out_name}_upload.mp4"
    shutil.copy2(src_video, out_path)
    print(f"[✅] Video kopyalandı: {out_path.name}")
    return out_path


# ─────────────────────────────────────────────────────────────────────────────
# 4. YouTube metadata oluştur
# ─────────────────────────────────────────────────────────────────────────────
def build_metadata(song: str, artist: str, extra_tags: list[str]) -> tuple[str, str, list[str]]:
    title = f"{artist} - {song} (Lyrics)"
    description = (
        f"🎵 {artist} — {song}\n\n"
        f"💿 Lyrics Video\n"
        f"🎧 Turn up the volume and enjoy!\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📌 All rights belong to their respective owners.\n"
        f"If you are the original creator and want this removed, please contact us.\n\n"
        f"#lyrics #{song.replace(' ', '')} #{artist.replace(' ', '')} #lyricsvideo #music"
    )
    tags = MUSIC_TAGS + [song.lower(), artist.lower()] + [t.lower() for t in extra_tags]
    tags = list(dict.fromkeys(tags))  # deduplicate
    return title, description, tags


def build_tiktok_caption(song: str, artist: str, extra_tags: list[str]) -> str:
    hashtags = ["#lyrics", "#music", f"#{song.replace(' ', '')}", f"#{artist.replace(' ', '')}", "#lyricsvideo"]
    for tag in extra_tags:
        clean_tag = tag.strip().replace(' ', '')
        if clean_tag:
            if not clean_tag.startswith('#'):
                clean_tag = f"#{clean_tag}"
            hashtags.append(clean_tag)
    hashtags = list(dict.fromkeys(hashtags))  # deduplicate
    return f"{artist} - {song} (Lyrics) " + " ".join(hashtags)


# ─────────────────────────────────────────────────────────────────────────────
# 5. İnteraktif prompt
# ─────────────────────────────────────────────────────────────────────────────
def ask(prompt: str, default: str = "") -> str:
    suffix = f" [{default}]" if default else ""
    val = input(f"  {prompt}{suffix}: ").strip()
    return val if val else default


def interactive_run():
    print("\n" + "═"*52)
    print("  🎵  Lyrics Video Uploader  🎵")
    print("═"*52 + "\n")

    # ── Video dosyası ──────────────────────────────────
    while True:
        video_path_str = ask("📁  Lyrics video dosya yolu (sürükle-bırak veya yaz)")
        video_path = Path(video_path_str.strip("'\""))
        if video_path.exists():
            break
        print(f"  [❌] Dosya bulunamadı: {video_path}")

    # ── Şarkı bilgileri ────────────────────────────────
    print()
    song   = ask("🎵  Şarkı adı")
    artist = ask("🎤  Sanatçı adı")
    extra  = ask("🏷️  Ekstra tag (virgülle ayır, boş bırakabilirsin)", "")
    extra_tags = [t.strip() for t in extra.split(",") if t.strip()]

    # ── Arka plan değişikliği ──────────────────────────
    print()
    change_bg = ask("🌅  Arka planı değiştirmek ister misin? (e/h)", "h").lower()
    new_bg_path = None

    if change_bg == "e":
        bg_choice = ask("   📂  Dosya yolu ver (boş = Unsplash'tan indir)", "")
        if bg_choice:
            new_bg_path = Path(bg_choice.strip("'\""))
            if not new_bg_path.exists():
                print(f"  [❌] Dosya bulunamadı, Unsplash'tan indirilecek.")
                new_bg_path = None

        if new_bg_path is None:
            bg_query = ask("   🔍  Unsplash arama kelimesi", "aesthetic sunset landscape")
            new_bg_path = download_background(bg_query)

    # ── Gizlilik ───────────────────────────────────────
    print()
    privacy_input = ask("🔒  Gizlilik (public / unlisted / private)", "public")
    privacy = privacy_input if privacy_input in ("public", "unlisted", "private") else "public"

    # ── İşleme ─────────────────────────────────────────
    print()
    out_name = f"lyrics_{int(time.time())}"
    if new_bg_path:
        final_video = replace_background(video_path, new_bg_path, out_name)
    else:
        final_video = prepare_video_no_change(video_path, out_name)

    # ── TikTok seçeneği ────────────────────────────────
    print()
    tiktok_confirm = ask("📱  TikTok'a da yüklensin mi? (e/h)", "h").lower()
    tiktok_headless = True
    if tiktok_confirm == "e":
        tiktok_headless = ask("   👁️  Tarayıcı arka planda mı çalışsın? (e/h)", "e").lower() == "e"

    # ── YouTube yükle ──────────────────────────────────
    title, description, tags = build_metadata(song, artist, extra_tags)
    print(f"\n[📝] Başlık: {title}")
    confirm = ask("   ✅  Yüklensin mi? (e/h)", "e").lower()
    if confirm != "e":
        print("  İptal edildi.")
        return

    service  = get_youtube_service()
    video_id = upload_video(service, final_video, title, description, tags, privacy)

    if video_id:
        print(f"\n🎉 YÜKLEME TAMAMLANDI!")
        print(f"   🔗 https://youtube.com/watch?v={video_id}")
    else:
        print("[❌] Yükleme başarısız.")

    if tiktok_confirm == "e":
        tiktok_caption = build_tiktok_caption(song, artist, extra_tags)
        print("\n[📱] TikTok yüklemesi başlatılıyor...")
        try:
            from tiktok_uploader import upload_tiktok_video
            tiktok_success = asyncio.run(upload_tiktok_video(str(final_video), tiktok_caption, headless=tiktok_headless))
            if tiktok_success:
                print("[✅] TikTok'a yükleme tamamlandı!")
            else:
                print("[❌] TikTok yüklemesi başarısız oldu.")
        except Exception as e:
            print(f"[❌] TikTok yüklemesi sırasında bir hata oluştu: {e}")


# ─────────────────────────────────────────────────────────────────────────────
# CLI argüman modu
# ─────────────────────────────────────────────────────────────────────────────
def parse_args():
    p = argparse.ArgumentParser(description="Lyrics Video YouTube Uploader")
    p.add_argument("--video",    required=True,  help="Lyrics video dosya yolu")
    p.add_argument("--song",     required=True,  help="Şarkı adı")
    p.add_argument("--artist",   required=True,  help="Sanatçı adı")
    p.add_argument("--bg",       default="",     help="Yeni arka plan dosya yolu (opsiyonel)")
    p.add_argument("--bg-query", default="",     help="Unsplash'tan arka plan indir (opsiyonel)")
    p.add_argument("--tags",     default="",     help="Ekstra tag, virgülle ayır")
    p.add_argument("--privacy",  default="public", choices=["public","unlisted","private"])
    p.add_argument("--hide-logo-start", type=int, default=0, help="Saniye olarak logonun başlangıcı")
    p.add_argument("--hide-logo-end", type=int, default=0, help="Saniye olarak logonun bitişi")
    p.add_argument("--custom-text", default="", help="Logo gizlenirken yazılacak custom metin")
    p.add_argument("--tiktok",   action="store_true", help="Aynı videoyu TikTok'a da yükle")
    p.add_argument("--tiktok-headless", action="store_true", help="TikTok tarayıcısını arka planda çalıştır")
    return p.parse_args()


def cli_run(args):
    print(f"\n🎵 {args.artist} — {args.song} | Lyrics Video Uploader\n")
    video_path = Path(args.video)
    if not video_path.exists():
        print(f"[❌] Video bulunamadı: {args.video}")
        sys.exit(1)

    new_bg_path = None
    if args.bg:
        new_bg_path = Path(args.bg)
    elif args.bg_query:
        new_bg_path = download_background(args.bg_query)

    out_name  = f"lyrics_{int(time.time())}"
    final_vid = replace_background(video_path, new_bg_path, out_name, args.hide_logo_start, args.hide_logo_end, args.custom_text) if new_bg_path \
                else prepare_video_no_change(video_path, out_name)

    extra_tags = [t.strip() for t in args.tags.split(",") if t.strip()]
    title, description, tags = build_metadata(args.song, args.artist, extra_tags)

    service  = get_youtube_service()
    video_id = upload_video(service, final_vid, title, description, tags, args.privacy)

    if video_id:
        print(f"\n🎉 YÜKLEME TAMAMLANDI!")
        print(f"   🔗 https://youtube.com/watch?v={video_id}")
    else:
        print("[❌] Yükleme başarısız.")

    if args.tiktok:
        tiktok_caption = build_tiktok_caption(args.song, args.artist, extra_tags)
        print("\n[📱] TikTok yüklemesi başlatılıyor...")
        try:
            from tiktok_uploader import upload_tiktok_video
            tiktok_success = asyncio.run(upload_tiktok_video(str(final_vid), tiktok_caption, headless=args.tiktok_headless))
            if tiktok_success:
                print("[✅] TikTok'a yükleme tamamlandı!")
            else:
                print("[❌] TikTok yüklemesi başarısız oldu.")
        except Exception as e:
            print(f"[❌] TikTok yüklemesi sırasında bir hata oluştu: {e}")


# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    if len(sys.argv) > 1:
        cli_run(parse_args())
    else:
        interactive_run()
