from abc import ABC, abstractmethod
from openfactory.kafka import KSQLDBClient


class DeviceStrategy(ABC):
    @abstractmethod
    def get_stats(self, ksql_client: KSQLDBClient, device_uuid: str) -> dict:
        pass

    @abstractmethod
    def process_update(self, ksql_client: KSQLDBClient, msg_value: dict):
        pass


class IvacStrategy(DeviceStrategy):
    def get_stats(self, ksql_client: KSQLDBClient, device_uuid: str) -> dict:
        try:
            result = ksql_client.query(
                f"SELECT IVAC_POWER_KEY, TOTAL_DURATION_SEC "
                f"FROM IVAC_POWER_STATE_TOTALS "
                f"WHERE IVAC_POWER_KEY LIKE '{device_uuid}%';"
            )
            return {
                _strip_prefix(row["IVAC_POWER_KEY"], device_uuid): row[
                    "TOTAL_DURATION_SEC"
                ]
                for row in result
                if "IVAC_POWER_KEY" in row and "TOTAL_DURATION_SEC" in row
            }
        except Exception as e:
            print(f"Error getting IVAC stats for {device_uuid}: {e}")
            return {}

    def process_update(self, ksql_client: KSQLDBClient, msg_value: dict):
        dataitem_id = msg_value.get("ID")
        if not dataitem_id:
            return
        try:
            result = ksql_client.query(
                f"SELECT IVAC_POWER_KEY, TOTAL_DURATION_SEC "
                f"FROM IVAC_POWER_STATE_TOTALS "
                f"WHERE IVAC_POWER_KEY LIKE '{dataitem_id}%';"
            )
            msg_value["durations"] = {
                _strip_prefix(row["IVAC_POWER_KEY"], dataitem_id): row[
                    "TOTAL_DURATION_SEC"
                ]
                for row in result
                if "IVAC_POWER_KEY" in row and "TOTAL_DURATION_SEC" in row
            }
        except Exception as e:
            print(f"Error adding duration updates for {dataitem_id}: {e}")
            msg_value["durations"] = {}


class DusttrakStrategy(DeviceStrategy):
    def get_stats(self, ksql_client: KSQLDBClient, device_uuid: str) -> dict:
        return {}

    def process_update(self, ksql_client: KSQLDBClient, msg_value: dict):
        dataitem_id = msg_value.get("ID")
        timestamp = msg_value.get("TIMESTAMP")
        if not dataitem_id or not timestamp:
            return
        try:
            result = ksql_client.query(
                f"SELECT AVERAGE_VALUE, TIMESTAMP "
                f"FROM {dataitem_id}_moving_average "
                f"WHERE timestamp LIKE '{timestamp[:-10]}%';"
            )
            first_row = next(
                (r for r in result if "AVERAGE_VALUE" in r and "TIMESTAMP" in r),
                None,
            )
            msg_value["avg_value"] = (
                {
                    "value": first_row["AVERAGE_VALUE"],
                    "timestamp": first_row["TIMESTAMP"],
                }
                if first_row
                else {}
            )
        except Exception as e:
            print(f"Error adding avg values for {dataitem_id}: {e}")
            msg_value["avg_value"] = {}


class DefaultStrategy(DeviceStrategy):
    def get_stats(self, ksql_client: KSQLDBClient, device_uuid: str) -> dict:
        return {}

    def process_update(self, ksql_client: KSQLDBClient, msg_value: dict):
        pass


def _strip_prefix(key: str, prefix: str) -> str:
    return key[len(prefix) + 1 :] if key.startswith(prefix + "_") else key


class DeviceService:
    _strategies: dict[str, DeviceStrategy] = {
        "IVAC": IvacStrategy(),
        "DUSTTRAK": DusttrakStrategy(),
    }
    _default_strategy = DefaultStrategy()

    def __init__(self, ksql_client: KSQLDBClient):
        self._ksql_client = ksql_client

    def _get_strategy(self, device_uuid: str) -> DeviceStrategy:
        for prefix, strategy in self._strategies.items():
            if device_uuid.startswith(prefix):
                return strategy
        return self._default_strategy

    def get_all_devices(self) -> list[str]:
        try:
            result = self._ksql_client.query(
                "SELECT ASSET_UUID FROM assets_type WHERE TYPE LIKE 'Device';"
            )
            return [row["ASSET_UUID"] for row in result if row.get("ASSET_UUID")]
        except Exception as e:
            print(f"Error getting devices: {e}")
            return []

    def get_device_dataitems(self, device_uuid: str) -> dict:
        try:
            result = self._ksql_client.query(
                f"SELECT ID, VALUE FROM assets "
                f"WHERE ASSET_UUID = '{device_uuid}' "
                f"AND TYPE IN ('Events', 'Condition') "
                f"AND VALUE != 'UNAVAILABLE';"
            )
            return {
                row["ID"]: row["VALUE"]
                for row in result
                if "ID" in row and "VALUE" in row
            }
        except Exception as e:
            print(f"Error getting dataitems for {device_uuid}: {e}")
            return {}

    def get_device_stats(self, device_uuid: str) -> dict:
        return self._get_strategy(device_uuid).get_stats(self._ksql_client, device_uuid)

    def process_update(self, device_uuid: str, msg_value: dict):
        self._get_strategy(device_uuid).process_update(self._ksql_client, msg_value)
