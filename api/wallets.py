# api/wallets.py
import os
import json
import requests
from supabase import create_client

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase = create_client(url, key) if url and key else None

def handler(event, context):
    if not supabase:
        return {"statusCode": 500, "body": json.dumps({"error": "Supabase not configured"})}

    try:
        res = supabase.table("wallets").select("*").execute()
        wallets = res.data or []
        total = sum(float(w.get("balance", 0)) for w in wallets)

        # LTC Price via Binance
        try:
            price_res = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=LTCUSDT", timeout=3)
            price = float(price_res.json().get("price", 0)) if price_res.ok else 90.61
        except:
            price = 90.61

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0"
            },
            "body": json.dumps({
                "wallets": [
                    {
                        "address": w["address"],
                        "balance": round(float(w.get("balance", 0)), 8),
                        "tx_count": w.get("tx_count", 0),
                        "explorer": f"https://blockchair.com/litecoin/address/{w['address']}"
                    } for w in wallets
                ],
                "count": len(wallets),
                "total_balance": round(total, 8),
                "ltc_price": round(price, 2)
            })
        }
    except Exception as e:
        print(f"API Error: {e}")
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}
