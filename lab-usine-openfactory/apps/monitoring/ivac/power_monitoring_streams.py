import time
from openfactory.kafka import KSQLDBClient


class PowerMonitoringStreams:
    """Sets up ksqlDB streams for power monitoring."""

    SQL_FILES = ("sql/cleanup.sql", "sql/usage_duration.sql", "sql/system_health.sql")

    def __init__(self, ksql_client: KSQLDBClient, logger):
        self.ksql_client = ksql_client
        self.logger = logger

        self.logger.info("Initializing power monitoring streams. Might take some time.")

    def setup(self) -> None:
        try:
            for query in self._load_queries():
                self._execute(query)
            self.logger.info("Power monitoring streams setup successfully.")
        except Exception as e:
            self.logger.error(f"KSQL setup error: {e}")

    def _load_queries(self) -> list[str]:
        queries = []
        for filename in self.SQL_FILES:
            with open(filename, "r") as f:
                queries += [q.strip() for q in f.read().split(";") if q.strip()]
        return queries

    def _execute(self, query: str) -> None:
        try:
            self.ksql_client.statement_query(query + ";")
            time.sleep(0.5)
        except Exception as e:
            self.logger.error(f"Error executing query: {query}\n{e}")
