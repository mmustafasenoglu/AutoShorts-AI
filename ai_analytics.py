import os
from dotenv import load_dotenv
from groq import Groq
from youtube_auth import get_youtube_service

load_dotenv()

def get_recent_videos_stats():
    try:
        service = get_youtube_service()
        
        # 1. Get the 'uploads' playlist ID for the channel
        channel_request = service.channels().list(
            part="contentDetails",
            mine=True
        )
        channel_response = channel_request.execute()
        
        if not channel_response.get("items"):
            return None
            
        uploads_playlist_id = channel_response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
        
        # 2. Get the last 10 videos from the uploads playlist
        playlist_request = service.playlistItems().list(
            part="snippet",
            playlistId=uploads_playlist_id,
            maxResults=10
        )
        playlist_response = playlist_request.execute()
        
        if not playlist_response.get("items"):
            return []
            
        video_ids = []
        for item in playlist_response["items"]:
            video_ids.append(item["snippet"]["resourceId"]["videoId"])
            
        if not video_ids:
            return []
            
        # 3. Get statistics for these videos
        videos_request = service.videos().list(
            part="snippet,statistics",
            id=",".join(video_ids)
        )
        videos_response = videos_request.execute()
        
        stats_list = []
        for video in videos_response.get("items", []):
            title = video["snippet"]["title"]
            published_at = video["snippet"]["publishedAt"]
            stats = video["statistics"]
            
            view_count = stats.get("viewCount", 0)
            like_count = stats.get("likeCount", 0)
            comment_count = stats.get("commentCount", 0)
            
            stats_list.append({
                "title": title,
                "published_at": published_at,
                "views": view_count,
                "likes": like_count,
                "comments": comment_count
            })
            
        return stats_list
    except Exception as e:
        print(f"YouTube verileri çekilirken hata: {e}")
        return None

def analyze_channel_with_ai(stats_list):
    if not stats_list:
        return "Analiz edilecek video bulunamadı."
        
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return "Hata: GROQ_API_KEY bulunamadı."
        
    try:
        client = Groq(api_key=api_key)
        
        # Prepare data text
        data_text = "Son Videoların İstatistikleri:\n"
        for i, stat in enumerate(stats_list):
            data_text += f"{i+1}. Başlık: {stat['title']}\n"
            data_text += f"   Yayınlanma Tarihi: {stat['published_at']}\n"
            data_text += f"   İzlenme: {stat['views']}, Beğeni: {stat['likes']}, Yorum: {stat['comments']}\n\n"
            
        prompt = f"""Sen uzman bir YouTube kanal yöneticisi ve veri analistisin. 
Kullanıcının son videolarının istatistikleri aşağıda verilmiştir:

{data_text}

Bu verilere bakarak:
1. Videoların genel performansını değerlendir (Hangi tür başlıklar/videolar daha çok izlenmiş veya az izlenmiş).
2. Son yüklenen videoların izlenme durumuna göre olası sorunları (örneğin dikkat çekmeyen başlık vs.) tespit et.
3. İleriki videolar için başlık, içerik türü ve yükleme saatleri/zamanlaması hakkında 3 adet çok somut, aksiyon alınabilir tavsiye ver. 
4. Açıklamanı çok uzun tutma, net, arkadaş canlısı ("Kanka" vs. diyerek) ve motive edici bir dille yaz. Sadece Türkçe kullan. Formatı düzgün, okunaklı madde işaretleri ile hazırla.
"""

        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            max_tokens=600,
            temperature=0.7,
        )
        
        return chat_completion.choices[0].message.content.strip()
        
    except Exception as e:
        return f"Yapay Zeka Analiz Hatası: {str(e)}"
        
def perform_analysis():
    stats = get_recent_videos_stats()
    if stats is None or len(stats) == 0:
        return "YouTube kanalında video bulunamadı veya bilgilere erişilemedi."
        
    return analyze_channel_with_ai(stats)
