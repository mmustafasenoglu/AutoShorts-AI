import os
import time
import undetected_chromedriver as uc

def setup_tiktok_login():
    print("="*50)
    print("  TikTok İlk Giriş & Captcha Çözme İşlemi")
    print("="*50)
    print("\n[⏳] Tarayıcı açılıyor...")
    print("[!] Lütfen açılan pencerede TikTok'a giriş yap ve ekranda (Cloudflare vb.) doğrulama çıkarsa ÇÖZ.")
    print("[!] İşlemi bitirdikten sonra tarayıcıyı KAPATMA, o kendi kapanacak.")
    print("[!] 5 Dakika(300 saniye) süren var...\n")

    profile_path = os.path.abspath("./chrome_profile")
    
    options = uc.ChromeOptions()

    try:
        driver = uc.Chrome(
            options=options,
            user_data_dir=profile_path,
            use_subprocess=True,
            version_main=148
        )
        
        # Direkt upload sayfasına gidelim ki Cloudflare çıkarsa halledelim
        driver.get("https://www.tiktok.com/tiktokstudio/upload")

        for i in range(300, 0, -1):
            time.sleep(1)
            if i % 30 == 0:
                print(f"[⏳] Kalan süre: {i} saniye...")

        print("\n[✅] Süre doldu. Profil bilgileri (ve Cloudflare geçiş çerezleri) kaydedildi!")
        driver.quit()
        print("[!] Artık bot çalışmaya hazır.")

    except Exception as e:
        print(f"\n[❌] Hata oluştu: {e}")

if __name__ == "__main__":
    setup_tiktok_login()
