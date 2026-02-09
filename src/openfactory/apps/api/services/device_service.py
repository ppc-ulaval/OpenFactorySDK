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
            result = self.ksqlClient.query(query)
            
            stats = {}
            for row in result:
                if 'IVAC_POWER_KEY' in row and 'TOTAL_DURATION_SEC' in row:
                    key = row['IVAC_POWER_KEY']
                    state = key[len(dataitem_id)+1:] if key.startswith(dataitem_id + '_') else key
                    stats[state] = row['TOTAL_DURATION_SEC']
            return stats
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
            result = self.ksqlClient.query(query)
            durations = {}
            for row in result:
                if 'IVAC_POWER_KEY' in row and 'TOTAL_DURATION_SEC' in row:
                    key = row['IVAC_POWER_KEY']
                    state = key[len(msg_value['ID'])+1:] if key.startswith(msg_value['ID'] + '_') else key
                    durations[state] = row['TOTAL_DURATION_SEC']
            msg_value['durations'] = durations
        except Exception as e:
            print(f"Error adding duration updates for {msg_value['ID']}: {e}")

    def add_avg_data(self, msg_value: dict):
        """Add average data for DUSTTRAK device"""
        try:
            query = (
                f"SELECT AVERAGE_VALUE, TIMESTAMP FROM {msg_value['ID']}_moving_average "
                f"WHERE timestamp LIKE '{msg_value['TIMESTAMP'][:-10]}%';"
            )
            result = self.ksqlClient.query(query)
            if result and len(result) > 0:
                first_row = result[0]
                if 'AVERAGE_VALUE' in first_row and 'TIMESTAMP' in first_row:
                    msg_value['avg_value'] = {
                        'value': first_row['AVERAGE_VALUE'],
                        'timestamp': first_row['TIMESTAMP']
                    }
                else:
                    msg_value['avg_value'] = {}
            else:
                msg_value['avg_value'] = {}
        except Exception as e:
            print(f"Error adding avg values for {msg_value['ID']}: {e}")