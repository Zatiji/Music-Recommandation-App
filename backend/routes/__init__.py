from flask import Flask
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    CORS(
      app,
      resources={r"/*": {"origins": "http://localhost:5173"}},
      supports_credentials=True
    )
        
    from .routes import generate_response
    app.register_blueprint(generate_response)

    return app