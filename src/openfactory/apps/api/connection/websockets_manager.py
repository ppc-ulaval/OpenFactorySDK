import asyncio
import json
import time
from queue import Queue
from models import ClientMessage
from websockets.exceptions import ConnectionClosed
from websockets.server import WebSocketServerProtocol

from exceptions import DeviceNotFoundException, StreamCreationException
from connection.connection_manager import ConnectionManager
from services.device_service import DeviceService
from services.stream_service import StreamService


class WebsocketsManager:
    def __init__(self, connection_manager: ConnectionManager, device_service: DeviceService, 
                 stream_service: StreamService, topic_subscriber, openfactory_app):
        self.connection_manager = connection_manager
        self.device_service = device_service
        self.stream_service = stream_service
        self.topic_subscriber = topic_subscriber
        self.openfactory_app = openfactory_app
        self.device_assets = {}
        self.device_topics = {}
        
        self.message_queue = Queue()
        self.running = True
        
        self.asyncio_loop = None
        
        self.message_processor_task = None
    
    def set_asyncio_loop(self, loop):
        """Set the asyncio loop reference"""
        self.asyncio_loop = loop
        if not self.message_processor_task:
            self.message_processor_task = asyncio.create_task(self._process_stream_messages())
    
    def _on_message(self, msg_key: str, msg_value: dict):
        """Handle messages from dedicated Kafka topic"""
        try:
            self.message_queue.put((msg_key, msg_value))
            
        except Exception as e:
            print(f"Error queuing Kafka message for {msg_key}: {e}")

    async def handle_connection(self, websocket: WebSocketServerProtocol):
        """Route websocket client to correct endpoint"""
        if not self.asyncio_loop:
            self.set_asyncio_loop(asyncio.get_running_loop())
        
        path = websocket.request.path
        
        if path == "/ws/devices":
            await self._send_devices_list(websocket) ##this is for dashboard app only
            return
        
        if not path.startswith("/ws/devices/"):
            await self._send_error(websocket, "Invalid endpoint")
            return
        
        device_uuid = path.split("/")[3]
        await self._handle_device_connection(websocket, device_uuid)
    
    async def _handle_device_connection(self, websocket: WebSocketServerProtocol, device_uuid: str):
        """Handle connection to a specific device"""
        try:
            await self.connection_manager.add_connection(websocket, device_uuid)
            await self._initialize_device(device_uuid)
            await self._send_initial_data(websocket, device_uuid)
            
            sender_task = asyncio.create_task(self._handle_outgoing_messages(websocket))
            receiver_task = asyncio.create_task(self._handle_incoming_messages(websocket, device_uuid))
            
            done, pending = await asyncio.wait(
                [sender_task, receiver_task], 
                return_when=asyncio.FIRST_COMPLETED
            )
            
            for task in pending:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
            
            for task in done:
                if task.exception():
                    print(f"Task completed with exception: {task.exception()}")
            
        except Exception as e:
            print(f"Error in device connection handler for {device_uuid}: {e}")
        finally:
            await self.connection_manager.remove_connection(websocket)
            print(f"WebSocket connection closed for device: {device_uuid}")

    async def _initialize_device(self, device_uuid: str):
        """Initialize device monitoring if not already done"""
        if device_uuid in self.device_assets:
            print(f"Device {device_uuid} already initialized")
            return
        
        try:
            self.openfactory_app.initialize_asset(device_uuid)
            
            topic = self.stream_service.create_device_stream(device_uuid)
            
            self.topic_subscriber.subscribe_to_kafka_topic(
                topic=topic,
                kafka_group_id=f'api_device_stream_group_{device_uuid}',
                on_message=self._on_message,
                message_filter=lambda key: key == device_uuid
            )
            
            self.device_topics[device_uuid] = topic
            self.device_assets[device_uuid] = True
            print(f"Successfully initialized monitoring for device {device_uuid}")
            
        except StreamCreationException as e:
            print(f"Failed to initialize device {device_uuid}: {e}")
            raise
        except Exception as e:
            print(f"Unexpected error initializing device {device_uuid}: {e}")
            raise
    
    async def _send_initial_data(self, websocket: WebSocketServerProtocol, device_uuid: str):
        """Send initial data to newly connected client"""
        try:
            data_items = self.device_service.get_device_dataitems(device_uuid)
            initial_data = {
                "event": "connection_established",
                "device_uuid": device_uuid,
                "timestamp": time.time(),
                "data_items": data_items,
                "connection_count": self.connection_manager.get_connection_count(device_uuid)
            }
            await websocket.send(json.dumps(initial_data))
            print(f"Sent initial data to client for device {device_uuid}")
            
        except DeviceNotFoundException as e:
            print(f"Device not found: {e}")
            await self._send_error(websocket, str(e))
        except Exception as e:
            print(f"Error sending initial data for {device_uuid}: {e}")
            await self._send_error(websocket, f"Failed to get initial data: {e}")

    async def _handle_outgoing_messages(self, websocket: WebSocketServerProtocol):
        """Handle outgoing messages to client"""
        queue = self.connection_manager.get_message_queue(websocket)
        if not queue:
            print("No message queue found for websocket")
            return
        
        try:
            while True:
                try:
                    message = await asyncio.wait_for(queue.get(), timeout=1.0)
                    await websocket.send(message)
                    
                except asyncio.TimeoutError:
                    ping_msg = {
                        "event": "ping", 
                        "timestamp": time.time()
                    }
                    await websocket.send(json.dumps(ping_msg))
                    
                except ConnectionClosed:
                    print("WebSocket connection closed in outgoing handler")
                    break
                    
        except Exception as e:
            print(f"Error in outgoing message handler: {e}")
    
    async def _handle_incoming_messages(self, websocket: WebSocketServerProtocol, device_uuid: str):
        """Handle incoming messages from client"""
        try:
            while True:
                try:
                    raw_message = await asyncio.wait_for(websocket.recv(), timeout=30.0)
                    
                    try:
                        message = json.loads(raw_message)
                        client_message = ClientMessage.from_dict(message)
                        await self._process_client_message(websocket, device_uuid, client_message)
                        
                    except json.JSONDecodeError as e:
                        print(f"Invalid JSON received from {device_uuid}: {e}")
                        await self._send_error(websocket, f"Invalid JSON: {e}")
                        
                    except Exception as e:
                        print(f"Error parsing client message from {device_uuid}: {e}")
                        await self._send_error(websocket, f"Message parsing error: {e}")
                
                except asyncio.TimeoutError:
                    continue
                    
                except ConnectionClosed:
                    print(f"WebSocket connection closed in incoming handler for {device_uuid}")
                    break
                    
        except Exception as e:
            print(f"Error in incoming message handler for {device_uuid}: {e}")
    
    async def _process_client_message(self, websocket: WebSocketServerProtocol, 
                                    device_uuid: str, message: ClientMessage):
        """Process client messages based on method"""
        try:
            print(f"Processing client message from {device_uuid}: {message.method}")
            
            if message.method == "simulation_mode":
                await self._send_simulation_mode(websocket, message.params)
                
            elif message.method == "drop_stream":
                await self._drop_stream(websocket, device_uuid)
                
            else:
                print(f"Unknown method from {device_uuid}: {message.method}")
                await self._send_error(websocket, f"Unknown method: {message.method}")
                
        except Exception as e:
            print(f"Error processing client message from {device_uuid}: {e}")
            await self._send_error(websocket, f"Processing error: {e}")

    async def _process_stream_messages(self):
        """Background task to process messages in async context (stream updates)"""
        while self.running:
            try:
                if not self.message_queue.empty():
                    try:
                        msg_key, msg_value = self.message_queue.get_nowait()
                        await self._handle_stream_message(msg_key, msg_value)
                    except Exception as e:
                        print(f"Error processing queued message: {e}")
                
                await asyncio.sleep(0.01)
                
            except Exception as e:
                print(f"Error in message processor: {e}")
                await asyncio.sleep(1)
    
    async def _handle_stream_message(self, msg_key: str, msg_value: dict):
        """Parse and thread messages for device updates"""
        try:
            device_uuid = msg_key
            
            if device_uuid == 'IVAC':
                self.device_service.add_duration_updates(msg_value)
            elif device_uuid == 'DUSTTRAK':
                self.device_service.add_avg_data(msg_value)
            
            message = {
                "asset_uuid": device_uuid,
                "data": dict(msg_value),
                "timestamp": time.time()
            }
            
            await self.connection_manager.broadcast_to_device_connections(device_uuid, message)
            
        except Exception as e:
            print(f"Error handling message for {msg_key}: {e}")
    
    async def _send_simulation_mode(self, websocket: WebSocketServerProtocol, params: dict):
        """Handle simulation mode request"""
        try:
            name = params.get("name")
            args = params.get("args")
            
            if not name or args is None:
                await self._send_error(websocket, "Missing name or args for simulation mode")
                return
            
            self.openfactory_app.send_method(name, str(args).lower())

            print(f'Sent to CMD_STREAM: {name} with value {str(args).lower()}')
            
            response = {
                "event": "simulation_mode_updated",
                "success": True,
                "value": args
            }
            await websocket.send(json.dumps(response))
            
        except Exception as e:
            print(f"Error sending simulation mode: {e}")
            error_response = {
                "event": "simulation_mode_updated",
                "success": False,
                "error": str(e),
                "timestamp": time.time()
            }
            await websocket.send(json.dumps(error_response))
    
    async def _drop_stream(self, websocket: WebSocketServerProtocol, device_uuid: str):
        """Handle stream drop request"""
        try:
            self.stream_service.drop_device_stream(device_uuid)
            
            if device_uuid in self.device_topics:
                del self.device_topics[device_uuid]
            if device_uuid in self.device_assets:
                del self.device_assets[device_uuid]
            
            response = {
                "event": "stream_dropped", 
                "success": True,
                "device_uuid": device_uuid,
                "timestamp": time.time()
            }
            await websocket.send(json.dumps(response))
            print(f"Dropped stream for device {device_uuid}")
            
        except StreamCreationException as e:
            print(f"Failed to drop stream for {device_uuid}: {e}")
            await self._send_error(websocket, f"Failed to drop stream: {e}")
        except Exception as e:
            print(f"Unexpected error dropping stream for {device_uuid}: {e}")
            await self._send_error(websocket, f"Unexpected error: {e}")
    
    async def _send_devices_list(self, websocket: WebSocketServerProtocol):
        """Send list of all available devices for demo dashboard"""
        try:
            devices = self.device_service.get_all_devices()
            device_list = []
            
            for device_uuid in devices:
                try:
                    device_info = {
                        "device_uuid": device_uuid,
                        "dataitems": self.device_service.get_device_dataitems(device_uuid),
                        "durations": self.device_service.get_device_stats(device_uuid)
                    }
                    device_list.append(device_info)
                except Exception as e:
                    print(f"Error getting info for device {device_uuid}: {e}")
            response = {
                "event": "devices_list",
                "timestamp": time.time(),
                "devices": device_list
            }
            await websocket.send(json.dumps(response))
            print(f"Sent devices list with {len(device_list)} devices")
            
            while True:
                try:
                    await asyncio.sleep(30)
                    ping = {
                        "event": "ping", 
                        "timestamp": time.time(),
                        "active_devices": len(device_list)
                    }
                    await websocket.send(json.dumps(ping))
                    
                except ConnectionClosed:
                    print("Devices list connection closed")
                    break
                except Exception as e:
                    print(f"Error sending ping to devices list connection: {e}")
                    break
                    
        except Exception as e:
            print(f"Error in devices list handler: {e}")
            await self._send_error(websocket, f"Failed to get devices list: {e}")
        finally:
            try:
                await websocket.close()
            except:
                pass
    
    async def _send_error(self, websocket: WebSocketServerProtocol, message: str):
        """Send error message to client"""
        error_msg = {
            "event": "error", 
            "message": message,
            "timestamp": time.time()
        }
        try:
            await websocket.send(json.dumps(error_msg))
        except ConnectionClosed:
            print("Cannot send error - connection closed")
        except Exception as e:
            print(f"Failed to send error message: {e}")