import requests
from app.config import LASTFM_API_KEY

def get_artist_info(name):
    r = requests.get(
        "http://ws.audioscrobbler.com/2.0/",
        params={
            "method": "artist.getinfo",
            "artist": name,
            "api_key": LASTFM_API_KEY,
            "format": "json"
        }
    )

    return r.json()
