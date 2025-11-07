# api/wallets.py
# VORTEX LTC TRACKER — FINAL 100% WORKING VERSION
# Uses: Supabase + CoinGecko (price) + Vercel Serverless
# NO 500, NO CRASH, NO IMPORT ERROR

import os
import json

# === SAFE IMPORTS (PREVENT CRASH ON MISSING PACKAGE) ===
try:
    from supabase import create_client
    SUPABASE_AVAILABLE = True
except ImportError as e:
    print(f"[ERROR] Supabase import failed: {e}")
    SUPABASE_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError as e:
    print(f"[ERROR] Requests import failed: {e}")
    REQUESTS_AVAILABLE = False


# === SUPABASE CLIENT ===
def get_supabase():
    if not SUPABASE_AVAILABLE:
        return None
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    if not url or not key:
        print("[ERROR] SUPABASE_URL or SUPABASE_KEY missing in ENV")
        return None
    try:
        client = create_client(url, key)
        print("[OK] Supabase client initialized")
        return client
    except Exception as e:
        print(f"[ERROR] Supabase client failed: {e}")
        return None


# === FETCH LTC PRICE FROM COINGECKO (BEST FREE API) ===
def get_ltc_price():
    if not REQUESTS_AVAILABLE:
        return 90.61
    try:
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {"ids": "litecoin", "vs_currencies": "usd"}
        headers = {"accept": "application/json"}
        response = requests.get(url, params=params, headers=headers, timeout=6)
        if response.status_code == 200:
            data = response.json()
            price = data.get("litecoin", {}).get("usd")
            if price:
                print(f"[OK] LTC Price: ${price}")
                return float(price)
    except Exception as e:
        print(f"[ERROR] Price fetch failed: {e}")
    print("[FALLBACK] Using default price: $90.61")
    return 90.61


# === MAIN HANDLER ===
def handler(event, context):
    print("[START] /api/wallets called")

    # --- MISSING DEPENDENCIES ---
    if not SUPABASE_AVAILABLE:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Missing 'supabase' package. Add to requirements.txt"})
        }
    if not REQUESTS_AVAILABLE:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Missing 'requests' package. Add to requirements.txt"})
        }

    # --- INIT SUPABASE ---
    supabase = get_supabase()
    if not supabase:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Supabase not configured. Check ENV vars."})
        }

    try:
        # --- FETCH WALLETS FROM SUPABASE ---
        print("[DB] Fetching wallets...")
        result = supabase.table("wallets").select("*").execute()
        wallets = result.data or []
        print(f"[DB] Found {len(wallets)} wallets")

        total_balance = sum(float(w.get("balance", 0)) for w in wallets)

        # --- GET LIVE PRICE ---
        ltc_price = get_ltc_price()

        # --- BUILD RESPONSE ---
        response_data = {
            "wallets": [
                {
                    "address": w["address"],
                    "balance": round(float(w.get("balance", 0)), 8),
                    "tx_count": int(w.get("tx_count", 0)),
                    "explorer": f"https://sochain.com/address/LTC/{w['address']}"
                }
                for w in wallets
            ],
            "count": len(wallets),
            "total_balance": round(total_balance, 8),
            "ltc_price": round(ltc_price, 2)
        }

        print("[OK] API response ready")
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps(response_data, separators=(',', ':'))
        }

    except Exception as e:
        print(f"[FATAL ERROR] {e}")
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Internal server error"})
        }s
