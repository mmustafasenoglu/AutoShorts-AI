import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

CLIENT_SECRET = "client_secret.json"
TOKEN_FILE    = "token.json"
SCOPES        = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.force-ssl",
]

def get_youtube_service():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception:
                creds = None
        if not creds:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, "w") as f:
            f.write(creds.to_json())
    return build("youtube", "v3", credentials=creds)


def upload_video(service, video_path, title, description, tags, privacy="public"):
    from googleapiclient.http import MediaFileUpload
    body = {
        "snippet": {
            "title":       title,
            "description": description,
            "tags":        tags,
            "categoryId":  "10",  # Music
        },
        "status": {
            "privacyStatus":           privacy,
            "selfDeclaredMadeForKids": False,
        },
    }
    media = MediaFileUpload(str(video_path), mimetype="video/mp4", resumable=True)
    req   = service.videos().insert(part="snippet,status", body=body, media_body=media)

    response = None
    print("[📤] YouTube'a yükleniyor...")
    
    import time
    import httplib2
    from googleapiclient.errors import HttpError
    
    retries = 0
    max_retries = 10
    
    while response is None:
        try:
            status, response = req.next_chunk()
            if status:
                pct = int(status.progress() * 100)
                print(f"\r    ⏳ %{pct}", end="", flush=True)
            retries = 0
        except (httplib2.HttpLib2Error, IOError) as e:
            if retries >= max_retries:
                raise e
            print(f"\n[Ağ Hatası] {e}. {2**retries} sn sonra yeniden deneniyor...")
            time.sleep(2 ** retries)
            retries += 1
        except HttpError as e:
            if e.resp.status in [500, 502, 503, 504]:
                if retries >= max_retries:
                    raise e
                print(f"\n[Sunucu Hatası] {e.resp.status}. {2**retries} sn sonra yeniden deneniyor...")
                time.sleep(2 ** retries)
                retries += 1
            else:
                raise e
    print()
    return response.get("id")
