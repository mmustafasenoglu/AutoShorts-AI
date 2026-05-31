# 🎬 YouTube Slowed+Reverbed Otomasyon — Kurulum Kılavuzu

## 📋 Gereksinimler
- Python 3.10+
- FFmpeg
- Bir sunucu (Ubuntu/Debian önerilir, VPS veya AWS/GCP)

---

## 1️⃣ Sunucuya Bağlan ve Hazırla

```bash
# Sunucuya SSH ile bağlan
ssh user@sunucu_ip

# Paketleri güncelle
sudo apt update && sudo apt upgrade -y

# FFmpeg kur
sudo apt install ffmpeg -y

# Python pip kur
sudo apt install python3-pip -y

# Proje klasörünü oluştur
mkdir ~/youtube-bot && cd ~/youtube-bot
```

---

## 2️⃣ API Key'leri Al ve .env Dosyasını Ayarla

Güvenlik sebebiyle API anahtarlarını artık kodun içine yazmıyoruz. Proje klasöründe `.env` adında bir dosya oluşturup içine koyacağız.

### .env Dosyasını Oluşturma
Sunucuda veya bilgisayarınızda şu komutla oluşturun:
```bash
nano .env
```
İçerisine şunları yazın (Kendi key'lerinizle değiştirerek):
```env
FREESOUND_API_KEY=senin_freesound_key_buraya
UNSPLASH_API_KEY=senin_unsplash_key_buraya
```

### Freesound Key Nasıl Alınır? (Müzik için)
1. https://freesound.org adresine git, hesap aç ve giriş yap.
2. https://freesound.org/apiv2/apply/ adresinden yeni bir API key al.
3. Aldığın key'i `.env` dosyasındaki ilgili yere yapıştır.

### Unsplash Key Nasıl Alınır? (Arka Plan Resimleri için)
1. https://unsplash.com/developers adresine git ve kayıt ol.
2. Yeni bir uygulama (New Application) oluştur.
3. Verilen **Access Key** değerini kopyala ve `.env` dosyasındaki ilgili yere yapıştır.

---

## 3️⃣ YouTube Data API Kurulumu

1. https://console.cloud.google.com adresine git
2. Yeni proje oluştur (örn. "youtube-bot")
3. **APIs & Services → Enable APIs** → "YouTube Data API v3" etkinleştir
4. **APIs & Services → Credentials → Create Credentials → OAuth 2.0 Client ID**
   - Application type: **Desktop app**
5. JSON dosyasını indir, adını `client_secret.json` yap
6. Sunucuya kopyala:
   ```bash
   scp client_secret.json user@sunucu_ip:~/youtube-bot/
   ```

---

## 4️⃣ Dosyaları Sunucuya At ve Kur

```bash
# Proje klasöründeki dosyaları sunucuya kopyala
scp main-2.py scheduler.py requirements.txt client_secret.json .env user@sunucu_ip:~/youtube-bot/
```

---

## 5️⃣ Local'de Oluşan Token Dosyasını Sunucuya Gönder

İlk çalıştırmada bilgisayarında oluşan `token.json` dosyası, YouTube hesabının giriş bilgilerini (refresh token) saklar. Bu dosya sayesinde sunucuda tarayıcı açmana gerek kalmaz.

```bash
# Local terminalinden bu komutu çalıştırarak token.json'ı sunucuya gönder:
scp token.json user@sunucu_ip:~/youtube-bot/
```

Sunucuya bağlanıp Python sanal ortamını (venv) kuralım ve kütüphaneleri yükleyelim:

```bash
# Sunucuya bağlan
ssh user@sunucu_ip

# youtube-bot klasörüne gir
cd ~/youtube-bot

# Sanal ortam oluştur ve aktifleştir
python3 -m venv venv
./venv/bin/pip install -r requirements.txt
```

Artık sunucu headless (tarayıcısız) olarak video yüklemeye hazır! ✅

---

## 6️⃣ Sunucuda Sürekli Çalıştırma Yöntemleri

Botun sunucuda her gün otomatik çalışması için 2 harika yöntem vardır:

### 📌 Yöntem A: Python Scheduler Kullanarak (Önerilen 🌟)
Sizin için hazırladığım `scheduler.py` scripti arka planda sürekli çalışır ve her gün belirlediğiniz saatte (örn. sabah 10:00) botu tetikler. Bir gün hata alsa bile durmaz, log tutup ertesi gün çalışmaya devam eder.

Arka planda (terminal kapansa bile) çalışması için şu komutla başlatın:
```bash
nohup ./venv/bin/python scheduler.py > scheduler_output.log 2>&1 &
```

- **Durumunu kontrol etmek için:** `cat scheduler.log` veya `tail -f scheduler.log` yazabilirsiniz.
- **Durdurmak için:** `ps aux | grep scheduler.py` ile işlem numarasını (PID) bulup `kill PID` yapabilirsiniz.

*(Çalışma saatini değiştirmek için `scheduler.py` içindeki `RUN_AT_HOUR = 10` değerini düzenleyebilirsiniz.)*

### 📌 Yöntem B: Cron Job ile Çalıştırma
Eğer sunucunun kendi zamanlayıcısını (cron) kullanmak isterseniz:

```bash
crontab -e
```

En alta şunu ekleyin (her gün sabah 10:00'da çalışır):
```
0 10 * * * cd /home/user/youtube-bot && ./venv/bin/python main-2.py >> /home/user/youtube-bot/log.txt 2>&1
```

> ⚠️ `/home/user/` kısmındaki `user` yerine kendi sunucu kullanıcı adınızı yazmayı unutmayın!

---

## 7️⃣ Logları Takip Etmek

- Python scheduler logları için: `tail -f ~/youtube-bot/scheduler.log`
- Botun anlık çıktıları için: `tail -f ~/youtube-bot/scheduler_output.log`

---

## 🎛️ Ayarları Özelleştir (main.py)

| Ayar | Açıklama | Varsayılan |
|------|----------|------------|
| `SLOW_FACTOR` | Yavaşlatma oranı (0.7=çok yavaş, 0.9=hafif) | 0.85 |
| `REVERB_ROOM` | Reverb miktarı (0.0-1.0) | 0.6 |
| `SEARCH_QUERIES` | Freesound'da aranacak terimler | ambient, lofi... |
| `TAGS` | Video etiketleri | slowed, reverbed... |

---

## ⚠️ Önemli Notlar

- Freesound'dan "Creative Commons 0" lisanslı sesler çekilir — tamamen telifsizdir.
- YouTube API'nin günlük bir kota limiti (upload kotası) vardır. Günde 1-2 video yüklemek en güvenlisidir.
- `token.json` dosyasını kimseyle paylaşmayın! Bu dosya doğrudan YouTube kanalınıza erişim sağlar.

---

## 🆘 Sorun mu Var?

`log.txt` dosyasına bak. Yaygın hatalar:
- `FFmpeg hatası` → `ffmpeg -version` ile kurulu olup olmadığını kontrol et
- `401 Unauthorized` → `token.json` süresi dolmuş, local'de tekrar çalıştır
- `quotaExceeded` → YouTube API günlük kotası doldu, yarın tekrar çalışır
