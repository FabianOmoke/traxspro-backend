import asyncio
import os
import httpx
from datetime import datetime
from app.db import supabase_db

LASTFM_API_KEY = os.getenv("LASTFM_API_KEY")
LASTFM_BASE_URL = "http://ws.audioscrobbler.com/2.0/"

DMA_MAP = {
    "Germany": "DACH",
    "United Kingdom": "UK_IRE",
    "France": "FRANCE"
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
        
        if res.status_code != 200:
            print(f"Failed to fetch {country}: {res.text}")
            return
            
        # Drill down into the exact Last.fm JSON structure
        data = res.json().get("topartists", {}).get("artist", [])

    dma_region = DMA_MAP.get(country, "OTHER")
    records = []
    
    for artist in data:
        # 1. Safely extract the best image (prefer extralarge or large)
        image_url = None
        images = artist.get("image", [])
        for img in images:
            if img.get("size") in ["extralarge", "large"] and img.get("#text"):
                image_url = img["#text"]
                
        # 2. Handle the MBID (Last.fm sometimes returns empty strings "")
        raw_mbid = artist.get("mbid", "").strip()
        clean_mbid = raw_mbid if raw_mbid else None
        
        # 3. Build the record
        records.append({
            "name": artist["name"],
            "listeners": int(artist["listeners"]), # Convert string to int
            "mbid": clean_mbid,
            "lastfm_url": artist.get("url", ""),
            "image_url": image_url,
            "geo_signal": country,
            "dma_region": dma_region,
            "captured_at": datetime.utcnow().isoformat()
        })

    # Bulk insert into Supabase
    if records:
        response = supabase_db.table("trending_artists").insert(records).execute()
        print(f"✅ Saved {len(records)} records for {country} ({dma_region} DMA).")

async def run_ingestion():
    # Test with just Austria to verify the parsing works
    await fetch_and_store_geo("Austria")

if __name__ == "__main__":
    asyncio.run(run_ingestion())