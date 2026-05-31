import os
from pathlib import Path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

YOUTUBE_CLIENT_SECRET = "client_secret.json"
SCOPES = ["https://www.googleapis.com/auth/youtube.upload", "https://www.googleapis.com/auth/youtube.force-ssl"]

def get_youtube_service():
    creds = None
    token_file = "token.json"
    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(YOUTUBE_CLIENT_SECRET, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_file, "w") as f:
            f.write(creds.to_json())
    return build("youtube", "v3", credentials=creds)

def upload_to_youtube(service, video_path: Path, title: str, description: str, tags: list, category_id: str):
    print(f"[📤] YouTube'a yükleniyor (YouTube API) ...")
    
    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": category_id,
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False,
        },
    }

    media = MediaFileUpload(str(video_path), mimetype="video/mp4", resumable=True)
    request = service.videos().insert(part="snippet,status", body=body, media_body=media)

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"[⏳] Yükleme: %{int(status.progress() * 100)}")

    video_id = response.get("id")
    print(f"[🎉] Yüklendi! https://youtube.com/watch?v={video_id}")
    return video_id

def add_first_comment(service, video_id, text):
    print(f"[💬] Videoya ilk yorum atılıyor: '{text}'")
    try:
        request = service.commentThreads().insert(
            part="snippet",
            body={
                "snippet": {
                    "videoId": video_id,
                    "topLevelComment": {
                        "snippet": {
                            "textOriginal": text
                        }
                    }
                }
            }
        )
        request.execute()
        print("[✅] İlk yorum başarıyla eklendi!")
    except Exception as e:
        print(f"[⚠️] Yorum eklenirken hata oluştu: {e}")
