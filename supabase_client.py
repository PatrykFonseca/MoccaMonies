# File: supabase_client.py
import os
from supabase import create_client, Client

# Configure suas variáveis de ambiente:
# SUPABASE_URL e SUPABASE_KEY
supabase_url: str = os.getenv("SUPABASE_URL")
supabase_key: str = os.getenv("SUPABASE_KEY")

if not supabase_url or not supabase_key:
    raise RuntimeError("Defina as variáveis SUPABASE_URL e SUPABASE_KEY no ambiente")

supabase: Client = create_client(supabase_url, supabase_key)
