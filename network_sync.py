import os
import json
import datetime
import uuid
from supabase import create_client, Client

SUPABASE_URL = "https://bnhpestcxuisikkbhwkc.supabase.co"
SUPABASE_KEY = "sb_publishable_LjCEE0ik3tcJBPpPqcESPw_31ImMTle"

NOTICE_BUCKET = "notice"

local_cache_file = "data.json"
attendance_sync_file = "attendance_sync.json"

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    print(f"Supabase initialization failed: {e}")
    supabase = None

realtime_channel = None
attendance_realtime_channel = None


# ============================================================
# EXISTING SCHOOL DATA FUNCTIONS
# DO NOT CHANGE THEIR PURPOSE
# ============================================================
def upload_notice_pdf(pdf_path):
    """
    Uploads a notice PDF to Supabase Storage and returns
    the cloud URL that can be used by other devices.
    """

    if not pdf_path:
        return None

    if not os.path.isfile(pdf_path):
        print(f"PDF file not found: {pdf_path}")
        return None

    if not supabase:
        print("Supabase unavailable. PDF upload skipped.")
        return None

    try:
        original_name = os.path.basename(pdf_path)

        # Create a unique filename so different notices
        # never overwrite each other.
        unique_name = f"{uuid.uuid4().hex}_{original_name}"

        storage_path = f"notices/{unique_name}"

        with open(pdf_path, "rb") as pdf_file:
            pdf_bytes = pdf_file.read()

        supabase.storage.from_(NOTICE_BUCKET).upload(
            storage_path,
            pdf_bytes,
            {
                "content-type": "application/pdf",
                "upsert": "true"
            }
        )

        public_url = (
            supabase
            .storage
            .from_(NOTICE_BUCKET)
            .get_public_url(storage_path)
        )

        print("PDF uploaded successfully.")
        print("Storage path:", storage_path)
        print("PDF URL:", public_url)

        return public_url

    except Exception as e:
        print(f"PDF upload failed: {e}")
        return None

def push_cloud_data(data_dict):
    """
    Pushes notices/substitutions from the Admin Panel to Supabase.

    PDFs are uploaded to Supabase Storage first.
    The notice then stores the cloud PDF URL instead
    of the computer's local PDF path.
    """

    try:
        # Make a separate copy so the original data structure
        # is not unexpectedly modified while uploading.
        cloud_data = json.loads(json.dumps(data_dict))

        # --------------------------------------------------------
        # UPLOAD NOTICE PDFs
        # --------------------------------------------------------

        notices = cloud_data.get("notices", [])

        for notice in notices:

            pdf_value = notice.get("pdf")

            if not pdf_value:
                continue

            # Only upload if this is still a local file.
            # If it is already an http/https URL, leave it alone.
            if isinstance(pdf_value, str) and pdf_value.startswith(("http://", "https://")):
                continue

            if os.path.isfile(pdf_value):

                pdf_url = upload_notice_pdf(pdf_value)

                if pdf_url:
                    notice["pdf"] = pdf_url

        # --------------------------------------------------------
        # SAVE CLOUD-READY DATA TO LOCAL CACHE
        # --------------------------------------------------------

        try:
            with open(local_cache_file, "w", encoding="utf-8") as f:
                json.dump(cloud_data, f, indent=4)

        except Exception as e:
            print(f"Local cache save failed: {e}")

        # --------------------------------------------------------
        # SEND NOTICE/SUBSTITUTION DATA TO SUPABASE
        # --------------------------------------------------------

        if supabase:

            try:

                supabase.table("school_data").upsert(
                    {
                        "id": 1,
                        "payload": cloud_data
                    }
                ).execute()

                print("Cloud data pushed successfully.")

            except Exception as e:

                print(
                    f"Cloud push failed, saved locally only: {e}"
                )

    except Exception as e:

        print(f"Cloud data processing failed: {e}")

def fetch_network_data(data_filename="data.json"):
    """Fetches the latest school_data payload."""

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


# ============================================================
# EXISTING SCHOOL DATA REALTIME
# ============================================================

