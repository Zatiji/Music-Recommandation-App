from dataclasses import dataclass, field
import os
from typing import Dict, Iterator, List

from groq import Groq

_API_KEY = os.getenv("GROQ_API_KEY")
if not _API_KEY:
    raise RuntimeError("Please set the GROQ_API_KEY environment variable")

_client = Groq(api_key=_API_KEY)

CLIENT = "user"
CHATBOT = "assistant"
SYSTEM = "system"

_SYSTEM_PROMPT = (
    "You are a music recommendation assistant. "
    "Ask concise questions when needed. "
    "When recommending tracks, explain why each fits the user's preferences."
)

_SUMMARY_PROMPT = (
    "Summarize the conversation focusing on the user's music tastes, dislikes, "
    "favorite artists/genres, energy/mood preferences, and goals. "
    "Return 2-3 sentences only."
)


@dataclass
class SessionState:
    messages: List[dict] = field(default_factory=list)
    summary: str = ""


_sessions: Dict[str, SessionState] = {}
_SUMMARY_TOKEN_LIMIT = 1700


def _estimateTokens(text: str) -> int:
    # Rough heuristic: ~4 characters per token for English text.
    return max(1, len(text) // 4)


def _estimateMessageTokens(messages: List[dict]) -> int:
    total = 0
    for message in messages:
        total += _estimateTokens(message.get("content", ""))
    return total


def _getSession(sessionId: str) -> SessionState:
    state = _sessions.get(sessionId)
    
    if state is None:
        state = SessionState()
        _sessions[sessionId] = state
        
    return state


def _buildMessages(state: SessionState, userMessage: str) -> List[dict]:
    messages = [{"role": SYSTEM, "content": _SYSTEM_PROMPT}]
    
    if state.summary:
        messages.append({"role": SYSTEM, "content": f"Summary so far: {state.summary}"})
        
    messages.extend(state.messages)
    messages.append({"role": CLIENT, "content": userMessage})
    return messages


def _summarizeSession(state: SessionState) -> None:
    if not state.messages:
        return
    
    messages = [{"role": SYSTEM, "content": _SUMMARY_PROMPT}] + state.messages
    
    completion = _client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=messages,
        temperature=0.3,
        max_completion_tokens=256,
        top_p=1,
        stream=False,
        stop=None,
    )
    
    summary = completion.choices[0].message.content
    state.summary = summary
    state.messages = []


def streamAiResponse(message: str, sessionId: str = "default") -> Iterator[str]:
    """
    Yields assistant text chunks as they arrive (for SSE).
    IMPORTANT: This is a synchronous generator; Flask will stream it.
    """
    state = _getSession(sessionId)
    pendingMessages = _buildMessages(state, message)
    
    if _estimateMessageTokens(pendingMessages) >= _SUMMARY_TOKEN_LIMIT:
        _summarizeSession(state)

    messages = _buildMessages(state, message)
    stream = _client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=messages,
        temperature=0.8,
        max_completion_tokens=1024,
        top_p=1,
        stream=True,
        stop=None,
    )

    fullText = []
    for chunk in stream:
        delta = chunk.choices[0].delta.content if chunk.choices and chunk.choices[0].delta else None
        if delta:
            fullText.append(delta)
            yield delta

    final = "".join(fullText) if fullText else ""
    state.messages.append({"role": CLIENT, "content": message})
    state.messages.append({"role": CHATBOT, "content": final})
