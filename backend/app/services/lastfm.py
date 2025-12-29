import logging
import os
from typing import List

import requests

_BASE_URL = "https://ws.audioscrobbler.com/2.0/"
_logger = logging.getLogger(__name__)


def _fetchApiKey() -> str:
    apiKey = os.getenv("LASTFM_API_KEY")
    if not apiKey:
        raise RuntimeError("Please set the LASTFM_API_KEY environment variable")
    return apiKey


def _lastfmGET(params: dict) -> dict:
    params = dict(params)
    params["api_key"] = _fetchApiKey()
    params["format"] = "json"
    log_params = dict(params)
    log_params.pop("api_key", None)
    _logger.info("Last.fm request: %s", log_params)
    response = requests.get(_BASE_URL, params=params, timeout=10)
    _logger.info("Last.fm response: %s %s", response.status_code, response.reason)
    response.raise_for_status()
    return response.json()


def getSimilarArtist(artist: str, limit: int = 10) -> List[dict]:
    if not artist:
        return []

    data = _lastfmGET({"method": "artist.getSimilar", "artist": artist, "limit": limit})
    artists = data.get("similarartists", {}).get("artist", [])
    results = []
    for item in artists:
        results.append(
            {
                "type": "artist",
                "name": item.get("name"),
                "url": item.get("url"),
                "match": item.get("match"),
            }
        )

    return results


def getSimilarTracks(track: str, artist: str = "", limit: int = 10) -> List[dict]:
    if not track:
        return []
    
    params = {"method": "track.getSimilar", "track": track, "limit": limit}
    if artist:
        params["artist"] = artist
    
    data = _lastfmGET(params)
    tracks = data.get("similartracks", {}).get("track", [])
    results = []
    for item in tracks:
        results.append(
            {
                "type": "track",
                "name": item.get("name"),
                "artist": (item.get("artist") or {}).get("name"),
                "url": item.get("url"),
                "match": item.get("match"),
            }
        )
    return results


def getTopTracksByTag(tag: str, limit: int = 10) -> List[dict]:
    if not tag:
        return []
    
    data = _lastfmGET({"method": "tag.getTopTracks", "tag": tag, "limit": limit})
    tracks = data.get("tracks", {}).get("track", [])
    results = []
    for item in tracks:
        results.append(
            {
                "type": "track",
                "name": item.get("name"),
                "artist": (item.get("artist") or {}).get("name"),
                "url": item.get("url"),
                "rank": (item.get("@attr") or {}).get("rank"),
            }
        )
    
    return results


def searchArtist(name: str, limit: int = 5) -> List[dict]:
    if not name:
        return []
    
    data = _lastfmGET({"method": "artist.search", "artist": name, "limit": limit})
    matches = data.get("results", {}).get("artistmatches", {}).get("artist", [])
    results = []
    for item in matches:
        results.append(
            {
                "type": "artist",
                "name": item.get("name"),
                "url": item.get("url"),
                "listeners": item.get("listeners"),
            }
        )
    
    return results


def searchTrack(name: str, limit: int = 5) -> List[dict]:
    if not name:
        return []
    
    data = _lastfmGET({"method": "track.search", "track": name, "limit": limit})
    matches = data.get("results", {}).get("trackmatches", {}).get("track", [])
    results = []
    for item in matches:
        results.append(
            {
                "type": "track",
                "name": item.get("name"),
                "artist": item.get("artist"),
                "url": item.get("url"),
                "listeners": item.get("listeners"),
            }
        )
    
    return results


def getArtistInfo(artist: str) -> dict:
    if not artist:
        return {}
    
    data = _lastfmGET({"method": "artist.getInfo", "artist": artist})
    artistData = data.get("artist", {})
    tags = [t.get("name") for t in artistData.get("tags", {}).get("tag", [])]
    summary = (artistData.get("bio", {}) or {}).get("summary", "")
    return {"name": artistData.get("name"), "tags": tags, "summary": summary}


def getTrackInfo(track: str, artist: str = "") -> dict:
    if not track:
        return {}
    
    params = {"method": "track.getInfo", "track": track}
    if artist:
        params["artist"] = artist
    
    data = _lastfmGET(params)
    trackData = data.get("track", {})
    tags = [t.get("name") for t in trackData.get("toptags", {}).get("tag", [])]
    summary = (trackData.get("wiki", {}) or {}).get("summary", "")
    return {
        "name": trackData.get("name"),
        "artist": (trackData.get("artist") or {}).get("name"),
        "tags": tags,
        "summary": summary,
    }


def getTopTracksChart(limit: int = 10) -> List[dict]:
    
    data = _lastfmGET({"method": "chart.getTopTracks", "limit": limit})
    tracks = data.get("tracks", {}).get("track", [])
    results = []
    for item in tracks:
        results.append(
            {
                "type": "track",
                "name": item.get("name"),
                "artist": (item.get("artist") or {}).get("name"),
                "url": item.get("url"),
                "rank": (item.get("@attr") or {}).get("rank"),
            }
        )
    
    return results