def listen_for_updates(on_update_callback, data_filename="data.json"):
    """
    Listens for changes to school_data.

    This keeps notices and substitutions synchronized
    while the APK is open.
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


# ============================================================
# ATTENDANCE SYNCHRONIZATION
# ============================================================

def _load_last_attendance_sync():
    """
    Reads the timestamp of the last successful attendance sync.
    """

    try:

        if os.path.exists(attendance_sync_file):

            with open(attendance_sync_file, "r", encoding="utf-8") as f:
                data = json.load(f)

                return data.get("last_sync")

    except Exception as e:

        print(f"Could not read attendance sync timestamp: {e}")

    return None


def _save_last_attendance_sync(timestamp):
    """
    Saves the timestamp after a successful attendance synchronization.
    """

    try:

        with open(attendance_sync_file, "w", encoding="utf-8") as f:

            json.dump(
                {
                    "last_sync": timestamp
                },
                f,
                indent=4
            )

    except Exception as e:

        print(f"Could not save attendance sync timestamp: {e}")


def fetch_attendance_catchup():
    """
    Called when the APK starts.

    Downloads attendance records created since the last
    successful synchronization.

    If this is the first run, today's attendance is downloaded.
    """

    if not supabase:
        print("Supabase unavailable. Attendance catch-up skipped.")
        return []

    try:

        last_sync = _load_last_attendance_sync()

        query = (
            supabase
            .table("attendance")
            .select("*")
            .order("created_at", desc=False)
        )

        if last_sync:

            query = query.gt("created_at", last_sync)

            print(
                f"Fetching attendance created after {last_sync}"
            )

        else:

            today = datetime.datetime.now().date().isoformat()

            query = query.eq("attendance_date", today)

            print(
                f"First attendance sync. Fetching today's attendance: {today}"
            )

        response = query.execute()

        records = response.data or []

        now_utc = datetime.datetime.now(
            datetime.timezone.utc
        ).isoformat()

        _save_last_attendance_sync(now_utc)

        print(
            f"Attendance catch-up complete: {len(records)} record(s)"
        )

        return records

    except Exception as e:

        print(
            f"Attendance catch-up failed: {e}"
        )

        return []


def fetch_today_attendance():
    """
    Gets all attendance for today.

    This is used for the attendance display.
    It does NOT delete old attendance from Supabase.
    """

    if not supabase:
        return []

    try:

        today = datetime.datetime.now().date().isoformat()

        response = (
            supabase
            .table("attendance")
            .select("*")
            .eq("attendance_date", today)
            .order("created_at", desc=False)
            .execute()
        )

        return response.data or []

    except Exception as e:

        print(
            f"Today's attendance fetch failed: {e}"
        )

        return []


def listen_for_attendance_updates(on_update_callback):
    """
    Listens to the existing attendance table.

    When the Admin Panel or another device creates/updates
    attendance, the APK receives the change immediately.
    """

    global attendance_realtime_channel

    if not supabase:

        print(
            "Supabase unavailable. Attendance realtime disabled."
        )

        return

    def handle_attendance_change(payload):

        try:

            if hasattr(payload, "get"):

                new_record = payload.get(
                    "new",
                    {}
                ) or {}

            else:

                new_record = {}

            if not new_record:

                return

            try:

                on_update_callback(new_record)

            except Exception as e:

                print(
                    f"Attendance UI callback failed: {e}"
                )

        except Exception as e:

            print(
                f"Attendance realtime processing error: {e}"
            )

    try:

        if attendance_realtime_channel is not None:

            try:

                supabase.remove_channel(
                    attendance_realtime_channel
                )

            except Exception:

                pass

            attendance_realtime_channel = None

        attendance_realtime_channel = (
            supabase.channel(
                "attendance_realtime"
            )
        )

        attendance_realtime_channel.on_postgres_changes(
            event="*",
            schema="public",
            table="attendance",
            callback=handle_attendance_change
        )

        attendance_realtime_channel.subscribe()

        print(
            "Listening for real-time attendance updates..."
        )

    except Exception as e:

        print(
            f"Failed to start attendance realtime listener: {e}"
        )

        attendance_realtime_channel = None
