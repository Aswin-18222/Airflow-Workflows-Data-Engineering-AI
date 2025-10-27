import json
import logging
from kafka import KafkaConsumer
from kafka.errors import KafkaError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("/app/data-store/consumer.log", mode='w', encoding='utf-8')
    ]
)

# Constants
KAFKA_TOPIC = "world_news"
KAFKA_BOOTSTRAP_SERVERS = ["kafka:9092"]
OUTPUT_FILE = "/app/data-store/news_articles.json"

def consume_messages():
    try:
        consumer = KafkaConsumer(
            KAFKA_TOPIC,
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            group_id='news-consumer-group',
            value_deserializer=lambda m: json.loads(json.loads(m.decode('utf-8')))
        )
        logging.info("Kafka consumer initialized.")
    except KafkaError as e:
        logging.error(f"Failed to initialize Kafka consumer: {e}")
        return
    articles = []

    try:
        logging.info("Consuming messages from Kafka...")
        for message in consumer:
            article = message.value
            articles.append(article)
            logging.info(f"Consumed article: {article.get('title')}")
            
            # Optional: break after consuming a fixed number for testing
            if len(articles) >= 12:
                break
    except Exception as e:
        logging.error(f"Error while consuming messages: {e}")
    finally:
        consumer.close()
        logging.info("Kafka consumer closed.")

    # Save to local JSON file
    try:
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(articles, f, indent=2, ensure_ascii=False)
        logging.info(f"Saved {len(articles)} articles to {OUTPUT_FILE}")
        print(f"Saving {len(articles)} articles to {OUTPUT_FILE}")

    except IOError as e:
        logging.error(f"Error writing to file: {e}")

if __name__ == "__main__":
    consume_messages()
