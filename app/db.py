import uuid
from datetime import date
from app.db import supabase_db


def get_or_create_artist(artist_data):

    # Try to find by MBID first
    if artist_data["mbid"]:
        existing = (
            supabase_db.table("artists")
            .select("*")
            .eq("mbid", artist_data["mbid"])
            .execute()
        )

        if existing.data:
            return existing.data[0]["id"]

    # Otherwise create new artist
    new_artist = {
        "id": str(uuid.uuid4()),
        "name": artist_data["name"],
        "mbid": artist_data["mbid"],
        "global_listeners": artist_data["listeners"],
        "last_updated_at": date.today()
    }

    supabase_db.table("artists").insert(new_artist).execute()

    return new_artist["id"]


from datetime import date
import uuid


def save_dma_artists(country: str, artists_list: list, snapshot_date: date):

    for artist in artists_list:

        artist_id = get_or_create_artist(artist)

        trending_row = {
            "id": str(uuid.uuid4()),
            "artist_id": artist_id,
            "listeners": artist["listeners"],
            "playcount": artist["playcount"],
            "rank_position": artist["rank_position"],
            "geo_signal": country,
            "captured_at": snapshot_date
        }

        # UPSERT prevents duplicates
        supabase_db.table("trending_artists") \
            .upsert(
                trending_row,
                on_conflict="artist_id,geo_signal,captured_at"
            ) \
            .execute()