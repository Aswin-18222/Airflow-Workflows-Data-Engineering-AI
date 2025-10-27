import requests
import json
import logging
from kafka import KafkaProducer
from kafka.errors import KafkaError

class SafeJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, bytes):
            return obj.decode('utf-8', errors='ignore')
        return super().default(obj)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler()]
)
# Enable debug-level logging
logging.getLogger().setLevel(logging.DEBUG)

# Constants
API_KEY = "65df78c64a554c33ae2352390410cda9"
API_URL = "https://api.worldnewsapi.com/search-news"
KAFKA_TOPIC = "world_news"
KAFKA_BOOTSTRAP_SERVERS = ["kafka:9092"]


def fetch_news_articles(query="technology", language="en", page_size=10):
    """Fetch news articles from World News API."""
    params = {
        "api-key": API_KEY,
        "text": query,
        "language": language,
        "number": page_size
    }
    try:
        logging.info("Fetching news articles from World News API...")
        response = requests.get(API_URL, params=params)
        response.raise_for_status()
        data = response.json()
        articles = data.get("news", [])
        logging.info(f"Fetched {len(articles)} articles.")
        return articles
    except requests.RequestException as e:
        logging.error(f"Error fetching news articles: {e}")
        return []
    
def clean_bytes(obj):
    """Recursively convert bytes to strings in any Python object."""
    if isinstance(obj, dict):
        return {clean_bytes(k): clean_bytes(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [clean_bytes(v) for v in obj]
    elif isinstance(obj, tuple):
        return tuple(clean_bytes(v) for v in obj)
    elif isinstance(obj, set):
        return {clean_bytes(v) for v in obj}
    elif isinstance(obj, bytes):
        return obj.decode('utf-8', errors='ignore')
    else:
        return obj
    
def send_to_kafka(producer, topic, articles):
    """Send articles to Kafka topic."""
    for article in articles:
        try:
            clean_article = clean_bytes(article)
            message = json.dumps(clean_article).encode('utf-8')
            producer.send(topic, value=message)
            logging.info(f"Sent article to Kafka: {clean_article.get('title')}")
        except KafkaError as e:
            logging.error(f"Error sending to Kafka: {e}")
        except TypeError as e:
            logging.error(f"Serialization error: {e}")
            logging.debug(f"Problematic article: {article}")
            
def main():
    # Initialize Kafka producer
    try:
        producer = KafkaProducer(
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v, cls=SafeJSONEncoder).encode('utf-8')
        )
        logging.info("Kafka producer initialized.")
    except KafkaError as e:
        logging.error(f"Failed to initialize Kafka producer: {e}")
        return

    # Fetch articles and send to Kafka
    articles = fetch_news_articles()
    if articles:
        send_to_kafka(producer, KAFKA_TOPIC, articles)
    else:
        logging.warning("No articles to send.")

    # Flush and close producer
    producer.flush()
    producer.close()
    logging.info("Kafka producer closed.")

if __name__ == "__main__":
    main()
