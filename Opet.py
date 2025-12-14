from selenium import webdriver
from bs4 import BeautifulSoup
import time
import re
import json
from datetime import datetime  # Tarih saat için gerekli kütüphane

print("1. Safari tarayıcı başlatılıyor...")

driver = webdriver.Safari()
driver.maximize_window()

# Şehir verilerini tutacak liste
sehir_listesi = []

try:
    url = "https://www.opet.com.tr/akaryakit-fiyatlari"
    print(f"2. {url} adresine gidiliyor...")
    driver.get(url)

    print("3. Verilerin yüklenmesi bekleniyor (5 sn)...")
    time.sleep(5)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    tbody = soup.find("tbody")
    
    if tbody:
        satirlar = tbody.find_all("tr")
        print(f"\n✅ BAŞARILI! Toplam {len(satirlar)} şehir bulundu. İşleniyor...\n")
        
        print(f"{'ŞEHİR':<20} | {'BENZİN':<10} | {'MOTORİN':<10}")
        print("-" * 50)
        
        for satir in satirlar:
            sutunlar = satir.find_all("td")
            
            if len(sutunlar) > 1:
                sehir = sutunlar[0].text.strip().replace("İl", "")
                satir_metni = " ".join([td.text for td in sutunlar])
                
                # Regex ile fiyatları bul
                bulunan_fiyatlar = re.findall(r'(\d+\.\d+)\s*TL', satir_metni)
                
                if len(bulunan_fiyatlar) >= 2:
                    benzin = bulunan_fiyatlar[0]
                    motorin = bulunan_fiyatlar[1]
                    
                    # '95' hatasını temizle (Örn: 9556.82 -> 56.82)
                    if float(benzin) > 200 and benzin.startswith("95"):
                        benzin = benzin[2:]

                    # Ekrana yazdır
                    print(f"{sehir:<20} | {benzin:<10} | {motorin:<10}")
                    
                    # Listeye ekle
                    sehir_listesi.append({
                        "sehir": sehir,
                        "benzin": float(benzin),
                        "motorin": float(motorin)
                    })

        # --- TARİH EKLEME VE KAYDETME KISMI ---
        
        # Şu anki tarih ve saati al
        zaman_damgasi = datetime.now().strftime("%d.%m.%Y %H:%M")
        
        # JSON dosyasının ana yapısını oluştur
        final_veri = {
            "son_guncelleme": zaman_damgasi,
            "kaynak": "Opet",
            "veriler": sehir_listesi
        }

        # Dosyayı kaydet
        with open("flutter_akaryakit/assets/opet_fiyatlari.json", "w", encoding="utf-8") as f:
            json.dump(final_veri, f, ensure_ascii=False, indent=4)
            
        print("-" * 50)
        print(f"💾 Veriler '{zaman_damgasi}' tarihiyle kaydedildi!")

    else:
        print("❌ HATA: Tablo bulunamadı.")

except Exception as e:
    print(f"❌ Bir hata oluştu: {e}")

finally:
    driver.quit()
    print("İşlem tamamlandı.")