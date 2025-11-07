# api/wallets.py
import os
import json
from supabase import create_client

# Supabase (anon key)
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

supabase = create_client(url, key) if url and key else None

def handler(event, context):
    if not supabase:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Supabase not configured"})
        }

    try:
        result = supabase.table("wallets").select("*").execute()
        wallets = result.data or []

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "wallets": [
                    {"address": w["address"], "balance": round(float(w["balance"]), 8)}
                    for w in wallets
                ],
                "count": len(wallets)
            })
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
