"""
config.py  – central constants, plus a rotating-key Gemini proxy that is API-
compatible with ChatGoogleGenerativeAI.  Nothing else in the repo must change.
"""
from __future__ import annotations
import itertools, threading, random, time
from typing import Any
from dotenv import load_dotenv
from pydantic import Field, ConfigDict
from pydantic import PrivateAttr
from app.core.config import _KEYS  # noqa: F401

from google.api_core.exceptions import ResourceExhausted
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.language_models.chat_models import BaseChatModel

from langchain_core.messages import BaseMessage
from langchain_core.tools import Tool
from typing import Sequence, Any
from langchain_core.messages import HumanMessage 
# ───────────────────────────────────────────────────────────────────────────────
# UI constants 
# ───────────────────────────────────────────────────────────────────────────────
load_dotenv()
PAGE_TITLE        = "Advanced RAG"
PAGE_ICON         = "🔎"
FILE_UPLOAD_PROMPT = "Upload your Text file here"
FILE_UPLOAD_TYPE   = ".txt"

# ───────────────────────────────────────────────────────────────────────────────
# Key-rotation setup
# ───────────────────────────────────────────────────────────────────────────────


random.shuffle(_KEYS)
_key_cycle = itertools.cycle(_KEYS)
_pool_lock = threading.Lock()      # thread-safe across Streamlit runners


def _next_key() -> str:
    with _pool_lock:
        return next(_key_cycle)


# ───────────────────────────────────────────────────────────────────────────────
# Rotating proxy class
# ───────────────────────────────────────────────────────────────────────────────
class RotatingGemini(BaseChatModel):
    """Proxy that creates a fresh ChatGoogleGenerativeAI per call, with key rotation."""
    model_name: str = Field(default="gemini-2.0-flash")
    temperature: float = Field(default=0.0)
    model_config = ConfigDict(extra="allow", arbitrary_types_allowed=True)
    tools: list = Field(default_factory=list)  # Add this line

    # OR, if you want it private and not part of the model schema:
    _tools: list = PrivateAttr(default_factory=list)

    def _generate(
        self,
        messages: list[BaseMessage] | str,
        stop: Any | None = None,
        run_manager=None,
        **kwargs: Any,
    ) -> Any:
        if isinstance(messages, str):
            messages = [HumanMessage(content=messages)]
        tried: set[str] = set()
        while len(tried) < len(_KEYS):
            key = _next_key()
            if key in tried:          # already failed with this one
                continue
            tried.add(key)
            llm = ChatGoogleGenerativeAI(
                model=self.model_name,
                temperature=self.temperature,
                google_api_key=key,
                # response_format={"type": "json_object"},
                **kwargs,
            )

            try:
                # delegate to the *real* model’s _generate()
                return llm._generate(messages, stop=stop, run_manager=run_manager, **kwargs)
            except ResourceExhausted as e:
                if "RATE_LIMIT" in str(e) or "quota" in str(e).lower():
                    delay = getattr(e, "retry_delay", 2)
                    time.sleep(delay.seconds if hasattr(delay, "seconds") else delay if isinstance(delay, (int, float)) else 2)
                    continue
                raise

        raise RuntimeError("All Gemini API keys exhausted for the current window.")


    # ---- plumbing so | operator & .bind keep working ------------------------
    @property
    def _llm_type(self) -> str:  # for LangChain internal checks
        return "rotating-gemini"

    def bind(self, **kwargs):        # keeps `.bind()` working
        return RotatingGemini(
            model_name=kwargs.get("model_name", self.model_name),
            temperature=kwargs.get("temperature", self.temperature),
        )


    # helper to make the object printable
    def __repr__(self):
        return f"<RotatingGemini model={self.model_name} active_key=***{_next_key()[-6:]}>"



# ───────────────────────────────────────────────────────────────────────────────
# Public symbols – names unchanged, rest of repo keeps working
# ───────────────────────────────────────────────────────────────────────────────
MAIN_LLM   = RotatingGemini(model_name = "gemini-2.0-flash")

GRAPH_LLM  = RotatingGemini(model_name = "gemini-2.5-flash")
