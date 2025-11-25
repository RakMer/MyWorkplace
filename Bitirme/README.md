# HackerNews Spark Web Arayüzü

Flask ve PySpark kullanarak HackerNews verilerini analiz etmek için web arayüzü.

## Kurulum

### Gerekli Paketleri Yükle

```bash
pip install flask pyspark pymongo
```

## Çalıştırma

### 1. Flask Uygulamasını Başlat

```bash
python app.py
```

Uygulama `http://localhost:5000` adresinde açılacak.

## Proje Yapısı

```
Bitirme/
├── app.py                 # Flask uygulaması
├── spark_queries.py       # Spark sorguları (helper modül)
├── templates/
│   └── index.html         # HTML arayüzü
├── static/
│   ├── style.css          # CSS stilleri
│   └── script.js          # JavaScript işlevleri
└── requirements.txt       # Bağımlılıklar
```

## API Endpoints

### GET /
Ana sayfa

### GET /api/statistics
İstatistikleri döner (toplam makale, yazarlı makale)

### GET /api/ai-articles
AI başlıklı makaleleri döner
- Query Parameter: `limit` (varsayılan: 50)

### GET /api/top-stories
En çok yorumlanan hikayeler
- Query Parameter: `limit` (varsayılan: 10)

### GET /api/top-authors
En çok haber yazan yazarlar
- Query Parameter: `limit` (varsayılan: 10)

### GET /api/top-articles
En yüksek puan alan makaleler
- Query Parameter: `limit` (varsayılan: 10)

### GET /api/all-data
Tüm verileri bir seferde döner

## Özellikler

✅ Hızlı veri yükleme (Spark optimizasyonları)
✅ Responsive tasarım (mobil uyumlu)
✅ MongoDB integrasyon
✅ Hataya karşı dayanıklı
✅ Renkli ve modern arayüz

## MongoDB Bağlantı

MongoDB'nin şu şekilde yapılandırılmış olduğundan emin olun:
- Host: `localhost`
- Port: `27017`
- Database: `HackerNewsDB`
- Collection: `HackerNews`

## Performance İpuçları

1. Spark konfigürasyonları `spark_queries.py`'de optimize edilmiştir
2. Projection pushdown veri transfer miktarını azaltır
3. Bellek tanımlamaları sistem kaynaklarına uygun şekilde ayarlanmıştır
4. Cache kullanılmamıştır (bellek sorunlarını önlemek için)

## Sorun Giderme

### OutOfMemory Hatası
- `spark_queries.py`'de memory ayarlarını artırın
- Veri set büyüklüğünü kontrol edin

### MongoDB Bağlantı Hatası
- MongoDB'nin çalışıp çalışmadığını kontrol edin
- Bağlantı bilgilerini doğrulayın

### Slowdown
- Spark UI'ye `http://localhost:4040` adresinden erişin
- Partition sayısını ayarla: `config("spark.sql.shuffle.partitions", "...")`
