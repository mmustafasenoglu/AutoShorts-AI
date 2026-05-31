# 🤖 AutoShorts-AI: Fully Automated YouTube Shorts Generator & Uploader 🚀

Welcome to **AutoShorts-AI**, a complete Python-based automation tool that tracks the latest Artificial Intelligence news, dynamically generates vertical videos (Shorts) with aesthetic backgrounds and ambient music, and uploads them directly to your YouTube channel—all without any manual intervention!

## 🌟 Why AutoShorts-AI?
Managing a YouTube channel can be time-consuming. This bot is designed for creators, developers, and tech enthusiasts who want to establish a continuous presence on YouTube with minimal effort. It handles everything from content curation to video rendering and API uploading.

## 📂 Project Structure Explained
Our modular architecture keeps the code clean and manageable:

- `news_bot.py`: The core engine. It fetches the news, downloads media, generates the video using FFmpeg, and orchestrates the YouTube upload process.
- `youtube_api.py`: A dedicated module handling the complex OAuth 2.0 authentication and the payload structure required by the YouTube Data API v3.
- `scheduler.py`: A utility script that allows you to run the bot continuously on a server or local machine. It acts as a cronjob, executing the upload task automatically every day at a specified time.

## ⚙️ Detailed Features

1. **📰 AI News Scraping:** Automatically pulls the latest headlines regarding OpenAI, ChatGPT, Anthropic, Gemini, and more via Google News RSS feeds.
2. **🖼️ Dynamic Visuals:** Uses the Unsplash API to fetch high-quality, aesthetic vertical backgrounds that match the technological vibe.
3. **🎵 Aesthetic Audio:** Connects to the Freesound API to find "Creative Commons 0" (100% royalty-free) ambient/lo-fi audio tracks.
4. **🎞️ FFmpeg Video Processing:** 
   - Scales and crops the background image to exactly 1080x1920.
   - Generates and overlays a dynamic audio waveform animation.
   - Renders a fast, crisp `.mp4` video optimized for YouTube Shorts.
5. **🎬 Auto YouTube Upload:** Uploads the final render securely using official Google Cloud credentials, complete with SEO-optimized titles, descriptions, and tags.
6. **💬 Engagement Booster:** Automatically pins a first comment on the uploaded video to encourage viewer interaction.

## 🛠️ Prerequisites & Requirements

Ensure your environment meets the following specifications:
- **Python 3.10+**
- **FFmpeg:** Must be installed and accessible via system PATH.
- **Google Cloud Platform:** A Google account with a project where the **YouTube Data API v3** is enabled.
- **API Keys:**
  - Freesound API Key (Free)
  - Unsplash API Key (Free)

## 🚀 Step-by-Step Installation

### 1. Clone the Repository
```bash
git clone https://github.com/mmustafasenoglu/AutoShorts-AI.git
cd AutoShorts-AI
```

### 2. Install Dependencies
It is highly recommended to use a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure API Keys
Create a `.env` file in the root directory:
```env
FREESOUND_API_KEY=your_freesound_api_key_here
UNSPLASH_API_KEY=your_unsplash_api_key_here
```

### 4. Setup YouTube Credentials
- Go to the [Google Cloud Console](https://console.cloud.google.com/).
- Create a project and enable the YouTube Data API v3.
- Navigate to **Credentials** > **Create Credentials** > **OAuth client ID** (Choose "Desktop App").
- Download the JSON file, rename it exactly to `client_secret.json`, and place it in the project root.

## 💻 Usage

### Method A: Manual Run (Single Upload)
To generate and upload one video immediately:
```bash
python news_bot.py
```
*Note: On your very first run, a browser tab will open asking you to log into your Google Account to authorize the app. This generates a `token.json` file. Subsequent runs will be completely headless and automatic.*

### Method B: Scheduled Automated Run (Server Deploy)
To let the script run continuously in the background (perfect for VPS or Raspberry Pi):
```bash
python scheduler.py
```
*You can configure the specific execution time by modifying the variables inside `scheduler.py`.*

## 🔧 Customization
You can easily tweak the bot's behavior by modifying variables inside `news_bot.py`:
- `VIDEO_DURATION_MAX`: Change the length of the shorts (default is 15 seconds).
- `TAGS`: Update the default YouTube tags for your specific niche.

## 🐛 Troubleshooting & FAQ
- **FFmpeg Error:** Ensure FFmpeg is correctly installed and added to your system's PATH. Test it by typing `ffmpeg -version` in your terminal.
- **OAuth / 401 Unauthorized:** Delete the `token.json` file and run `python news_bot.py` again to force a new authentication prompt.
- **Quota Exceeded Error:** The YouTube API has a daily limit (10,000 units), which normally allows for about 6 video uploads per day. Wait 24 hours to reset.

## 🔒 Security Best Practices
**Never** commit your `client_secret.json`, `token.json`, or `.env` files to a public repository. The included `.gitignore` file is pre-configured to keep these credentials safe.

---

🔥 **Keywords:**
#YouTubeBot #YouTubeAutomation #AI #ChatGPT #OpenAI #YouTubeAPI #Python #PythonBot #Automation #GoogleNewsBot #VideoGenerator #VideoCreator #AutoUpload #FFmpeg #OpenSource #TechNews #YouTubeShorts #ShortsAutomation #Freesound #Unsplash #ContentCreator #Developer
