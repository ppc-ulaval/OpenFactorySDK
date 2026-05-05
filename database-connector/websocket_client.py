import asyncio
import os
import websockets
from typing import Dict, Callable, List, Optional

class OpenFactoryWebSocketClient:
    """WebSocket client for OpenFactory to connect and interact with devices."""
    
    def __init__(self, base_url: str = "ws://ofa-api:8000"):
        """Initialize the WebSocket client with the base URL."""
        self.base_url = base_url
        self.connection_tasks: Dict[str, asyncio.Task] = {}
        self.message_handler: Optional[Callable] = None
        self.running = False
        
    def set_message_handler(self, handler: Callable):
        """Set the message handler function"""
        self.message_handler = handler

    async def start(self, assets: List[str]):
        """Start the WebSocket client and begin listening for messages"""
        self.running = True
        
        print(f"Starting WebSocket client with assets: {assets}")
        
        for asset_uuid in assets:
            if asset_uuid not in self.connection_tasks:
                print(f"Creating connection task for asset: {asset_uuid}")
                task = asyncio.create_task(self._maintain_connection(asset_uuid))
                self.connection_tasks[asset_uuid] = task
        
        if self.connection_tasks:
            await asyncio.gather(*self.connection_tasks.values(), return_exceptions=True)

    async def _maintain_connection(self, device_uuid: str):
        """Maintain a persistent connection to a device's WebSocket"""
        while self.running:
            try:
                await self._listen_for_messages(device_uuid)
            except Exception as e:
                print(f"Connection error for device {device_uuid}: {e}")
                print("Retrying connection in 5 seconds...")
                await asyncio.sleep(5)

    async def _listen_for_messages(self, device_uuid: str):
        """Subscribe to a device's WebSocket stream and listen for messages"""
        device_ws_url = f"{self.base_url}/ws/devices/{device_uuid}"
        
        print(f"Attempting to connect to: {device_ws_url}")
        
        try:
            async with websockets.connect(device_ws_url) as ws:
                print(f"Successfully connected to WebSocket for device {device_uuid}")
                
                while self.running:
                    try:
                        msg = await ws.recv()
                        self.message_handler(msg)
                    except websockets.exceptions.ConnectionClosed as e:
                        print(f"WebSocket connection closed for {device_uuid}: {e}")
                        break
                        
        except websockets.exceptions.InvalidURI as e:
            print(f"Invalid WebSocket URI for {device_uuid}: {e}")
            print(f"Attempted URL: {device_ws_url}")
            raise
        except asyncio.TimeoutError:
            print(f"Connection timeout for {device_uuid}")
            raise
        except Exception as e:
            print(f"Unexpected error connecting to {device_uuid}: {type(e).__name__}: {e}")
            raise

    async def stop(self):
        """Stop the WebSocket client"""
        self.running = False
        
        for task in self.connection_tasks.values():
            task.cancel()
            
        if self.connection_tasks:
            await asyncio.gather(*self.connection_tasks.values(), return_exceptions=True)