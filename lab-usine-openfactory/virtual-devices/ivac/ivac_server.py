from asyncua.common.methods import uamethod
from asyncua import ua
from opcua_server import OPCUAServer
from virtual_ivac import VirtualIVAC
import os
import asyncio
import random


class IVACServer(OPCUAServer):
    def __init__(self, namespace, endpoint):
        super().__init__(namespace=namespace, endpoint=endpoint)
        self.device_browse_name: str = os.environ.get(
            "DEVICE_BROWSE_NAME", "VIRTUAL-IVAC"
        )
        self.variable_names: list[str] = [
            "A1ToolPlus",
            "A2ToolPlus",
            "A3ToolPlus",
            "A1BlastGate",
            "A2BlastGate",
            "A3BlastGate",
        ]
        self.method_names = ["BuzzerControl", "SimulationMode"]
        self.ivac = VirtualIVAC()

    async def run(self):
        await self._initialize_server()
        await self.start()
        try:
            while True:
                await self._update_variables()
                await asyncio.sleep(
                    random.uniform(self.ivac.MIN_TOGGLE_TIME, self.ivac.MAX_TOGGLE_TIME)
                )
        except asyncio.CancelledError:
            pass
        finally:
            await self.stop()

    async def _initialize_server(self):
        await self._setup()
        await self.create_equipment_node(self.device_browse_name)

        for var in self.variable_names:
            await self.add_variable(
                self.device_browse_name, var, initial_value="OFF", writable=False
            )
        for method in self.method_names:
            await self.add_method(
                self.device_browse_name,
                method,
                callback=getattr(self, f"_{method.lower()}_method"),
                command_type=ua.VariantType.String,
            )

    @uamethod
    def _buzzercontrol_method(self, command: str):
        print(f"BuzzerControl command received: {command}")
        self.ivac.set_buzzer_status(command)

    @uamethod
    def _simulationmode_method(self, command: str):
        print(f"SimulationMode command received: {command}")
        self.ivac.set_simulation_mode(command.lower() == "true")

    async def _update_variables(self):
        data = self.ivac.read_data()
        for var in self.variable_names:
            await self.set_value(self.device_browse_name, var, data[var])
