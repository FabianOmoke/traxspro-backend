from app.services.spotify import search_artist
from app.db import supabase

def ingest_artist(name):
    artist = search_artist(name)

    if not artist:
        return

    supabase.table("artists").insert({
        "name": artist["name"],
        "spotify_id": artist["id"],
        "genres": artist["genres"],
        "image_url": artist["images"][0]["url"] if artist["images"] else None
    }).execute()

if __name__ == "__main__":
    ingest_artist("Burial")
