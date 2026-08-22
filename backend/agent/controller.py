from agent.graph import run_agent
from storage import history_store


def handle_task(instruction: str) -> dict:
    state = run_agent(instruction)
    tool_results = state.get("tool_results") or []

    if not tool_results:
        tool_name = "none"
        params: dict = {}
    elif len(tool_results) == 1:
        tool_name = tool_results[0]["tool"]
        params = tool_results[0]["params"]
    else:
        tool_name = "multiple"
        params = {"calls": tool_results}

    record = history_store.save(
        instruction=instruction,
        tool=tool_name,
        params=params,
        result=state["final_result"],
        trace=state["trace"],
    )

    return {
        "task_id": record["id"],
        "result": state["final_result"],
        "trace": state["trace"],
    }
