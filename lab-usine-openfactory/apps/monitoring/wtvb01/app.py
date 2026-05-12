import os
import time
from openfactory.apps import OpenFactoryApp
from openfactory.assets import Asset
from openfactory.kafka import KSQLDBClient
from kafka_processor import KafkaProcessor


class WTVB01Monitoring(OpenFactoryApp):
    WTVB01_SYSTEM_UUID: str = os.getenv("WTVB01_SYSTEM_UUID", "WTVB01")

    def __init__(self, ksqlClient, bootstrap_servers, loglevel="INFO"):
        super().__init__(
            ksqlClient=ksqlClient,
            bootstrap_servers=bootstrap_servers,
            loglevel=loglevel,
        )

        self.kafka_processor_frequencyX = KafkaProcessor(
            ksqlClient,
            bootstrap_servers,
            input_topic="time_series_dx",
            output_topic="spectrogram_stream_dx",
            plot_dir="spectrogram_plotx",
        )

        self.setup_streams(ksqlClient)

    def setup_streams(self, ksqlClient: KSQLDBClient) -> None:
        try:
            queries = []
            with open("sql/spectrogram_cleanup.sql", "r") as sql_file:
                sql_script = sql_file.read()
                queries += sql_script.split(";")

            with open("sql/spectrogram.sql", "r") as sql_file:
                sql_script = sql_file.read()
                queries += sql_script.split(";")

            for query in queries:
                query = query.strip()
                if not query:
                    continue
                try:
                    ksqlClient.statement_query(query + ";")
                except Exception as e:
                    print(f"Error in query execution:{query}, {e}")
            print("Streams setup successfully.")

        except Exception as e:
            print(f"KSQL setup error: {e}")

    def app_event_loop_stopped(self) -> None:
        print("Stopping iVAC consumer thread ...")

    def main_loop(self) -> None:
        """Main loop of the App."""
        while True:
            self.kafka_processor_frequencyX.run_streaming_processing()
            time.sleep(1)


app = WTVB01Monitoring(
    ksqlClient=KSQLDBClient(os.getenv("KSQLDB_URL", "http://ksqldb-server:8088")),
    bootstrap_servers=os.getenv("KAFKA_BROKER", "broker:29092"),
)
app.run()
