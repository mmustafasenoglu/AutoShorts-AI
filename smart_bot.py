import os
import subprocess
import asyncio
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENCODE_PATH = "/Users/mustafasenoglu/.opencode/bin/opencode"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hey kanka! 👋 Ben Opencode Bot'uyum.\n\n"
        "Bana ne yazsan, opencode'a soracağım ve cevabı sana vereceğim.\n"
        "Seninle aynı dili konuşuyorum!\n\n"
        "Yaz bakalım, ne sormak istersen... 🔥"
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    user_name = update.message.from_user.first_name

    await update.message.chat.send_action("typing")

    try:
        process = await asyncio.create_subprocess_exec(
            OPENCODE_PATH, "run", user_message,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd="/Users/mustafasenoglu/Desktop/lyrics_uploader"
        )

        stdout, stderr = await asyncio.wait_for(
            process.communicate(),
            timeout=120
        )

        response = stdout.decode("utf-8").strip()

        if not response:
            response = stderr.decode("utf-8").strip()

        if not response:
            response = "🤔 Düşünüyorum ama cevap bulamadım kanka..."

        if len(response) > 4000:
            response = response[:4000] + "\n\n... (kesildi)"

        await update.message.reply_text(response)

    except asyncio.TimeoutError:
        await update.message.reply_text("⏱️ Çok uzun sürdü kanka, biraz daha kısa sor dene.")
    except FileNotFoundError:
        await update.message.reply_text("❌ opencode bulunamadı! Yolu kontrol et.")
    except Exception as e:
        await update.message.reply_text(f"❌ Hata: {str(e)}")


def main():
    if not TELEGRAM_TOKEN:
        print("❌ TELEGRAM_BOT_TOKEN tanımlı değil!")
        return

    print("🤖 Opencode Bot başlatılıyor...")
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("✅ Bot çalışıyor! Telegram'dan mesaj gönder.")
    app.run_polling()


if __name__ == "__main__":
    main()
