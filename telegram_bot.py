import os
import asyncio
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

from schedule_manager import get_next_slot
from youtube_auth import get_youtube_service
from schedule_upload import upload_scheduled
from utils import rewrite_description_with_groq, download_video

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip('"').strip("'")
ALLOWED_USER_ID = os.getenv("TELEGRAM_ALLOWED_USER_ID")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    if ALLOWED_USER_ID and user_id != ALLOWED_USER_ID:
        await update.message.reply_text("⛔ Yetkisiz erişim.")
        return
    await update.message.reply_text("👋 Merhaba! Bana YouTube/TikTok linki gönder, senin için sıraya alıp otomatik YouTube'a yükleyeyim.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    if ALLOWED_USER_ID and user_id != ALLOWED_USER_ID:
        await update.message.reply_text("⛔ Yetkisiz erişim.")
        return
    url = update.message.text.strip()
    if not url.startswith("http"):
        await update.message.reply_text("Lütfen geçerli bir URL gönderin.")
        return
    asyncio.create_task(process_video(update, url))

async def process_video(update: Update, url: str):
    await update.message.reply_text(f"⏳ Link alındı, işleniyor: {url}")
    loop = asyncio.get_running_loop()
    try:
        result = await loop.run_in_executor(None, download_and_schedule, url)
        await update.message.reply_text(f"✅ Başarılı!\n📅 Yayın Tarihi: {result['local_time']}\n🔗 URL: {result['url']}")
    except Exception as e:
        await update.message.reply_text(f"❌ Bir hata oluştu: {str(e)}")

def download_and_schedule(url):
    ydl_opts = {
        'format': '22/18/best[ext=mp4]/best',
        'outtmpl': 'videos/%(title)s.%(ext)s',
        'noplaylist': True,
        'quiet': True,
        'postprocessors': [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4',
        }],
    }
    
    try:
        result = download_video(url, ydl_opts)
        title = result["title"]
        description = rewrite_description_with_groq(result["description"], title)
        filename = result["filename"]
        duration = result["duration"]
    except Exception as e:
        raise Exception(f"Video indirilemedi: {e}")
    
    local_dt, publish_at_iso = get_next_slot()
    service = get_youtube_service()
    video_id = upload_scheduled(service, filename, title, description, result["tags"], publish_at_iso)
    
    if video_id:
        try:
            os.remove(filename)
        except:
            pass
        return {
            "local_time": local_dt.strftime('%d.%m.%Y %H:%M'),
            "url": f"https://youtube.com/shorts/{video_id}" if duration <= 60 else f"https://youtube.com/watch?v={video_id}"
        }
    else:
        raise Exception("YouTube Yükleme başarısız oldu.")

def main():
    if not TELEGRAM_TOKEN:
        print("TELEGRAM_BOT_TOKEN .env içinde bulunamadı!")
        return
    application = Application.builder().token(TELEGRAM_TOKEN).connect_timeout(30.0).read_timeout(30.0).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("🤖 Telegram Bot başlatıldı... Mesajları bekliyor.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
