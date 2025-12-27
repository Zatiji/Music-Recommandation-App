from flask import Blueprint, request, Response, stream_with_context

from app.services.llm import stream_ai_response
import json

generate_response = Blueprint("generate_response", __name__)

@generate_response.route("/generate-response", methods=["OPTIONS", "POST"])
def handle_generate_response():
    if request.method == "OPTIONS":
        return "", 204
    
    data = request.get_json(silent=True) or {}
    user_message = data.get("message", "")
    if not user_message:
        return Response('Missing "message"', status=400)

    # Create generator for SSE
    @stream_with_context
    def generate():
        # Send each chunk as JSON: {"delta": "..."}
        for chunk in stream_ai_response(user_message):
            yield f"data: {json.dumps({'delta': chunk})}\n\n"
        # Signal completion
        yield f"data: {json.dumps({'done': True})}\n\n"

    return Response(generate(), mimetype="text/event-stream")
