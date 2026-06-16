import os
import sys
import argparse
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

async def upload_tiktok_video(video_path: str, caption: str, headless: bool = False) -> bool:
    video_abs_path = str(Path(video_path).resolve())
    if not os.path.exists(video_abs_path):
        print(f"[❌] Video dosyası bulunamadı: {video_abs_path}")
        return False

    session_dir = os.path.join(os.getcwd(), ".tiktok_session")
    if not os.path.exists(session_dir):
        print("[❌] TikTok oturumu bulunamadı! Lütfen önce 'python tiktok_auth.py' çalıştırarak giriş yapın.")
        return False

    print("\n" + "="*50)
    print("      📱  TikTok Video Yükleyici Otomasyonu  📱")
    print("="*50)
    print(f"[📁] Video: {video_path}")
    print(f"[📝] Caption: {caption}")
    print(f"[🌐] Tarayıcı modu: {'Arka plan (Headless)' if headless else 'Ön plan (Headful)'}")
    print("="*50 + "\n")

    async with async_playwright() as p:
        user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        
        print("[🌐] Tarayıcı başlatılıyor...")
        context = await p.chromium.launch_persistent_context(
            user_data_dir=session_dir,
            headless=headless,
            viewport=None if not headless else {"width": 1280, "height": 720},
            user_agent=user_agent,
            args=["--start-maximized"] if not headless else []
        )
        
        page = await context.new_page()
        
        # Go to upload page
        print("[🚀] TikTok Studio upload sayfasına gidiliyor...")
        await page.goto("https://www.tiktok.com/tiktokstudio/upload?lang=en", wait_until="domcontentloaded")
        
        # Check login status
        await asyncio.sleep(5)
        if "login" in page.url:
            print("[❌] Giriş yapmamış görünüyorsunuz. Lütfen 'python tiktok_auth.py' çalıştırıp giriş yapın.")
            await context.close()
            return False

        # Find upload file input
        print("[🔍] Dosya yükleme alanı aranıyor...")
        file_input = None
        target_page = page
        
        try:
            file_input = await page.wait_for_selector('input[type="file"]', timeout=8000)
        except Exception:
            pass

        # If not found on main frame, search in all subframes (iframes)
        if not file_input:
            for frame in page.frames:
                try:
                    el = await frame.query_selector('input[type="file"]')
                    if el:
                        file_input = el
                        target_page = frame
                        print("[📂] Yükleme alanı iframe içinde bulundu.")
                        break
                except Exception:
                    continue

        if not file_input:
            print("[❌] Dosya yükleme alanı bulunamadı! Sayfa yüklenemedi veya TikTok arayüzü güncellendi.")
            # Hata ekran görüntüsü alalım (sorun giderme için)
            os.makedirs("output", exist_ok=True)
            await page.screenshot(path="output/tiktok_upload_error.png")
            print("[📸] Ekran görüntüsü kaydedildi: output/tiktok_upload_error.png")
            await context.close()
            return False

        # Start uploading
        print("[📤] Video yükleniyor...")
        await file_input.set_input_files(video_abs_path)
        print("[✅] Video yüklemesi başlatıldı.")
        
        # Wait a moment for UI to update
        await asyncio.sleep(5)
        
        # Set Caption / Description
        print("[📝] Caption alanı aranıyor...")
        caption_selectors = [
            'div[data-e2e="caption-input"]',
            'div[contenteditable="true"]',
            '.public-DraftEditor-editor',
            '[data-text="true"]'
        ]
        
        caption_el = None
        for sel in caption_selectors:
            try:
                caption_el = await target_page.wait_for_selector(sel, timeout=5000)
                if caption_el:
                    print(f"[📌] Caption alanı bulundu: {sel}")
                    break
            except Exception:
                continue

        if not caption_el:
            print("[⚠️] Caption alanı bulunamadı! Varsayılan caption kullanılacak.")
        else:
            print("[✍️] Caption yazılıyor...")
            await caption_el.click()
            await asyncio.sleep(0.5)
            
            # Select all and delete current text
            await target_page.keyboard.press("Meta+A")
            await target_page.keyboard.press("Control+A")
            await target_page.keyboard.press("Backspace")
            await asyncio.sleep(0.5)
            
            # Type the new caption with human-like delay
            await target_page.keyboard.type(caption, delay=40)
            await asyncio.sleep(1)

        # Wait for processing / post button to be active
        print("[⏳] Videonun yüklenmesi ve işlenmesi bekleniyor (bu işlem birkaç dakika sürebilir)...")
        post_btn = None
        post_btn_selectors = [
            'button[data-e2e="post_video_button"]',
            'button:has-text("Post")',
            'button:has-text("Yayınla")',
            'button:has-text("Paylaş")',
            'button[type="submit"]'
        ]
        
        for sel in post_btn_selectors:
            try:
                post_btn = await target_page.wait_for_selector(sel, timeout=5000)
                if post_btn:
                    print(f"[📌] Paylaş butonu bulundu: {sel}")
                    break
            except Exception:
                continue

        if not post_btn:
            print("[❌] Paylaş butonu bulunamadı!")
            await target_page.screenshot(path="output/tiktok_post_btn_error.png")
            await context.close()
            return False

        # Wait loop for the button to become enabled
        is_ready = False
        max_wait = 150  # 150 * 2s = 5 dakikalık maksimum bekleme süresi
        for i in range(max_wait):
            try:
                aria_disabled = await post_btn.get_attribute("aria-disabled")
                disabled = await post_btn.get_attribute("disabled")
                
                # Check if it is enabled (no disabled attribute, and aria-disabled is not true/None)
                if aria_disabled != "true" and disabled is None:
                    print("\n[🎉] Video yüklemesi ve kontrolü tamamlandı, paylaşmaya hazır!")
                    is_ready = True
                    break
            except Exception:
                pass
                
            progress_text = ""
            try:
                # Progress percent'i ekrana yazmaya çalışalım
                # TikTok arayüzüne göre element sınıfları değişebilir, genel bir arama yapalım
                progress_el = await target_page.query_selector('[class*="progress"], [class*="percent"]')
                if progress_el:
                    progress_text = await progress_el.text_content()
                    if progress_text:
                        progress_text = f" ({progress_text.strip()})"
            except Exception:
                pass
                
            print(f"\r⏳ Bekleniyor... {i * 2}s{progress_text}", end="", flush=True)
            await asyncio.sleep(2)

        if not is_ready:
            print("\n[⚠️] Video işlenmesi zaman aşımına uğradı. Buton aktifleşmedi.")
            await target_page.screenshot(path="output/tiktok_timeout_error.png")
            await context.close()
            return False

        # Click Post!
        print("[🚀] Paylaş butonuna tıklanıyor...")
        await post_btn.click()
        
        # Wait for the post to finalize
        print("[⏳] Paylaşımın tamamlanması bekleniyor...")
        await asyncio.sleep(12)
        
        print("[✅] TikTok video paylaşma işlemi tamamlandı!")
        await context.close()
        return True

if __name__ == "__main__":
    p = argparse.ArgumentParser(description="TikTok Video Uploader via Playwright")
    p.add_argument("--video", required=True, help="Video dosyasının yolu")
    p.add_argument("--caption", required=True, help="Video açıklaması / caption")
    p.add_argument("--headless", action="store_true", help="Tarayıcıyı arka planda (headless) çalıştır")
    args = p.parse_args()

    try:
        success = asyncio.run(upload_tiktok_video(args.video, args.caption, args.headless))
        if success:
            sys.exit(0)
        else:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n[⚠️] İşlem iptal edildi.")
        sys.exit(1)
