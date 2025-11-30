# Akaryakıt Takip

Türkiye'deki akaryakıt şirketlerinin güncel fiyatlarını gösteren modern web uygulaması.

## Özellikler

- 📡 **CollectAPI entegrasyonu** - Gerçek zamanlı akaryakıt fiyatları
- 💾 **Akıllı caching** - API isteği sınırını koruma (ilk çalışmada bir kez çağrı)
- 🏢 6+ ana akaryakıt şirketi (SHELL, OPET, AYGAZ, TOTAL, PETREN, BATTAL, LUKOIL vb.)
- ⛽ 4 yakıt türü (Benzin 95, Benzin 98, Diesel, LPG)
- 📊 Ortalama fiyat analizi
- 💰 En ucuz ve en pahalı şirketleri gösterme
- 📱 Responsive tasarım
- 🎨 Modern arayüz

## API Kaynağı

Uygulama **CollectAPI** hizmetini kullanarak Türkiye'deki akaryakıt fiyatlarını gerçek zamanlı olarak çeker:
- **Hizmet**: CollectAPI - Turkey Gasoline Prices
- **Endpoint**: `https://api.collectapi.com/gasPrice/turkeyGasoline`
- **Lokasyon**: Kadıköy/İstanbul (değiştirilebilir)

### Caching Sistemi
- ✅ Uygulama başladığında **bir kez** API'ye istek atılır
- ✅ Sonra **cache'den** veriler kullanılır
- ✅ API isteği sınırlarını aşmaz
- ✅ En hızlı yanıt süresi (~5-10ms)

## Teknolojiler

- **Frontend**: Next.js 15, React 18, TypeScript, Tailwind CSS
- **Backend**: Next.js API Routes
- **Icons**: Lucide React
- **HTTP Client**: Node.js Fetch API
- **Veri Kaynağı**: CollectAPI

## Kurulum

```bash
# Bağımlılıkları yükle
npm install

# Geliştirme sunucusunu başlat
npm run dev

# Üretim için build yap
npm run build

# Üretim sunucusunu başlat
npm start
```

## Kullanım

1. Geliştirme sunucusunu başlattıktan sonra [http://localhost:3000](http://localhost:3000) adresine gidin
2. Ilk sayfa yüklemesinde CollectAPI'den gerçek fiyatlar çekilir
3. Tüm akaryakıt şirketlerinin güncel fiyatlarını görüntüleyin
4. Ortalama fiyatları ve en ucuz/pahalı şirketleri takip edin
5. Herhangi bir şirketin detaylarını görmek için kartına tıklayın

## API Endpoints

### Tüm Şirketleri Getir
```
GET /api/fuel-companies
```

Yanıt:
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "SHELL",
      "logo": "🔴",
      "gasoline95": 54.86,
      "gasoline98": 57.36,
      "diesel": 54.36,
      "lpg": 30.48,
      "headquarters": "İstanbul",
      "founded": 1980,
      "priceUpdateTime": "2025-11-25T10:30:00.000Z"
    }
  ],
  "lastUpdated": "2025-11-25T10:30:00.000Z"
}
```

### Şirket Fiyatlarını Güncelle
```
POST /api/fuel-companies
```

İstek Gövdesi:
```json
{
  "id": 1,
  "gasoline95": 55.00,
  "gasoline98": 57.50,
  "diesel": 54.50,
  "lpg": 30.60
}
```

### Belirli Şirketin Fiyatlarını Getir
```
GET /api/fuel-companies/[id]
```

## Şirketler

| No | Şirket | Logo | Merkez | Kuruluş |
|----|--------|------|--------|---------|
| 1 | SHELL | 🔴 | İstanbul | 1980 |
| 2 | OPET | 🟠 | İstanbul | 1974 |
| 3 | AYGAZ | 🟡 | Ankara | 1972 |
| 4 | TOTAL | 🔵 | İstanbul | 1980 |
| 5 | PETREN | 🟢 | İzmir | 1993 |
| 6 | BATTAL | 🟣 | Ankara | 1998 |
| 7 | LUKOIL | 🟤 | Rusya | 1991 |

## Klasör Yapısı

```
├── src/
│   ├── app/
│   │   ├── api/
│   │   │   └── fuel-companies/
│   │   │       ├── route.ts          (Ana API route)
│   │   │       └── [id]/
│   │   │           └── route.ts      (Belirli şirket API)
│   │   ├── globals.css
│   │   ├── layout.tsx
│   │   └── page.tsx                  (Ana sayfa bileşeni)
│   └── lib/
│       ├── fuelPriceApi.ts           (CollectAPI entegrasyonu)
│       └── priceCache.ts             (Cache yönetimi)
├── package.json
├── tsconfig.json
├── next.config.ts
├── tailwind.config.ts
└── postcss.config.js
```

## Geliştirme

Geliştirme sırasında:

1. `npm run dev` ile geliştirme sunucusunu başlatın
2. Dosyalar otomatik olarak yeniden derlenecektir
3. Tarayıcıda otomatik olarak yenileme (hot reload) yapılacaktır

## Build

Üretim için derleme:

```bash
npm run build
npm start
```

## Lint

Kod kalitesi kontrol etmek için:

```bash
npm run lint
```

## Performans

- **İlk Yükleme**: ~5-6 saniye (CollectAPI çağrısı ile)
- **Sonraki İstekler**: ~5-15ms (cache'den)
- **Ortalama Sayfa Yüklemesi**: ~50-100ms
- **API Response**: ~5-25ms (cache'den)

## Gelecek Geliştirmeler

- [ ] Farklı şehirler/bölgeler için fiyatlar
- [ ] Fiyat geçmişi ve grafikleri
- [ ] İstasyonların konum haritası
- [ ] Push bildirim sistemi (fiyat düşüşünde uyarı)
- [ ] Mobil uygulama (React Native)
- [ ] Kullanıcı hesapları ve tercihleri
- [ ] Günlük/saatlik fiyat raporları
- [ ] Veritabanı entegrasyonu (PostgreSQL)

## Lisans

MIT License © 2025 Akaryakıt Takip

## İletişim

Soru ve önerileriniz için bir issue açabilir veya proje yöneticisine ulaşabilirsiniz.
