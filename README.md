# Music Recommendation App

An LLM-powered chatbot fused with the Spotify API to recommend music based on user preferences, with explanations for why each recommendation fits.

## Structure

```
backend/
  app/
    routes/
    services/
  main.py
  requirements.txt
frontend/
  src/
```

## Setup

Backend:
1. Create a virtual environment in `backend/venv` or `.venv`.
2. Install dependencies: `pip install -r backend/requirements.txt`.
3. Copy env values into `backend/.env` (see `backend/.env.example`).
4. Run: `python backend/main.py`.

Frontend:
1. Install deps: `npm install`.
2. Run: `npm run dev`.

## Run the Project

1. Start the backend: `python backend/main.py`.
2. In a separate terminal, start the frontend: `npm run dev`.
3. Open the app at `http://localhost:5173`.
