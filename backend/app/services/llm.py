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
   "You are a strict intent classification engine. Your ONLY job is to output a valid JSON object.\n"
    "Identify if the user wants music recommendations or is just chatting.\n\n"
    "### RULES\n"
    "1. Output RAW JSON only. Do NOT use Markdown code blocks (no ```json).\n"
    "2. If the user mentions a specific artist/song, set search_type to 'artist' or 'track'.\n"
    "3. If the user mentions a vibe/mood/genre (e.g. 'chill', 'rock', 'workout'), set search_type to 'tag'.\n"
    "4. If the user asks for recommendations generally without details, set search_type to 'none'.\n\n"
    "### SCHEMA\n"
    '{"intent": "recommendation"|"chat", "search_type": "artist"|"track"|"tag"|"none", "query": "string", "user_mood": "string"}\n\n'
    "### EXAMPLES\n"
    'User: "I need songs that have a lofi vibe"\n'
    'You: {"intent": "recommendation", "search_type": "tag", "query": "lofi", "user_mood": "chill"}\n'
    'User: "I love Daft Punk, anything similar?"\n'
    'You: {"intent": "recommendation", "search_type": "artist", "query": "Daft Punk", "user_mood": ""}\n\n'
    'User: "Find me the song Yesterday"\n'
    'You: {"intent": "recommendation", "search_type": "track", "query": "Yesterday", "user_mood": ""}\n\n'
    'User: "Suggest me some music"\n'
    'You: {"intent": "recommendation", "search_type": "none", "query": "", "user_mood": ""}\n\n'
    'User: "How are you doing?"\n'
    'You: {"intent": "chat", "search_type": "none", "query": "", "user_mood": ""}'
)

_PRESENTER_PROMPT = (
    "You are a music recommendation assistant. Persona: A helpful, slightly sarcastic, "
    "funny Gen Z teenager who takes the music seriously but not themselves.\n\n"
    "### INSTRUCTIONS\n"
    "You will receive raw music data. Present it to the user nicely.\n"
    "1. **USE MARKDOWN**: Use bolding (**text**) for artist/song names and bullet points (-) for lists.\n"
    "2. Explain briefly why these tracks fit the vibe.\n"
    "3. Keep it short. Don't write a novel.\n"
    "4. If you mention where the data came from, refer to it as \"my phone\" "
    "(e.g., \"I looked it up on my phone and here's what I can show you\").\n\n"
    "### FORMATTING EXAMPLE\n"
    "Here is what I found for you:\n"
    "- **Song Name** by **Artist**: Because it matches your moody vibe.\n"
    "- **Another Song** by **Artist**: Total banger for this genre.\n\n"
    "Now respond to the user:"
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
        temperature=0.0,
        max_completion_tokens=128,
        top_p=1,
        stream=False,
        stop=None,
    )

    content = completion.choices[0].message.content or ""
    content = content.replace("```json", "").replace("```", "").strip()
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
