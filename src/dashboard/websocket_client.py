import json
import asyncio
import websockets
from typing import Dict, Any, Optional, Set



class WebSocketClient:
    """
    WebSocket client for OpenFactory websockets API.
    """
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.devices: Dict[str, Dict[str, Any]] = {}
        self.message_queue = asyncio.Queue()
        self.device_tasks: Set[asyncio.Task] = set()
        self.initialized = False
        
        self.max_retries = 5
        self.base_retry_delay = 1
        self.max_retry_delay = 30

    async def initialize(self):
        """Initialize client and start monitoring all devices"""
        if self.initialized:
            print("WebSocket client already initialized")
            return
  
        try:
            await self._fetch_initial_devices()
            
            await self._start_device_monitoring()
            self.initialized = True

        except Exception as e:
            print(f"Failed to initialize WebSocket client: {e}")
            
    async def cleanup(self):
        """Clean up all resources"""
        print("Cleaning up WebSocket client...")
        
        for task in self.device_tasks:
            if not task.done():
                task.cancel()
        
        if self.device_tasks:
            await asyncio.gather(*self.device_tasks, return_exceptions=True)
        
        while not self.message_queue.empty():
            try:
                self.message_queue.get_nowait()
            except asyncio.QueueEmpty:
                break
        
        self.initialized = False
        print("WebSocket client cleanup completed")

    async def _fetch_initial_devices(self):
        """Fetch the initial list of devices from the API"""
        try:
            async with websockets.connect(f"{self.base_url}/ws/devices") as ws:
                message = await ws.recv()
                data = json.loads(message)
                
                if data.get("event") == "devices_list":
                    for device in data.get("devices", []):
                        device_uuid = device["device_uuid"]
                        self.devices[device_uuid] = {
                            "device_uuid": device_uuid,
                            "dataitems": self._format_dataitems(device.get("dataitems", {})),
                            "stats": device.get("durations", {}),
                        }
                
        except Exception as e:
            print(f"Failed to fetch initial devices: {e}")
            
    async def _start_device_monitoring(self):
        """Start monitoring tasks for all devices"""
        for device_uuid in self.devices:
            task = asyncio.create_task(
                self._monitor_device(device_uuid),
                name=f"monitor-{device_uuid}"
            )
            self.device_tasks.add(task)
            
            task.add_done_callback(self.device_tasks.discard)

    async def _monitor_device(self, device_uuid: str):
        """Monitor a single device with automatic reconnection"""
        retry_count = 0
        
        while retry_count < self.max_retries:
            try:
                await self._device_connection_loop(device_uuid)
                break
                
            except Exception as e:
                retry_count += 1
                
                print(
                    f"Device {device_uuid} connection failed (attempt {retry_count}): {e}"
                )
                
                if retry_count < self.max_retries:
                    delay = min(
                        self.base_retry_delay * (2 ** (retry_count - 1)),
                        self.max_retry_delay
                    )
                    print(f"Retrying {device_uuid} in {delay}s...")
                    await asyncio.sleep(delay)
                else:
                    print(f"Max retries reached for device {device_uuid}")

    async def _device_connection_loop(self, device_uuid: str):
        """Main connection loop for a device"""
        async with websockets.connect(f"{self.base_url}/ws/devices/{device_uuid}") as ws:
            print(f"Connected to device {device_uuid}")
            while True:
                try:
                    data = await ws.recv()
                    await self._handle_device_message(device_uuid, data)
                    
                except websockets.exceptions.ConnectionClosed:
                    print(f"Connection closed for device {device_uuid}")
                    break
                    
                except json.JSONDecodeError as e:
                    print(f"JSON decode error for {device_uuid}: {e}")
                    continue

    async def _handle_device_message(self, device_uuid: str, raw_data: str):
        """Process a message from a device"""
        try:
            parsed_data = json.loads(raw_data)
            parsed_data["device_uuid"] = device_uuid
            
            self._update_device_data(device_uuid, parsed_data)
            
            await self.message_queue.put(parsed_data)
            
        except Exception as e:
            print(f"Error handling message from {device_uuid}: {e}")

    def _update_device_data(self, device_uuid: str, data: Dict[str, Any]):
        """Update device data from incoming message"""
        if device_uuid in self.devices:
            device = self.devices[device_uuid]
            
            if "dataitems" in data:
                device["dataitems"] = self._format_dataitems(data["dataitems"])
            
            if "stats" in data:
                device["stats"] = data["stats"]

    def _format_dataitems(self, device_data: dict) -> list:
        """Format device data for frontend consumption"""
        items = []
        for item_id, value in device_data.items():
            item_type = self._determine_item_type(item_id)
            items.append({
                'id': item_id, 
                'value': value, 
                'type': item_type
            })
        return items

    def _determine_item_type(self, item_id: str) -> str:
        """Determine the type of data item based on its ID"""
        if 'Tool' in item_id:
            return 'tool'
        elif 'Gate' in item_id:
            return 'gate'
        elif 'concentration' in item_id:
            return 'sensor'
        else:
            return 'condition'

    async def send_simulation_mode(self, device_uuid: str, enabled: bool):
        """Send simulation mode command to a specific device"""
        if device_uuid not in self.devices:
             ValueError(f"Device {device_uuid} not found")
        
        try:
            async with websockets.connect(f"{self.base_url}/ws/devices/{device_uuid}") as ws:
                command = {
                    "method": "simulation_mode",
                    "params": {
                        "name": "SimulationMode",
                        "args": enabled
                    }
                }
                
                await ws.send(json.dumps(command))
                response_data = await ws.recv()
                response = json.loads(response_data)
                
                print(f"Simulation mode {'enabled' if enabled else 'disabled'}")
                return response
                
        except Exception as e:
            print(f"Failed to send simulation mode to {device_uuid}: {e}")
            

    def get_device(self, device_uuid: str) -> Optional[Dict[str, Any]]:
        """Get a specific device"""
        return self.devices.get(device_uuid)

    def get_all_devices(self) -> Dict[str, Dict[str, Any]]:
        """Get all devices"""
        return self.devices.copy()

    def is_device_connected(self, device_uuid: str) -> bool:
        """Check if a device is currently connected"""
        device = self.devices.get(device_uuid)
        return device.get("connection_status", "") == "connected"