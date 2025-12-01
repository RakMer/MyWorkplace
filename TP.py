from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
import time
import json
from datetime import datetime


url = "https://www.tppd.com.tr/akaryakit-fiyatlari"
driver = webdriver.Safari()
DOSYA_ADI= "tp_fiatlari.json"


driver.maximize_window()
wait = WebDriverWait(driver, 20)
actions = ActionChains(driver)
tum_veriler= []

try:
    driver.get(url)
    time.sleep(2)
    sehirler= []
    sehir_count = 0
    
    soup = BeautifulSoup(driver.page_source, "html.parser")
    liste_items = soup.find_all("path")
    print(len(liste_items))
    for deneme in liste_items:
        text = deneme.text.strip()
        id = deneme.get("id")
        if deneme.get("id") != None:
            sehirler.append(deneme.get("id"))

    for sehir in sehirler:
        try:
            sehir_count+=1
            print(sehir_count, " Tane şehir eklendi")
            kayit_sayisi = 0
          

            # Önce element'in tıklanabilir olmasını bekle
            sehir_el = wait.until(EC.element_to_be_clickable((By.ID, f"citylink{sehir}")))
            
            # JavaScript ile tıklama (daha güvenilir)
            driver.execute_script("arguments[0].click();", sehir_el)
            # veya direkt click:
            # sehir_el.click()
            
            time.sleep(2)
            print(f"✅ {sehir} tıklandı")

            soup=BeautifulSoup(driver.page_source,"html.parser")
            table = soup.find("section", id="results")
            
            
            if table:
                satirlar = table.find_all("tr")
                for row in satirlar:
                    cols = row.find_all("td")
                    if len(cols) >= 3:
                        ilce = cols[0].text.strip()
                        benzin = cols[1].text.strip().replace(',', '.')
                        motorin = cols[3].text.strip().replace(',', '.')
                        

                        if (any(c.isdigit() for c in benzin) and sehir.upper() == ilce) or ilce == "ISTANBUL - ANADOLU" or ilce == "AFYON" or ilce == "K.MARAS":
                            tum_veriler.append({
                                "sehir": sehir.upper(),
                                "ilce": ilce,
                                "benzin": float(benzin),
                                "motorin": float(motorin)
                            })
                            kayit_sayisi += 1
                print(f"✅ {kayit_sayisi} ilçe alındı.")
            else:
                print(" ⚠️ Tablo yok.")

            
        except Exception as e:
            print(f"❌ {sehir} için hata: {e}")
            continue  # bir sonraki şehre geç

    print("-" * 50)
    final_veri = {
        "son_guncelleme": datetime.now().strftime("%d.%m.%Y %H:%M"),
        "kaynak": "Shell",
        "url": url,
        "veriler": tum_veriler
    }
    
    with open(DOSYA_ADI, "w", encoding="utf-8") as f:
        json.dump(final_veri, f, ensure_ascii=False, indent=4)
        
    print(f"💾 İŞLEM TAMAMLANDI! {len(tum_veriler)} kayıt kaydedildi.")


except Exception as e:
    print(f"❌ Kritik Hata: {e}")