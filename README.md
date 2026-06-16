# 🎵 Lyrics Video Uploader Bot

Bu proje, hazır olarak bulunan "Lyrics" (şarkı sözü) videolarınızın arka planlarını isteğe bağlı olarak değiştirmenizi ve doğrudan YouTube ile TikTok hesaplarınıza otomatik olarak yüklemenizi sağlayan bir Python otomasyon aracıdır.

## 🚀 Özellikler

- **İnteraktif ve CLI Modu:** İsterseniz komut satırı argümanlarıyla, isterseniz de ekrandaki yönergeleri (interaktif) takip ederek kullanabilirsiniz.
- **Çift Platform Desteği (YouTube & TikTok):** Hazırlanan videoları hem YouTube Shorts hem de TikTok'a aynı anda veya ayrı ayrı otomatik olarak yükleyebilirsiniz. TikTok için tarayıcı otomasyonu (Playwright) kullanılır.
- **Otomatik Arka Plan Değiştirme:** Unsplash API kullanarak şarkının moduna veya verdiğiniz kelimeye uygun estetik resimler indirir. Mevcut siyah arka planlı lyrics videonuzu `ffmpeg` kullanarak bu yeni resimle birleştirir (blend).
- **Yerel Arka Plan:** İsterseniz kendi bilgisayarınızdaki bir fotoğraf veya videoyu da arka plan olarak ayarlayabilirsiniz.
- **Akıllı Metadata Oluşturma:** Şarkı adı, sanatçı adı ve verdiğiniz etiketleri birleştirerek otomatik SEO uyumlu başlık, açıklama ve YouTube Tag'leri ile TikTok Caption/Etiketleri oluşturur.
- **Logoları Gizleme (Opsiyonel):** Orijinal videoda istenmeyen bir filigran veya logo varsa belirli saniyeler arasında siyah bir bant çekerek veya üzerine yazı yazarak bu alanı gizleyebilirsiniz.

## 📂 Proje Yapısı

- `upload_lyrics.py` : Otomasyonun ana dosyasıdır. Bütün indirme, render (`ffmpeg`), YouTube ve TikTok yükleme işlemlerini yönetir.
- `tiktok_auth.py` : TikTok'a ilk kullanımdan önce manuel oturum açmanızı sağlayan yardımcı araçtır.
- `tiktok_uploader.py` : TikTok Studio'ya otomatik video yükleme ve paylaşma işini yapan çekirdek Playwright modülüdür.
- `youtube_auth.py` : YouTube API OAuth 2.0 kimlik doğrulama işlemlerini ve video yükleme çekirdek kodunu barındırır.
- `upload_one_video.py` : Tek bir videoyu arka planı değiştirmeden hızlıca YouTube'a yüklemek için basit yardımcı script'tir.
- `videos/` : Orijinal söz videolarınızı koyabileceğiniz klasör.
- `output/` : İşlemler sonrasında arka planı değişmiş olan nihai videoların render alındığı ve kaydedildiği klasördür.
- `backgrounds/` : Kendi özel arka plan dosyalarınızı barındırabileceğiniz klasördür.
- `client_secret.json` : Google Cloud Console üzerinden alınmış YouTube Data API v3 yetki dosyasıdır.
- `.env` : Unsplash API vb. özel anahtarların bulunduğu ayar dosyasıdır.

## ⚙️ Kurulum ve Gereksinimler

Sistemin düzgün çalışması için bilgisayarınızda aşağıdaki araçların kurulu olması gerekir:

1. **Python 3.x**
2. **FFmpeg:** Video render ve arka plan birleştirme işlemleri için gereklidir.
   - macOS için: `brew install ffmpeg`
3. **Python Kütüphaneleri:** Projenin bulunduğu klasörde terminal açıp gereken paketleri yükleyin:
   ```bash
   pip install requests python-dotenv google-api-python-client google-auth-httplib2 google-auth-oauthlib playwright
   ```
4. **Playwright Kurulumu (TikTok İçin):**
   - Playwright tarayıcı binaries dosyasını kurun:
     ```bash
     playwright install chromium
     ```
5. **Google Cloud / YouTube API:**
   - Google Cloud üzerinden bir proje oluşturup `YouTube Data API v3` aktif edilmelidir.
   - `OAuth 2.0 Client IDs` oluşturulup JSON dosyası `client_secret.json` adıyla bu klasöre konulmalıdır.
6. **Unsplash API (Opsiyonel):**
   - Otomatik görsel indirmek isterseniz [Unsplash Developers](https://unsplash.com/developers) üzerinden bir API key alıp proje dizinindeki `.env` dosyasına eklemelisiniz.

---

## 🔑 TikTok Giriş Kurulumu (İlk Seferlik)

TikTok'un bot korumalarını aşmak için şifrenizi koda yazmak yerine tarayıcı oturumunu saklarız. İlk kullanımdan önce:

1. Terminalde şu komutu çalıştırın:
   ```bash
   python tiktok_auth.py
   ```
2. Açılan tarayıcı penceresinde TikTok Studio hesabınıza giriş yapın.
3. Giriş yaptıktan sonra tarayıcı penceresini kapatabilir ya da terminalde `ENTER` tuşuna basabilirsiniz.
4. Oturum bilgileriniz güvenli bir şekilde `.tiktok_session` klasörüne kaydedilir ve sonraki yüklemelerde otomatik kullanılır.

---

## 🎮 Kullanım

### 1. İnteraktif Mod (Önerilen)
Terminali açıp sadece ana dosyayı çalıştırın. Script size adım adım ne yapmak istediğinizi soracaktır:
```bash
python upload_lyrics.py
```
- Video dosyasını sürükleyip bırakabilirsiniz.
- Şarkı adını ve sanatçıyı girersiniz.
- Arka planın değişip değişmeyeceğine karar verirsiniz.
- **YouTube ile birlikte TikTok'a da yüklemek isteyip istemediğinizi seçersiniz.** Tarayıcının arka planda (headless) veya görünür şekilde çalışmasını ayarlayabilirsiniz.

### 2. Komut Satırı (CLI) Modu
Eğer toplu işlemler yapıyorsanız argümanları dışarıdan verebilirsiniz.

**YouTube ve TikTok'a Birlikte Yükleme:**
```bash
python upload_lyrics.py --video "videos/sarki.mp4" --song "Self Aware" --artist "Temper City" --tags "speedup,trend" --bg-query "neon city" --privacy "public" --tiktok
```

*TikTok tarayıcısının görünmeden arka planda çalışmasını isterseniz `--tiktok-headless` parametresini de ekleyebilirsiniz.*

Tüm komutları görmek için:
```bash
python upload_lyrics.py --help
```

## ⚠️ Önemli Notlar

- İlk çalıştırmada YouTube API sizden yetki isteyecek ve tarayıcıda bir Google giriş sayfası açacaktır. İzin verdikten sonra oluşan `token.json` dosyası sonraki kullanımlarda şifresiz giriş yapmanızı sağlar.
- `ffmpeg` blend (birleştirme) modunu kullanır. En iyi sonucu alabilmek için orijinal Lyrics videonuzun arka planının siyah olması tavsiye edilir.
- TikTok uploader'ın düzgün çalışabilmesi için `.tiktok_session` klasörünün silinmemesi gerekir. Oturumunuz kapandıysa veya hata alıyorsanız `python tiktok_auth.py` komutunu yeniden çalıştırıp giriş yapabilirsiniz.
