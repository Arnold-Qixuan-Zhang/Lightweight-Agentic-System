import re

from tools.base import BaseTool


class TextProcessorTool(BaseTool):
    name = "TextProcessorTool"

    _KEYWORDS = re.compile(
        r"\b(uppercase|upper case|lowercase|lower case|word count|count words)\b",
        re.IGNORECASE,
    )

    def can_handle(self, instruction: str) -> bool:
        return bool(self._KEYWORDS.search(instruction))

    def parse(self, instruction: str) -> dict:
        lowered = instruction.lower()
        if "uppercase" in lowered or "upper case" in lowered:
            operation = "uppercase"
        elif "lowercase" in lowered or "lower case" in lowered:
            operation = "lowercase"
        else:
            operation = "wordcount"

        text = instruction
        for phrase in (
            "convert",
            "to uppercase",
            "to upper case",
            "to lowercase",
            "to lower case",
            "word count",
            "count words",
            "count the words in",
            "in",
        ):
            text = re.sub(re.escape(phrase), "", text, flags=re.IGNORECASE)
        text = text.strip(" \"'.,!?")

        if not text:
            text = instruction

        return {"operation": operation, "text": text}

    def execute(self, params: dict) -> str | int:
        operation = params["operation"]
        text = params["text"]

        if operation == "uppercase":
            return text.upper()
        if operation == "lowercase":
            return text.lower()
        if operation == "wordcount":
            return len(text.split())
        raise ValueError("operation must be uppercase, lowercase, or wordcount")
