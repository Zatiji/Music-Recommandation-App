from groq import Groq
import os

_API_KEY = os.getenv("GROQ_API_KEY")
if not _API_KEY:
    raise RuntimeError("Please set the GROQ_API_KEY environment variable")

_client = Groq(api_key=_API_KEY)
messages = []
CLIENT = "user"
CHATBOT = "assistant"

def generateAiResponse(message: str) -> str:
    if (len(messages) >= 8):
        summarizeConversation()

    messages.append({"role": CLIENT, "content": message})

    completion = _client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=messages,
        temperature=1,
        max_completion_tokens=1024,
        top_p=1,
        stream=False, # TO CHANGE FOR LATER
        stop=None,
    )

    # response_text = ""
    # for chunk in completion:
    #     delta = chunk.choices[0].delta.content
    #     if delta:
    #         response_text += delta

    awnser = completion.choices[0].message.content
    messages.append({"role": CHATBOT, "content": awnser})
    print(messages)
    return awnser

def summarizeConversation():
    context = list(messages)
    summarizePrompt = {
        "role": CLIENT,
        "content": (
            "Please read the full conversation history and produce a single, concise summary "
            "that highlights the user's key information, goals, and preferences "
            "Limit it to 2-3 sentences, include only essential facts, and avoid any irrelevant details."
        )
    }

    completion = _client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=context + [summarizePrompt],
        temperature=1,
        max_completion_tokens=1024,
        top_p=1,
        stream=False,
        stop=None,
    )
    summary = completion.choices[0].message.content

    messages.clear()
    messages.append({"role": CLIENT, "content": summary})