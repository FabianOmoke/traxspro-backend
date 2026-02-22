from fastapi import FastAPI, HTTPException
from app.db import supabase_db
from app.db import save_dma_artists, get_cached_dma_artists
from services.lastfm import fetch_geo_top_artists

app = FastAPI(title="Traxspro Signal API")

@app.get("/")
async def root():
    return {
        "platform": "Traxspro Intelligence API",
        "status": "online",
        "docs": "/docs"
    }

# Mapping of DMAs to their constituent countries
DMA_MAP = {
    "dach": ["germany", "austria", "switzerland"],
    "benelux": ["belgium", "netherlands", "luxembourg"],
    "nordics": ["sweden", "denmark", "norway", "finland", "iceland"]
}

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

@app.get("/api/intelligence/dma/{country}")
def get_dma_intelligence(country: str):
    # Check Database first
    cached = get_cached_dma_artists(country)
    if cached:
        return {"source": "cache", "data": cached}
        
    # If not in DB, fetch from Last.fm
    fresh_data = fetch_geo_top_artists(country)
    
    # Save to both tables in Supabase
    save_dma_artists(fresh_data)
    
    return {"source": "live", "data": fresh_data}

@app.get("/api/intelligence/market/{dma_name}")
def get_market_intelligence(dma_name: str):
    dma_key = dma_name.lower()
    if dma_key not in DMA_MAP:
        raise HTTPException(status_code=404, detail="DMA region not supported yet.")
    
    countries = DMA_MAP[dma_key]
    market_data = {}

    for country in countries:
        # Re-use our Smart Proxy logic for each country
        cached = get_cached_dma_artists(country)
        if cached:
            market_data[country] = cached
        else:
            fresh = fetch_geo_top_artists(country)
            save_dma_artists(fresh)
            market_data[country] = fetch_geo_top_artists(country) # Re-fetch to get flattened format

    return {
        "market": dma_name.upper(),
        "countries_included": countries,
        "data": market_data
    }