from fastapi import FastAPI, HTTPException
from app.db import supabase_db, save_dma_artists, get_cached_dma_artists
from services.lastfm import (
    fetch_global_top_artists,
    fetch_global_top_tags,
    fetch_tag_top_artists,
    fetch_geo_top_artists
)

app = FastAPI(title="Traxspro Signal API")


@app.get("/")
async def root():
    return {
        "platform": "Traxspro Intelligence API",
        "status": "online",
        "docs": "/docs"
    }


DMA_MAP = {
    "dach": ["germany", "austria", "switzerland"],
    "benelux": ["belgium", "netherlands", "luxembourg"],
    "nordics": ["sweden", "denmark", "norway", "finland", "iceland"]
}


# -----------------------
# GLOBAL LIVE SIGNAL
# -----------------------

@app.get("/api/trending/global/live")
def global_live(limit: int = 10):
    return {
        "source": "live",
        "data": fetch_global_top_artists(limit)
    }


@app.get("/api/trending/tags/global")
def trending_tags(limit: int = 10):
    return {
        "source": "live",
        "data": fetch_global_top_tags(limit)
    }


@app.get("/api/genre/{tag}")
def genre_top(tag: str, limit: int = 10):
    return {
        "genre": tag,
        "data": fetch_tag_top_artists(tag, limit)
    }


# -----------------------
# CACHE SERVED SIGNAL
# -----------------------

@app.get("/api/trending/global")
async def get_global_trending(limit: int = 10):
    response = (
        supabase_db.table("trending_artists")
        .select("""
            id,
            rank_position,
            listeners,
            playcount,
            geo_signal,
            captured_at,
            artists (
                id,
                name,
                mbid,
                global_listeners,
                last_updated_at
            )
        """)
        .eq("geo_signal", "global")
        .order("captured_at", desc=True)
        .order("rank_position", desc=False)
        .limit(limit)
        .execute()
    )

    return {"status": "success", "data": response.data}


@app.get("/api/trending/geo/{country}")
async def get_country_trending(country: str, limit: int = 10):
    response = (
        supabase_db.table("trending_artists")
        .select("""
            id,
            rank_position,
            listeners,
            playcount,
            geo_signal,
            captured_at,
            artists (
                id,
                name,
                mbid,
                global_listeners,
                last_updated_at
            )
        """)
        .eq("geo_signal", country)
        .order("captured_at", desc=True)
        .order("rank_position", desc=False)
        .limit(limit)
        .execute()
    )

    return {"status": "success", "region": country, "data": response.data}


# -----------------------
# DMA INTELLIGENCE
# -----------------------

@app.get("/api/intelligence/geo/{country}")
def get_geo_intelligence(country: str, limit: int = 10):

    cached = get_cached_dma_artists(country)

    if cached:
        return {"source": "cache", "data": cached}

    fresh_data = fetch_geo_top_artists(country, limit)
    save_dma_artists(country, fresh_data)

    return {"source": "live", "data": fresh_data}


@app.get("/api/intelligence/market/{dma_name}")
def get_market_intelligence(dma_name: str, limit: int = 10):

    dma_key = dma_name.lower()

    if dma_key not in DMA_MAP:
        raise HTTPException(status_code=404, detail="DMA region not supported.")

    countries = DMA_MAP[dma_key]
    market_data = {}

    for country in countries:

        cached = get_cached_dma_artists(country)

        if cached:
            market_data[country] = cached
        else:
            fresh = fetch_geo_top_artists(country, limit)
            save_dma_artists(country, fresh)
            market_data[country] = fresh

    return {
        "market": dma_name.upper(),
        "countries": countries,
        "data": market_data
    }