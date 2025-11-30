from selenium import webdriver
from bs4 import BeautifulSoup
import time
import json
from datetime import datetime

print("1. Safari tarayıcı başlatılıyor...")
driver = webdriver.Safari()
driver.maximize_window()

sehir_list = []

try:
    url = "https://www.petrolofisi.com.tr/akaryakit-fiyatlari"
    print(f"2. {url} adresine gidiliyor...")
    driver.get(url)
    
    # Sayfa yüklenene kadar bekle
    time.sleep(5)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    tbody = soup.find("tbody")

    if tbody:
        satirlar = tbody.find_all("tr")
        print(f"\n✅ BAŞARILI! Toplam {len(satirlar)} şehir bulundu. Doğru fiyatlar alınıyor...\n")
        
        print(f"{'ŞEHİR':<20} | {'BENZİN':<10} | {'MOTORİN':<10}")
        print("-" * 50)

        for satir in satirlar:
            sutunlar = satir.find_all("td")

            if len(sutunlar) > 2: # En az 3 sütun olduğundan emin olalım
                # 1. Sütun: Şehir Adı
                sehir = sutunlar[0].text.strip().replace("İl", "")
                
                # 2. Sütun: Benzin (Kurşunsuz 95)
                # Regex yerine direkt "with-tax" (vergili) class'ını buluyoruz
                benzin_span = sutunlar[1].find("span", class_="with-tax")
                benzin = benzin_span.text.strip() if benzin_span else "0"

                # 3. Sütun: Motorin (V/Max Diesel)
                motorin_span = sutunlar[2].find("span", class_="with-tax")
                motorin = motorin_span.text.strip() if motorin_span else "0"

                # Ekrana yazdır
                print(f"{sehir:<20} | {benzin:<10} | {motorin:<10}")
                
                # Listeye ekle
                sehir_list.append({
                    "sehir": sehir,
                    "benzin": float(benzin),
                    "motorin": float(motorin)
                })
        
        # Dosyayı kaydetmeyi unutmayalım
        zaman_damgasi = datetime.now().strftime("%d.%m.%Y %H:%M")
        final_veri = {
            "son_guncelleme": zaman_damgasi,
            "kaynak": "Petrol Ofisi",
            "veriler": sehir_list
        }
        
        with open("petrol_ofisi_fiyatlari.json", "w", encoding="utf-8") as f:
            json.dump(final_veri, f, ensure_ascii=False, indent=4)
        print("\n💾 Veriler kaydedildi.")

    else:
        print("❌ HATA: Tablo bulunamadı.")

except Exception as e:
    print(f"❌ Bir hata oluştu: {e}")

finally:
    driver.quit()