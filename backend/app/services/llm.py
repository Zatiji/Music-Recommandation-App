from dataclasses import dataclass, field
import json
import os
from typing import Dict, Iterator, List, Optional

from groq import Groq

_API_KEY = os.getenv("GROQ_API_KEY")
if not _API_KEY:
    raise RuntimeError("Please set the GROQ_API_KEY environment variable")

_client = Groq(api_key=_API_KEY)

CLIENT = "user"
CHATBOT = "assistant"
SYSTEM = "system"

_INTENT_PROMPT = (
    "You are a music recommendation assistant. Your personality is chill, helpful, "
    "and knowledgeable, like a friend recommending music.\n\n"
    "### ROLE: INTENT EXTRACTOR\n"
    "When the user asks for music, DO NOT reply with text. DO NOT hallucinate songs.\n"
    "Instead, analyze their request and output a STRICT JSON object to trigger the music database.\n\n"
    "Classify as intent \"recommendation\" whenever the user asks for songs, music, "
    "artists, albums, genres, vibes, moods, or anything like \"I need songs\" or "
    "\"recommend me\".\n\n"
    "Format:\n"
    '{\n  "intent": "recommendation" | "chat",\n'
    '  "search_type": "artist" | "track" | "tag" | "none",\n'
    '  "query": "string",\n  "user_mood": "string"\n}\n'
    "\nExamples:\n"
    'User: "I need songs that have a lofi vibe"\n'
    'You: {"intent": "recommendation", "search_type": "tag", "query": "lofi", "user_mood": "chill"}\n'
    'User: "Hello, how are you?"\n'
    'You: {"intent": "chat", "search_type": "none", "query": "", "user_mood": ""}\n'
)

_PRESENTER_PROMPT = (
    "You are a music recommendation assistant. Your personality is chill, helpful, "
    "and knowledgeable, like a friend recommending music.\n\n"
    "### ROLE: PRESENTER\n"
    "You will receive raw data from the Last.fm API (a list of artists/tracks).\n"
    "Your job is to present these recommendations to the user in your chill persona.\n"
    "- Explain briefly why these fit the user's request.\n"
    "- If the user asks \"Why?\", use the context of the genre/style to explain.\n"
    "- Keep it concise and engaging.\n"
    "Format your response in Markdown (use short lists, bold labels, and line breaks).\n"
    "Never output JSON."
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


def _buildBaseMessages(state: SessionState, systemPrompt: str) -> List[dict]:
    messages = [{"role": SYSTEM, "content": systemPrompt}]
    
    if state.summary:
        messages.append({"role": SYSTEM, "content": f"Summary so far: {state.summary}"})
        
    messages.extend(state.messages)
    return messages


def _buildMessages(
    state: SessionState,
    userMessage: str,
    systemPrompt: str,
) -> List[dict]:
    messages = _buildBaseMessages(state, systemPrompt)
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


def extractIntent(message: str, sessionId: str = "default") -> dict:
    state = _getSession(sessionId)
    pendingMessages = _buildMessages(state, message, _INTENT_PROMPT)
    
    if _estimateMessageTokens(pendingMessages) >= _SUMMARY_TOKEN_LIMIT:
        _summarizeSession(state)

    messages = _buildMessages(state, message, _INTENT_PROMPT)
    completion = _client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=messages,
        temperature=0.2,
        max_completion_tokens=256,
        top_p=1,
        stream=False,
        stop=None,
    )

    content = completion.choices[0].message.content or ""
    try:
        parsed = json.loads(content)
    except json.JSONDecodeError:
        return {"intent": "chat", "search_type": "none", "query": "", "user_mood": ""}

    return {
        "intent": parsed.get("intent", "chat"),
        "search_type": parsed.get("search_type", "none"),
        "query": parsed.get("query", ""),
        "user_mood": parsed.get("user_mood", ""),
    }


def streamPresenterResponse(
    message: str,
    sessionId: str = "default",
    system_data: Optional[str] = None,
) -> Iterator[str]:
    """
    Yields assistant text chunks as they arrive (for SSE).
    IMPORTANT: This is a synchronous generator; Flask will stream it.
    """
    state = _getSession(sessionId)
    pendingMessages = _buildMessages(state, message, _PRESENTER_PROMPT)
    
    if _estimateMessageTokens(pendingMessages) >= _SUMMARY_TOKEN_LIMIT:
        _summarizeSession(state)

    messages = _buildMessages(state, message, _PRESENTER_PROMPT)
    if system_data:
        messages.append({"role": SYSTEM, "content": system_data})
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


def streamAiResponse(message: str, sessionId: str = "default") -> Iterator[str]:
    return streamPresenterResponse(message, sessionId=sessionId)
