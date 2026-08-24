import os
import json
from supabase import create_client, Client

SUPABASE_URL = "https://bnhpestcxuisikkbhwkc.supabase.co"
SUPABASE_KEY = "sb_publishable_LjCEE0ik3tcJBPpPqcESPw_31ImMTle"

local_cache_file = "data.json"

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    print(f"Supabase initialization failed: {e}")
    supabase = None

realtime_channel = None


def push_cloud_data(data_dict):
    """Pushes new notices/substitutions from the Admin Panel instantly to the cloud."""
    try:
        with open(local_cache_file, "w", encoding="utf-8") as f:
            json.dump(data_dict, f, indent=4)
    except Exception as e:
        print(f"Local cache save failed: {e}")

    if supabase:
        try:
            supabase.table("school_data").upsert(
                {
                    "id": 1,
                    "payload": data_dict
                }
            ).execute()
            print("Cloud data pushed successfully.")
        except Exception as e:
            print(f"Cloud push failed, saved locally only: {e}")


def fetch_network_data(data_filename="data.json"):
    """Called by Smart Boards to fetch the latest schedule/notices from the cloud."""
    if supabase:
        try:
            response = (
                supabase.table("school_data")
                .select("payload")
                .eq("id", 1)
                .execute()
            )

            if response.data and len(response.data) > 0:
                cloud_data = response.data[0].get("payload")

                if cloud_data is not None:
                    try:
                        with open(data_filename, "w", encoding="utf-8") as f:
                            json.dump(cloud_data, f, indent=4)
                    except Exception as e:
                        print(f"Error saving cloud cache: {e}")

                    return cloud_data

        except Exception as e:
            print(f"Cloud fetch failed, using local cache: {e}")

    if os.path.exists(data_filename):
        try:
            with open(data_filename, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Local cache read failed: {e}")

    return {}


def listen_for_updates(on_update_callback, data_filename="data.json"):
    """
    Subscribes to real-time changes on the 'school_data' table (id=1).
    When the admin pushes new data, this callback runs automatically.
    """
    global realtime_channel

    if not supabase:
        print("Supabase client is not initialized. Realtime disabled.")
        return

    def handle_change(payload):
        try:
            if hasattr(payload, "get"):
                new_record = payload.get("new", {}) or {}
            else:
                new_record = {}

            record_id = new_record.get("id")

            if str(record_id) != "1":
                return

            cloud_data = new_record.get("payload")

            if cloud_data is None:
                return

            try:
                with open(data_filename, "w", encoding="utf-8") as f:
                    json.dump(cloud_data, f, indent=4)
            except Exception as e:
                print(f"Error saving realtime cache: {e}")

            try:
                on_update_callback(cloud_data)
            except Exception as e:
                print(f"Realtime UI callback failed: {e}")

        except Exception as e:
            print(f"Error processing realtime update: {e}")

    try:
        if realtime_channel is not None:
            try:
                supabase.remove_channel(realtime_channel)
            except Exception:
                pass

            realtime_channel = None

        realtime_channel = supabase.channel("school_data_realtime")

        realtime_channel.on_postgres_changes(
            event="*",
            schema="public",
            table="school_data",
            callback=handle_change
        )

        realtime_channel.subscribe()

        print("Listening for real-time notice/substitution updates...")

    except Exception as e:
        print(f"Failed to start realtime listener: {e}")
        realtime_channel = None
