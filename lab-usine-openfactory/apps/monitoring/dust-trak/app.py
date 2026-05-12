import os
import time
from openfactory.apps import OpenFactoryApp
from openfactory.kafka import KSQLDBClient
from openfactory.assets import Asset, AssetAttribute


class DustTrakAverage(OpenFactoryApp):
    DUSTTRAK_SYSTEM_UUID: str = os.getenv("DUSTTRAK_SYSTEM_UUID", "DUSTTRAK")

    def __init__(self, ksqlClient, bootstrap_servers, loglevel="INFO"):
        super().__init__(
            ksqlClient=ksqlClient,
            bootstrap_servers=bootstrap_servers,
            loglevel=loglevel,
        )
        self.tool_states = {}
        self.dustttrak = Asset(
            asset_uuid=self.DUSTTRAK_SYSTEM_UUID,
            ksqlClient=ksqlClient,
            bootstrap_servers=bootstrap_servers,
        )
        self.setup_moving_average_stream(ksqlClient)

    def setup_moving_average_stream(self, ksqlClient: KSQLDBClient) -> None:
        try:
            queries = []
            with open("sql/moving_average_cleanup.sql", "r") as sql_file:
                sql_script = sql_file.read()
                queries += sql_script.split(";")

            with open("sql/moving_average.sql", "r") as sql_file:
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
            print("Power monitoring streams setup successfully.")

        except Exception as e:
            print(f"KSQL setup error: {e}")

    def app_event_loop_stopped(self) -> None:
        print("Application event loop stopped.")

    def main_loop(self) -> None:
        while True:
            time.sleep(1)


app = DustTrakAverage(
    ksqlClient=KSQLDBClient(os.getenv("KSQLDB_URL", "http://ksqldb-server:8088")),
    bootstrap_servers=os.getenv("KAFKA_BROKER", "broker:29092"),
)
app.run()
