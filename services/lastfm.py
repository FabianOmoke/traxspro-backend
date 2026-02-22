import requests
from app.config import LASTFM_API_KEY
import os

LASTFM_API_KEY = os.getenv("LASTFM_API_KEY")
BASE_URL = "http://ws.audioscrobbler.com/2.0/"


def _parse_artist_list(artist_list):
    parsed = []

    for artist in artist_list:
        parsed.append({
            "name": artist["name"],
            "mbid": artist.get("mbid"),
            "listeners": int(artist.get("listeners", 0)),
            "playcount": int(artist.get("playcount", 0)),
            "rank_position": int(artist["@attr"]["rank"]),
            "image_url": artist["image"][-1]["#text"],
            "lastfm_url": artist["url"]
        })

    return parsed


def fetch_geo_top_artists(country: str, limit: int = 10):
    params = {
        "method": "geo.getTopArtists",
        "country": country,
        "api_key": LASTFM_API_KEY,
        "format": "json",
        "limit": limit
    }

    response = requests.get(BASE_URL, params=params)
    response.raise_for_status()
    data = response.json()

    artists = data["topartists"]["artist"]

    return _parse_artist_list(artists)


def fetch_global_top_artists(limit: int = 10):
    params = {
        "method": "chart.getTopArtists",
        "api_key": LASTFM_API_KEY,
        "format": "json",
        "limit": limit
    }

    response = requests.get(BASE_URL, params=params)
    response.raise_for_status()
    data = response.json()

    artists = data["artists"]["artist"]

    return _parse_artist_list(artists)


def fetch_global_top_tags(limit: int = 10):
    params = {
        "method": "chart.getTopTags",
        "api_key": LASTFM_API_KEY,
        "format": "json",
        "limit": limit
    }

    response = requests.get(BASE_URL, params=params)
    response.raise_for_status()
    data = response.json()

    return [
        {
            "name": tag["name"],
            "tag_count": int(tag["count"]),
            "url": tag["url"]
        }
        for tag in data["tags"]["tag"]
    ]


def fetch_tag_top_artists(tag: str, limit: int = 10):
    params = {
        "method": "tag.getTopArtists",
        "tag": tag,
        "api_key": LASTFM_API_KEY,
        "format": "json",
        "limit": limit
    }

    response = requests.get(BASE_URL, params=params)
    response.raise_for_status()
    data = response.json()

    artists = data["topartists"]["artist"]

    return _parse_artist_list(artists)