from supabase import create_client, Client
from app.config import SUPABASE_URL, SUPABASE_SERVICE_KEY
from datetime import date

# 1. Initialize the client once at the module level
def get_supabase() -> Client:
    if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
        raise ValueError("Supabase credentials not found in environment or config.")
    return create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

supabase_db = get_supabase()

# 2. Optimized Cache Reader
def get_cached_dma_artists(country: str):
    """Checks cache for today's data and joins artist details in one call."""
    today = date.today().isoformat()
    
    # We join the 'artists' table to get name/mbid/listeners in one go
    response = (
        supabase_db.table("dma_top_artists")
        .select("rank, country, artists(name, mbid, global_listeners)")
        .eq("country", country.lower())
        .eq("captured_at", today)
        .order("rank")
        .execute()
    )
    
    if not response.data:
        return None
        
    # Flatten the response for a cleaner API output
    return [{
        "rank": r["rank"],
        "artist_name": r["artists"]["name"],
        "mbid": r["artists"]["mbid"],
        "listeners": r["artists"]["global_listeners"]
    } for r in response.data]

# 3. High-Performance Batch Upsert
def save_dma_artists(country: str, artists_list: list, snapshot_date: date):
    """Saves artists and daily ranks using only 2 network requests."""
    if not artists_list:
        return

    # --- Step A: Batch Upsert to 'artists' table ---
    # Prepare unique artist profiles
    artists_to_upsert = [
        {
            "name": a["name"],
            "mbid": a.get("mbid"),
            "global_listeners": int(a.get("listeners", 0))
        }
        for a in artists_list
    ]

    # This handles all artists at once and returns their generated UUIDs
    artist_results = (
        supabase_db.table("artists")
        .upsert(artists_to_upsert, on_conflict="name")
        .execute()
    )

    # Map names to their new UUIDs: {"Artist Name": "uuid-123"}
    name_to_id = {artist["name"]: artist["id"] for artist in artist_results.data}

    # --- Step B: Batch Upsert to 'dma_top_artists' table ---
    dma_records = []
    for a in artists_list:
        artist_id = name_to_id.get(a["name"])
        if artist_id:
            dma_records.append({
                "country": country.lower(),
                "artist_id": artist_id,
                "rank": a.get("rank_position") or a.get("rank"),
                "captured_at": snapshot_date.isoformat()
            })

    return (
        supabase_db.table("dma_top_artists")
        .upsert(dma_records, on_conflict="country, artist_id, captured_at")
        .execute()
    )