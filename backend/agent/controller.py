from agent.router import select_tool
from storage import history_store


def handle_task(instruction: str) -> dict:
    trace: list[dict] = []

    trace.append(
        {"step": 1, "message": f'Received the input "{instruction}"'}
    )

    tool, params = select_tool(instruction)
    param_summary = ", ".join(f"{k}: {v}" for k, v in params.items())
    trace.append(
        {
            "step": 2,
            "message": f"Selected tool: {tool.name} ({param_summary})",
        }
    )

    result = tool.execute(params)
    trace.append(
        {"step": 3, "message": f"Executed {tool.name} → {result}"}
    )

    record = history_store.save(
        instruction=instruction,
        tool=tool.name,
        params=params,
        result=result,
        trace=trace,
    )

    return {
        "task_id": record["id"],
        "result": result,
        "trace": trace,
    }
