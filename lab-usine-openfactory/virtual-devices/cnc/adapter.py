import time
import random
import os
from mtcadapter.mtcdevices import MTCDevice
from mtcadapter.adapters import MTCAdapter

class Virtual_CNC(MTCDevice):
    """
    Virtual adapter for iVAC Tool Plus, which detects current on any electrical powered device.
    """

    MIN_TOGGLE_TIME = float(os.environ.get("MIN_TOGGLE_TIME", 5))
    MAX_TOGGLE_TIME = float(os.environ.get("MAX_TOGGLE_TIME", 10))
    MAX_SPINDLE_SPEED = 25000
    MIN_SPINDLE_SPEED = 10000

    def __init__(self):
        self._spindle_speed = 0
        self._vacuum_status = 'ACTIVE'

    def read_data(self) -> dict:
        """Read and toggle tool states with random delay"""

        time.sleep(round(random.uniform(self.MIN_TOGGLE_TIME, self.MAX_TOGGLE_TIME), 2))
        self._spindle_speed = random.randint(self.MIN_SPINDLE_SPEED, self.MAX_SPINDLE_SPEED)

        if self._vacuum_status == 'ACTIVE':
            self._vacuum_status = 'INACTIVE'
        else:
            self._vacuum_status = 'ACTIVE'

        return {
            'spindle_speed': self._spindle_speed,
            'vacuum_status': self._vacuum_status
        }


class Virtual_CNCAdapter(MTCAdapter):
    device_class = Virtual_CNC
    adapter_port = 7879

    def __init__(self):
        super().__init__()
        self.opcua_server = None
        self.device = self.device_class()

    def run(self):
        """Start both MTConnect server"""
        print("Starting MTConnect adapter...")
        super().run()


def main():
    adapter = Virtual_CNCAdapter()
    adapter.run()


if __name__ == "__main__":
    main()
