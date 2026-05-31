import os
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc

def get_driver():
    """Önceden kaydedilmiş Chrome profilini yükleyip driver'ı döndürür."""
    profile_path = os.path.abspath("./chrome_profile")
    
    options = uc.ChromeOptions()
    
    # version_main=148 diyerek kurulu olan güncel Chrome sürümüne uyduruyoruz
    driver = uc.Chrome(
        options=options,
        user_data_dir=profile_path,
        use_subprocess=True,
        version_main=148
    )
    
    return driver

def upload_to_tiktok(video_path, description):
    """TikTok'a Selenium kullanarak video yükler."""
    print("[🚀] TikTok tarayıcısı başlatılıyor...")
    driver = get_driver()
    
    try:
        driver.get("https://www.tiktok.com/tiktokstudio/upload")
        time.sleep(5) 
        
        try:
            iframe = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//iframe"))
            )
            driver.switch_to.frame(iframe)
            print("[🔍] iframe'e geçiş yapıldı.")
        except:
            pass

        print("[📤] Video doyası seçiliyor...")
        file_input = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//input[@type='file']"))
        )
        file_input.send_keys(os.path.abspath(video_path))
        
        print("[⏳] Videonun işlenmesi bekleniyor (yaklaşık 15-20 saniye)...")
        time.sleep(20)
        
        try:
            print("[📝] Başlık ve hashtagler yazılıyor...")
            editor = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".public-DraftEditor-content"))
            )
            driver.execute_script("arguments[0].innerText = ''", editor)
            editor.send_keys(description)
            time.sleep(3)
        except Exception as e:
            print(f"[⚠️] Açıklama TextBox'ı bulunamadı. Hata: {e}")
        
        print("[🔥] Post butonuna basılıyor...")
        post_btn = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Post') or contains(., 'Gönder')]"))
        )
        driver.execute_script("arguments[0].click();", post_btn)
        
        print("[⏳] Gönderinin tamamlanması bekleniyor...")
        time.sleep(10)
        
        print("[🎉] TikTok'a başarıyla yüklendi!")
        
    except Exception as e:
        print(f"[❌] TikTok yüklerken hata oluştu: {e}")
        driver.save_screenshot("tiktok_error.png")
        print("[!] Ekran görüntüsü 'tiktok_error.png' olarak kaydedildi.")
    finally:
        driver.quit()
