import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
HISTORY_FILE = DATA_DIR / "history.json"


def _ensure_data_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not HISTORY_FILE.exists():
        HISTORY_FILE.write_text("[]", encoding="utf-8")


def _load() -> list[dict]:
    _ensure_data_dir()
    with HISTORY_FILE.open(encoding="utf-8") as f:
        return json.load(f)


def _write(history: list[dict]) -> None:
    _ensure_data_dir()
    with HISTORY_FILE.open("w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)


def save(
    instruction: str,
    tool: str,
    params: dict,
    result,
    trace: list[dict],
) -> dict:
    record = {
        "id": str(uuid.uuid4()),
        "instruction": instruction,
        "tool": tool,
        "params": params,
        "result": result,
        "trace": trace,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    history = _load()
    history.append(record)
    _write(history)
    return record


def list_recent(limit: int = 50) -> list[dict]:
    history = _load()
    return list(reversed(history[-limit:]))


def export_all() -> list[dict]:
    return _load()
