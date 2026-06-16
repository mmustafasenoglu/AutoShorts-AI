from youtube_auth import get_youtube_service

def get_channel_stats():
    try:
        service = get_youtube_service()
        
        # Get the authenticated user's channel
        request = service.channels().list(
            part="snippet,statistics",
            mine=True
        )
        response = request.execute()
        
        if "items" in response and len(response["items"]) > 0:
            channel = response["items"][0]
            title = channel["snippet"]["title"]
            stats = channel["statistics"]
            
            print(f"Kanal Adı: {title}")
            print(f"Abone Sayısı: {stats.get('subscriberCount', 'Gizli')}")
            print(f"Toplam Görüntülenme: {stats.get('viewCount', '0')}")
            print(f"Toplam Video: {stats.get('videoCount', '0')}")
        else:
            print("Kanal bulunamadı.")
    except Exception as e:
        print(f"Hata oluştu: {e}")

if __name__ == "__main__":
    get_channel_stats()
