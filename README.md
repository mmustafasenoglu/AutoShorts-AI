# 🤖 AutoShorts-AI: YouTube AI News Automation Bot 🚀

A fully automated Python bot that tracks the latest AI trends, generates engaging YouTube Shorts videos, and auto-uploads them directly to your YouTube channel.

## ⚡ Features

1. **📰 Fetches News:** Scans Google News for the latest updates on Artificial Intelligence, ChatGPT, Anthropic, Gemini, etc.
2. **🖼️ Background Generation:** Finds an aesthetic background image related to the topic via the Unsplash API.
3. **🎵 Adds Music:** Fetches a copyright-free, aesthetic ambient track from Freesound.
4. **✏️ Video Editing:** Uses FFmpeg to merge the image, sound, and a dynamic text overlay into a 9:16 vertical video suitable for YouTube Shorts.
5. **🎬 Auto Upload:** Uploads the generated Short directly to YouTube using the YouTube Data API v3 with a title, description, and SEO tags.
6. **💬 First Comment:** Automatically leaves a first comment to increase viewer engagement.

## 🛠️ Prerequisites

Before you begin, ensure you have met the following requirements:
- **Python 3.10+** installed on your system.
- **FFmpeg** installed and added to your system's PATH.
- **Google Cloud Account** with the **YouTube Data API v3** enabled. You must download the OAuth 2.0 Credentials as `client_secret.json`.
- **Freesound API Key** (Free from freesound.org)
- **Unsplash API Key** (Free from unsplash.com/developers)

## 🚀 Installation & How to Run

1. **Clone the repository:**
   ```bash
   git clone https://github.com/mmustafasenoglu/AutoShorts-AI.git
   cd AutoShorts-AI
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   Create a `.env` file in the root directory of the project and add your API keys:
   ```env
   FREESOUND_API_KEY=your_freesound_api_key_here
   UNSPLASH_API_KEY=your_unsplash_api_key_here
   ```

4. **Add your YouTube API Credentials:**
   Place your `client_secret.json` file (downloaded from Google Cloud Console) into the root directory of the project.

5. **Run the bot:**
   ```bash
   python news_bot.py
   ```
   *Note: On the first run, a browser window will open asking you to log into your Google Account to authorize the YouTube upload. This will generate a `token.json` file for future automated runs.*

## 🔒 Security Note
Never commit your `client_secret.json`, `token.json`, or `.env` files to GitHub. This repository already includes a `.gitignore` file to prevent accidental uploads of your sensitive credentials.

---

🔥 **Tags:**
#YouTubeBot #YouTubeAutomation #AI #ChatGPT #OpenAI #YouTubeAPI #Python #PythonBot #Automation #GoogleNewsBot #VideoGenerator #VideoCreator #AutoUpload #FFmpeg #OpenSource #TechNews #YouTubeShorts #ShortsAutomation #Freesound #Unsplash #ContentCreator
