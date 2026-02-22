from datetime import date
from services.lastfm import (
    fetch_geo_top_artists,
    fetch_global_top_artists
)
from app.db import save_dma_artists

COUNTRIES = ["germany", "austria", "switzerland"]
LIMIT = 25

today = date.today()

# Populate global
global_artists = fetch_global_top_artists(LIMIT)
save_dma_artists("global", global_artists, today)

# Populate countries
for country in COUNTRIES:
    artists = fetch_geo_top_artists(country, LIMIT)
    save_dma_artists(country, artists, today)

print("Population complete.")