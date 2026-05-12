from cnc_server import CNCServer
import asyncio
import os


class CNCAdapter:
    def __init__(self):
        self.opcua_port = int(os.environ.get("OPCUA_PORT", 4840))
        self.namespace_uri = os.environ.get("NAMESPACE_URI", "lab-usine-virtuel")
        self.server_ip = os.environ.get("SERVER_IP", "localhost")

        self.cnc_server = CNCServer(
            namespace=self.namespace_uri,
            endpoint=f"opc.tcp://{self.server_ip}:{self.opcua_port}",
        )

    async def run(self):
        try:
            await asyncio.gather(self.cnc_server.run())
        except asyncio.CancelledError:
            pass
        finally:
            await asyncio.gather(self.cnc_server.stop())


if __name__ == "__main__":
    adapter = CNCAdapter()
    asyncio.run(adapter.run())
