import json
from typing import Any, Literal

from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langgraph.graph import END, START, StateGraph

from agent.lc_tools import TOOL_MAP
from agent.state import AgentState
from llm.config import MAX_TOOL_CALLS
from llm.groq_client import get_llm

SYSTEM_PROMPT = """You are a helpful agent with exactly three tools:
- TextProcessorTool: uppercase, lowercase, or word count on a given text.
- CalculatorTool: basic arithmetic with +, -, *, /. Pass a simple expression like "15 * 4".
- WeatherMockTool: mock weather for a city (not live data).

Rules:
- Call a tool when the user needs text processing, math, or weather.
- You may use more than one tool (or the same tool twice) if the request needs multiple steps.
- After tools have produced the answer, reply with a short final message. Do not call more tools.
- If the user asks for anything else (jokes, news, web search, general chat, etc.), do NOT call a tool. Reply in one or two polite sentences that you can only help with text processing, basic math, or mock weather. Suggest an example such as "weather in Toronto" or "what's 15 * 4".
"""

OUT_OF_SCOPE_FALLBACK = (
    "I can only help with text processing (upper/lowercase, word count), "
    "basic math, or mock weather for a city. Try “weather in Toronto” or “what’s 15 * 4”."
)

SKIPPED_TOOL_CONTENT = (
    "Skipped: this demo runs one tool per step. You may call this tool on a later turn if needed."
)


def _next_step(trace: list) -> int:
    return len(trace) + 1


def _append_trace(trace: list, message: str) -> list:
    updated = list(trace)
    updated.append({"step": _next_step(updated), "message": message})
    return updated


def _text_content(response) -> str:
    content = getattr(response, "content", None)
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict) and block.get("text"):
                parts.append(str(block["text"]))
        return "".join(parts).strip()
    return str(content or "").strip()


def _format_result(result: Any) -> str:
    if isinstance(result, (dict, list)):
        return json.dumps(result, ensure_ascii=False)
    return str(result)


def _param_summary(params: dict) -> str:
    if not params:
        return ""
    return ", ".join(f"{k}: {v}" for k, v in params.items())


def _build_final_result(state: AgentState, summary: str) -> Any:
    results = state.get("tool_results") or []
    if not results:
        return summary or OUT_OF_SCOPE_FALLBACK
    if len(results) == 1:
        return results[0]["result"]
    return {
        "steps": results,
        "summary": summary or _format_result(results[-1]["result"]),
    }


def reason_node(state: AgentState) -> dict:
    trace = list(state.get("trace") or [])

    if state.get("step_count", 0) >= MAX_TOOL_CALLS:
        last = state.get("last_result")
        summary = (
            _format_result(last)
            if last is not None
            else OUT_OF_SCOPE_FALLBACK
        )
        trace = _append_trace(
            trace,
            f"Reached the maximum of {MAX_TOOL_CALLS} tool calls — finishing.",
        )
        final = _build_final_result(state, summary)
        trace = _append_trace(trace, f"Finished → {final}")
        return {
            "pending_tool": None,
            "pending_params": {},
            "pending_tool_call_id": None,
            "skipped_tool_messages": [],
            "trace": trace,
            "final_result": final,
        }

    llm = get_llm()
    response = llm.invoke(state["messages"])
    messages = list(state["messages"]) + [response]
    tool_calls = getattr(response, "tool_calls", None) or []

    if tool_calls:
        first = tool_calls[0]
        args = first.get("args") or {}
        summary = _param_summary(args)
        selected = first["name"] if not summary else f"{first['name']} ({summary})"
        trace = _append_trace(trace, f"Selected tool: {selected}")

        skipped = []
        for extra in tool_calls[1:]:
            skipped.append(
                ToolMessage(
                    content=SKIPPED_TOOL_CONTENT,
                    tool_call_id=extra.get("id") or extra.get("name") or "skipped",
                )
            )
            trace = _append_trace(
                trace,
                f"Deferred extra tool call: {extra.get('name')} (one tool per step)",
            )

        return {
            "messages": messages,
            "pending_tool": first["name"],
            "pending_params": args,
            "pending_tool_call_id": first.get("id") or "call_0",
            "skipped_tool_messages": skipped,
            "trace": trace,
        }

    content = _text_content(response) or OUT_OF_SCOPE_FALLBACK
    if not (state.get("tool_results") or []):
        trace = _append_trace(
            trace, "No matching tool — replied without calling a tool"
        )
    final = _build_final_result(state, content)
    if not (state.get("tool_results") or []):
        final = content
    trace = _append_trace(trace, f"Finished → {final}")
    return {
        "messages": messages,
        "pending_tool": None,
        "pending_params": {},
        "pending_tool_call_id": None,
        "skipped_tool_messages": [],
        "trace": trace,
        "final_result": final,
    }


def execute_tool_node(state: AgentState) -> dict:
    name = state.get("pending_tool") or ""
    params = dict(state.get("pending_params") or {})
    call_id = state.get("pending_tool_call_id") or "call_0"
    trace = list(state.get("trace") or [])
    messages = list(state["messages"])
    tool_results = list(state.get("tool_results") or [])

    tool = TOOL_MAP.get(name)
    if tool is None:
        result = (
            f"I could not run “{name}”. I only have text processing, "
            "basic math, and mock weather."
        )
        trace = _append_trace(trace, result)
    else:
        try:
            result = tool.execute(params)
            trace = _append_trace(trace, f"Executed {name} → {result}")
        except Exception as exc:
            result = (
                f"I couldn’t complete that {name} request ({exc}). "
                "Please try a simpler instruction."
            )
            trace = _append_trace(trace, result)

    tool_results.append({"tool": name, "params": params, "result": result})
    messages.append(ToolMessage(content=_format_result(result), tool_call_id=call_id))
    messages.extend(state.get("skipped_tool_messages") or [])

    return {
        "messages": messages,
        "pending_tool": None,
        "pending_params": {},
        "pending_tool_call_id": None,
        "skipped_tool_messages": [],
        "step_count": state.get("step_count", 0) + 1,
        "tool_results": tool_results,
        "last_result": result,
        "last_tool": name,
        "last_params": params,
        "trace": trace,
    }


def route_after_reason(state: AgentState) -> Literal["execute_tool", "end"]:
    if state.get("pending_tool"):
        return "execute_tool"
    return "end"


def build_graph():
    graph = StateGraph(AgentState)
    graph.add_node("reason", reason_node)
    graph.add_node("execute_tool", execute_tool_node)
    graph.add_edge(START, "reason")
    graph.add_conditional_edges(
        "reason",
        route_after_reason,
        {"execute_tool": "execute_tool", "end": END},
    )
    graph.add_edge("execute_tool", "reason")
    return graph.compile()


_app = None


def get_graph():
    global _app
    if _app is None:
        _app = build_graph()
    return _app


def run_agent(instruction: str) -> dict:
    initial: AgentState = {
        "instruction": instruction,
        "messages": [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=instruction),
        ],
        "pending_tool": None,
        "pending_params": {},
        "pending_tool_call_id": None,
        "skipped_tool_messages": [],
        "step_count": 0,
        "tool_results": [],
        "last_result": None,
        "last_tool": "none",
        "last_params": {},
        "trace": [
            {"step": 1, "message": f'Received the input "{instruction}"'},
        ],
        "final_result": None,
    }
    return get_graph().invoke(initial)
