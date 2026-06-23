import os
import sys
from dotenv import load_dotenv
from youtube_auth import get_youtube_service, upload_video
from utils import rewrite_description_with_groq, download_video

load_dotenv()

def download_and_upload(url):
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': 'videos/%(title)s.%(ext)s',
        'noplaylist': True,
        'merge_output_format': 'mp4',
        'quiet': False
    }
    
    try:
        result = download_video(url, ydl_opts)
        title = result["title"]
        description = rewrite_description_with_groq(result["description"], title)
        filename = result["filename"]
    except Exception as e:
        print(f"[!] Video indirilemedi: {e}")
        return
    
    print(f"[*] YouTube'a Yükleniyor...")
    service = get_youtube_service()
    
    try:
        video_id = upload_video(service, filename, title, description, result["tags"], privacy="public")
        if video_id:
            if result["duration"] <= 60 or "tiktok.com" in url.lower() or "instagram.com" in url.lower():
                print(f"[+] Yükleme Başarılı! URL: https://youtube.com/shorts/{video_id}")
            else:
                print(f"[+] Yükleme Başarılı! URL: https://youtube.com/watch?v={video_id}")
            try:
                os.remove(filename)
                print(f"[*] Yerel dosya silindi: {filename}")
            except Exception as e:
                print(f"[!] Yerel dosya silinirken hata oluştu: {e}")
        else:
            print("[!] Yükleme başarısız.")
    except Exception as e:
        print(f"[!] Yükleme sırasında hata oluştu: {e}")

def main():
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        try:
            url = input("Klonlanacak YouTube URL'sini girin: ")
        except KeyboardInterrupt:
            print("\nİşlem iptal edildi.")
            return
            
    if not url.strip():
        print("[!] Geçerli bir URL girmediniz.")
        return
        
    download_and_upload(url.strip())

if __name__ == "__main__":
    main()
