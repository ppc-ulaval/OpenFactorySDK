import threading
import json
from typing import Callable, Optional, Dict, Any
from kafka import KafkaConsumer


class TopicSubscriber:
    
    
    def __init__(self):
        self._active_consumers: Dict[str, KafkaConsumer] = {}
        self._consumer_threads: Dict[str, threading.Thread] = {}
        self._stop_flags: Dict[str, threading.Event] = {}

    def subscribe_to_kafka_topic(self, 
                            topic: str, 
                            kafka_group_id: str,
                            on_message: Callable[[Dict[str, Any]], None],
                            bootstrap_servers: str = "broker:29092",
                            message_filter: Optional[Callable[[Dict[str, Any]], bool]] = None) -> None:
        """
        Subscribe to a Kafka topic with a callback function
        
        Args:
            topic: Kafka topic name
            kafka_group_id: Consumer group ID
            on_message: Callback function for processing messages
            bootstrap_servers: Kafka bootstrap servers
            message_filter: Optional filter function
        """
        if topic in self._active_consumers:
            print(f"Already subscribed to topic: {topic}")
            return
        
        self._stop_flags[topic] = threading.Event()
        
        consumer_thread = threading.Thread(
            target=self._consume_kafka_topic,
            args=(topic, kafka_group_id, on_message, bootstrap_servers, message_filter),
            daemon=True
        )
        consumer_thread.start()
        self._consumer_threads[topic] = consumer_thread

    def _consume_kafka_topic(self, 
                        topic: str, 
                        kafka_group_id: str,
                        on_message: Callable[[str, Dict[str, Any]], None],
                        bootstrap_servers: str,
                        message_filter: Optional[Callable[[Dict[str, Any]], bool]] = None) -> None:
        """Internal function to consume messages from a topic"""
        try:
            consumer = KafkaConsumer(
                topic,
                bootstrap_servers=bootstrap_servers,
                group_id=kafka_group_id,
                value_deserializer=lambda m: json.loads(m.decode('utf-8')) if m else None,
                key_deserializer=lambda m: m.decode('utf-8') if m else None,
                auto_offset_reset='latest',
                enable_auto_commit=True
            )
            
            self._active_consumers[topic] = consumer

            for message in consumer:
                if self._stop_flags[topic].is_set():
                    break
                if message.value is not None:
                    if message_filter and not message_filter(message.key):
                        continue
                    
                    on_message(message.key, message.value)
                    
        except Exception as e:
            print(f"Error in topic consumer for {topic}: {e}")
        finally:
            if topic in self._active_consumers:
                self._active_consumers[topic].close()
                del self._active_consumers[topic]

    def stop_kafka_topic_subscription(self, topic: str) -> None:
        """Stop subscription to a specific topic"""
        if topic in self._stop_flags:
            self._stop_flags[topic].set()
            
        if topic in self._consumer_threads:
            self._consumer_threads[topic].join(timeout=5)
            del self._consumer_threads[topic]
            
        if topic in self._stop_flags:
            del self._stop_flags[topic]

    def stop_all_kafka_subscriptions(self) -> None:
        """Stop all topic subscriptions"""
        topics_to_stop = list(self._stop_flags.keys())
        for topic in topics_to_stop:
            self.stop_kafka_topic_subscription(topic)

    def get_active_kafka_subscriptions(self) -> list:
        """Get list of currently active subscriptions"""
        return list(self._active_consumers.keys())