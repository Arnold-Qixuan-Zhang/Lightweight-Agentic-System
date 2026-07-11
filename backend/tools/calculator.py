import ast
import operator
import re

from tools.base import BaseTool


class CalculatorTool(BaseTool):
    name = "CalculatorTool"

    _MATH_PATTERN = re.compile(
        r"(\d+\.?\d*)\s*([+\-*/])\s*(\d+\.?\d*)|"
        r"\b(calculate|compute|add|subtract|multiply|divide)\b",
        re.IGNORECASE,
    )

    _OPERATORS = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
    }

    def can_handle(self, instruction: str) -> bool:
        return bool(self._MATH_PATTERN.search(instruction))

    def parse(self, instruction: str) -> dict:
        match = re.search(
            r"(\d+\.?\d*)\s*([+\-*/])\s*(\d+\.?\d*)", instruction
        )
        if match:
            left, op, right = match.groups()
            return {"expression": f"{left} {op} {right}"}

        numbers = re.findall(r"\d+\.?\d*", instruction)
        lowered = instruction.lower()
        if len(numbers) >= 2:
            if "add" in lowered or "plus" in lowered or "+" in instruction:
                return {"expression": f"{numbers[0]} + {numbers[1]}"}
            if "subtract" in lowered or "minus" in lowered or "-" in instruction:
                return {"expression": f"{numbers[0]} - {numbers[1]}"}
            if "multiply" in lowered or "times" in lowered or "*" in instruction:
                return {"expression": f"{numbers[0]} * {numbers[1]}"}
            if "divide" in lowered or "/" in instruction:
                return {"expression": f"{numbers[0]} / {numbers[1]}"}

        return {"expression": instruction}

    def execute(self, params: dict) -> float | int:
        expression = params["expression"]
        return self._safe_eval(expression)

    def _safe_eval(self, expression: str) -> float | int:
        node = ast.parse(expression, mode="eval").body
        return self._eval_node(node)

    def _eval_node(self, node: ast.AST) -> float | int:
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        if isinstance(node, ast.BinOp):
            op_type = type(node.op)
            if op_type not in self._OPERATORS:
                raise ValueError(f"Unsupported operator: {op_type}")
            left = self._eval_node(node.left)
            right = self._eval_node(node.right)
            return self._OPERATORS[op_type](left, right)
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
            return -self._eval_node(node.operand)
        raise ValueError(f"Unsupported expression node: {type(node).__name__}")
