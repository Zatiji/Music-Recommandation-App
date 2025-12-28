from flask import Blueprint, request, Response, stream_with_context

from app.services.LLM import streamAiResponse
import json

generateResponse = Blueprint("generate_response", __name__)

@generateResponse.route("/generate-response", methods=["OPTIONS", "POST"])
def handleGenerateResponse():
    if request.method == "OPTIONS":
        return "", 204
    
    data = request.get_json(silent=True) or {}
    user_message = data.get("message", "")
    session_id = data.get("session_id", "default")
    if not user_message:
        return Response('Missing "message"', status=400)

    # Create generator for SSE
    @stream_with_context
    def generate():
        # Send each chunk as JSON: {"delta": "..."}
        for chunk in streamAiResponse(user_message, sessionId=session_id):
            yield f"data: {json.dumps({'delta': chunk})}\n\n"
        # Signal completion
        yield f"data: {json.dumps({'done': True})}\n\n"

    return Response(generate(), mimetype="text/event-stream")
