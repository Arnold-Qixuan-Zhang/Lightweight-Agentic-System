from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from agent.controller import handle_task
from models.schemas import HistoryRecord, TaskRequest, TaskResponse
from storage import history_store

app = FastAPI(title="Agentic AI Demo", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/tasks", response_model=TaskResponse)
def create_task(request: TaskRequest):
    try:
        return handle_task(request.instruction.strip())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/api/history", response_model=list[HistoryRecord])
def get_history(limit: int = 50):
    return history_store.list_recent(limit=limit)


@app.get("/api/history/export")
def export_history():
    history_store.export_all()
    history_file = Path(__file__).resolve().parent / "data" / "history.json"
    if not history_file.exists():
        history_file.parent.mkdir(parents=True, exist_ok=True)
        history_file.write_text("[]", encoding="utf-8")
    return FileResponse(
        path=history_file,
        media_type="application/json",
        filename="history.json",
    )


@app.get("/api/health")
def health_check():
    return {"status": "ok"}
