import json
import traceback
from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import KafkaError
from signal_processor import SignalProcessor


class KafkaProcessor:
    """
    KafkaProcessor class for handling Kafka messages and processing them.
    This class provides methods to produce and consume messages from Kafka topics.
    """

    def __init__(self, ksqlClient, bootstrap_servers, input_topic, output_topic, 
                plot_dir="spectrogram_plots"):
        """
        Initializes the KafkaProducer and KafkaConsumer.
        Args:
            bootstrap_servers (str): Comma-separated list of Kafka bootstrap servers.
            input_topic (str): The topic to consume time series data from.
            output_topic (str): The topic to produce spectrogram data to.
            log_file (str): Path to the log file for spectrogram data.
            plot_dir (str): Directory to save spectrogram plot images.
        """
        self.ksqlClient = ksqlClient
        self.bootstrap_servers = bootstrap_servers
        self.input_topic = input_topic
        self.output_topic = output_topic
        
        self._setup_kafka()
        self.signal_processor = SignalProcessor(plot_dir)
    

    def safe_deserialize_value(self, x):
        """Safe value deserializer with multiple fallback strategies"""
        if x is None:
            return None
        
        try:
            return json.loads(x.decode('utf-8'))
        except UnicodeDecodeError:
            try:
                decoded = x.decode('utf-8', errors='replace')
                return json.loads(decoded)
            except json.JSONDecodeError:
                try:
                    return json.loads(x.decode('latin-1'))
                except:
                    return x.decode('utf-8', errors='ignore')
        except json.JSONDecodeError:
            try:
                return x.decode('utf-8', errors='replace')
            except:
                return str(x)
    
    def safe_deserialize_key(self, x):
        """Safe key deserializer"""
        if x is None:
            return None
        try:
            decoded = x.decode('utf-8', errors='replace')
            clean_key = decoded.split('\x00')[0] if '\x00' in decoded else decoded
            return ''.join(c for c in clean_key if c.isprintable()) if clean_key else 'unknown'
        except:
            return 'unknown'
    
    def _setup_kafka(self):
        """
        Sets up the Kafka producer and consumer.
        """
        self.consumer = KafkaConsumer(
            self.input_topic,
            bootstrap_servers=self.bootstrap_servers,
            group_id="stft_processor_group",
            value_deserializer=self.safe_deserialize_value,
            key_deserializer=self.safe_deserialize_key,
            auto_offset_reset='latest',
            enable_auto_commit=True,
            auto_commit_interval_ms=1000
        )
        
        self.producer = KafkaProducer(
            bootstrap_servers=self.bootstrap_servers,
            value_serializer=lambda x: json.dumps(x, default=str).encode('utf-8'),
            key_serializer=lambda x: x.encode('utf-8') if x else None,
            acks='all',
            retries=3
        )

    def send_spectrogram_data(self, spectrogram_data):
        """
        Send spectrogram data to output Kafka topic
        """
        try:
            message = {
                'key': 'WTVB01',
                'spectrogram_data': spectrogram_data['spectrogram']
            }
            
            self.producer.send(
                self.output_topic,
                key='WTVB01',
                value=message
            )
            self.producer.send(
                self.output_topic,
                key='WTVB01',
                value=spectrogram_data
            )
            self.producer.flush()
        except KafkaError as e:
            print(f"Error sending spectrogram data: {e}")

    def process_message(self, key, value):
        """
        Process incoming time series message
        """
        try:
            if 'VALUE_LIST' not in value or 'TIMESTAMPS' not in value:
                print(f"Invalid message format: {value}")
                return
            
            result = self.signal_processor.compute_spectrogram(value['VALUE_LIST'], value['TIMESTAMPS'])

            if result:
                self.send_spectrogram_data(result)
            
        except Exception as e:
            print(traceback.format_exception(e))

    
    def run_streaming_processing(self):
        """Main processing loop with real-time processing"""
        print(f"Starting STFT processor - Input: {self.input_topic}, Output: {self.output_topic}")
        
        try:
            for message in self.consumer:
                self.process_message(message.key, message.value)
                
        except KeyboardInterrupt:
            print("STFT Processor stopped by user")
        except Exception as e:
            print(f"Error in processing loop: {e}")
        finally:
            self.consumer.close()
            self.producer.close()
            print("STFT Processor closed")