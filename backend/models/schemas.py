from typing import Any

from pydantic import BaseModel, Field


class TaskRequest(BaseModel):
    instruction: str = Field(..., min_length=1)


class TraceStep(BaseModel):
    step: int
    message: str


class TaskResponse(BaseModel):
    task_id: str
    result: Any
    trace: list[TraceStep]


class HistoryRecord(BaseModel):
    id: str
    instruction: str
    tool: str
    params: dict
    result: Any
    trace: list[TraceStep]
    created_at: str
