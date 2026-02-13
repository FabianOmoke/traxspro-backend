import requests

def search_artist(name):
    r = requests.get(
        "https://musicbrainz.org/ws/2/artist",
        params={
            "query": f"artist:{name}",
            "fmt": "json"
        },
        headers={
            "User-Agent": "Traxspro/0.1 ( contact@traxspro.com )"
        }
    )

    artists = r.json().get("artists", [])
    return artists[0] if artists else None
