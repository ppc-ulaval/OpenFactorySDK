from typing import List

class DeviceService:
    """Handles device-related business logic""" 

    def __init__(self, ksql_client):
        self.ksqlClient = ksql_client

    def get_all_devices(self) -> List[str]:
        """Get all devices from the database."""
        devices = []
        try:
            query = "SELECT ASSET_UUID FROM assets_type WHERE TYPE LIKE 'Device';"
            result = self.ksqlClient.query(query)
            for row in result:
                asset_uuid = row.get('ASSET_UUID')
                if asset_uuid:
                    devices.append(asset_uuid)
            return devices
        except Exception as e:
            print(f"Error getting devices: {e}")
            return devices

    def get_device_dataitems(self, device_uuid: str) -> dict:
        try:
            query = (
                f"SELECT ID, VALUE FROM assets WHERE ASSET_UUID = '{device_uuid}' "
                f"AND TYPE IN ('Events', 'Condition') AND VALUE != 'UNAVAILABLE';"
            )
            result = self.ksqlClient.query(query)
            return {row['ID']: row['VALUE'] for row in result if 'ID' in row and 'VALUE' in row}
        except Exception as e:
            print(f"Error getting device dataitems for {device_uuid}: {e}")
            return {}

    def get_device_stats(self, dataitem_id) -> dict:
        try:
            query = (
                f"SELECT IVAC_POWER_KEY, TOTAL_DURATION_SEC FROM IVAC_POWER_STATE_TOTALS "
                f"WHERE IVAC_POWER_KEY LIKE '{dataitem_id}%';"
            )
            df = self.ksqlClient.query(query)
            return dict(zip(df.IVAC_POWER_KEY.str[11:].tolist(), df.TOTAL_DURATION_SEC.tolist())) if 'IVAC_POWER_KEY' in df.columns and 'TOTAL_DURATION_SEC' in df.columns else {}
        except Exception as  e:
            print(f"Error getting dataitems stats:{e}")
            return {}
        
    def add_duration_updates(self, msg_value: dict):
        """Add duration data for IVAC device"""
        try:
            query = (
                f"SELECT IVAC_POWER_KEY, TOTAL_DURATION_SEC FROM IVAC_POWER_STATE_TOTALS "
                f"WHERE IVAC_POWER_KEY LIKE '{msg_value['ID']}%';"
            )
            df = self.ksqlClient.query(query)
            msg_value['durations'] = dict(zip(df.IVAC_POWER_KEY.str[11:].tolist(), df.TOTAL_DURATION_SEC.tolist())) if 'IVAC_POWER_KEY' in df.columns and 'TOTAL_DURATION_SEC' in df.columns else {}
        except Exception as e:
            print(f"Error adding duration updates for {msg_value['ID']}: {e}")

    def add_avg_data(self, msg_value: dict):
        """Add average data for DUSTTRAK device"""
        try:
            query = (
                f"SELECT AVERAGE_VALUE, TIMESTAMP FROM {msg_value['ID']}_moving_average "
                f"WHERE timestamp LIKE '{msg_value['TIMESTAMP'][:-10]}%';"
            )
            df = self.ksqlClient.query(query)
            if 'AVERAGE_VALUE' in df.columns and 'TIMESTAMP' in df.columns and not df['AVERAGE_VALUE'].empty and not df['TIMESTAMP'].empty:
                msg_value['avg_value'] = {
                    'value': df['AVERAGE_VALUE'].tolist()[0],
                    'timestamp': df['TIMESTAMP'].tolist()[0]
                }
            else:
                msg_value['avg_value'] = {}
        except Exception as e:
            print(f"Error adding avg values for {msg_value['ID']}: {e}")