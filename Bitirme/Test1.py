import time
import requests
from pymongo import MongoClient, UpdateOne # UpdateOne'ı içe aktar


client = MongoClient('mongodb://localhost:27017/')
db = client['HackerNewsDB']
collection = db['HackerNews']


try:
    collection.create_index(
        [("objectID", 1)],
        unique=True,
        name="objectID_unique_index" # İndekse isim verelim
    )
    print("objectID indeksi oluşturuldu/doğrulandı.")
except Exception as e:
    
    if "index already exists" in str(e):
         print("objectID indeksi zaten mevcut.")
    else:
        print(f"İndeks oluşturma hatası: {e}")

# Veri Çekme ve Kaydetme 

last_time = None
all_hits_count = 0
request_session = requests.Session() 

while True:
    params = {"tags": "story", "hitsPerPage": 1000, "page": 0}
    if last_time:
        params["numericFilters"] = f"created_at_i<{last_time}"
    
    # 1. API İsteği
    try:
        r = request_session.get("https://hn.algolia.com/api/v1/search_by_date", params=params, timeout=30)
        r.raise_for_status() 
        data = r.json()
    except requests.exceptions.RequestException as e:
        print(f"API isteği hatası: {e}")
        time.sleep(10) # Hata durumunda bekle ve tekrar dene
        continue
    
    hits = data.get("hits", [])
    if not hits:
        break
    
    # --- OPTİMİZASYON: Bulk Write (Yığın Yazma) İşlemi ---
    operations = []
    
    for hit in hits:
        # Her bir hit için bir UpdateOne operasyonu hazırlar
        update_operation = UpdateOne(
            {'objectID': hit['objectID']},  # Filtre
            {'$set': hit},                  # Güncelleme
            upsert=True                     # Ekle/Güncelle
        )
        operations.append(update_operation)
    
    
    if operations:
        try:
            result = collection.bulk_write(operations, ordered=False) # ordered=False daha hızlı olabilir
            
          
            print(f"Bulk Write Başarılı. Yeni Eklenen: {result.upserted_count}, Güncellenen: {result.modified_count + result.matched_count}")
        except Exception as e:
            print(f"MongoDB Bulk Write Hatası: {e}")
            
    
    all_hits_count += len(hits)
    last_time = min(int(h["created_at_i"]) for h in hits)
    
    print(f"Toplam: {all_hits_count} | Son zaman: {last_time} | Alınan: {len(hits)}")

print(f"Bitti, toplam işlenen veri: {all_hits_count}")