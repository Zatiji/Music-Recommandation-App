from .generateResponse import generateResponse


def register_routes(app):
    app.register_blueprint(generateResponse)
