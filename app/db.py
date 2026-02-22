from supabase import create_client, Client
from app.config import SUPABASE_URL, SUPABASE_SERVICE_KEY
from datetime import date

"""Create and expose a Supabase client using credentials from `app.config`.

This lets credentials be provided either via environment variables or
directly placed in `app/config.py` for local development.
"""

def get_supabase() -> Client:
    if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
        raise ValueError("Supabase credentials not found in environment or config.")
    return create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

# This is your active database connection
supabase_db = get_supabase()

# ---------------------------------------------------------
# DMA Intelligence Cache Functions
# ---------------------------------------------------------

from datetime import date

def get_cached_dma_artists(country: str):
    today = date.today().isoformat()
    response = (
        supabase_db.table("dma_top_artists")
        .select("rank, country, artists(name, mbid, global_listeners)")
        .eq("country", country.lower())
        .eq("captured_at", today)
        .order("rank").execute()
    )
    
    if not response.data: return None
        
    return [{
        "rank": r["rank"],
        "artist_name": r["artists"]["name"],
        "mbid": r["artists"]["mbid"],
        "listeners": r["artists"]["global_listeners"]
    } for r in response.data]

def save_dma_artists(artists_data: list):
    # 1. Update Artist Table & Get IDs
    core_artists = [{"name": a["artist_name"], "mbid": a["mbid"], "global_listeners": a["listeners"]} 
                    for a in artists_data]
    
    artist_records = supabase_db.table("artists").upsert(core_artists, on_conflict="name").execute()
    name_to_id = {a["name"]: a["id"] for a in artist_records.data}

    # 2. Map IDs to DMA records
    dma_records = [{
        "country": a["country"],
        "artist_id": name_to_id[a["artist_name"]],
        "rank": a["rank"]
    } for a in artists_data]

    return supabase_db.table("dma_top_artists").upsert(dma_records).execute()