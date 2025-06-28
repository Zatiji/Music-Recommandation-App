from flask import Blueprint, request, jsonify
from LLM.ai import generateAiResponse

generate_response = Blueprint('generate_response', __name__)

@generate_response.route("/generate-response", methods=["OPTIONS", "POST"])
def handle_generate_response():
    if request.method == "OPTIONS":
        return '', 204
    
    data = request.get_json(silent=True) or {}
    user_message = data.get("message", "")
    if not user_message:
        return jsonify({"error": "Missing 'message' in request body"}), 400

    response = generateAiResponse(user_message)
    
    # data = request.json
    # message = data.get("message", "")
    # response = f"Tu as dit : {message}"
    return jsonify({"response": response})