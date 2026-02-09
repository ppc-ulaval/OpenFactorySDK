import os
import time
from openfactory.apps import OpenFactoryApp
from openfactory.kafka import KSQLDBClient


class DustTrakAverage(OpenFactoryApp):
    """
    DustTrakAverage application for monitoring the average dust concentration
    in an IVAC system. Inherits from `OpenFactoryApp` and extends it to represent a specific application
    that monitors the average dust concentration, updating the average based on events.
    Class Attributes:
        DUSTTRAK_SYSTEM_UUID (str): Unique identifier for the IVAC system, defaults to 'DUSTTRAK'.
    Instance Attributes:
        dust_trak_average (float): Variable to hold the average dust concentration.
        ivac (Asset): Asset instance representing the IVAC system.
    """

    DUSTTRAK_SYSTEM_UUID: str = os.getenv('DUSTTRAK_SYSTEM_UUID', 'DUSTTRAK')

    def __init__(self, app_uuid, ksqlClient, bootstrap_servers, loglevel='INFO'):
        """
        Initializes the ToolMonitoring application.
        Sets up the application with the provided UUID, KSQLDB client, and Kafka bootstrap servers.
        Args:
            app_uuid (str): Unique identifier for the application.
            ksqlClient: KSQLDB client instance for interacting with KSQLDB.
            bootstrap_servers (str): Comma-separated list of Kafka bootstrap servers.
            loglevel (str): Logging level for the application. Defaults to 'INFO'.
        """
        super().__init__(app_uuid, ksqlClient, bootstrap_servers, loglevel)
        self.tool_states = {}
        object.__setattr__(self, 'ASSET_ID', 'DUSTTRAK')
        self.setup_moving_average_stream(ksqlClient)

    def setup_moving_average_stream(self, ksqlClient: KSQLDBClient) -> None:
        """
        Setup KSQL streams for monitoring power events and durations.
        Creates the necessary streams and tables for power state monitoring.
        """
        try:
            queries = []
            with open('moving_average_cleanup.sql', "r") as sql_file:
                sql_script = sql_file.read()
                queries += sql_script.split(';')

            with open('moving_average.sql', "r") as sql_file:
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
            print('Power monitoring streams setup successfully.')

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
            time.sleep(1)


app = DustTrakAverage(
    app_uuid='MOVING-AVERAGE-DUSTTRAK',
    ksqlClient=KSQLDBClient("http://ksqldb-server:8088"),
    bootstrap_servers="broker:29092"
)
app.run()
