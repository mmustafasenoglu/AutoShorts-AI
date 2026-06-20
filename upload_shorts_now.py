from youtube_auth import get_youtube_service, upload_video
import os
import re

def main():
    service = get_youtube_service()

    # Video dosyası
    video_dir = 'videos'
    video_files = [f for f in os.listdir(video_dir) if f.endswith('.mp4')]

    if not video_files:
        print("[!] Videos klasöründe mp4 dosyası bulunamadı.")
        return

    video_file = video_files[0]
    video_path = os.path.join(video_dir, video_file)
    print(f"[*] Video bulundu: {video_path}")

    # Dosya adından temiz bir başlık üret
    name = os.path.splitext(video_file)[0]
    # Çok uzun veya anlamsız dosya adı ise kısa bir başlık koy
    if len(name) > 60 or re.match(r'^[A-Za-z0-9_\-]{30,}$', name):
        title = "🔥 Viral Clip #Shorts"
    else:
        clean = re.sub(r'[^\w\s]', ' ', name).strip()
        if len(clean) > 92:
            clean = clean[:89] + "..."
        title = f"{clean} #Shorts"

    description = f"{title}\n\n#shorts #viral #trending #fyp #edit"
    tags = ["shorts", "viral", "trending", "fyp", "edit", "tiktok"]

    print(f"[*] Başlık: {title}")
    print(f"[*] Açıklama: {description}")
    print(f"[*] Tags: {tags}")
    print(f"[*] YouTube'a yükleniyor (Public)...")

    video_id = upload_video(service, video_path, title, description, tags, privacy="public")

    if video_id:
        print(f"\n✅ Yükleme Başarılı!")
        print(f"🔗 URL: https://youtube.com/shorts/{video_id}")
    else:
        print("\n❌ Yükleme başarısız.")

if __name__ == "__main__":
    main()
