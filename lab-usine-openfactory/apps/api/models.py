from dataclasses import dataclass
from typing import Dict, Any
import json

@dataclass
class DeviceMessage:
    device_uuid: str
    event_type: str
    data: Dict[str, Any]
    timestamp: float

    def to_json(self) -> str:
        return json.dumps({
            "device_uuid": self.device_uuid,
            "event": self.event_type,
            "data": self.data,
            "timestamp": self.timestamp
        })

@dataclass
class ClientMessage:
    method: str
    params: Dict[str, Any]
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ClientMessage':
        return cls(
            method=data.get("method", ""),
            params=data.get("params", {})
        )