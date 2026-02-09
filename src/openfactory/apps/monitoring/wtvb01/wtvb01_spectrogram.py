import os
import time
from openfactory.apps import OpenFactoryApp
from openfactory.kafka import KSQLDBClient
from kafka_processor import KafkaProcessor



class WTVB01Monitoring(OpenFactoryApp):

    WTVB01_SYSTEM_UUID: str = os.getenv('WTVB01_SYSTEM_UUID',  'WTVB01')

    def __init__(self, app_uuid, ksqlClient, bootstrap_servers, loglevel='INFO'):
        """
        Initializes the WTVB01Monitoring application.
        Sets up the application with the provided UUID, KSQLDB client, and Kafka bootstrap servers.
        Args:
            app_uuid (str): Unique identifier for the application.
            ksqlClient: KSQLDB client instance for interacting with KSQLDB.
            bootstrap_servers (str): Comma-separated list of Kafka bootstrap servers.
            loglevel (str): Logging level for the application. Defaults to 'INFO'.
        """
        super().__init__(app_uuid, ksqlClient, bootstrap_servers, loglevel)
        self.kafka_processor_frequencyX = KafkaProcessor(ksqlClient, bootstrap_servers, input_topic='time_series_dx', output_topic='spectrogram_stream_dx', plot_dir='spectrogram_plotx')
        self.tool_states = {}
        object.__setattr__(self, 'ASSET_ID',  'WTVB01')
        self.setup_streams(ksqlClient)

    def setup_streams(self, ksqlClient: KSQLDBClient) -> None:
        """
        Setup KSQL streams and tables to convert frequencies to spectrogram data.
        """
        try:
            queries = []
            with open('spectrogram_cleanup.sql', "r") as sql_file:
                sql_script = sql_file.read()
                queries += sql_script.split(';')

            with open('spectrogram.sql', "r") as sql_file:
                sql_script = sql_file.read()
                queries += sql_script.split(';')

            for query in queries:
                query = query.strip()
                if not query:
                    continue
                try:
                    ksqlClient.statement_query(query + ';')
                except Exception as e:
                    print(f"Error in query execution:{query}, {e}")
            print('Streams setup successfully.')

        except Exception as e:
            print(f"KSQL setup error: {e}")

    def app_event_loop_stopped(self) -> None:
        """
        Called automatically when the main application event loop is stopped.
        """
        print("Stopping iVAC consumer thread ...")


    def main_loop(self) -> None:
        """ Main loop of the App. """
        while True:
            self.kafka_processor_frequencyX.run_streaming_processing()
            time.sleep(1)


app = WTVB01Monitoring(
    app_uuid='WTVB01-SPECTROGRAM',
    ksqlClient=KSQLDBClient("http://ksqldb-server:8088"),
    bootstrap_servers="broker:29092"
)
app.run()
