# api/wallets.py
import os
import json
from supabase import create_client

# Load Supabase
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

if not url or not key:
    def handler(event, context):
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Supabase not configured"})
        }
else:
    supabase = create_client(url, key)

def handler(event, context):
    try:
        if not supabase:
            raise Exception("Supabase client not initialized")

        result = supabase.table('wallets').select('*').execute()
        wallets = result.data

        total_balance = sum(float(w.get('balance', 0)) for w in wallets)

        return {
            "statusCode": 200,
            "headers": { "Content-Type": "application/json" },
            "body": json.dumps({
                "wallets": [
                    {
                        "address": w['address'],
                        "balance": round(float(w['balance']), 8)
                    }
                    for w in wallets
                ],
                "count": len(wallets),
                "total_balance": round(total_balance, 8)
            })
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
