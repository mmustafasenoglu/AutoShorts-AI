from youtube_auth import get_youtube_service, upload_video
import os

def main():
    service = get_youtube_service()
    video_path = 'videos/vidssave.com I made millions. | better call Saul #edit #shorts#movie #breakingbad#bettercallsaul#saulgoodman 720P.mp4'
    
    quote = 'I made millions. | Better Call Saul 🤑'
    
    title = f"{quote} #Shorts"
    description = f"{quote}\n\n#edit #shorts #movie #breakingbad #bettercallsaul #saulgoodman"
    tags = ["edit", "shorts", "movie", "breakingbad", "bettercallsaul", "saulgoodman", "AMC", "viral"]

    
    if not os.path.exists(video_path):
        print(f"Video bulunamadı: {video_path}")
        return
        
    print(f"Uploading {video_path}...")
    video_id = upload_video(service, video_path, title, description, tags, privacy="public")
    if video_id:
        print(f"Yükleme Başarılı! URL: https://youtube.com/shorts/{video_id}")
    else:
        print("Yükleme başarısız.")

if __name__ == "__main__":
    main()
