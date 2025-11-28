from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import json
from datetime import datetime

print("1. Safari tarayıcı başlatılıyor (Shell - Güçlü Mod)...")
driver = webdriver.Safari()
driver.maximize_window()
wait = WebDriverWait(driver, 15)

tum_veriler = []

try:
    url = "https://www.turkiyeshell.com/pompatest/"
    print(f"2. {url} adresine gidiliyor...")
    driver.get(url)
    time.sleep(5)

    # --- ŞEHİR LİSTESİNİ AL ---
    print("3. Şehir listesi hazırlanıyor...")
    dropdown_ok = wait.until(EC.element_to_be_clickable((By.ID, "cb_all_cb_province_B-1")))
    dropdown_ok.click()
    time.sleep(2)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    liste_items = soup.find_all("td", class_="dxeListBoxItem")
    
    sehirler = []
    for item in liste_items:
        text = item.text.strip()
        item_id = item.get("id")
        if text and text != "" and "Seçiniz" not in text:
            sehirler.append({"ad": text, "id": item_id})
    
    print(f"\n📋 Toplam {len(sehirler)} şehir bulundu. Veriler çekiliyor...\n")
    
    # Listeyi kapat
    webdriver.ActionChains(driver).move_by_offset(10, 10).click().perform()
    time.sleep(1)

    # --- DÖNGÜ ---
    for sehir in sehirler:
        sehir_adi = sehir["ad"]
        sehir_id = sehir["id"]
        
        try:
            print(f"🔄 {sehir_adi} taranıyor...", end="")
            
            # 1. Dropdown'ı Aç
            dropdown_ok = wait.until(EC.element_to_be_clickable((By.ID, "cb_all_cb_province_B-1")))
            driver.execute_script("arguments[0].click();", dropdown_ok)
            
            # 2. Şehre Tıkla
            sehir_elementi = wait.until(EC.presence_of_element_located((By.ID, sehir_id)))
            driver.execute_script("arguments[0].scrollIntoView(true);", sehir_elementi)
            driver.execute_script("arguments[0].click();", sehir_elementi)
            
            # 3. Bekle (Loading)
            try:
                wait.until(EC.invisibility_of_element_located((By.ID, "cb_all_cb_province_LP")))
            except: pass
            time.sleep(1.5)

            # 4. TABLOYU ÇEK (Düzeltilmiş Kısım)
            soup = BeautifulSoup(driver.page_source, "html.parser")
            
            # Tablo ID'sinde 'gv_prices' geçen tabloyu bul (En garantisi bu)
            # Eğer bulamazsa sayfadaki en büyük tabloyu alacak
            tablo = soup.find("table", {"id": lambda x: x and "gv_prices" in x})
            
            if not tablo:
                # Yedek: Class ismi dxgvTable olanı bul
                tablo = soup.find("table", class_="dxgvTable")

            if tablo:
                satirlar = tablo.find_all("tr")
                kayit = 0
                
                for satir in satirlar:
                    cols = satir.find_all("td")
                    
                    # Filtreyi kaldırdık! Sadece sütun sayısına bakıyoruz.
                    # Shell tablosu: İlçe | Benzin | V-Power | Motorin ... (En az 3-4 sütun olur)
                    if len(cols) >= 3:
                        # İçerik temizliği
                        sutun_verileri = [c.text.strip() for c in cols]
                        
                        ilce = sutun_verileri[0]
                        fiyat_1 = sutun_verileri[1] # Muhtemelen Benzin
                        fiyat_2 = sutun_verileri[2] # Muhtemelen Diğer Yakıt
                        
                        # --- DOĞRULAMA ---
                        # Bu satırın başlık satırı olmadığından emin olalım.
                        # Fiyatın içinde virgül veya nokta var mı? Ve sayı mı?
                        if any(char.isdigit() for char in fiyat_1) and (',' in fiyat_1 or '.' in fiyat_1):
                            tum_veriler.append({
                                "sehir": sehir_adi,
                                "ilce": ilce,
                                "benzin": fiyat_1,
                                "motorin": fiyat_2
                            })
                            kayit += 1
                
                if kayit > 0:
                    print(f" ✅ {kayit} ilçe alındı.")
                else:
                    print(" ⚠️ Tablo bulundu ama veri satırı tespit edilemedi. (HTML değişmiş olabilir)")
            else:
                print(" ⚠️ Tablo bulunamadı.")

        except Exception as e:
            print(f" ❌ Hata: {e}")
            # Hata durumunda kurtarma: sayfayı yenile
            driver.refresh()
            time.sleep(4)
            continue

    # --- KAYDET ---
    print("-" * 50)
    final_veri = {
        "son_guncelleme": datetime.now().strftime("%d.%m.%Y %H:%M"),
        "kaynak": "Shell",
        "veriler": tum_veriler
    }
    
    with open("shell_fiyatlari.json", "w", encoding="utf-8") as f:
        json.dump(final_veri, f, ensure_ascii=False, indent=4)
        
    print(f"💾 Tamamlandı! Veriler 'shell_fiyatlari.json' dosyasına kaydedildi.")

except Exception as e:
    print(f"❌ Kritik Hata: {e}")

finally:
    driver.quit()