from langchain_groq import ChatGroq

from agent.lc_tools import LANGCHAIN_TOOLS
from llm.config import get_groq_api_key, get_groq_model

_llm = None


def get_llm():
    global _llm
    if _llm is None:
        _llm = ChatGroq(
            api_key=get_groq_api_key(),
            model=get_groq_model(),
            temperature=0,
            max_tokens=400,
        ).bind_tools(LANGCHAIN_TOOLS)
    return _llm
