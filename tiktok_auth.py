import os
import sys
import asyncio
from playwright.async_api import async_playwright

async def main():
    print("\n" + "="*50)
    print("      🎵  TikTok Oturum Açma Yardımcısı  🎵")
    print("="*50 + "\n")
    
    session_dir = os.path.join(os.getcwd(), ".tiktok_session")
    print(f"[📂] Oturum klasörü: {session_dir}")
    
    async with async_playwright() as p:
        print("[🌐] Tarayıcı başlatılıyor (Headful)...")
        # Kalıcı bir tarayıcı profili (persistent context) açıyoruz
        context = await p.chromium.launch_persistent_context(
            user_data_dir=session_dir,
            headless=False,
            viewport=None,
            args=["--start-maximized"]
        )
        
        page = await context.new_page()
        print("[🚀] TikTok Studio yükleme sayfasına yönlendiriliyor...")
        await page.goto("https://www.tiktok.com/tiktokstudio/upload?lang=en")
        
        print("\n" + "!"*60)
        print("  ÖNEMLİ: Tarayıcı penceresinde TikTok hesabınıza giriş yapın.")
        print("  Giriş yaptıktan sonra tarayıcı penceresini kapatabilir ")
        print("  ya da bu terminalde ENTER tuşuna basabilirsiniz.")
        print("!"*60 + "\n")
        
        loop = asyncio.get_event_loop()
        stop_event = asyncio.Event()
        
        def on_close():
            print("\n[✅] Tarayıcı kapatıldı.")
            stop_event.set()
            
        page.on("close", lambda p: on_close())
        
        async def wait_for_input():
            try:
                await loop.run_in_executor(None, input, "  Oturum açtıktan sonra bitirmek için ENTER tuşuna basın...\n")
                stop_event.set()
            except asyncio.CancelledError:
                pass
            
        input_task = asyncio.create_task(wait_for_input())
        
        # stop_event tetiklenene kadar bekleyelim
        while not stop_event.is_set():
            await asyncio.sleep(0.5)
            if page.is_closed():
                break
                
        # input task'i iptal edelim
        input_task.cancel()
        
        # Oturumun geçerli olup olmadığını kontrol edelim
        try:
            if not page.is_closed():
                current_url = page.url
                if "login" not in current_url:
                    print("[🎉] TikTok hesabına başarıyla giriş yapıldı ve oturum kaydedildi.")
                else:
                    print("[⚠️] Giriş tamamlanmamış olabilir. Lütfen giriş yaptığınızdan emin olun.")
        except Exception:
            pass
            
        print("[🔒] Tarayıcı kapatılıyor...")
        await context.close()
        print("[✅] Oturum başarıyla kaydedildi. Artık tiktok_uploader.py'yi kullanabilirsiniz.\n")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[⚠️] İşlem kullanıcı tarafından iptal edildi.")
