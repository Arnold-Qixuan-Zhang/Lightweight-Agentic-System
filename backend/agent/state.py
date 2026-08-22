from typing import Any, TypedDict


class AgentState(TypedDict):
    instruction: str
    messages: list
    pending_tool: str | None
    pending_params: dict
    pending_tool_call_id: str | None
    skipped_tool_messages: list
    step_count: int
    tool_results: list
    last_result: Any
    last_tool: str
    last_params: dict
    trace: list
    final_result: Any
