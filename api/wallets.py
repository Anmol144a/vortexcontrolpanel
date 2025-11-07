# api/wallets.py
import os
import json
import requests
from supabase import create_client, Client

def handler(event, context):
    try:
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")

        if not url or not key:
            raise ValueError("Missing SUPABASE_URL or SUPABASE_KEY environment variables.")

        supabase: Client = create_client(url, key)

        res = supabase.table("wallets").select("*").execute()
        wallets = res.data or []

        total_balance = 0.0
        for w in wallets:
            try:
                total_balance += float(w.get("balance", 0))
            except (TypeError, ValueError):
                continue

        try:
            price_res = requests.get(
                "https://api.coingecko.com/api/v3/simple/price?ids=litecoin&vs_currencies=usd",
                timeout=10
            )
            price_data = price_res.json()
            ltc_price = float(price_data.get("litecoin", {}).get("usd", 0)) if price_res.ok else 0.0
        except Exception:
            ltc_price = 0.0

        response = {
            "wallets": [
                {
                    "address": w.get("address", "unknown"),
                    "balance": round(float(w.get("balance", 0)), 8)
                } for w in wallets
            ],
            "count": len(wallets),
            "total_balance": round(total_balance, 8),
            "ltc_price": round(ltc_price, 2)
        }

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Cache-Control": "no-store, max-age=0, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0"
            },
            "body": json.dumps(response)
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": str(e)})
        }
