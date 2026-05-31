import undetected_chromedriver as uc
import time
import os

if __name__ == '__main__':
    profile_path = os.path.abspath("./chrome_profile")
    options = uc.ChromeOptions()
    options.add_argument("--disable-popup-blocking")

    try:
        print("UC starting...")
        driver = uc.Chrome(options=options, user_data_dir=profile_path, use_subprocess=True, version_main=148)
        print("Driver started. Navigating to tiktok...")
        driver.get("https://www.tiktok.com/tiktokstudio/upload")
        time.sleep(5)
        print("Success. Current title:", driver.title)
        driver.quit()
    except Exception as e:
        print("Error:", e)
