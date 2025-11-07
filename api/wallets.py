# api/wallets.py
import os
import json
import requests
from supabase import create_client

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase = create_client(url, key)

def handler(event, context):
    try:
        res = supabase.table("wallets").select("*").execute()
        wallets = res.data or []
        total = sum(float(w["balance"]) for w in wallets)

        # LTC Price (server-side)
        price_res = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=litecoin&vs_currencies=usd", timeout=5)
        price = price_res.json().get("litecoin", {}).get("usd", 0) if price_res.ok else 0

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0"
            },
            "body": json.dumps({
                "wallets": [{"address": w["address"], "balance": round(float(w["balance"]), 8)} for w in wallets],
                "count": len(wallets),
                "total_balance": round(total, 8),
                "ltc_price": round(price, 2)
            })
        }
    except Exception as e:
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}
