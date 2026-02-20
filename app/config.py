import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("https://vwwjhhdbsldnevpccpmj.supabase.co")
SUPABASE_SERVICE_KEY = os.getenv("sb_publishable_1tUU7Yjw9oOwYHOcwbMQIg_nhyjEpDY")

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

LASTFM_API_KEY = os.getenv("791e35407d0dba66f434eb0949eda95a")
