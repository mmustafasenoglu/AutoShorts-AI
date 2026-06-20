import os
import sys
import yt_dlp
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
from groq import Groq
from youtube_auth import get_youtube_service
from googleapiclient.http import MediaFileUpload

load_dotenv()

def rewrite_description_with_groq(original_description, title):
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("[!] GROQ_API_KEY bulunamadı, orijinal açıklama kullanılacak.")
        return original_description
    try:
        client = Groq(api_key=api_key)
        desc_snippet = original_description[:1000] if original_description else ""
        prompt = f"""You are a YouTube content creator. Rewrite the following YouTube video description to be similar in theme and tone but completely original. 
Keep any hashtags (#) and relevant keywords. Remove any channel-specific links, promotional text, or references to other people's channels. 
Keep it natural, engaging, and under 500 characters. Use the same language as the original description.

Video Title: {title}
Original Description:
{desc_snippet}

Write only the new description, nothing else."""
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            max_tokens=300,
            temperature=0.7,
        )
        new_description = chat_completion.choices[0].message.content.strip()
        print(f"[🤖] Groq ile açıklama yeniden yazıldı.")
        return new_description
    except Exception as e:
        print(f"[!] Groq hatası: {e}. Orijinal açıklama kullanılacak.")
        return original_description


def upload_scheduled(service, video_path, title, description, tags, publish_at_iso):
    """Upload video as private with a scheduled publishAt time."""
    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": "10",  # Music
        },
        "status": {
            "privacyStatus": "private",
            "publishAt": publish_at_iso,       # YouTube Schedule!
            "selfDeclaredMadeForKids": False,
        },
    }
    media = MediaFileUpload(str(video_path), mimetype="video/mp4", resumable=True)
    req = service.videos().insert(part="snippet,status", body=body, media_body=media)

    response = None
    import time, httplib2
    from googleapiclient.errors import HttpError

    retries = 0
    max_retries = 10
    print("[📤] YouTube'a yükleniyor (scheduled)...")
    while response is None:
        try:
            status, response = req.next_chunk()
            if status:
                pct = int(status.progress() * 100)
                print(f"\r    ⏳ %{pct}", end="", flush=True)
            retries = 0
        except (httplib2.HttpLib2Error, IOError) as e:
            if retries >= max_retries:
                raise e
            time.sleep(2 ** retries)
            retries += 1
        except HttpError as e:
            if e.resp.status in [500, 502, 503, 504]:
                if retries >= max_retries:
                    raise e
                time.sleep(2 ** retries)
                retries += 1
            else:
                raise e
    print()
    return response.get("id")


def main():
    url = sys.argv[1] if len(sys.argv) > 1 else "https://youtube.com/shorts/RJ6-qKa5Ovs?si=XByvWMdbDrHeP1on"

    # --- Hedef saat: bugün 21:00 (UTC+3 = Istanbul) ---
    istanbul_tz = timezone(timedelta(hours=3))
    now = datetime.now(istanbul_tz)
    publish_local = now.replace(hour=21, minute=0, second=0, microsecond=0)
    if publish_local <= now:
        print("[!] 21:00 geçmiş, yarına ayarlanıyor.")
        publish_local += timedelta(days=1)
    # YouTube API RFC3339 formatında UTC ister
    publish_utc = publish_local.astimezone(timezone.utc)
    publish_at_iso = publish_utc.strftime("%Y-%m-%dT%H:%M:%S.000Z")
    print(f"[⏰] Yayın zamanı: {publish_local.strftime('%d.%m.%Y %H:%M')} (İstanbul) → {publish_at_iso} (UTC)")

    # --- İndir ---
    os.makedirs('videos', exist_ok=True)
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': 'videos/%(title)s.%(ext)s',
        'noplaylist': True,
        'merge_output_format': 'mp4',
        'quiet': False,
    }

    print(f"[*] Bilgiler çekiliyor: {url}")
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
        except Exception as e:
            print(f"[!] Video bilgileri alınamadı: {e}")
            return

        title = info.get('title', 'Bilinmeyen Başlık')
        description = info.get('description', '')
        tags = info.get('tags', []) or []
        duration = info.get('duration', 0)

        if duration <= 60 and "#shorts" not in title.lower():
            if len(title) > 92:
                title = title[:89] + "..."
            title = f"{title} #Shorts"
            if "shorts" not in [t.lower() for t in tags]:
                tags.append("shorts")
        elif len(title) > 100:
            title = title[:97] + "..."

        print(f"[🤖] Açıklama Groq AI ile yeniden yazılıyor...")
        description = rewrite_description_with_groq(description, title)

        print(f"[*] Video indiriliyor: {title}")
        try:
            info = ydl.extract_info(url, download=True)
        except Exception as e:
            print(f"[!] Video indirilemedi: {e}")
            return

        filename = ydl.prepare_filename(info)
        base, _ = os.path.splitext(filename)
        expected_filename = f"{base}.mp4"
        if os.path.exists(expected_filename):
            filename = expected_filename
        elif not os.path.exists(filename):
            print(f"[!] İndirilen dosya bulunamadı: {filename}")
            return

    # --- YouTube'a scheduled olarak yükle ---
    service = get_youtube_service()
    try:
        video_id = upload_scheduled(service, filename, title, description, tags, publish_at_iso)
        if video_id:
            print(f"\n✅ Zamanlama Başarılı!")
            print(f"📅 Yayın: {publish_local.strftime('%d.%m.%Y %H:%M')} İstanbul")
            print(f"🔗 URL: https://youtube.com/shorts/{video_id}")
            try:
                os.remove(filename)
                print(f"[*] Yerel dosya silindi: {filename}")
            except:
                pass
        else:
            print("❌ Yükleme başarısız.")
    except Exception as e:
        print(f"[!] Hata: {e}")


if __name__ == "__main__":
    main()
