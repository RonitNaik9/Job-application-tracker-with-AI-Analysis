from kafka import KafkaProducer
import json
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class KafkaProducerService:
    def __init__(self):
        self.producer = None
        self._connect()
    
    def _connect(self):
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                api_version=(0, 10, 1)
            )
            logger.info("Kafka producer connected successfully")
        except Exception as e:
            logger.error(f"Failed to connect to Kafka: {e}")
            self.producer = None
    
    def publish_event(self, topic: str, event_data: dict):
        """Publish an event to Kafka topic"""
        if not self.producer:
            logger.error("Kafka producer not connected")
            return False
        
        try:
            future = self.producer.send(topic, value=event_data)
            future.get(timeout=10)  # Wait for confirmation
            logger.info(f"Event published to {topic}: {event_data}")
            return True
        except Exception as e:
            logger.error(f"Failed to publish event to {topic}: {e}")
            return False
    
    def close(self):
        if self.producer:
            self.producer.close()

# Singleton instance
kafka_producer = KafkaProducerService()