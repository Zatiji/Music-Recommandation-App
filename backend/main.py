from routes import create_app
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(env_path)

app = create_app()

if __name__ == "__main__":
    app.run(debug=False, port=5001)