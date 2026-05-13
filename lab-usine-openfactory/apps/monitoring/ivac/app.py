import os
import time
import csv
from typing import cast
from openfactory.apps import OpenFactoryApp
from openfactory.kafka import KSQLDBClient
from openfactory.assets import Asset, AssetAttribute
from power_monitoring_streams import PowerMonitoringStreams
from tool_states_rules import ToolStateRules


class EventCSVWriter:
    def write(self, msg_key: str, msg_value: dict) -> None:
        date = msg_value["attributes"]["timestamp"].split("T")[0]
        filename = f"{msg_key}_{date}_msgs.csv"
        with open(filename, "a", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(msg_value.keys()))
            if f.tell() == 0:
                writer.writeheader()
            writer.writerow(msg_value)


class ToolMonitoring(OpenFactoryApp):
    IVAC_SYSTEM_UUID: str = "VIRTUAL-IVAC"
    SIMULATION_MODE: str = "false"

    def __init__(self, ksqlClient, bootstrap_servers, loglevel="INFO"):
        super().__init__(
            ksqlClient=ksqlClient,
            bootstrap_servers=bootstrap_servers,
            loglevel=loglevel,
        )

        self.rules = ToolStateRules()
        self.csv_writer = EventCSVWriter()
        self.tool_states: dict[str, str | int | float] = {}
        self.ivac_system = self.IVAC_SYSTEM_UUID

        self.ivac = Asset(
            self.IVAC_SYSTEM_UUID,
            ksqlClient=ksqlClient,
            bootstrap_servers=bootstrap_servers,
        )
        self.ivac.add_attribute(
            AssetAttribute(
                id="ivac_tools_status",
                value="UNAVAILABLE",
                type="Condition",
                tag="UNAVAILABLE",
            )
        )

        self.tool_states["A2ToolPlus"] = cast(
            AssetAttribute, self.ivac.A2ToolPlus
        ).value
        self.tool_states["A3ToolPlus"] = cast(
            AssetAttribute, self.ivac.A3ToolPlus
        ).value
        self.gate_state: str | int | float = cast(
            AssetAttribute, self.ivac.A2BlastGate
        ).value
        self.logger.info(f"Tool states initialized: {self.tool_states}")
        self.logger.info(f"Gate state initialized: {self.gate_state}")

        PowerMonitoringStreams(ksqlClient, self.logger).setup()

        self.ivac.method("SimulationMode", self.SIMULATION_MODE)
        self.logger.info(f"Sent SimulationMode: {self.SIMULATION_MODE}")

        self.verify_tool_states()
        self.ivac.subscribe_to_events(self.on_event)

    def app_event_loop_stopped(self) -> None:
        self.logger.info("Stopping iVAC consumer thread ...")
        self.ivac.stop_events_subscription()

    def main_loop(self) -> None:
        while True:
            time.sleep(1)

    def on_event(self, msg_subject: str, msg_value: dict) -> None:
        self.logger.debug(f"Received event: {msg_subject} = {msg_value}")

        if "id" not in msg_value or "value" not in msg_value:
            return

        if msg_value["id"] in self.tool_states:
            prev = self.tool_states[msg_value["id"]]
            self.tool_states[msg_value["id"]] = msg_value["value"]
            if prev != msg_value["value"]:
                self.verify_tool_states()

        elif msg_value["id"] == "Buzzer":
            current_tag = cast(
                AssetAttribute, self.ivac.__getattr__("ivac_tools_status")
            ).tag
            if msg_value["value"] != current_tag:
                self.ivac.method("BuzzerControl", current_tag)
                self.logger.info(f"Sent BuzzerControl: {current_tag}")

        self.csv_writer.write(msg_subject, msg_value)

    def verify_tool_states(self) -> None:
        self.logger.info(f"Current tool states: {self.tool_states.values()}")
        tag, msg = self.rules.evaluate(self.tool_states)
        self.ivac.add_attribute(
            AssetAttribute(id="ivac_tools_status", value=msg, type="Condition", tag=tag)
        )
        time.sleep(0.5)  # ensure ivac_tools_status is set before sending
        self.ivac.method("BuzzerControl", tag)
        self.logger.info(f"Sent BuzzerControl: {tag}")


app = ToolMonitoring(
    ksqlClient=KSQLDBClient(os.getenv("KSQLDB_URL", "http://ksqldb-server:8088")),
    bootstrap_servers=os.getenv("KAFKA_BROKER", "broker:29092"),
)

app.run()
