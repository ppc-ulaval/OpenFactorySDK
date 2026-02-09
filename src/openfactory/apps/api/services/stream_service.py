from exceptions import StreamCreationException

class StreamService:
    """Handles Kafka stream operations"""
    
    def __init__(self, ksqlClient):
        self.ksqlClient = ksqlClient
    
    def create_device_stream(self, device_uuid: str) -> str:
        """Create a Kafka stream for device monitoring"""
        topic_name = f'{device_uuid}_monitoring'
        try:
            query = (
                f"CREATE STREAM IF NOT EXISTS device_stream_{device_uuid} "
                f"WITH (KAFKA_TOPIC='{topic_name}', PARTITIONS=1) AS "
                f"SELECT ASSET_UUID AS KEY, ID, VALUE, "
                f"TIMESTAMPTOSTRING(ROWTIME, 'yyyy-MM-dd''T''HH:mm:ss[.nnnnnnn]', 'Canada/Eastern') AS TIMESTAMP "
                f"FROM ASSETS_STREAM WHERE ASSET_UUID = '{device_uuid}' "
                f"AND TYPE IN ('Events', 'Condition', 'Samples') AND VALUE != 'UNAVAILABLE' "
                f"EMIT CHANGES;"
            )
            self.ksqlClient.statement_query(query)
            return topic_name
        except Exception as e:
            print(f"Failed to create stream for {device_uuid}: {e}")
            raise StreamCreationException(f"Failed to create stream for device {device_uuid}: {e}")
    
    def drop_device_stream(self, device_uuid: str) -> None:
        """Drop a device stream"""
        try:
            query = f"DROP STREAM IF EXISTS device_stream_{device_uuid};"
            self.ksqlClient.statement_query(query)
            print(f"Dropped stream for device {device_uuid}")
        except Exception as e:
            print(f"Failed to drop stream for {device_uuid}: {e}")
            raise StreamCreationException(f"Failed to drop stream for device {device_uuid}: {e}")