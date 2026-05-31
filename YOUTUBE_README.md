# 🤖 YouTube AI News Automation Bot 🚀

Bu proje, yapay zeka gündemini takip eden, popüler "Yapay Zeka" haberlerini otomatik olarak bulan ve bunlardan dikkat çekici YouTube Shorts videoları oluşturarak **YouTube hesabınıza otomatik yükleyen** tam teşekküllü bir bot otomasyonudur. 

## ⚡ Neler Yapıyor?

1. **📰 Haberi Bulur:** Google News NLP, AI, ChatGPT, Anthropic gibi konulardaki en güncel haberleri otomatik tarar.
2. **🖼️ Görsel Oluşturur/Bulur:** Haber başlığına uygun bir arka plan görselini (Unsplash üzerinden) arar.
3. **🎵 Müzik Ekler:** Videoya Freesound üzerinden arka plana estetik bir ses/müzik yerleştirir.
4. **✏️ Video Montajı:** FFmpeg kullanarak görselin üzerine dikkat çekici bir metin animasyonu ve ses ekler.
5. **🎬 Otomatik YouTube Upload:** Oluşturulan bu kısa videoyu (Shorts formatında) başlık, açıklama ve SEO uyumlu etiketlerle belirlediğiniz YouTube kanalına yükler.
6. **💬 İlk Yorumu Atar:** Videonun altına otomatik olarak etkileşim artırıcı "İlk yorum benden, haber hakkında ne düşünüyorsunuz?" tarzı yorumlar bırakır.

## 🛠️ Kurulum Gereksinimleri

- Python 3.10+
- FFmpeg (Sistemde yüklü ve ortam değişkenlerine eklenmiş olması gerekmektedir)
- Google Cloud - YouTube Data API v3 yetkilendirmesi (`client_secret.json`)
- Freesound ve Unsplash API keyleri
- Yüklü Python kütüphaneleri (Detaylar `requirements.txt` dosyasındadır)

## 🚀 Çalıştırma

Gerekli `.env` ayarlarını yaptıktan ve `client_secret.json` dosyasını ana dizine koyduktan sonra botu çalıştırmak çok basit:

```bash
# İlk önce paketleri kurun
pip install -r requirements.txt

# YouTube botunu başlatın
python news_bot.py
```

## 🔒 Güvenlik Notu
Bu repo içerisinde `client_secret.json`, `token.json` veya API kodlarınızı dahil etmeyin. Git'e dahil edilmesini engellemek için `.gitignore` dosyasını mutlaka kullanın!

---

🔥 **Hashtags:**
#YouTubeBot #YouTubeAutomation #AI #ChatGPT #OpenAI #YouTubeAPI #Python #PythonBot #Automation #GoogleNewsBot #VideoGenerator #VideoCreator #AutoUpload #FFmpeg #Code #OpenSource #Dev #Software #Developers #Tech #TechNews #Programming #GitHub #Project #Shorts #YouTubeShorts #ShortsAutomation #Anthropic #Claude #Gemini #Freesound #Unsplash #ContentCreator #Bot #YapayZeka #YapayZekaGündemi #TeknolojiHaberleri #Yazılım
