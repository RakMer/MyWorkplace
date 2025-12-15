from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import json
from datetime import datetime

# Şehir normalizasyon fonksiyonu
def sehir_normalize(sehir_adi):
    """Web sitesinden alınan şehir adını uygulamanın beklediği formata çevirir."""
    normalize_map = {
        "AFYON": "AFYONKARAHİSAR",
        "AGRI": "AĞRI",
        "ISTANBUL": "İSTANBUL",
        "IZMIR": "İZMİR",
        "K.MARAS": "KAHRAMANMARAŞ",
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
        "BALIKESIR": "BALIKESİR",
        "BILECIK": "BİLECİK",
        "BINGOL": "BİNGÖL",
        "BITLIS": "BİTLİS",
        "KARABUK": "KARABÜK",
        "KAYSERI": "KAYSERİ"
    }
    sehir_upper = sehir_adi.upper().strip()
    return normalize_map.get(sehir_upper, sehir_upper)

print("1. Safari tarayıcı başlatılıyor (Lukoil)...")
driver = webdriver.Safari()
driver.maximize_window()
wait = WebDriverWait(driver, 10)

tum_veriler = []

try:
    url = "https://www.lukoil.com.tr/PompaFiyatlari"
    print(f"2. {url} adresine gidiliyor...")
    driver.get(url)
    time.sleep(3)

    # --- ŞEHİR LİSTESİNİ AL ---
    select_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "select[id*='ddlCity']")))
    select = Select(select_element)
    
    sehir_isimleri = [opt.text for opt in select.options if "Seçiniz" not in opt.text and opt.text.strip() != ""]
    print(f"\n📋 Toplam {len(sehir_isimleri)} şehir tespit edildi. Tarama başlıyor...\n")

    # --- DÖNGÜ ---
    for sehir_adi in sehir_isimleri:
        try:
            print(f"🔄 {sehir_adi} işleniyor...", end="")
            
            # 1. Şehri Seç
            select_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "select[id*='ddlCity']")))
            dropdown = Select(select_element)
            dropdown.select_by_visible_text(sehir_adi)
            
            # 2. BUTONA TIKLA (ID ile)
            sorgula_btn = wait.until(EC.element_to_be_clickable((By.ID, "ContentPlaceHolder1_btnGetPrices")))
            driver.execute_script("arguments[0].click();", sorgula_btn)
            
            # Tablonun gelmesi için bekle
            time.sleep(2.5)
            
            # --- HTML ANALİZİ (RESME GÖRE) ---
            soup = BeautifulSoup(driver.page_source, "html.parser")
            
            # Resimdeki yapı: <div class="listPrice left"> -> <table>
            container_div = soup.find("div", class_="listPrice")
            
            if container_div:
                tablo = container_div.find("table")
                
                if tablo:
                    satirlar = tablo.find_all("tr")
                    kayit_sayisi = 0
                    
                    # İlk satır başlık olduğu için atlıyoruz ([1:])
                    for satir in satirlar[1:]:
                        sutunlar = satir.find_all("td")
                        
                        # Resme göre: [0]=İlçe, [1]=Benzin, [2]=Motorin
                        if len(sutunlar) >= 3:
                            ilce = sutunlar[0].text.strip()
                            benzin = sutunlar[1].text.strip()
                            motorin = sutunlar[2].text.strip()
                            
                            if ilce and benzin and ilce == "MERKEZ":
                                if ilce =="MERKEZ":
                                    # Şehir adını normalize et
                                    sehir_normalized = sehir_normalize(sehir_adi)
                                    
                                    tum_veriler.append({
                                        "sehir": sehir_normalized,
                                        "ilce": ilce,
                                        "benzin": float(benzin.replace(',', '.')),
                                        "motorin": float(motorin.replace(',', '.'))
                                    })
                                    kayit_sayisi += 1
                            if ilce and benzin and (sehir_adi == "ISTANBUL" or sehir_adi == "AMASYA"):
                                if ilce =="ISTANBUL_ANA" or ilce == "AMASYA":
                                    # Şehir adını normalize et
                                    sehir_normalized = sehir_normalize(sehir_adi)
                                    
                                    tum_veriler.append({
                                        "sehir": sehir_normalized,
                                        "ilce": ilce,
                                        "benzin": float(benzin.replace(',', '.')),
                                        "motorin": float(motorin.replace(',', '.'))
                                    })
                                    kayit_sayisi += 1
                        
                    print(f" ✅ {kayit_sayisi} ilçe alındı.")
                else:
                    print(" ⚠️ Div bulundu ama Tablo yok.")
            else:
                print(" ⚠️ 'listPrice' alanı bulunamadı.")

        except Exception as e:
            print(f" ❌ Hata: {e}")
            continue

    # --- KAYDET ---
    print("-" * 50)
    final_veri = {
        "son_guncelleme": datetime.now().strftime("%d.%m.%Y %H:%M"),
        "kaynak": "Lukoil",
        "veriler": tum_veriler
    }
    
    with open("flutter_akaryakit/assets/lukoil_fiyatlari.json", "w", encoding="utf-8") as f:
        json.dump(final_veri, f, ensure_ascii=False, indent=4)
        
    print(f"💾 İşlem bitti! 'lukoil_fiyatlari.json' dosyasına bakabilirsin.")

except Exception as e:
    print(f"❌ Genel Hata: {e}")

finally:
    driver.quit()