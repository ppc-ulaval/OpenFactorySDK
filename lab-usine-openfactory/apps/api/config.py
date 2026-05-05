from dataclasses import dataclass

@dataclass
class Config:
    ksqldb_url: str = "http://ksqldb-server:8088"
    kafka_brokers: str = "broker:29092"
    websocket_host: str = "0.0.0.0"
    websocket_port: int = 8000
    ping_interval: int = 30
    ping_timeout: int = 10
    message_timeout: int = 30
    log_level: str = "INFO"