from pyspark.sql import SparkSession
from pyspark.sql import functions as F
import time

spark = (
    SparkSession.builder
    .appName("MongoSparkTest")
    .config("spark.jars.packages", "org.mongodb.spark:mongo-spark-connector_2.13:10.3.0")
    .config("spark.mongodb.read.connection.uri", "mongodb://localhost:27017/HackerNewsDB")
    .config("spark.sql.adaptive.enabled", "true")  # Adaptive Query Execution
    .config("spark.sql.adaptive.coalescePartitions.enabled", "true")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("ERROR")

df = (
    spark.read.format("mongodb")
    .option("database", "HackerNewsDB")
    .option("collection", "HackerNews")
    .load()
)

start_time = time.time()

df.printSchema()


df.createOrReplaceTempView("news_table")
spark.sql("Select title, author from news_table where title like '%AI%'").show()
print(time.time() - start_time)
spark.sql("select  story_id, count(*) as IDs from news_table group by story_id order by IDs desc limit 10 ").show()
print(time.time() - start_time)
spark.sql("SELECT COUNT(*) FROM news_table").show()
print(time.time() - start_time)
spark.sql("SELECT COUNT(author) FROM news_table ").show()
print(time.time() - start_time)
spark.sql("SELECT author, COUNT(*) as news_count FROM news_table GROUP BY author ORDER BY news_count DESC LIMIT 10").show()
print(time.time() - start_time)
spark.sql("select title, points from news_table order by points desc limit 10").show()

print(f"Toplam çalişma süresi: {time.time() - start_time} saniye")

while True:
    inp = input("Sorgu: ").strip()
    if inp.lower() == "exit":
        break
    if inp:
        try:
            spark.sql(inp).show()
        except Exception as e:
            print(f"Hata: {e}")


print(f"Toplam çalişma süresi: {time.time() - start_time} saniye")