from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
import time
import json
from datetime import datetime

# --- AYARLAR ---
URL = "https://www.turkiyeshell.com/pompatest/"
DOSYA_ADI = "shell_fiyatlari.json"

print("1. Safari tarayıcı başlatılıyor (Shell - Refresh Mode)...")
driver = webdriver.Safari()
driver.maximize_window()
wait = WebDriverWait(driver, 20)
actions = ActionChains(driver)

tum_veriler = []

try:
    print(f"2. {URL} adresine gidiliyor...")
    driver.get(URL)
    time.sleep(2)

    # --- ADIM 1: ŞEHİR İSİMLERİNİ BİR KERE ALIP SAKLAYALIM ---
    print("3. Şehir listesi hafızaya alınıyor...")
    
    # Dropdown'ı aç
    dropdown_ok = wait.until(EC.visibility_of_element_located((By.ID, "cb_all_cb_province_B-1")))
    actions.move_to_element(dropdown_ok).click().perform()
    time.sleep(2)

    # HTML'den isimleri ve ID'leri al
    soup = BeautifulSoup(driver.page_source, "html.parser")
    liste_items = soup.find_all("td", class_="dxeListBoxItem")
    
    sehirler = []
    for item in liste_items:
        text = item.text.strip()
        item_id = item.get("id")
        if text and text != "" and "Seçiniz" not in text:
            sehirler.append({"ad": text, "id": item_id})
    
    print(f"\n📋 Toplam {len(sehirler)} şehir bulundu. İşlem başlıyor...\n")

    # --- ADIM 2: DÖNGÜ (HER ŞEHİR İÇİN SAYFA YENİLEME) ---
    for i, sehir in enumerate(sehirler):
        try:
            sehir_adi = sehir['ad']
            # Dikkat: Sayfa yenilenince ID'ler değişmiyor ama elementler bayatlıyor.
            # ID'yi listeden aldığımız gibi kullanabiliriz çünkü Shell ID'leri sabit (LBI0T0, LBI1T0...)
            sehir_id = sehir['id'] 

            print(f"[{i+1}/{len(sehirler)}] 🔄 {sehir_adi:<15} işleniyor...", end="")

            # A. SAYFAYI YENİLE (Garanti temizlik)
            # Adana bittikten sonra sayfa durumu bozuluyor, o yüzden her seferinde taze sayfa açıyoruz.
            if i >= 0: # İlk şehirde zaten açığız, sonrakilerde yenile
                driver.get(URL)
                time.sleep(1) # Sayfanın oturmasını bekle

            # B. Dropdown'ı Tekrar Bul ve Aç
            dropdown_ok = wait.until(EC.visibility_of_element_located((By.ID, "cb_all_cb_province_B-1")))
            actions.move_to_element(dropdown_ok).click().perform()
            time.sleep(1.5) # Menü açılma süresi

            # C. Şehri Bul ve Tıkla
            # Sayfa yenilendiği için elementi tekrar bulmalıyız
            sehir_el = wait.until(EC.presence_of_element_located((By.ID, sehir_id)))
            
            # Elemente kaydır ve tıkla
            driver.execute_script("arguments[0].scrollIntoView(true);", sehir_el)
            time.sleep(0.5)
            actions.move_to_element(sehir_el).click().perform()

            # D. Yükleniyor Panelini Bekle
            try:
                # Panel görünene kadar bekle (kısa)
                WebDriverWait(driver, 3).until(EC.visibility_of_element_located((By.ID, "cb_all_grdPrices_LP")))
                # Panel kaybolana kadar bekle (uzun)
                WebDriverWait(driver, 15).until(EC.invisibility_of_element_located((By.ID, "cb_all_grdPrices_LP")))
            except:
                time.sleep(1) # Manuel bekleme

            # E. Veriyi Çek
            #soup = BeautifulSoup(driver.page_source, "html.parser")
            tablo = soup.find("table", id="cb_all_grdPrices_DXMainTable")
            
            if tablo:
                satirlar = tablo.find_all("tr", class_="dxgvDataRow")
                kayit_sayisi = 0
                for row in satirlar:
                    cols = row.find_all("td")
                    if len(cols) >= 3:
                        ilce = cols[0].text.strip()
                        benzin = cols[1].text.strip().replace(',', '.')
                        motorin = cols[2].text.strip().replace(',', '.')
                        
                        if any(c.isdigit() for c in benzin):
                            tum_veriler.append({
                                "sehir": sehir_adi,
                                "ilce": ilce,
                                "benzin": float(benzin),
                                "motorin": float(motorin)
                            })
                            kayit_sayisi += 1
                print(f" ✅ {kayit_sayisi} ilçe alındı.")
            else:
                print(" ⚠️ Tablo yok.")

        except Exception as e:
            print(f" ❌ Hata: {str(e).splitlines()[0][:50]}...")
            continue # Hata olsa bile döngü devam etsin, sonraki şehirde sayfa zaten yenilenecek

    # --- KAYDET ---
    print("-" * 50)
    final_veri = {
        "son_guncelleme": datetime.now().strftime("%d.%m.%Y %H:%M"),
        "kaynak": "Shell",
        "url": URL,
        "veriler": tum_veriler
    }
    
    with open(DOSYA_ADI, "w", encoding="utf-8") as f:
        json.dump(final_veri, f, ensure_ascii=False, indent=4)
        
    print(f"💾 İŞLEM TAMAMLANDI! {len(tum_veriler)} kayıt kaydedildi.")

except Exception as e:
    print(f"❌ Kritik Hata: {e}")

finally:
    try: driver.quit()
    except: pass