class VirtualIVAC:
    LED_MODES = ["NORMAL", "FAULT", "WARNING"]

    def __init__(self):
        self._tool_states = {
            "A1ToolPlus": "OFF",
            "A2ToolPlus": "OFF",
            "A3ToolPlus": "OFF",
        }
        self._gates_states = {
            "A1BlastGate": "OPEN",
            "A2BlastGate": "OPEN",
            "A3BlastGate": "CLOSED",
        }
        self._simulation_mode = False
        self._buzzer_status = "WARNING"

        self._led_states = {state: False for state in self.LED_MODES}
        self._current_led_state = "WARNING"
        self._led_states[self._current_led_state] = True

    def set_led_state(self, state: str) -> bool:
        """Set the LED mode (NORMAL/FAULT/WARNING)"""
        state = state.upper()
        if state not in self.LED_MODES:
            return False

        for m in self._led_states:
            self._led_states[m] = False

        self._led_states[state] = True
        self._current_led_state = state
        print(f"LED state changed to: {state}")
        return True

    def set_simulation_mode(self, value: bool):
        self._simulation_mode = value
        print(f"Simulation mode {'activated' if value else 'deactivated'}")

    def set_buzzer_status(self, status: str):
        self._buzzer_status = status.upper()
        print(f"Buzzer status set to: {self._buzzer_status}")

    def read_data(self) -> dict:
        for tool in self._tool_states:
            self._tool_states[tool] = (
                "ON" if self._tool_states[tool] == "OFF" else "OFF"
            )
            self._gates_states[tool[:-8] + "BlastGate"] = (
                "CLOSED" if self._tool_states[tool] == "OFF" else "OPEN"
            )

        return {
            "A1ToolPlus": self._tool_states["A1ToolPlus"],
            "A2ToolPlus": self._tool_states["A2ToolPlus"],
            "A3ToolPlus": self._tool_states["A3ToolPlus"],
            "A1BlastGate": self._gates_states["A1BlastGate"],
            "A2BlastGate": self._gates_states["A2BlastGate"],
            "A3BlastGate": self._gates_states["A3BlastGate"],
            "Buzzer": self._buzzer_status,  # TODO buzzer state is always delayed (will be the status of previous tool state)...
        }
