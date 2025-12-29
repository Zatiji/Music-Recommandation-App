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

## Backend Workflow

1. The frontend sends a POST to `/generate-response` with the user message and session id.
2. The backend calls the LLM intent extractor to decide if the message is a recommendation request and to parse query/mood.
3. If it is a recommendation, the backend queries Last.fm based on the intent:
   - `artist` -> search + similar artists, with extra artist info for context.
   - `track` -> search + similar tracks, with extra track info for context.
   - `tag` -> top tracks by tag.
   - fallback -> top trending tracks.
4. The backend builds system context from the Last.fm results (or an empty-result prompt) and streams the LLM presenter response.
5. The response is streamed back to the client as SSE:
   - first optional `cards` payload for UI rendering,
   - then incremental `delta` chunks,
   - finally a `done` event.
6. The session stores a running summary when the token budget is near the limit, keeping context small for future turns.
