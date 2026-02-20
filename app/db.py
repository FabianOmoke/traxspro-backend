from supabase import create_client, Client
from app.config import SUPABASE_URL, SUPABASE_SERVICE_KEY

"""Create and expose a Supabase client using credentials from `app.config`.

This lets credentials be provided either via environment variables or
directly placed in `app/config.py` for local development.
"""

def get_supabase() -> Client:
    if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
        raise ValueError("Supabase credentials not found in environment or config.")
    return create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

supabase_db = get_supabase()