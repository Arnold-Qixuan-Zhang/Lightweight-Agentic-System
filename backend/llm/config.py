import os
from pathlib import Path

from dotenv import load_dotenv

_BACKEND_DIR = Path(__file__).resolve().parent.parent
load_dotenv(_BACKEND_DIR / ".env")
load_dotenv(_BACKEND_DIR.parent / ".env")

DEFAULT_MODEL = "openai/gpt-oss-20b"
MAX_TOOL_CALLS = 3


class GroqConfigError(RuntimeError):
    pass


def get_groq_api_key() -> str:
    key = os.getenv("GROQ_API_KEY", "").strip()
    if not key:
        raise GroqConfigError(
            "GROQ_API_KEY is not set. Copy backend/.env.example to backend/.env "
            "and add your Groq API key."
        )
    return key


def get_groq_model() -> str:
    return os.getenv("GROQ_MODEL", DEFAULT_MODEL).strip() or DEFAULT_MODEL
