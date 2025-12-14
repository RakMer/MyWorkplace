import requests
import json
from datetime import datetime
import time

print("1. TotalEnergies (Güzel Enerji) API taraması başlatılıyor...")

BASE_URL = "https://apimobile.guzelenerji.com.tr/exapi/fuel_prices"

tum_veriler = []

headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
    "Accept": "application/json"
}

# Şehir Adları Sözlüğü (Plakadan Şehre)
# API şehir adını vermediği için manuel ekleyelim, daha şık görünür.
SEHIRLER = {
    1: "ADANA", 2: "ADIYAMAN", 3: "AFYONKARAHİSAR", 4: "AĞRI", 6: "AMASYA", 7: "ANKARA", 8: "ANTALYA", 66: "ARTVİN", 9: "AYDIN", 10: "BALIKESİR",
    13: "BİLECİK", 67: "BİNGÖL", 68: "BİTLİS", 14: "BOLU", 15: "BURDUR", 16: "BURSA", 17: "ÇANAKKALE", 18: "ÇANKIRI", 19: "ÇORUM", 20: "DENİZLİ",
    21: "DİYARBAKIR", 23: "EDİRNE", 69: "ELAZIĞ", 24: "ERZİNCAN", 25: "ERZURUM", 26: "ESKİŞEHİR", 27: "GAZİANTEP", 28: "GİRESUN", 70: "GÜMÜŞHANE", 71: "HAKKARİ",
    29: "HATAY", 31: "ISPARTA", 47: "MERSİN", 32: "İSTANBUL", 33: "İZMİR", 72: "KARS", 37: "KASTAMONU", 38: "KAYSERİ", 40: "KIRKLARELİ", 41: "KIRŞEHİR",
    42: "KOCAELİ", 43: "KONYA", 44: "KÜTAHYA", 45: "MALATYA", 46: "MANİSA", 34: "KAHRAMANMARAŞ", 73: "MARDİN", 48: "MUĞLA", 74: "MUŞ", 49: "NEVŞEHİR",
    50: "NİĞDE", 51: "ORDU", 53: "RİZE", 54: "SAKARYA", 55: "SAMSUN", 78: "SİİRT", 57: "SİNOP", 56: "SİVAS", 59: "TEKİRDAĞ", 60: "TOKAT",
    61: "TRABZON", 79: "TUNCELİ", 58: "ŞANLIURFA", 62: "UŞAK", 80: "VAN", 64: "YOZGAT", 65: "ZONGULDAK", 5: "AKSARAY", 81: "BAYBURT", 36: "KARAMAN",
    39: "KIRIKKALE", 12: "BATMAN", 82: "ŞIRNAK", 11: "BARTIN", 84: "ARDAHAN", 30: "IĞDIR", 63: "YALOVA", 35: "KARABÜK", 86: "KİLİS", 52: "OSMANİYE", 22: "DÜZCE"
}

print(f"📋 Toplam 81 il taranacak...\n")

for plaka in range(1, 87):
    try:
        url = f"{BASE_URL}/{plaka}"
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if data and isinstance(data, list) and len(data) > 0:
                ilce_sayisi = 0
                sehir_adi = SEHIRLER.get(plaka, f"IL-{plaka}")

                for istasyon in data:
                    # JSON'dan doğru anahtarları alıyoruz
                    ilce = istasyon.get("county_name")
                    
                    # Fiyatlar (Null gelirse 0.0 yap)
                    benzin = istasyon.get("kursunsuz_95_excellium_95")
                    motorin = istasyon.get("motorin")
                    
                    if benzin is None: benzin = 0.0
                    if motorin is None: motorin = 0.0
                    
                    if ilce and( ilce == "MERKEZ" or ilce == "MERKEZ-ANADOLU"):
                        tum_veriler.append({
                            "plaka": plaka,
                            "sehir": sehir_adi,
                            "ilce": ilce,
                            "benzin": float(benzin),
                            "motorin": float(motorin)
                        })
                        ilce_sayisi += 1
                
                print(f"✅ {sehir_adi:<15} alındı ({ilce_sayisi} ilçe)")
            else:
                # Veri boşsa (Ardahan vb.) uyar ama kaydetme
                sehir_adi = SEHIRLER.get(plaka, f"IL-{plaka}")
                print(f"⚠️ {sehir_adi:<15}: Veri yok.")
        else:
            print(f"❌ Plaka {plaka}: Hata ({response.status_code})")
            
    except Exception as e:
        print(f"❌ Hata (Plaka {plaka}): {e}")
        
    time.sleep(0.1)

# --- KAYDET ---
print("-" * 50)
if len(tum_veriler) > 0:
    final_veri = {
        "son_guncelleme": datetime.now().strftime("%d.%m.%Y %H:%M"),
        "kaynak": "TotalEnergies",
        "veriler": tum_veriler
    }
    
    with open("flutter_akaryakit/assets/total_fiyatlari.json", "w", encoding="utf-8") as f:
        json.dump(final_veri, f, ensure_ascii=False, indent=4)
        
    print(f"💾 İŞLEM TAMAMLANDI! {len(tum_veriler)} satır veri kaydedildi.")
else:
    print("😔 Veri çekilemedi.")