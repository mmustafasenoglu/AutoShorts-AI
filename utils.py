import os
from groq import Groq
from dotenv import load_dotenv

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


def ensure_shorts_tag(title, tags, duration, url=""):
    is_tiktok_or_insta = "tiktok.com" in url.lower() or "instagram.com" in url.lower() if url else False
    
    if tags is None:
        tags = []
    
    append_shorts = False
    if (duration <= 60 or is_tiktok_or_insta) and "#shorts" not in title.lower():
        append_shorts = True
        if "shorts" not in [t.lower() for t in tags]:
            tags.append("shorts")
    
    if append_shorts:
        if len(title) > 92:
            title = title[:89] + "..."
        title = f"{title} #Shorts"
    else:
        if len(title) > 100:
            title = title[:97] + "..."
    
    return title, tags


def download_video(url, ydl_opts):
    import yt_dlp
    
    os.makedirs('videos', exist_ok=True)
    
    print(f"[*] Bilgiler çekiliyor: {url}")
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        title = info.get('title', 'Bilinmeyen Başlık')
        description = info.get('description', '')
        tags = info.get('tags', []) or []
        duration = info.get('duration', 0)
        
        title, tags = ensure_shorts_tag(title, tags, duration, url)
        
        print(f"[*] Video indiriliyor: {title}")
        info = ydl.extract_info(url, download=True)
        
        filename = ydl.prepare_filename(info)
        base, _ = os.path.splitext(filename)
        expected_filename = f"{base}.mp4"
        
        if os.path.exists(expected_filename):
            filename = expected_filename
        elif not os.path.exists(filename):
            raise Exception(f"İndirilen dosya bulunamadı: {filename}")
    
    return {
        "title": title,
        "description": description,
        "tags": tags,
        "duration": duration,
        "filename": filename
    }
