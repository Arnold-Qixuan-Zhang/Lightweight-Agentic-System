import re

from tools.base import BaseTool


class WeatherMockTool(BaseTool):
    name = "WeatherMockTool"

    _WEATHER_DATA = {
        "toronto": {"temp": "22°C", "condition": "Partly cloudy"},
        "vancouver": {"temp": "18°C", "condition": "Rainy"},
        "montreal": {"temp": "20°C", "condition": "Sunny"},
        "calgary": {"temp": "15°C", "condition": "Windy"},
        "ottawa": {"temp": "19°C", "condition": "Overcast"},
        "new york": {"temp": "25°C", "condition": "Humid"},
        "london": {"temp": "16°C", "condition": "Foggy"},
        "paris": {"temp": "21°C", "condition": "Clear"},
    }

    _WEATHER_PATTERN = re.compile(
        r"\b(weather|temperature|forecast)\b", re.IGNORECASE
    )

    def can_handle(self, instruction: str) -> bool:
        return bool(self._WEATHER_PATTERN.search(instruction))

    def parse(self, instruction: str) -> dict:
        match = re.search(
            r"(?:weather|temperature|forecast)\s+(?:in|for|at)\s+([a-zA-Z\s]+)",
            instruction,
            re.IGNORECASE,
        )
        if match:
            city = match.group(1).strip(" .?!")
            return {"city": city}

        match = re.search(
            r"(?:in|for|at)\s+([a-zA-Z\s]+?)(?:\s*\?|$)",
            instruction,
            re.IGNORECASE,
        )
        if match:
            return {"city": match.group(1).strip(" .?!")}

        return {"city": "Unknown City"}

    def execute(self, params: dict) -> dict:
        city = params["city"]
        key = city.lower().strip()
        weather = self._WEATHER_DATA.get(
            key, {"temp": "20°C", "condition": "Mild"}
        )
        return {
            "city": city.title(),
            "temperature": weather["temp"],
            "condition": weather["condition"],
        }
