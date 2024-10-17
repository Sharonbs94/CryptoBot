import os
import json
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, FloatType
from utils.functions import send_to_telegram_cryptocurrency, send_to_telegram_graph, send_to_telegram_news

if __name__ == "__main__":
    kafka_broker = os.getenv('KAFKA_BROKERCONNECT', 'kafka:9092')
    telegram_token = os.getenv('TELEGRAM_TOKEN')
    if not telegram_token:
        print("TELEGRAM_TOKEN environment variable not set.")
        exit(1)

    spark = SparkSession.builder \
        .appName("KafkaSparkConsumer") \
        .config("spark.jars", "/opt/spark/jars/spark-sql-kafka-0-10_2.12-3.5.2.jar,/opt/spark/jars/kafka-clients-3.5.1.jar") \
        .getOrCreate()

    schema = StructType([
        StructField("coin", StringType(), True),
        StructField("currency", StringType(), True),
        StructField("chat_id", IntegerType(), True),
        StructField("price", FloatType(), True),
        StructField("command", StringType(), True),
        StructField("data", StringType(), True),
        StructField("days", IntegerType(), True)
    ])

    df = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", kafka_broker) \
        .option("subscribe", "user_requests") \
        .load()

    df = df.selectExpr("CAST(value AS STRING)") \
        .select(from_json(col("value"), schema).alias("data")) \
        .select("data.*")

    def process_row(row):
        coin = row.coin
        currency = row.currency
        chat_id = row.chat_id
        price = row.price
        command = row.command
        data = row.data
        days = row.days

        try:
            if command == 'cryptocurrency':
                send_to_telegram_cryptocurrency(coin, currency, price, chat_id)
            elif command == 'graph':
                if isinstance(data, str):
                    data = json.loads(data)
                send_to_telegram_graph(data, chat_id, coin, currency, days)
            elif command == 'news':
                if isinstance(data, str):
                    data = json.loads(data)
                send_to_telegram_news(data, chat_id, coin)
        except Exception as e:
            print(f"Error sending message to Telegram: {e}")

    query = df.writeStream \
        .foreach(process_row) \
        .start()

    query.awaitTermination()
