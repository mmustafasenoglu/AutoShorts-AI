import os
import sys
import yt_dlp
from dotenv import load_dotenv
from groq import Groq
from youtube_auth import get_youtube_service, upload_video

load_dotenv()

def rewrite_description_with_groq(original_description, title):
    """Use Groq AI to rewrite the description to be similar but unique."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("[!] GROQ_API_KEY bulunamadı, orijinal açıklama kullanılacak.")
        return original_description

    try:
        client = Groq(api_key=api_key)

        # Keep description concise - take first 1000 chars to avoid token limits
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

def download_and_upload(url):
    # Ensure videos directory exists
    os.makedirs('videos', exist_ok=True)
    
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': 'videos/%(title)s.%(ext)s',
        'noplaylist': True,
        'merge_output_format': 'mp4',
        'quiet': False
    }
    
    print(f"[*] Bilgiler çekiliyor: {url}")
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        # First, extract info to understand the metadata
        try:
            info = ydl.extract_info(url, download=False)
        except Exception as e:
            print(f"[!] Video bilgileri alınamadı: {e}")
            return
            
        title = info.get('title', 'Bilinmeyen Başlık')
        description = info.get('description', '')
        tags = info.get('tags', [])
        duration = info.get('duration', 0)
        is_tiktok_or_insta = "tiktok.com" in url.lower() or "instagram.com" in url.lower()
        
        # Shorts detection and tag insertion
        if (duration <= 60 or is_tiktok_or_insta) and "#shorts" not in description.lower() and "#shorts" not in title.lower():
            title = f"{title} #Shorts"
            if tags is None:
                tags = []
            if "shorts" not in [t.lower() for t in tags]:
                tags.append("shorts")
                
        # Limit description and title length if necessary (YouTube limits: Title 100, Description 5000)
        if len(title) > 100:
            title = title[:97] + "..."

        # Rewrite description using Groq AI to make it similar but unique
        print(f"[🤖] Açıklama Groq AI ile yeniden yazılıyor...")
        description = rewrite_description_with_groq(description, title)
            
        print(f"[*] Video İndiriliyor: {title}")
        # Download the video
        try:
            info = ydl.extract_info(url, download=True)
        except Exception as e:
            print(f"[!] Video indirilemedi: {e}")
            return
            
        # The actual filename might have been altered by merge_output_format
        filename = ydl.prepare_filename(info)
        base, _ = os.path.splitext(filename)
        expected_filename = f"{base}.mp4"
        
        if os.path.exists(expected_filename):
            filename = expected_filename
        elif not os.path.exists(filename):
            print(f"[!] İndirilen dosya bulunamadı: {filename}")
            return
            
    print(f"[*] YouTube'a Yükleniyor...")
    service = get_youtube_service()
    
    try:
        video_id = upload_video(service, filename, title, description, tags, privacy="public")
        if video_id:
            if duration <= 60 or is_tiktok_or_insta:
                print(f"[+] Yükleme Başarılı! URL: https://youtube.com/shorts/{video_id}")
            else:
                print(f"[+] Yükleme Başarılı! URL: https://youtube.com/watch?v={video_id}")
                
            # Clean up the file
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
