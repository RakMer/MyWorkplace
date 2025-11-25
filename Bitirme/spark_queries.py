"""Spark sorguları için helper modül"""
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
import time

def get_spark_session():
    """Spark session'ı başlat veya mevcut olanı döndür"""
    return (
        SparkSession.builder
        .appName("MongoSparkTest")
        .config("spark.jars.packages", "org.mongodb.spark:mongo-spark-connector_2.13:10.3.0")
        .config("spark.mongodb.read.connection.uri", "mongodb://localhost:27017/HackerNewsDB")
        .config("spark.driver.memory", "4g")
        .config("spark.executor.memory", "2g")
        .config("spark.sql.adaptive.enabled", "true")
        .config("spark.sql.shuffle.partitions", "8")
        .getOrCreate()
    )

def get_dataframe(spark):
    """MongoDB'den veri çek ve DataFrame oluştur"""
    df = (
        spark.read.format("mongodb")
        .option("database", "HackerNewsDB")
        .option("collection", "HackerNews")
        .load()
        .select("title", "author", "story_id", "points")
    )
    spark.sparkContext.setLogLevel("ERROR")
    return df

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
