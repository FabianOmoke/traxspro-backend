from fastapi import FastAPI, HTTPException
from app.db import supabase_db, save_dma_artists, get_cached_dma_artists
from services.lastfm import (
    fetch_global_top_artists,
    fetch_global_top_tags,
    fetch_tag_top_artists,
    fetch_geo_top_artists
)
from datetime import date
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Traxspro Signal API")

# ... (root and global endpoints remain same)
# Add this block right after initializing 'app'
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For development. Change to your Lovable domain for security later.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# --- 1. Core Logic Helper ---
def get_or_fetch_country_signal(country: str, limit: int = 10):
    cached = get_cached_dma_artists(country.lower())

    if cached:
        return {"source": "cache", "data": cached[:limit]}

    fresh_data = fetch_geo_top_artists(country, limit)
    
    if not fresh_data:
        raise HTTPException(status_code=404, detail=f"No data for {country}")

    # SAFE MAPPING: We check for 'artist_name' OR 'name'
    save_data = []
    for a in fresh_data:
        # Use .get() to avoid KeyErrors if the source naming changes
        name = a.get("artist_name") or a.get("name")
        
        if name:
            save_data.append({
                "name": name,
                "mbid": a.get("mbid"),
                "listeners": a.get("listeners", 0),
                "rank": a.get("rank", 0)
            })
    
    # Only save if we actually processed artists
    if save_data:
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

@app.get("/api/visualize/map")
def get_map_visualization():
    """Returns the 'Music Heat' for every country currently in our system."""
    # We pull the total listeners per country for the last 24 hours
    stats = (
        supabase_db.table("dma_top_artists")
        .select("country, listeners")
        .eq("captured_at", date.today().isoformat())
        .execute()
    )

    # Aggregate the data so each country has one total 'heat' score
    heat_map = {}
    for entry in stats.data:
        c = entry["country"]
        heat_map[c] = heat_map.get(c, 0) + entry["listeners"]

    # Format it as a simple list for Lovable's Map components
    return [
        {"id": country.upper(), "value": value} 
        for country, value in heat_map.items()
    ]