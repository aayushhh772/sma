import os
import json
from supabase import create_client, Client

# --- YOUR SUPABASE CREDENTIALS ---
SUPABASE_URL = "https://bnhpestcxuisikkbhwkc.supabase.co"
SUPABASE_KEY = "sb_publishable_LjCEE0ik3tcJBPpPqcESPw_31ImMTle"
# ---------------------------------

local_cache_file = "data.json"

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception:
    supabase = None


def push_cloud_data(data_dict):
    """Pushes new notices/substitutions from the Admin Panel instantly to the cloud."""
    # Always save locally first as a backup
    with open(local_cache_file, "w") as f:
        json.dump(data_dict, f, indent=4)

    if supabase:
        try:
            # Using upsert instead of update so it automatically creates row id=1 if it's missing
            supabase.table("school_data").upsert({"id": 1, "payload": data_dict}).execute()
        except Exception as e:
            print(f"Cloud push failed, saved locally only: {e}")


def fetch_network_data(data_filename="data.json"):
    """Called by Smart Boards to fetch the latest schedule/notices from the cloud."""
    if supabase:
        try:
            response = supabase.table("school_data").select("payload").eq("id", 1).execute()
            if response.data and len(response.data) > 0:
                cloud_data = response.data[0].get("payload")
                if cloud_data:
                    # Fixed the malformed json.json check
                    with open(data_filename, "w") as f:
                        json.dump(cloud_data, f, indent=4)
                    return cloud_data
        except Exception as e:
            print(f"Cloud fetch failed, using local cache: {e}")

    # Fallback to local file if offline
    if os.path.exists(data_filename):
        try:
            with open(data_filename, "r") as f:
                return json.load(f)
        except Exception:
            pass

    return {}
