import os
from supabase import create_client, Client

# These will be pulled from Railway's environment variables
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") # Use service role for backend writes

def get_supabase() -> Client:
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError("Supabase credentials not found in environment.")
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase_db = get_supabase()