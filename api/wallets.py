# api/wallets.py
import os
import json
import requests
from supabase import create_client

# SUPABASE
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase = create_client(url, key) if url and key else None

def handler(event, context):
    if not supabase:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Supabase not configured"})
        }

    try:
        # GET WALLETS FROM DB
        res = supabase.table("wallets").select("*").execute()
        wallets = res.data or []
        total = sum(float(w.get("balance", 0)) for w in wallets)

        # BEST FREE PRICE API: COINGECKO (REAL-TIME, NO KEY, NO CORS)
        try:
            price_res = requests.get(
                "https://api.coingecko.com/api/v3/simple/price?ids=litecoin&vs_currencies=usd",
                timeout=6
            )
            price = price_res.json().get("litecoin", {}).get("usd", 90.61) if price_res.ok else 90.61
        except:
            price = 90.61  # fallback

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({
                "wallets": [
                    {
                        "address": w["address"],
                        "balance": round(float(w.get("balance", 0)), 8),
                        "tx_count": w.get("tx_count", 0),
                        "explorer": f"https://sochain.com/address/LTC/{w['address']}"
                    } for w in wallets
                ],
                "count": len(wallets),
                "total_balance": round(total, 8),
                "ltc_price": round(price, 2)
            })
        }
    except Exception as e:
        print(f"API Error: {e}")
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": str(e)})
        }
