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
        cursor = collection.find(
            {},
            {
                "_id": 0,
                "title": 1,
                "author": 1,
                "story_id": 1,
                "points": 1,
                "created_at_i": 1,
            },
        )
        raw_data = list(cursor)

        if not raw_data:
            print("Uyarı: MongoDB'den veri alınamadı. Boş bir DataFrame döndürülüyor.")
            return spark.createDataFrame(
                [],
                "title STRING, author STRING, story_id STRING, points INT, created_at_i LONG, created_at TIMESTAMP",
            )

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

            created_at_i = doc.get("created_at_i")
            if created_at_i is not None:
                try:
                    created_at_i = int(created_at_i)
                except Exception:
                    created_at_i = None

            data.append(
                {
                    "title": title,
                    "author": author,
                    "story_id": story_id,
                    "points": points,
                    "created_at_i": created_at_i,
                }
            )

        # DataFrame oluştur
        df = spark.createDataFrame(data)
        df = df.withColumn("created_at", F.to_timestamp(F.from_unixtime(F.col("created_at_i"))))
        spark.sparkContext.setLogLevel("ERROR")
        return df
    except Exception as e:
        print(f"MongoDB bağlantı hatası: {e}")
        print("Boş DataFrame döndürülüyor...")
        return spark.createDataFrame(
            [],
            "title STRING, author STRING, story_id STRING, points INT, created_at_i LONG, created_at TIMESTAMP",
        )

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


def query_articles(df, keyword=None, author=None, sort="date_desc", limit=20):
    """Başlık, yazar ve tarihe göre arama/filtreleme"""
    try:
        limit_val = int(limit or 20)
    except Exception:
        limit_val = 20
    limit = max(1, min(limit_val, 100))

    result_df = df

    if keyword:
        kw = keyword.lower()
        result_df = result_df.filter(F.lower(F.col("title")).contains(kw))

    if author:
        au = author.lower()
        result_df = result_df.filter(F.lower(F.col("author")) == au)

    sort_key = {
        "date_desc": F.col("created_at").desc_nulls_last(),
        "date_asc": F.col("created_at").asc_nulls_last(),
        "points_desc": F.col("points").desc_nulls_last(),
        "points_asc": F.col("points").asc_nulls_last(),
    }.get(sort, F.col("created_at").desc_nulls_last())

    result = (
        result_df
        .select("title", "author", "points", "created_at")
        .orderBy(sort_key)
        .limit(limit)
        .collect()
    )

    articles = []
    for row in result:
        created_at = row["created_at"]
        created_at_iso = created_at.isoformat() if created_at else None
        articles.append(
            {
                "title": row["title"],
                "author": row["author"],
                "points": row["points"],
                "created_at": created_at_iso,
            }
        )

    return articles
