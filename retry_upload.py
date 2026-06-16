from youtube_auth import get_youtube_service, upload_video
import os

def main():
    service = get_youtube_service()
    video_path = "output/lyrics_1780923994_new_bg.mp4"
    title = "Empire of the Sun - We Are The People (Lyrics) 🌅"
    description = "🎵 Empire of the Sun — We Are The People\n\n💿 Lyrics Video\n🎧 Turn up the volume and enjoy!\n\n#lyrics #wearethepeople #empireofthesun #lyricsvideo #music #speedup"
    tags = ["lyrics", "wearethepeople", "empireofthesun", "speedup", "sped up", "music", "lyricsvideo"]
    
    if not os.path.exists(video_path):
        print(f"Video bulunamadı: {video_path}")
        return
        
    print(f"Uploading {video_path}...")
    try:
        video_id = upload_video(service, video_path, title, description, tags, privacy="public")
        if video_id:
            print(f"Yükleme Başarılı! URL: https://youtube.com/watch?v={video_id}")
    except Exception as e:
        print(f"Hata: {e}")

if __name__ == "__main__":
    main()
