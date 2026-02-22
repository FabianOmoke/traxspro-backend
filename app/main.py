from fastapi import FastAPI, HTTPException
from app.db import supabase_db, save_dma_artists, get_cached_dma_artists
from services.lastfm import (
    fetch_global_top_artists,
    fetch_global_top_tags,
    fetch_tag_top_artists,
    fetch_geo_top_artists
)
from datetime import date

app = FastAPI(title="Traxspro Signal API")

# ... (root and global endpoints remain same)

# --- 1. Core Logic Helper ---
def get_or_fetch_country_signal(country: str, limit: int = 10):
    # Only pass country name to the cache checker
    cached = get_cached_dma_artists(country.lower())

    if cached:
        return {"source": "cache", "data": cached[:limit]}

    # Fetch live if no cache
    fresh_data = fetch_geo_top_artists(country, limit)
    
    if not fresh_data:
        raise HTTPException(status_code=404, detail=f"No data for {country}")

    # Save to DB (this expects list, and date)
    # We map 'artist_name' to 'name' for compatibility
    save_data = [{
        "name": a["artist_name"],
        "mbid": a["mbid"],
        "listeners": a["listeners"],
        "rank": a["rank"]
    } for a in fresh_data]
    
    save_dma_artists(country.lower(), save_data, date.today())

    return {"source": "live", "data": fresh_data}

# --- 2. Routes ---
@app.get("/api/intelligence/geo/{country}")
def get_geo_intelligence(country: str, limit: int = 10):
    return get_or_fetch_country_signal(country, limit)

@app.get("/api/intelligence/market/{dma_name}")
def get_market_intelligence(dma_name: str, limit: int = 10):
    DMA_MAP = {
        "dach": ["germany", "austria", "switzerland"],
        "benelux": ["belgium", "netherlands", "luxembourg"],
        "nordics": ["sweden", "denmark", "norway", "finland", "iceland"]
    }
    
    dma_key = dma_name.lower()
    if dma_key not in DMA_MAP:
        raise HTTPException(status_code=404, detail="DMA region not supported.")

    market_data = {}
    for country in DMA_MAP[dma_key]:
        result = get_or_fetch_country_signal(country, limit)
        market_data[country] = result["data"]

    return {
        "market": dma_name.upper(),
        "data": market_data
    }