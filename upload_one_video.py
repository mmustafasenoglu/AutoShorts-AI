from youtube_auth import get_youtube_service, upload_video
import os

def main():
    service = get_youtube_service()
    video_path = 'videos/vidssave.com ｄｙｉｎｇ ａｌｏｎｅ 1080P.mp4'
    
    title = 'dying alone'
    description = """dying alone

━━━━━━━━━━━━━━━━━━━━━━
#music #edit #cinematic #dyingalone #bojackhorseman"""
    
    tags = [
        "dying alone", "music", "edit", "cinematic", "bojack horseman", "bojack"
    ]
    
    if not os.path.exists(video_path):
        print(f"Video bulunamadı: {video_path}")
        return
        
    print(f"Uploading {video_path}...")
    video_id = upload_video(service, video_path, title, description, tags, privacy="public")
    if video_id:
        print(f"Yükleme Başarılı! URL: https://youtube.com/watch?v={video_id}")

if __name__ == "__main__":
    main()
