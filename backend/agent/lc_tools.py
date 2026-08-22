from typing import Literal

from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

from tools.calculator import CalculatorTool
from tools.text_processor import TextProcessorTool
from tools.weather_mock import WeatherMockTool

text_processor = TextProcessorTool()
calculator = CalculatorTool()
weather_mock = WeatherMockTool()

TOOL_MAP = {
    text_processor.name: text_processor,
    calculator.name: calculator,
    weather_mock.name: weather_mock,
}


class TextProcessorArgs(BaseModel):
    operation: Literal["uppercase", "lowercase", "wordcount"] = Field(
        description="uppercase, lowercase, or wordcount"
    )
    text: str = Field(description="The text to transform or count")


class CalculatorArgs(BaseModel):
    expression: str = Field(
        description='A simple arithmetic expression using +, -, *, / such as "15 * 4"'
    )


class WeatherArgs(BaseModel):
    city: str = Field(description="City name, for example Toronto")


def _run_text_processor(operation: str, text: str) -> str:
    return str(text_processor.execute({"operation": operation, "text": text}))


def _run_calculator(expression: str) -> str:
    return str(calculator.execute({"expression": expression}))


def _run_weather(city: str) -> str:
    return str(weather_mock.execute({"city": city}))


LANGCHAIN_TOOLS = [
    StructuredTool.from_function(
        name=text_processor.name,
        description=(
            "Process text: convert to uppercase, convert to lowercase, "
            "or count words."
        ),
        func=_run_text_processor,
        args_schema=TextProcessorArgs,
    ),
    StructuredTool.from_function(
        name=calculator.name,
        description="Evaluate basic arithmetic: addition, subtraction, multiplication, division.",
        func=_run_calculator,
        args_schema=CalculatorArgs,
    ),
    StructuredTool.from_function(
        name=weather_mock.name,
        description="Return mock weather (temperature and condition) for a given city. No live weather data.",
        func=_run_weather,
        args_schema=WeatherArgs,
    ),
]
