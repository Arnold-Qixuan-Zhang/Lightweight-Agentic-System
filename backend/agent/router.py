from tools.calculator import CalculatorTool
from tools.text_processor import TextProcessorTool
from tools.weather_mock import WeatherMockTool
from tools.base import BaseTool

_weather_tool = WeatherMockTool()
_calculator_tool = CalculatorTool()
_text_tool = TextProcessorTool()

_TOOLS: list[BaseTool] = [_weather_tool, _calculator_tool, _text_tool]


def select_tool(instruction: str) -> tuple[BaseTool, dict]:
    for tool in _TOOLS:
        if tool.can_handle(instruction):
            return tool, tool.parse(instruction)
    raise ValueError(
        "Could not determine an appropriate tool for this instruction. "
        "Try asking about weather, math, or text processing."
    )
