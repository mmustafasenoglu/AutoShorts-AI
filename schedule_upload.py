import os
import sys
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
from youtube_auth import get_youtube_service
from googleapiclient.http import MediaFileUpload
from utils import rewrite_description_with_groq, download_video

load_dotenv()


def upload_scheduled(service, video_path, title, description, tags, publish_at_iso):
    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": "10",
        },
        "status": {
            "privacyStatus": "private",
            "publishAt": publish_at_iso,
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
    url = sys.argv[1] if len(sys.argv) > 1 else input("YouTube URL'sini girin: ")

    istanbul_tz = timezone(timedelta(hours=3))
    now = datetime.now(istanbul_tz)
    publish_local = now.replace(hour=21, minute=0, second=0, microsecond=0)
    if publish_local <= now:
        print("[!] 21:00 geçmiş, yarına ayarlanıyor.")
        publish_local += timedelta(days=1)
    publish_utc = publish_local.astimezone(timezone.utc)
    publish_at_iso = publish_utc.strftime("%Y-%m-%dT%H:%M:%S.000Z")
    print(f"[⏰] Yayın zamanı: {publish_local.strftime('%d.%m.%Y %H:%M')} (İstanbul) → {publish_at_iso} (UTC)")

    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': 'videos/%(title)s.%(ext)s',
        'noplaylist': True,
        'merge_output_format': 'mp4',
        'quiet': False,
    }

    try:
        result = download_video(url, ydl_opts)
        title = result["title"]
        description = rewrite_description_with_groq(result["description"], title)
        filename = result["filename"]
    except Exception as e:
        print(f"[!] Video indirilemedi: {e}")
        return

    service = get_youtube_service()
    try:
        video_id = upload_scheduled(service, filename, title, description, result["tags"], publish_at_iso)
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
