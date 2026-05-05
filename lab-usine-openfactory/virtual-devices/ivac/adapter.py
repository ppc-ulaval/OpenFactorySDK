import asyncio
import threading
import time
import random
import os
from mtcadapter.mtcdevices import MTCDevice
from mtcadapter.adapters import MTCAdapter

from asyncua import Server, ua, uamethod


class OPCUAServerThread:
    """OPC UA Server running in separate thread"""

    def __init__(self, device):
        self.device = device
        self.server = None
        self.loop = None
        self.namespace_idx = 0
        self.buzzer_status_var = None
        self.simulation_status_var = None

        self.opcua_port = int(os.environ.get("OPCUA_PORT", 4840))
        self.namespace_uri = os.environ.get("NAMESPACE_URI", "demofactory")
        self.device_browse_name = os.environ.get("DEVICE_BROWSE_NAME", "IVAC")
        self.server_ip = os.environ.get("SERVER_IP", "virtual-ivac-tool-plus-adapter")

    def start(self):
        """Start OPC UA server in separate thread"""
        self.thread = threading.Thread(target=self._run_server, daemon=True)
        self.thread.start()
        print("OPC UA server thread started")

    def _run_server(self):
        """Run OPC UA server in asyncio loop"""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

        try:
            self.loop.run_until_complete(self._start_opcua_server())
        except Exception as e:
            print(f"OPC UA server error: {e}")
        finally:
            self.loop.close()

    async def _start_opcua_server(self):
        """Initialize and start OPC UA server"""
        self.server = Server()
        await self.server.init()

        endpoint = f"opc.tcp://{self.server_ip}:{self.opcua_port}/freeopcua/server/"
        self.server.set_endpoint(endpoint)
        self.server.set_server_name("iVAC Tool Plus Integrated Server")

        self.server.set_security_policy([ua.SecurityPolicyType.NoSecurity])

        self.namespace_idx = await self.server.register_namespace(self.namespace_uri)
        print(f"Created OPC UA namespace '{self.namespace_uri}' with index {self.namespace_idx}")

        objects = self.server.get_objects_node()
        device_node = await objects.add_object(self.namespace_idx, self.device_browse_name)

        await self._add_methods_to_device(device_node)

        print("OPC UA server initialized")
        print(f"OPC UA: {endpoint}")
        print(f"Namespace: {self.namespace_uri}")
        print(f"Device: {self.device_browse_name}")

        async with self.server:
            print("OPC UA server is running...")
            try:
                while True:
                    await asyncio.sleep(1)
            except Exception as e:
                print(f"OPC UA server loop error: {e}")

    async def _add_methods_to_device(self, device_node):
        """Add control methods to device node"""

        input_args = [
            ua.Argument(
                Name="Command",
                DataType=ua.NodeId(ua.ObjectIds.String),
                ValueRank=-1,
                Description=ua.LocalizedText("Command: NORMAL/FAULT/WARNING")
            )
        ]

        output_args = [
            ua.Argument(
                Name="Result",
                DataType=ua.NodeId(ua.ObjectIds.String),
                ValueRank=-1,
                Description=ua.LocalizedText("Operation result")
            )
        ]

        buzzer_method = await device_node.add_method(
            self.namespace_idx,
            "BuzzerControl",
            self._buzzer_control_method,
            input_args,
            output_args
        )

        simulation_method = await device_node.add_method(
            self.namespace_idx,
            "SimulationMode",
            self._simulation_mode_method,
            input_args,
            output_args
        )

        print(f"Added OPC UA methods BuzzerControl ({buzzer_method}), SimulationMode ({simulation_method})")

    @uamethod
    async def _buzzer_control_method(self, parent, command: str) -> str:
        """OPC UA method for buzzer/LED control"""
        print(f"BuzzerControl command received: {command}")

        if self.device.simulation_mode:
            print("Command ignored: simulation mode is activated")
            return "Command ignored: simulation mode active"

        if self.device.set_led_state(command):
            self.device.set_buzzer_status(command)
            return "OK"
        else:
            error_msg = "Unknown command. Use: NORMAL, FAULT, WARNING"
            print(f"Invalid buzzer command: {command}")
            return error_msg

    @uamethod
    async def _simulation_mode_method(self, parent, command: str) -> str:
        """OPC UA method for simulation mode control"""
        print(f"SimulationMode command received: {command}")

        if command.lower() == "true":
            self.device.set_simulation_mode(True)
        elif command.lower() == "false":
            self.device.set_simulation_mode(False)
        else:
            return "Invalid command. Use: true or false"

        mode_str = "activated" if self.device.simulation_mode else "deactivated"
        print(f"Simulation mode is {mode_str}")

        return "OK"


