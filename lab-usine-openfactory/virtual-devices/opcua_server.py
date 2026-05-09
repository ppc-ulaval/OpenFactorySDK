from typing import Callable
from asyncua import Server, Node, ua


class OPCUAServer:
    def __init__(
        self, endpoint="opc.tcp://0.0.0.0:4840", namespace="lab-usine-virtuel"
    ):
        self.endpoint = endpoint
        self.namespace = namespace
        self.server = None  # ty:ignore[invalid-assignment]
        self.idx = None  # ty:ignore[invalid-assignment]
        self.objects = None  # ty:ignore[invalid-assignment]
        self.equipment_nodes = {}
        self.variables = {}
        self.methods = {}

    async def _setup(self):
        self.server: Server = Server()
        await self.server.init()
        self.server.set_endpoint(self.endpoint)
        self.server.set_server_name("Virtual LabUsine OPC-UA Server")
        self.server.set_security_policy([ua.SecurityPolicyType.NoSecurity])
        self.idx: int = await self.server.register_namespace(self.namespace)
        self.objects: Node = self.server.get_objects_node()

    async def create_equipment_node(self, equipment_name) -> None:
        equipment_node = await self.objects.add_object(self.idx, equipment_name)
        self.equipment_nodes[equipment_name] = equipment_node

    async def add_variable(
        self, equipment_name, variable_name, initial_value=0.0, writable=False
    ):
        node = self.equipment_nodes.get(equipment_name)
        if node is None:
            raise ValueError(f"Equipment '{equipment_name}' not found.")
        var = await node.add_variable(self.idx, variable_name, initial_value)
        if writable:
            await var.set_writable()
        self.variables[f"{equipment_name}.{variable_name}"] = var
        return var

    async def set_value(self, equipment_name, variable_name, value):
        key = f"{equipment_name}.{variable_name}"
        var = self.variables.get(key)
        if var is None:
            raise ValueError(f"Variable '{key}' not found.")
        await var.write_value(value)

    async def get_value(self, equipment_name, variable_name):
        key = f"{equipment_name}.{variable_name}"
        var = self.variables.get(key)
        if var is None:
            raise ValueError(f"Variable '{key}' not found.")
        return await var.read_value()

    async def add_method(
        self,
        equipment_name,
        method_name,
        callback: Callable,
        command_type: ua.VariantType,
    ):
        node = self.equipment_nodes.get(equipment_name)
        if node is None:
            raise ValueError(f"Equipment '{equipment_name}' not found.")
        method = await node.add_method(self.idx, method_name, callback, [command_type])
        self.methods[f"{equipment_name}.{method_name}"] = method
        return method

    async def start(self):
        await self.server.start()
        print(f"OPC UA Server started at {self.endpoint}")

    async def stop(self):
        await self.server.stop()
        print("OPC UA Server stopped.")

    async def __aenter__(self):
        await self.start()
        return self

    async def __aexit__(self, *args):
        await self.stop()
