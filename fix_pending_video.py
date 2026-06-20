from youtube_auth import get_youtube_service

def list_recent_videos(service, max_results=10):
    """Son yüklenen videoları listele"""
    response = service.channels().list(part="contentDetails", mine=True).execute()
    uploads_playlist = response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

    playlist_response = service.playlistItems().list(
        part="snippet",
        playlistId=uploads_playlist,
        maxResults=max_results
    ).execute()

    video_ids = [item["snippet"]["resourceId"]["videoId"] for item in playlist_response["items"]]
    return video_ids

def get_video_details(service, video_ids):
    """Video detaylarını getir (status dahil)"""
    response = service.videos().list(
        part="snippet,status,processingDetails",
        id=",".join(video_ids)
    ).execute()
    return response["items"]

def force_publish_video(service, video_id, current_title):
    """Videoyu herkese açık yap"""
    service.videos().update(
        part="status",
        body={
            "id": video_id,
            "status": {
                "privacyStatus": "public",
                "selfDeclaredMadeForKids": False
            }
        }
    ).execute()
    print(f"✅ Video yayınlandı: '{current_title}'")
    print(f"   🔗 https://youtube.com/watch?v={video_id}")

def main():
    print("🔐 YouTube'a bağlanılıyor...")
    service = get_youtube_service()

    print("📋 Son videolar getiriliyor...")
    video_ids = list_recent_videos(service, max_results=10)
    videos = get_video_details(service, video_ids)

    print(f"\n{'='*60}")
    print(f"{'BAŞLIK':<40} {'DURUM':<15} {'İŞLEM'}")
    print(f"{'='*60}")

    pending_videos = []
    for v in videos:
        vid_id    = v["id"]
        title     = v["snippet"]["title"][:38]
        privacy   = v["status"]["privacyStatus"]
        upload_st = v["status"].get("uploadStatus", "?")
        proc      = v.get("processingDetails", {}).get("processingStatus", "-")

        durum = f"{upload_st}/{privacy}"
        print(f"{title:<40} {durum:<15} proc={proc}")

        # Beklemede veya işlenmekte olan public videoları bul
        if upload_st in ("uploaded", "processed") and privacy != "public":
            pending_videos.append(v)
        elif upload_st == "uploaded" and privacy == "public":
            pending_videos.append(v)  # yüklenmiş ama henüz işlenmemiş

    print(f"{'='*60}\n")

    # Sadece 'uploaded' durumundaki (işlenmeyi bekleyen) videoları göster
    candidates = [v for v in videos if v["status"].get("uploadStatus") == "uploaded"]

    if not candidates:
        # Tüm public olmayanları göster
        candidates = [v for v in videos if v["status"]["privacyStatus"] != "public"]

    if not candidates:
        print("🎉 Bekleyen veya gizli video bulunamadı, hepsi zaten yayında!")
        return

    print(f"⚠️  {len(candidates)} adet bekleyen/gizli video bulundu:\n")
    for i, v in enumerate(candidates):
        print(f"  [{i+1}] {v['snippet']['title']}")
        print(f"       ID: {v['id']} | Durum: {v['status'].get('uploadStatus')} / {v['status']['privacyStatus']}")

    print()
    choice = input("Hangi videoyu yayınlamak istiyorsun? (numara gir, hepsi için 'h', çıkış için 'q'): ").strip()

    if choice.lower() == 'q':
        print("İptal edildi.")
        return
    elif choice.lower() == 'h':
        for v in candidates:
            force_publish_video(service, v["id"], v["snippet"]["title"])
    else:
        try:
            idx = int(choice) - 1
            v = candidates[idx]
            force_publish_video(service, v["id"], v["snippet"]["title"])
        except (ValueError, IndexError):
            print("❌ Geçersiz seçim.")

if __name__ == "__main__":
    main()
