import time
import sys
import logging
from datetime import datetime, timedelta
import importlib

# Logging ayarları
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("scheduler.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)

# Ayarlar
RUN_AT_HOUR = 10  
RUN_AT_MINUTE = 0 

# Bot modüllerini dinamik olarak import et
try:
    tiktok_bot = importlib.import_module("tiktok_bot")
    news_bot = importlib.import_module("news_bot")
except ImportError as e:
    logging.error(f"Bot modüllerinden biri bulunamadı: {e}")
    sys.exit(1)

def get_seconds_until_next_run(target_hour, target_minute):
    now = datetime.now()
    target_time = now.replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)
    
    if now >= target_time:
        target_time += timedelta(days=1)
        
    delta = target_time - now
    return delta.total_seconds(), target_time

def main():
    logging.info("=== YOUTUBE & TIKTOK BOT SCHEDULER BAŞLATILDI ===")
    logging.info(f"Botlar her gün saat {RUN_AT_HOUR:02d}:{RUN_AT_MINUTE:02d} civarında çalışacak.")
    
    while True:
        seconds_to_wait, next_run_time = get_seconds_until_next_run(RUN_AT_HOUR, RUN_AT_MINUTE)
        logging.info(f"Bir sonraki işlem şu tarihte planlandı: {next_run_time.strftime('%Y-%m-%d %H:%M:%S')}")
        logging.info(f"Bekleme süresi: {seconds_to_wait / 3600:.2f} saat ({int(seconds_to_wait)} saniye)")
        
        try:
            while seconds_to_wait > 0:
                sleep_chunk = min(600, seconds_to_wait)
                time.sleep(sleep_chunk)
                seconds_to_wait -= sleep_chunk
        except KeyboardInterrupt:
            logging.info("Zamanlayıcı kullanıcı tarafından durduruldu.")
            break
            
        logging.info("Zaman geldi! Video hazırlama işlemleri başlatılıyor...")
        
        # 1. Müzik Botu (YouTube Shorts + TikTok)
        try:
            logging.info(">>> Müzik botu (YouTube + TikTok) çalıştırılıyor...")
            tiktok_bot.run()
            logging.info("Müzik başarıyla oluşturuldu ve YouTube/TikTok platformlarına yüklendi! [SUCCESS]")
        except Exception as e:
            logging.error(f"Müzik botunda hata oluştu: {e}", exc_info=True)
            
        # 2. News Bot
        try:
            logging.info(">>> Haber botu çalıştırılıyor...")
            news_bot.run()
            logging.info("Haber videosu başarıyla oluşturuldu ve YouTube'a yüklendi! [SUCCESS]")
        except Exception as e:
            logging.error(f"Haber botunda hata oluştu: {e}", exc_info=True)
            
        time.sleep(65)

if __name__ == "__main__":
    main()
