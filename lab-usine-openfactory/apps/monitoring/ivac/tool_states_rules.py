class ToolStateRules:
    """Maps tool states to a condition tag and message."""

    def evaluate(self, states: dict[str, str | int | float]) -> tuple[str, str]:
        values = states.values()
        if any(s == "UNAVAILABLE" for s in values):
            return "WARNING", "At least one tool is UNAVAILABLE"
        if any(s == "OFF" for s in values):
            return "NORMAL", "No more than one connected tool is powered ON"
        return "FAULT", "More than one connected tool is powered ON"
