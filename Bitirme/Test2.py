import time, requests
from pymongo import MongoClient


client = MongoClient('mongodb://localhost:27017/')
db = client['HackerNewsDB']  
collection = db['News']  

last_time = None
all_hits = []
while True:
    params = {"tags": "story", "hitsPerPage": 1000, "page": 0}
    if last_time:
        params["numericFilters"] = f"created_at_i<{last_time}"
    r = requests.get("https://hn.algolia.com/api/v1/search_by_date", params=params)
    data = r.json()
    hits = data["hits"]
    if not hits:
        break
    
    # Her bir hit'i MongoDB'ye kaydet
    for hit in hits:
        collection.update_one(
            {'objectID': hit['objectID']},  # unique ID ile kontrol
            {'$set': hit},  # dökümanı güncelle veya ekle
            upsert=True  # döküman yoksa yeni ekle
        )
    
    all_hits.extend(hits)
    last_time = min(int(h["created_at_i"]) for h in hits)
    print("Toplam:", len(all_hits), "Son zaman:", last_time, "Alınan:", len(hits), "Sayfa:", params["tags"], "HitsPerPage:", params["hitsPerPage"])
    
print("Bitti, toplam:", len(all_hits))