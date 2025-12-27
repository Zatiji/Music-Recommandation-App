from .generate_response import generate_response


def register_routes(app):
    app.register_blueprint(generate_response)
