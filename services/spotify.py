import requests
from app.config import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET

def get_spotify_token():
    r = requests.post(
        "https://accounts.spotify.com/api/token",
        data={"grant_type": "client_credentials"},
        auth=(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET)
    )
    return r.json()["access_token"]

def search_artist(name):
    token = get_spotify_token()

    headers = {
        "Authorization": f"Bearer {token}"
    }

    r = requests.get(
        "https://api.spotify.com/v1/search",
        headers=headers,
        params={"q": name, "type": "artist", "limit": 1}
    )

    items = r.json()["artists"]["items"]
    return items[0] if items else None
