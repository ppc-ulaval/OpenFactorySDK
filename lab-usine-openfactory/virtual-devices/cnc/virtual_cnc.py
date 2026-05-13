import random


class Virtual_CNC:
    MAX_SPINDLE_SPEED = 25000
    MIN_SPINDLE_SPEED = 10000

    def __init__(self):
        self._spindle_speed = 0
        self._vacuum_status = "ACTIVE"

    def read_data(self) -> dict:
        self._spindle_speed = random.randint(
            self.MIN_SPINDLE_SPEED, self.MAX_SPINDLE_SPEED
        )

        if self._vacuum_status == "ACTIVE":
            self._vacuum_status = "INACTIVE"
        else:
            self._vacuum_status = "ACTIVE"

        return {
            "spindle_speed": self._spindle_speed,
            "vacuum_status": self._vacuum_status,
        }
