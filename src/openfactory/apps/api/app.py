import asyncio
import os
import threading
import time
import websockets
from openfactory.apps import OpenFactoryApp
from openfactory.assets import Asset
from openfactory.kafka import KSQLDBClient

from config import Config
from services.device_service import DeviceService
from services.stream_service import StreamService
from connection.connection_manager import ConnectionManager
from connection.websockets_manager import WebsocketsManager
from topic_subscription import TopicSubscriber

class OpenFactoryAPI(OpenFactoryApp):
    """Main application class that orchestrates all components"""

    def __init__(self, config: Config, app_uuid, ksqlClient, bootstrap_servers, loglevel='INFO'):
        super().__init__(app_uuid, ksqlClient, bootstrap_servers, loglevel)
        object.__setattr__(self, 'ASSET_ID', 'IVAC')
        self.running = True
        self.config = config


        self.ksqlClient = ksqlClient
        self.topic_subscriber = TopicSubscriber()
        self.connection_manager = ConnectionManager()
        self.websockets_manager = WebsocketsManager(
            self.connection_manager,
            DeviceService(self.ksqlClient), 
            StreamService(self.ksqlClient),
            self.topic_subscriber,
            self
        )
        
        self.websocket_server = None
        self.websocket_task = None
        self.websocket_thread = None

    def initialize_asset(self, device_uuid: str):
        return Asset(
            device_uuid,
            ksqlClient=self.ksqlClient,
            bootstrap_servers=self.config.kafka_brokers
        )
    
    def send_method(self, name, args):
        self.method(name, args)

    def main_loop(self):
        """
        Main loop
        """
        print("Starting OpenFactory main loop...")
        
        self.websocket_thread = threading.Thread(
            target=self._run_websocket_server_thread, 
            daemon=True
        )
        self.websocket_thread.start()
        
        while self.running:
            try:
                total_connections = sum(
                    len(connections) for connections in self.connection_manager.device_connections.values()
                )
                if total_connections > 0:
                    print(
                        f"Active WebSocket connections: {total_connections} "
                        f"across {len(self.connection_manager.device_connections)} devices"
                    )
                time.sleep(30)
            except KeyboardInterrupt:
                print("Shutting down WebSocket API...")
                self.running = False
                break

    def _run_websocket_server_thread(self):
        """
        Run WebSocket server in its own thread with its own event loop.
        """
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            loop.run_until_complete(self._start_websocket_server())
        except Exception as e:
            print(f"WebSocket server thread error: {e}")
            self.running = False
        finally:
            loop.close()

    async def _start_websocket_server(self):
        """Start the actual WebSocket server (async)"""
        try:
            self.websocket_server = await websockets.serve(
                self.websockets_manager.handle_connection,
                self.config.websocket_host,
                self.config.websocket_port,
                ping_interval=self.config.ping_interval,
                ping_timeout=self.config.ping_timeout
            )
            print(f"WebSocket server started on {self.config.websocket_host}:{self.config.websocket_port}")
            
            while self.running:
                await asyncio.sleep(1)
                
        except Exception as e:
            print(f"WebSocket server error: {e}")
            self.running = False
        finally:
            if self.websocket_server:
                self.websocket_server.close()
                await self.websocket_server.wait_closed()

    def app_event_loop_stopped(self):
        """
        Override parent method
        """
        print("OpenFactory app event loop stopped, cleaning up...")
        self.running = False


def main():
    """Main entry point"""
    config = Config()
    
    api = OpenFactoryAPI(
        app_uuid='OFA-API',
        config=config,
        ksqlClient=KSQLDBClient(os.getenv('KSQLDB_URL', 'http://ksqldb-server:8088')),
        bootstrap_servers=os.getenv('KAFKA_BROKER', 'broker:29092')
    )
    
    try:
        api.run()
    except KeyboardInterrupt:
        print("Received shutdown signal")
    finally:
        api.running = False

if __name__ == "__main__":
    main()