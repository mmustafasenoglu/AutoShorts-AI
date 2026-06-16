# 🎵 Lyrics Video Uploader & AutoShorts-AI Bot

This project is a Python automation tool that allows you to optionally change the backgrounds of your pre-made "Lyrics" videos and automatically upload them directly to your YouTube and TikTok accounts. It also includes an AI-powered Channel Analytics feature to evaluate your channel's performance.

## 🚀 Features

- **Interactive and CLI Mode:** You can use it via command line arguments or follow the interactive prompts on the screen.
- **Dual Platform Support (YouTube & TikTok):** Upload your prepared videos automatically to both YouTube Shorts and TikTok simultaneously or separately. Uses Playwright for TikTok browser automation.
- **Automatic Background Replacement:** Uses the Unsplash API to download aesthetic images matching the song's mood or a keyword you provide. It blends this new image with your existing black-background lyrics video using `ffmpeg`.
- **Local Backgrounds:** You can also set a local photo or video from your computer as the background.
- **Smart Metadata Generation:** Automatically creates SEO-friendly titles, descriptions, YouTube Tags, and TikTok Captions/Tags by combining the song name, artist name, and tags you provide.
- **Logo Hiding (Optional):** If the original video has an unwanted watermark or logo, you can obscure this area by placing a black bar or writing text over it between specific timestamps.
- **AI Channel Analytics (GUI):** A built-in PyQt6 desktop interface that integrates with Groq AI to analyze your recent YouTube uploads (views, likes) and provide smart recommendations on titles, posting times, and content strategy.
- **TikTok & Instagram Support:** Automatically detects TikTok and Instagram video links via `yt-dlp` and enforces them to be uploaded as Shorts.

## 📂 Project Structure

- `app_gui.py` : The main Desktop GUI application. Provides a user-friendly interface to paste links, view logs, and run AI channel analytics.
- `ai_analytics.py` : Connects to YouTube API to fetch recent video stats and uses Groq AI to provide insights and recommendations.
- `clone_youtube.py` : Uses `yt-dlp` to download a video from YouTube, TikTok, or Instagram, automatically rewrites its description using Groq AI, and uploads it back to your channel.
- `upload_lyrics.py` : The main CLI automation script for downloading, rendering (`ffmpeg`), and managing YouTube and TikTok uploads.
- `tiktok_auth.py` : A helper script that lets you manually log in to TikTok before the first use.
- `tiktok_uploader.py` : The core Playwright module that handles automatic video uploading and sharing to TikTok Studio.
- `youtube_auth.py` : Handles YouTube API OAuth 2.0 authentication and core video uploading logic.
- `upload_one_video.py` : A simple helper script to quickly upload a single video to YouTube without modifying the background.
- `videos/` : The directory where you can place your original lyrics videos or where downloaded videos are stored.
- `output/` : The directory where final rendered videos with replaced backgrounds are saved.
- `backgrounds/` : The directory for storing your custom background files.
- `client_secret.json` : Your YouTube Data API v3 authorization file obtained via Google Cloud Console.
- `.env` : Configuration file containing private keys such as Unsplash API and Groq API keys.

## ⚙️ Setup and Requirements

For the system to work properly, you need the following tools installed on your computer:

1. **Python 3.x**
2. **FFmpeg:** Required for video rendering and background blending.
   - For macOS: `brew install ffmpeg`
3. **Python Libraries:** Open a terminal in the project folder and install the required packages:
   ```bash
   pip install PyQt6 yt-dlp groq requests python-dotenv google-api-python-client google-auth-httplib2 google-auth-oauthlib playwright
   ```
4. **Playwright Setup (For TikTok):**
   - Install the Playwright browser binaries:
     ```bash
     playwright install chromium
     ```
5. **Google Cloud / YouTube API:**
   - Create a project on Google Cloud and enable the `YouTube Data API v3`.
   - Create `OAuth 2.0 Client IDs`, download the JSON file, and place it in this folder named `client_secret.json`.
6. **Unsplash API & Groq API:**
   - To automatically download images, get an API key from [Unsplash Developers](https://unsplash.com/developers) and add it to your `.env` file.
   - To use AI features, get a Groq API key from [Groq Console](https://console.groq.com) and add it to your `.env` file (`GROQ_API_KEY=...`).

---

## 🎮 Usage

### 1. GUI Mode (Recommended)
You can launch the PyQt6 Desktop Interface to easily download and upload videos, and analyze your channel with AI:
```bash
python app_gui.py
```
- Paste a YouTube, TikTok, or Instagram link.
- Click "İndir & Yükle" (Download & Upload) to process the video.
- Click "Kanal Analizi Yap 🤖" (Run Channel Analytics) to get AI recommendations based on your recent video performance.

### 2. Interactive CLI Mode
Open the terminal and run the main upload script. The script will guide you step-by-step:
```bash
python upload_lyrics.py
```

### 3. Command Line (CLI) Mode
If you are doing batch processing, you can pass arguments externally.

**Uploading to both YouTube and TikTok:**
```bash
python upload_lyrics.py --video "videos/song.mp4" --song "Self Aware" --artist "Temper City" --tags "speedup,trend" --bg-query "neon city" --privacy "public" --tiktok
```

*To run the TikTok browser silently in the background, add the `--tiktok-headless` parameter.*

To view all commands:
```bash
python upload_lyrics.py --help
```

## ⚠️ Important Notes

- On the first run, the YouTube API will request authorization and open a Google login page in your browser. After granting permission, the generated `token.json` file will allow password-less logins for subsequent uses.
- `ffmpeg` uses a blend mode. For best results, it's recommended that your original lyrics video has a solid black background.
- For the TikTok uploader to work properly, the `.tiktok_session` folder must not be deleted. If your session expires or you encounter errors, you can run `python tiktok_auth.py` to log in again.
