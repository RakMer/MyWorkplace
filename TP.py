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


driver.maximize_window()
wait = WebDriverWait(driver, 20)
actions = ActionChains(driver)

try:
    driver.get(url)
    time.sleep(2)
    sehirler= []
    
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
           
            driver.get(url)
            time.sleep(2) # Sayfanın oturmasını bekle

            # Önce element'in tıklanabilir olmasını bekle
            sehir_el = wait.until(EC.element_to_be_clickable((By.ID, f"citylink{sehir}")))
            
            # JavaScript ile tıklama (daha güvenilir)
            driver.execute_script("arguments[0].click();", sehir_el)
            # veya direkt click:
            # sehir_el.click()
            
            time.sleep(5)
            print(f"✅ {sehir} tıklandı")

            table = soup.find("section",id="results")
            if table:
                satirlar = table.find_all("tr")
                for row in satirlar:
                    cols = row.find_all("td")
                    if len(cols) >= 3:
                        ilce = cols[0].text.strip()
                        benzin = cols[1].text.strip().replace(',', '.')
                        motorin = cols[3].text.strip().replace(',', '.')
                        print(ilce,benzin,motorin)
            

            
        except Exception as e:
            print(f"❌ {sehir} için hata: {e}")
            continue  # bir sonraki şehre geç

except Exception as e:
    print(f"❌ Kritik Hata: {e}")