class Virtual_iVACToolPlus(MTCDevice):
    """
    Virtual adapter for iVAC Tool Plus, which detects current on any electrical powered device.
    """

    MIN_TOGGLE_TIME = float(os.environ.get("MIN_TOGGLE_TIME", 5))
    MAX_TOGGLE_TIME = float(os.environ.get("MAX_TOGGLE_TIME", 10))
    LED_MODES = ['NORMAL', 'FAULT', 'WARNING']

    def __init__(self):
        self._tool_states = {'A2ToolPlus': 'OFF', 'A3ToolPlus': 'OFF'}
        self._gates_states = {'A2BlastGate': 'OPEN', 'A3BlastGate': 'CLOSED'}
        self._simulation_mode = False
        self._buzzer_status = 'WARNING'

        self._led_states = {state: False for state in self.LED_MODES}
        self._current_led_state = 'WARNING'
        self._led_states[self._current_led_state] = True

    def set_led_state(self, state: str) -> bool:
        """Set the LED mode (NORMAL/FAULT/WARNING)"""
        state = state.upper()
        if state not in self.LED_MODES:
            return False

        for m in self._led_states:
            self._led_states[m] = False

        self._led_states[state] = True
        self._current_led_state = state
        print(f"LED state changed to: {state}")
        return True

    @property
    def simulation_mode(self) -> bool:
        return self._simulation_mode

    @simulation_mode.setter
    def simulation_mode(self, value: bool):
        self._simulation_mode = value
        print(f"Simulation mode {'activated' if value else 'deactivated'}")

    def set_buzzer_status(self, status: str):
        self._buzzer_status = status.upper()
        print(f"Buzzer status set to: {self._buzzer_status}")

    def read_data(self) -> dict:
        """Read and toggle tool states with random delay"""
        time.sleep(round(random.uniform(self.MIN_TOGGLE_TIME, self.MAX_TOGGLE_TIME), 2))

        for tool in self._tool_states:
            self._tool_states[tool] = 'ON' if self._tool_states[tool] == 'OFF' else 'OFF'
            self._gates_states[tool[:-8]+'BlastGate'] = 'CLOSED' if self._tool_states[tool] == 'OFF' else 'OPEN'

        return {
            'A2ToolPlus': self._tool_states['A2ToolPlus'],
            'A3ToolPlus': self._tool_states['A3ToolPlus'],
            'A2BlastGate': self._gates_states['A2BlastGate'],
            'A3BlastGate': self._gates_states['A3BlastGate'],
            'Buzzer': self._buzzer_status,  # TODO buzzer state is always delayed (will be the status of previous tool state)...
        }


class Virtual_iVACToolPlusAdapter(MTCAdapter):
    device_class = Virtual_iVACToolPlus
    adapter_port = int(os.environ.get("ADAPTER_PORT", 7878))

    def __init__(self):
        super().__init__()
        self.opcua_server = None
        self.device = self.device_class()

    def run(self):
        """Start both MTConnect and OPC UA servers with shared device instance"""
        self.opcua_server = OPCUAServerThread(self.device)
        self.opcua_server.start()

        time.sleep(2)

        print("Starting MTConnect adapter...")
        super().run()


def main():
    adapter = Virtual_iVACToolPlusAdapter()
    adapter.run()


if __name__ == "__main__":
    main()
