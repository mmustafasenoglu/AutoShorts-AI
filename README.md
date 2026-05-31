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
2. **🖼️ Dynamic Visuals:** Uses the [Unsplash API](https://unsplash.com/developers) to fetch high-quality, aesthetic vertical backgrounds that match the technological vibe.
3. **🎵 Aesthetic Audio:** Connects to the [Freesound API](https://freesound.org/help/developers/) to find "Creative Commons 0" (100% royalty-free) ambient/lo-fi audio tracks.
4. **🎞️ FFmpeg Video Processing:** 
   - Scales and crops the background image to exactly 1080x1920.
   - Generates and overlays a dynamic audio waveform animation.
   - Renders a fast, crisp `.mp4` video optimized for YouTube Shorts.
5. **🎬 Auto YouTube Upload:** Uploads the final render securely using official Google Cloud credentials, complete with SEO-optimized titles, descriptions, and tags.
6. **💬 Engagement Booster:** Automatically pins a first comment on the uploaded video to encourage viewer interaction.

## 🛠️ Prerequisites & Requirements

Ensure your environment meets the following specifications:
- **Python 3.10+** (Download from [python.org](https://www.python.org/downloads/))
- **FFmpeg:** Must be installed and accessible via system PATH. (Download from [ffmpeg.org](https://ffmpeg.org/download.html))
- **Google Cloud Platform Account:** To access the YouTube Data API.

## 🚀 Step-by-Step Installation Guide

Follow these exact steps to get your bot running:

### 1. Clone the Repository
Open your terminal or command prompt and clone the project to your local machine:
```bash
git clone https://github.com/mmustafasenoglu/AutoShorts-AI.git
cd AutoShorts-AI
```

### 2. Install Dependencies
It is highly recommended to use a virtual environment to avoid conflicts:
```bash
# Create a virtual environment
python3 -m venv venv

# Activate it
# On Mac/Linux:
source venv/bin/activate  
# On Windows:
venv\Scripts\activate

# Install the required Python packages
pip install -r requirements.txt
```

### 3. Get Your API Keys
You need two free API keys for media generation.
1. **Freesound:** Go to [freesound.org/apiv2/apply/](https://freesound.org/apiv2/apply/), create an account, and request a new API key.
2. **Unsplash:** Go to [unsplash.com/developers](https://unsplash.com/developers), register as a developer, create a "New Application", and copy the **Access Key**.

Create a new file named `.env` in the root folder of your project and paste your keys like this:
```env
FREESOUND_API_KEY=your_freesound_api_key_here
UNSPLASH_API_KEY=your_unsplash_api_key_here
```

### 4. Setup YouTube Credentials (Google Cloud)
This step allows the bot to upload to your YouTube channel securely.
1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Click on the project drop-down at the top and select **"New Project"**. Name it something like "YouTube-AutoBot".
3. In the search bar at the top, type **"YouTube Data API v3"**, select it, and click **"Enable"**.
4. On the left sidebar, click on **Credentials**, then click **"+ CREATE CREDENTIALS"** and choose **OAuth client ID**.
5. *Note: If asked to configure the Consent Screen, choose "External", fill in the required names and emails, and click Save/Continue until finished. Add your own Google email as a "Test User".*
6. Select **"Desktop App"** as the Application type and click Create.
7. Click the **Download JSON** button (the small down-arrow icon).
8. **CRITICAL:** Rename this downloaded file exactly to `client_secret.json` and place it inside the `AutoShorts-AI` project folder.

## 💻 Usage

### Method A: Manual Run (Single Upload)
To generate and upload one video immediately, make sure your virtual environment is active and run:
```bash
python news_bot.py
```
*Note: On your very first run, a browser tab will automatically open asking you to log into your Google Account to authorize the app. Once authorized, it will create a `token.json` file in your folder. Subsequent runs will be completely headless and automatic without needing the browser.*

### Method B: Scheduled Automated Run (For Servers/VPS)
To let the script run continuously in the background and automatically upload a video every day:
```bash
python scheduler.py
```
*You can configure the specific execution time (e.g., 10:00 AM) by modifying the `RUN_AT_HOUR` variable inside `scheduler.py`.*

## 🔧 Customization
You can easily tweak the bot's behavior by modifying variables inside `news_bot.py`:
- `VIDEO_DURATION_MAX`: Change the length of the shorts (default is 15 seconds).
- `TAGS`: Update the default YouTube tags for your specific niche.

## 🐛 Troubleshooting & FAQ
- **FFmpeg Error:** Ensure FFmpeg is correctly installed and added to your system's PATH. Test it by typing `ffmpeg -version` in your terminal.
- **OAuth / 401 Unauthorized:** If your token expires, just delete the `token.json` file and run `python news_bot.py` again to force a new authentication prompt.
- **Quota Exceeded Error:** The YouTube API has a daily limit (10,000 units), which normally allows for about 6 video uploads per day. Wait 24 hours for it to reset.

## 🔒 Security Best Practices
**Never** commit your `client_secret.json`, `token.json`, or `.env` files to a public repository. The included `.gitignore` file is pre-configured to keep these credentials safe locally.

---

🔥 **Keywords:**
#YouTubeBot #YouTubeAutomation #AI #ChatGPT #OpenAI #YouTubeAPI #Python #PythonBot #Automation #GoogleNewsBot #VideoGenerator #VideoCreator #AutoUpload #FFmpeg #OpenSource #TechNews #YouTubeShorts #ShortsAutomation #Freesound #Unsplash #ContentCreator #Developer
