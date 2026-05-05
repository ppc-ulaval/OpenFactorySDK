import asyncio
import json
from collections import defaultdict
from typing import Dict, Set
from websockets.server import WebSocketServerProtocol


class ConnectionManager:
    def __init__(self):
        self.device_connections: Dict[str, Set[WebSocketServerProtocol]] = defaultdict(set)
        self.connection_to_device: Dict[WebSocketServerProtocol, str] = {}
        self.message_queues: Dict[WebSocketServerProtocol, asyncio.Queue] = {}
        self._lock = asyncio.Lock()
    
    async def add_connection(self, websocket: WebSocketServerProtocol, device_uuid: str):
        """Add a new WebSocket connection for a device"""
        async with self._lock:
            self.device_connections[device_uuid].add(websocket)
            self.connection_to_device[websocket] = device_uuid
            self.message_queues[websocket] = asyncio.Queue()
    
    async def remove_connection(self, websocket: WebSocketServerProtocol):
        """Remove a WebSocket connection"""
        async with self._lock:
            if websocket in self.connection_to_device:
                device_uuid = self.connection_to_device[websocket]
                self.device_connections[device_uuid].discard(websocket)
                del self.connection_to_device[websocket]
                if websocket in self.message_queues:
                    del self.message_queues[websocket]

    async def cleanup_all_connections(self):
        for websocket in self.connection_to_device.keys():
            await self.remove_connection(websocket)
    
    async def broadcast_to_device_connections(self, device_uuid: str, message: Dict):
        """Broadcast a message to all connections for a specific device"""
        if device_uuid not in self.device_connections:
            return
        
        connections_copy = self.device_connections[device_uuid].copy()
        for connection in connections_copy:
            if connection in self.message_queues:
                queue = self.message_queues[connection]
                try:
                    await queue.put(json.dumps(message))
                except Exception as e:
                    print(f"Error queuing message for connection: {e}")
                    await self.remove_connection(connection)

    def get_connection_count(self, device_uuid: str) -> int:
        """Get the number of active connections for a device"""
        return len(self.device_connections[device_uuid])
    
    def get_message_queue(self, websocket: WebSocketServerProtocol) -> asyncio.Queue:
        """Get the message queue for a connection"""
        return self.message_queues.get(websocket)