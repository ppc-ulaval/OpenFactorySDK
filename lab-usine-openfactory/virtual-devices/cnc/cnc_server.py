from opcua_server import OPCUAServer
from virtual_cnc import VirtualCNC
import os
import asyncio
import random


class CNCServer(OPCUAServer):
    MIN_TOGGLE_TIME = float(os.environ.get("MIN_TOGGLE_TIME", 5))
    MAX_TOGGLE_TIME = float(os.environ.get("MAX_TOGGLE_TIME", 10))

    def __init__(self, namespace, endpoint):
        super().__init__(namespace=namespace, endpoint=endpoint)
        self.device_browse_name: str = os.environ.get(
            "DEVICE_BROWSE_NAME", "VIRTUAL-CNC"
        )
        self.variable_names: list[str] = [
            "spindle_speed",
            "vacuum_status",
        ]
        self.cnc = VirtualCNC()

    async def run(self):
        await self._initialize_server()
        await self.start()
        try:
            while True:
                await self._update_variables()
                await asyncio.sleep(random.uniform(MIN_TOGGLE_TIME, MAX_TOGGLE_TIME))
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

    async def _update_variables(self):
        data = self.cnc.read_data()
        for var in self.variable_names:
            await self.set_value(self.device_browse_name, var, data[var])
