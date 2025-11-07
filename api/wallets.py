import os
import json
import requests

def handler(event, context):
    try:
        SUPABASE_URL = os.environ.get("SUPABASE_URL")
        SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

        if not SUPABASE_URL or not SUPABASE_KEY:
            raise Exception("Missing SUPABASE_URL or SUPABASE_KEY")

        # --- Get wallet data from Supabase REST API ---
        rest_url = f"{SUPABASE_URL}/rest/v1/wallets?select=*"
        headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json"
        }

        response = requests.get(rest_url, headers=headers, timeout=15)
        if response.status_code != 200:
            raise Exception(f"Supabase request failed: {response.text}")

        wallets = response.json()

        # --- Get LTC price from CoinGecko ---
        price_res = requests.get(
            "https://api.coingecko.com/api/v3/simple/price?ids=litecoin&vs_currencies=usd",
            timeout=10
        )
        price_data = price_res.json() if price_res.ok else {}
        ltc_price = float(price_data.get("litecoin", {}).get("usd", 0))

        # --- Calculate total balance ---
        total = 0.0
        for w in wallets:
            try:
                total += float(w.get("balance", 0))
            except:
                pass

        # --- Build final data ---
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Cache-Control": "no-cache"
            },
            "body": json.dumps({
                "wallets": [{"address": w["address"], "balance": float(w["balance"])} for w in wallets],
                "count": len(wallets),
                "total_balance": round(total, 8),
                "ltc_price": round(ltc_price, 2)
            })
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": str(e)})
        }
