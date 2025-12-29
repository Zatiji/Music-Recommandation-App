import json
import logging
from flask import Blueprint, request, Response, stream_with_context

from app.services.llm import extractIntent, streamPresenterResponse
from app.services import lastfm

generateResponse = Blueprint("generate_response", __name__)
_logger = logging.getLogger(__name__)


def _buildSystemDataForResults(
    query: str,
    mood: str,
    results: list,
    extraInfo: list,
) -> str:
    return (
        "SYSTEM DATA: Here are the results from Last.fm "
        f"for '{query}' (mood: {mood or 'neutral'}):\n"
        f"{json.dumps(results, ensure_ascii=True)}\n"
        f"EXTRA CONTEXT: {json.dumps(extraInfo, ensure_ascii=True)}\n"
        "Instruction: Present these to the user casually. "
        "Mention that these are similar. "
        "If extra context is provided, use it to avoid hallucinations."
    )


def _buildSystemDataForEmpty() -> str:
    return (
        "SYSTEM DATA: No results were returned from Last.fm. "
        "Ask a short clarifying question or suggest a nearby artist/tag."
    )


def _handleArtistRecommendation(query: str) -> tuple[list, list, str]:
    results = []
    extraInfo = []
    correctedQuery = query

    correction = lastfm.searchArtist(query, limit=1)
    if correction:
        correctedQuery = correction[0].get("name") or query
    results = lastfm.getSimilarArtist(correctedQuery, limit=10)
    for item in results[:3]:
        info = lastfm.getArtistInfo(item.get("name", ""))
        if info:
            extraInfo.append(info)

    return results, extraInfo, correctedQuery


def _handleTrackRecommendation(query: str) -> tuple[list, list, str]:
    results = []
    extraInfo = []
    correctedTrack = query
    correctedArtist = ""

    correction = lastfm.searchTrack(query, limit=1)
    if correction:
        correctedTrack = correction[0].get("name") or query
        correctedArtist = correction[0].get("artist") or ""
    results = lastfm.getSimilarTracks(correctedTrack, artist=correctedArtist, limit=10)
    for item in results[:3]:
        info = lastfm.getTrackInfo(item.get("name", ""), artist=item.get("artist", ""))
        if info:
            extraInfo.append(info)

    return results, extraInfo, correctedTrack


def _handleTagRecommendation(query: str) -> tuple[list, list, str]:
    results = lastfm.getTopTracksByTag(query, limit=10)
    return results, [], query


def _handleTrendingRecommendation() -> tuple[list, list, str]:
    results = lastfm.getTopTracksChart(limit=10)
    return results, [], "Trending"


@generateResponse.route("/generate-response", methods=["OPTIONS", "POST"])
def handleGenerateResponse():
    if request.method == "OPTIONS":
        return "", 204
    
    data = request.get_json(silent=True) or {}
    user_message = data.get("message", "")
    session_id = data.get("session_id", "default")
    
    if not user_message:
        return Response('Missing "message"', status=400)

    intent = extractIntent(user_message, sessionId=session_id)
    systemData = None
    cardsPayload = None

    _logger.info("Intent extracted: %s", intent)

    if intent.get("intent") == "recommendation":
        
        query = intent.get("query", "")
        searchType = intent.get("search_type", "none")
        mood = intent.get("user_mood", "")
        results = []
        correctedQuery = query
        extraInfo = []

        _logger.info("Intent: recommendation type=%s query=%s", searchType, query)

        if searchType == "artist" and query:
            results, extraInfo, correctedQuery = _handleArtistRecommendation(query)
        elif searchType == "track" and query:
            results, extraInfo, correctedQuery = _handleTrackRecommendation(query)
        elif searchType == "tag" and query:
            results, extraInfo, correctedQuery = _handleTagRecommendation(query)
        else:
            results, extraInfo, correctedQuery = _handleTrendingRecommendation()

        if results:
            systemData = _buildSystemDataForResults(
                correctedQuery or query,
                mood,
                results,
                extraInfo,
            )
            cardsPayload = results
            
        else:
            systemData = _buildSystemDataForEmpty()

    # Create generator for SSE
    @stream_with_context
    def generate():
        if cardsPayload:
            yield f"data: {json.dumps({'cards': cardsPayload, 'source': 'lastfm'})}\n\n"
        # Send each chunk as JSON: {"delta": "..."}
        for chunk in streamPresenterResponse(
            user_message,
            sessionId=session_id,
            system_data=systemData,
        ):
            yield f"data: {json.dumps({'delta': chunk})}\n\n"
        # Signal completion
        yield f"data: {json.dumps({'done': True})}\n\n"

    return Response(generate(), mimetype="text/event-stream")
