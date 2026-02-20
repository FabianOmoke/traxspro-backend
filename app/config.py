import os
from dotenv import load_dotenv

load_dotenv()

# Read from environment first, fall back to values present in this file if any
# (useful for local development where secrets were placed directly in `config.py`).
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://vwwjhhdbsldnevpccpmj.supabase.co")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "sb_publishable_1tUU7Yjw9oOwYHOcwbMQIg_nhyjEpDY")

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

LASTFM_API_KEY = os.getenv("LASTFM_API_KEY", "791e35407d0dba66f434eb0949eda95a")
