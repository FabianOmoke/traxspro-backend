from collections import OrderedDict
from datetime import datetime
from app.db import supabase_db


def aggregate_top_to_global(limit=20):
    # Fetch recent country-specific rows ordered by listeners
    resp = (
        supabase_db
        .table("trending_artists")
        .select("*")
        .order("listeners", desc=True)
        .limit(200)
        .execute()
    )
    rows = resp.data or []

    # Keep top entry per artist name
    by_name = OrderedDict()
    for r in rows:
        name = r.get("name")
        if not name:
            continue
        if name not in by_name:
            by_name[name] = r

    # Prepare global records
    global_records = []
    for r in list(by_name.values())[:limit]:
        global_records.append({
            "name": r.get("name"),
            "mbid": r.get("mbid"),
            "listeners": r.get("listeners", 0),
            "playcount": r.get("playcount", 0),
            "image_url": r.get("image_url"),
            "geo_signal": "global",
            "dma_region": "GLOBAL",
            "captured_at": datetime.utcnow().isoformat()
        })

    if global_records:
        res = supabase_db.table("trending_artists").insert(global_records).execute()
        print(f"Inserted {len(global_records)} global records")
        return getattr(res, "data", res)
    print("No global records to insert")
    return []


if __name__ == "__main__":
    aggregate_top_to_global()
