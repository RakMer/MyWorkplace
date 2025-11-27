"""Spark sorguları için helper modül"""
from pymongo import MongoClient
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
import time

def get_spark_session():
    """Spark session'ı başlat veya mevcut olanı döndür"""
    return (
        SparkSession.builder
        .appName("MongoSparkTest")
        .config("spark.driver.memory", "3g")
        .config("spark.executor.memory", "2g")
        .config("spark.sql.adaptive.enabled", "true")
        .config("spark.sql.shuffle.partitions", "8")
        .getOrCreate()
    )

def get_dataframe(spark):
    """MongoDB'den veri çek ve DataFrame oluştur"""
    try:
        # MongoDB'ye bağlan
        client = MongoClient("mongodb://localhost:27017/")
        db = client["HackerNewsDB"]
        collection = db["HackerNews"]
        
        # Verileri al — `_id` alanını hariç tut ve gelen dökümanları sanitize et
        cursor = collection.find({}, {"_id": 0, "title": 1, "author": 1, "story_id": 1, "points": 1})
        raw_data = list(cursor)

        if not raw_data:
            print("Uyarı: MongoDB'den veri alınamadı. Boş bir DataFrame döndürülüyor.")
            return spark.createDataFrame([], "title STRING, author STRING, story_id STRING, points INT")

        # Mongo dökümanlarını Spark uyumlu basit dict'lere dönüştür
        data = []
        for doc in raw_data:
            title = doc.get("title")
            author = doc.get("author")
            # story_id bazen ObjectId veya int olabilir, stringify etmek güvenli
            story_id = doc.get("story_id")
            if story_id is not None:
                try:
                    story_id = str(story_id)
                except Exception:
                    story_id = None

            points = doc.get("points")
            if points is not None:
                try:
                    points = int(points)
                except Exception:
                    points = None

            data.append({"title": title, "author": author, "story_id": story_id, "points": points})

        # DataFrame oluştur
        df = spark.createDataFrame(data)
        spark.sparkContext.setLogLevel("ERROR")
        return df
    except Exception as e:
        print(f"MongoDB bağlantı hatası: {e}")
        print("Boş DataFrame döndürülüyor...")
        return spark.createDataFrame([], "title STRING, author STRING, story_id STRING, points INT")

def query_ai_articles(df, limit=50):
    """AI başlıklı makaleleri bul"""
    result = (
        df.filter(F.lower(F.col("title")).contains("ai"))
        .select("title", "author")
        .limit(limit)
        .collect()
    )
    return [{"title": row["title"], "author": row["author"]} for row in result]

def query_top_stories(df, limit=10):
    """En çok yoruma sahip hikayeler"""
    result = (
        df.groupBy("story_id").count()
        .orderBy(F.desc("count"))
        .limit(limit)
        .collect()
    )
    return [{"story_id": row["story_id"], "comment_count": row["count"]} for row in result]

def query_statistics(df):
    """İstatistikler"""
    stats = df.agg(
        F.count("*").alias("Toplam"),
        F.count("author").alias("Yazarı olan")
    ).collect()[0]
    return {
        "total": stats["Toplam"],
        "with_author": stats["Yazarı olan"]
    }

def query_top_authors(df, limit=10):
    """En çok haber yazan yazarlar"""
    result = (
        df.filter(F.col("author").isNotNull())
        .groupBy("author").count()
        .orderBy(F.desc("count"))
        .limit(limit)
        .collect()
    )
    return [{"author": row["author"], "article_count": row["count"]} for row in result]

def query_top_articles_by_points(df, limit=10):
    """En yüksek puan alan makaleler"""
    result = (
        df.filter(F.col("points").isNotNull())
        .select("title", "points")
        .orderBy(F.desc("points"))
        .limit(limit)
        .collect()
    )
    return [{"title": row["title"], "points": row["points"]} for row in result]
