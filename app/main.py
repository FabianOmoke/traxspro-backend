from fastapi import FastAPI, HTTPException
from app.db import supabase_db

app = FastAPI(title="Traxspro Signal API")

@app.get("/api/trending/global")
async def get_global_trending(limit: int = 10):
    """Serve global trends directly from Supabase cache."""
    response = (
        supabase_db.table("trending_artists")
        .select("*")
        .eq("geo_signal", "global")
        .order("captured_at", desc=True)
        .order("listeners", desc=True)
        .limit(limit)
        .execute()
    )
    return {"status": "success", "data": response.data}

@app.get("/api/trending/geo/{country}")
async def get_country_trending(country: str, limit: int = 10):
    """Serve country-specific trends from Supabase."""
    response = (
        supabase_db.table("trending_artists")
        .select("*")
        .eq("geo_signal", country)
        .order("captured_at", desc=True)
        .order("listeners", desc=True)
        .limit(limit)
        .execute()
    )
    return {"status": "success", "region": country, "data": response.data}