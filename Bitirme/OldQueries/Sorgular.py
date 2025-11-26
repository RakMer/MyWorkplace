from pyspark.sql import SparkSession
from pyspark.sql import functions as F
import time

spark = (
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

spark.sparkContext.setLogLevel("ERROR")

start_time = time.time()

df = (
    spark.read.format("mongodb")
    .option("database", "HackerNewsDB")
    .option("collection", "HackerNews")
    .load()
    .select("title", "author", "story_id", "points")  # Projection pushdown
)

df.printSchema()

# Sorgu 1: AI başlıklı haberleri bul
print("--- AI ile ilgili başlıklar ---")
q1_start = time.time()
df.filter(F.lower(F.col("title")).contains("ai")).select("title", "author").limit(50).show()
print(f"Süre: {time.time() - q1_start:.3f}s\n")

# Sorgu 2: En çok yoruma sahip story_id'ler (group by optimize)
print("--- En çok yoruma sahip hikayeler ---")
q2_start = time.time()
df.groupBy("story_id").count().orderBy(F.desc("count")).limit(10).show()
print(f"Süre: {time.time() - q2_start:.3f}s\n")

# Sorgu 3 & 4: İstatistikler
print("--- İstatistikler ---")
q3_start = time.time()
stats = df.agg(
    F.count("*").alias("Toplam"),
    F.count("author").alias("Yazarı olan")
).collect()[0]
print(f"Toplam: {stats['Toplam']}")
print(f"Yazarı olan: {stats['Yazarı olan']}")
print(f"Süre: {time.time() - q3_start:.3f}s\n")

# Sorgu 5: En çok haber yazan yazarlar
print("--- En çok haber yazan yazarlar ---")
q5_start = time.time()
df.filter(F.col("author").isNotNull()).groupBy("author").count().orderBy(F.desc("count")).limit(10).show()
print(f"Süre: {time.time() - q5_start:.3f}s\n")

# Sorgu 6: En yüksek puan alan haberler
print("--- En yüksek puan alan haberler ---")
q6_start = time.time()
df.filter(F.col("points").isNotNull()).select("title", "points").orderBy(F.desc("points")).limit(10).show()
print(f"Süre: {time.time() - q6_start:.3f}s\n")

print(f"\nToplam çalışma süresi: {time.time() - start_time:.2f} saniye")

# İnteraktif sorgu modu
print("--- İnteraktif Sorgu Modu ---")
print("Spark DataFrame üzerinde sorgu çalıştır. 'exit' yazarak çık.")
df.createOrReplaceTempView("news_table")

while True:
    inp = input("Sorgu: ").strip()
    if inp.lower() == "exit":
        break
    if inp:
        try:
            spark.sql(inp).show()
        except Exception as e:
            print(f"Hata: {e}")

print(f"\nToplam çalışma süresi: {time.time() - start_time:.2f} saniye")