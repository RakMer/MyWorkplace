from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
import time
import json
from datetime import datetime

# Türkçe karakter normalizasyon
def sehir_normalize(sehir_adi):
    """Web sitesinden alınan şehir adını uygulamanın beklediği formata çevirir."""
    normalize_map = {
        "AFYON": "AFYONKARAHİSAR",
        "AFYONKARAHISAR": "AFYONKARAHİSAR",
        "AGRI": "AĞRI",
        "ISTANBUL": "İSTANBUL",
        "IZMIR": "İZMİR",
        "K.MARAS": "KAHRAMANMARAŞ",
        "KAHRAMANMARAS": "KAHRAMANMARAŞ",
        "SANLIURFA": "ŞANLIURFA",
        "SIRNAK": "ŞIRNAK",
        "IGDIR": "IĞDIR",
        "CANAKKALE": "ÇANAKKALE",
        "CANKIRI": "ÇANKIRI",
        "CORUM": "ÇORUM",
        "DENIZLI": "DENİZLİ",
        "DIYARBAKIR": "DİYARBAKIR",
        "DUZCE": "DÜZCE",
        "EDIRNE": "EDİRNE",
        "ELAZIG": "ELAZIĞ",
        "ERZINCAN": "ERZİNCAN",
        "ESKISEHIR": "ESKİŞEHİR",
        "GAZIANTEP": "GAZİANTEP",
        "GIRESUN": "GİRESUN",
        "GUMUSHANE": "GÜMÜŞHANE",
        "HAKKARI": "HAKKARİ",
        "KIRIKKALE": "KIRIKKALE",
        "KIRKLARELI": "KIRKLARELİ",
        "KIRSEHIR": "KIRŞEHİR",
        "KILIS": "KİLİS",
        "KOCAELI": "KOCAELİ",
        "KUTAHYA": "KÜTAHYA",
        "MANISA": "MANİSA",
        "MARDIN": "MARDİN",
        "MERSIN": "MERSİN",
        "MUGLA": "MUĞLA",
        "MUS": "MUŞ",
        "NEVSEHIR": "NEVŞEHİR",
        "NIGDE": "NİĞDE",
        "OSMANIYE": "OSMANİYE",
        "RIZE": "RİZE",
        "SIIRT": "SİİRT",
        "SINOP": "SİNOP",
        "SIVAS": "SİVAS",
        "TEKIRDAG": "TEKİRDAĞ",
        "TUNCELI": "TUNCELİ",
        "USAK": "UŞAK",
        "ARTVIN": "ARTVİN",
        "AYDIN": "AYDIN",
        "BALIKESIR": "BALIKESİR",
        "BARTIN": "BARTIN",
        "BILECIK": "BİLECİK",
        "BINGOL": "BİNGÖL",
        "BITLIS": "BİTLİS",
        "KARABUK": "KARABÜK",
        "KAYSERI": "KAYSERİ"
    }
    sehir_upper = sehir_adi.upper().strip()
    return normalize_map.get(sehir_upper, sehir_upper)


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
                            # Şehir ve ilçe isimlerini normalize et
                            sehir_normalized = sehir_normalize(sehir)
                            ilce_normalized = ilce
                            
                            # İlçe özel durumları
                            if ilce == "ISTANBUL - ANADOLU":
                                sehir_normalized = "İSTANBUL"
                                ilce_normalized = "İSTANBUL ANADOLU"
                            elif ilce == "AFYON":
                                sehir_normalized = "AFYONKARAHİSAR"
                                ilce_normalized = "AFYONKARAHİSAR"
                            elif ilce == "K.MARAS":
                                sehir_normalized = "KAHRAMANMARAŞ"
                                ilce_normalized = "KAHRAMANMARAŞ"
                            
                            tum_veriler.append({
                                "sehir": sehir_normalized,
                                "ilce": ilce_normalized,
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
        "kaynak": "TP",
        "url": url,
        "veriler": tum_veriler
    }
    
    with open(f"flutter_akaryakit/assets/{DOSYA_ADI}", "w", encoding="utf-8") as f:
        json.dump(final_veri, f, ensure_ascii=False, indent=4)
        
    print(f"💾 İŞLEM TAMAMLANDI! {len(tum_veriler)} kayıt kaydedildi.")


except Exception as e:
    print(f"❌ Kritik Hata: {e}")