import os
import time
import csv
from openfactory.apps import OpenFactoryApp
from openfactory.kafka import KSQLDBClient
from openfactory.assets import Asset, AssetAttribute


class ToolMonitoring(OpenFactoryApp):
    """
    ToolMonitoring application for monitoring the state of tools in an IVAC system.
    Inherits from `OpenFactoryApp` and extends it to represent a specific application
    that monitors the state of tools in an IVAC system, updating their conditions based on events.
    Class Attributes:
        IVAC_SYSTEM_UUID (str): Unique identifier for the IVAC system, defaults to 'IVAC'.
    Instance Attributes:
        tool_states (dict): Dictionary to hold the states of tools in the IVAC system.
        ivac (Asset): Asset instance representing the IVAC system.
    """

    IVAC_SYSTEM_UUID: str = os.getenv('IVAC_SYSTEM_UUID', 'IVAC')
    SIMULATION_MODE: str = os.getenv('SIMULATION_MODE', 'false')

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
        object.__setattr__(self, 'ASSET_ID', 'IVAC')

        self.add_attribute(AssetAttribute(
            id='ivac_system',
            value=self.IVAC_SYSTEM_UUID,
            type='Events',
            tag='DeviceUuid'))

        self.ivac = Asset(self.IVAC_SYSTEM_UUID,
                          ksqlClient=ksqlClient,
                          bootstrap_servers=bootstrap_servers)

        self.ivac.add_attribute(AssetAttribute(
                                    id='ivac_tools_status',
                                    value='UNAVAILABLE',
                                    type='Condition',
                                    tag='UNAVAILABLE'))

        self.tool_states['A2ToolPlus'] = self.ivac.A2ToolPlus.value
        self.tool_states['A3ToolPlus'] = self.ivac.A3ToolPlus.value
        self.gate_state = self.ivac.A2BlastGate.value

        print(f"Tool states initialized: {self.tool_states}")
        print(f'Gate state initialized: {self.gate_state}')

        self.setup_power_monitoring_streams(ksqlClient)

        self.method('SimulationMode', self.SIMULATION_MODE)
        print(f'Sent to CMD_STREAM: SimulationMode with value {self.SIMULATION_MODE}')

        # Initialize buzzer state
        self.verify_tool_states()

        self.ivac.subscribe_to_events(self.on_event)

    def setup_power_monitoring_streams(self, ksqlClient: KSQLDBClient) -> None:
        """
        Setup KSQL streams for monitoring power events and durations.
        Creates the necessary streams and tables for power state monitoring.
        """
        try:
            queries = []
            with open('cleanup.sql', "r") as sql_file:
                sql_script = sql_file.read()
                queries += sql_script.split(';')

            with open('usage_duration.sql', "r") as sql_file:
                sql_script = sql_file.read()
                queries += sql_script.split(';')
            
            with open('system_health.sql', "r") as sql_file:
                sql_script = sql_file.read()
                queries += sql_script.split(';')

            for query in queries:
                query = query.strip()
                if not query:
                    continue
                try:
                    ksqlClient.statement_query(query + ';')
                    time.sleep(0.5)
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
        self.ivac.stop_events_subscription()

    def main_loop(self) -> None:
        """ Main loop of the App. """
        while True:
            time.sleep(1)

    def on_event(self, msg_subject: str, msg_value: dict):
        """
        Callback for handling new events from the ivac system.

        Verifies the state of the tools of the ivac system and updates
        the ivac_condition attribute based on these conditions:
        - If all tools are in 'ON' state, sets ivac_condition to 'ERROR'..
        - If any tool is in 'UNAVAILABLE' state, sets ivac_condition to 'UNAVAILABLE'.
        - Else, sets ivac_condition to 'OK'.

        Writes the event data to a CSV file.

        Args:
            msg_subject (str): The key of the Kafka message (the sensor ID).
            msg_value (dict): The message payload containing sample data.
                              Expected keys: 'id' (str), 'value' (float or str).
        """
        prev_state = 'UNAVAILABLE'
        if (msg_value['id'] == 'A2ToolPlus'):
            prev_state = self.tool_states.get('A2ToolPlus', 'UNAVAILABLE')
            self.tool_states['A2ToolPlus'] = msg_value['value']
        elif (msg_value['id'] == 'A3ToolPlus'):
            prev_state = self.tool_states.get('A3ToolPlus', 'UNAVAILABLE')
            self.tool_states['A3ToolPlus'] = msg_value['value']
        
        if (msg_value['id'] == 'Buzzer') and msg_value['value'] != self.ivac.__getattr__('ivac_tools_status').tag:
            self.method("BuzzerControl", self.ivac.__getattr__('ivac_tools_status').tag)
            print(f"Sent to CMD_STREAM: BuzzerControl with value {self.ivac.__getattr__('ivac_tools_status').tag}")

        if (prev_state != msg_value['value'] and msg_value['id'] in self.tool_states.keys()):
            self.verify_tool_states()

        self.write_message_to_csv(msg_subject, msg_value)

    def verify_tool_states(self) -> None:
        """
        Verifies the state of the tools and updates the ivac_condition attribute.

        This method checks the states of the tools in the ivac system and updates
        the ivac_condition attribute based on the following conditions:
        - If all tools are in 'ON' state, sets ivac_condition to 'ERROR'.
        - If any tool is in 'UNAVAILABLE' state, sets ivac_condition to 'UNAVAILABLE'.
        - Else, sets ivac_condition to 'OK'.

        Sends the updated ivac_condition to the CMDS_STREAM to control the buzzer.

        Args:
            tool_states (dict): A dictionary containing tool states with tool IDs as keys.
        """
        print(f"Current tool states: {self.tool_states.values()}")

        if any(state == 'UNAVAILABLE' for state in self.tool_states.values()):
            self.ivac.add_attribute(AssetAttribute(id='ivac_tools_status',
                                                   value='At least one tool is UNAVAILABLE',
                                                   type='Condition',
                                                   tag='WARNING'))
        elif any(state == 'OFF' for state in self.tool_states.values()):
            self.ivac.add_attribute(AssetAttribute(id='ivac_tools_status',
                                                   value='No more than one connected tool is powered ON',
                                                   type='Condition',
                                                   tag='NORMAL'))
        else:
            self.ivac.add_attribute(AssetAttribute(id='ivac_tools_status',
                                                   value='More than one connected tool is powered ON.',
                                                   type='Condition',
                                                   tag='FAULT'))

        time.sleep(0.5)  # Ensure that ivac_tools_status is set before sending
        self.method("BuzzerControl", self.ivac.__getattr__('ivac_tools_status').tag)
        print(f"Sent to CMD_STREAM: BuzzerControl with value {self.ivac.__getattr__('ivac_tools_status').tag}")

    def write_message_to_csv(self, msg_key: str, msg_value: dict) -> None:
        """
        Writes the relevant message data to a CSV file named '${DEVICE_UUID}_msgs.csv'.

        This method appends the event data to the CSV file, creating the file
        if it does not exist. It ensures that the header is written only once.

        Args:
            msg_key (str): The key of the Kafka message (the sensor ID).
            msg_value (dict): The message payload containing sample data.
                              Expected keys: 'id' (str), 'value' (float or str).
        """
        with open(f"{msg_key}_{msg_value['attributes']['timestamp'].split('T')[0]}_msgs.csv'", 'a', newline='') as csvfile:
            fieldnames = list(msg_value.keys())
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            csvfile.seek(0, 2)
            if csvfile.tell() == 0:
                writer.writeheader()

            writer.writerow(msg_value)


app = ToolMonitoring(
    app_uuid=os.getenv('APP_UUID', 'TOOL-MONITORING'),
    ksqlClient=KSQLDBClient(os.getenv('KSQLDB_URL', 'http://ksqldb-server:8088')),
    bootstrap_servers=os.getenv('KAFKA_BROKER', 'broker:29092')
)

app.run()
