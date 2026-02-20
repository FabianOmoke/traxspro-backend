import asyncio
import os
import httpx
from datetime import datetime
from app.db import supabase_db

LASTFM_API_KEY = os.getenv("LASTFM_API_KEY")
LASTFM_BASE_URL = "http://ws.audioscrobbler.com/2.0/"

# Strategic market grouping
DMA_MAP = {
    "Austria": "DACH",
    "Germany": "DACH",
    "Switzerland": "DACH",
    "United Kingdom": "UK_IRE",
    "Ireland": "UK_IRE"
}

async def fetch_and_store_geo(country: str):
    print(f"Fetching data for {country}...")
    params = {
        "method": "geo.gettopartists",
        "country": country,
        "api_key": LASTFM_API_KEY,
        "format": "json",
        "limit": 20
    }
    
    async with httpx.AsyncClient() as client:
        res = await client.get(LASTFM_BASE_URL, params=params)
        data = res.json().get("topartists", {}).get("artist", [])

    dma_region = DMA_MAP.get(country, "OTHER")
    
    records = []
    for artist in data:
        records.append({
            "name": artist["name"],
            "listeners": int(artist["listeners"]),
            "image_url": artist["image"][2]["#text"] if len(artist["image"]) > 2 else None,
            "geo_signal": country,
            "dma_region": dma_region,
            "captured_at": datetime.utcnow().isoformat()
        })

    # Bulk insert into Supabase
    if records:
        supabase_db.table("trending_artists").insert(records).execute()
        print(f"Saved {len(records)} records for {country} ({dma_region} DMA).")

async def run_ingestion():
    target_countries = ["Austria", "Germany", "United Kingdom", "France"]
    for country in target_countries:
        await fetch_and_store_geo(country)

if __name__ == "__main__":
    asyncio.run(run_ingestion())