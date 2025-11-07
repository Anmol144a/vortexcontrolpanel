# database.py
import os
from supabase import create_client, Client
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

supabase: Client | None = None
if supabase_url and supabase_key:
    try:
        supabase = create_client(supabase_url, supabase_key)
        print("Supabase connected")
    except Exception as e:
        print(f"Supabase init failed: {e}")
else:
    print("SUPABASE_URL or SUPABASE_KEY missing")

async def add_wallet_to_db(user_id: str, address: str, balance: float, tx_count: int):
    if not supabase: return False
    try:
        data = {
            "user_id": user_id,
            "address": address,
            "balance": balance,
            "tx_count": tx_count,
            "updated_at": datetime.utcnow().isoformat()
        }
        supabase.table("wallets").upsert(data, on_conflict="user_id,address").execute()
        return True
    except Exception as e:
        print(f"DB Add Error: {e}")
        return False

async def remove_wallet_from_db(user_id: str, address: str):
    if not supabase: return False
    try:
        supabase.table("wallets").delete().eq("user_id", user_id).eq("address", address).execute()
        return True
    except Exception as e:
        print(f"DB Remove Error: {e}")
        return False

async def get_user_wallets(user_id: str):
    if not supabase: return []
    try:
        res = supabase.table("wallets").select("*").eq("user_id", user_id).execute()
        return res.data or []
    except Exception as e:
        print(f"DB GetUser Error: {e}")
        return []

async def get_all_wallets():
    if not supabase: return []
    try:
        res = supabase.table("wallets").select("*").execute()
        return res.data or []
    except Exception as e:
        print(f"DB GetAll Error: {e}")
        return []

async def update_wallet_balance(address: str, balance: float, tx_count: int):
    if not supabase: return False
    try:
        supabase.table("wallets").update({
            "balance": balance,
            "tx_count": tx_count,
            "updated_at": datetime.utcnow().isoformat()
        }).eq("address", address).execute()
        return True
    except Exception as e:
        print(f"DB Update Error: {e}")
        return False
