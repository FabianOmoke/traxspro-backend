import requests
from app.config import LASTFM_API_KEY

BASE_URL = "http://ws.audioscrobbler.com/2.0/"

# Your existing function (unchanged!)
def get_artist_info(name):
    r = requests.get(
        BASE_URL,
        params={
            "method": "artist.getinfo",
            "artist": name,
            "api_key": LASTFM_API_KEY,
            "format": "json"
        }
    )
    return r.json()

# Our NEW DMA fetcher, matching your exact style
def fetch_geo_top_artists(country: str, limit: int = 50):
    r = requests.get(
        BASE_URL,
        params={
            "method": "geo.gettopartists",
            "country": country,
            "api_key": LASTFM_API_KEY,
            "format": "json",
            "limit": limit
        }
    )
    r.raise_for_status()
    data = r.json()
    artists = data.get("topartists", {}).get("artist", [])
    
    clean_artists = []
    for idx, artist in enumerate(artists):
        clean_artists.append({
            "country": country.lower(),
            "artist_name": artist.get("name"),
            "listeners": int(artist.get("listeners", 0)) if artist.get("listeners") else 0,
            "mbid": artist.get("mbid") or None,
            "rank": idx + 1,
        })
    return clean_artists