import os
import json
import datetime
import uuid
import asyncio
import threading
from urllib.parse import urlparse
from urllib.request import urlopen, Request

from supabase import (
    create_client,
    acreate_client,
    Client,
    AsyncClient,
)


SUPABASE_URL = (
    "https://bnhpestcxuisikkbhwkc.supabase.co"
)

SUPABASE_KEY = (
    "sb_publishable_LjCEE0ik3tcJBPpPqcESPw_31ImMTle"
)

NOTICE_BUCKET = "notices"

local_cache_file = "data.json"
attendance_sync_file = "attendance_sync.json"


try:

    supabase: Client = create_client(
        SUPABASE_URL,
        SUPABASE_KEY
    )

except Exception as e:

    print(
        f"Supabase initialization failed: {e}"
    )

    supabase = None



realtime_channel = None
attendance_realtime_channel = None

_realtime_threads = []
_realtime_stop_events = []

# Local mirror of cloud PDFs so the existing PyQt test.py can continue
# to use QDesktopServices.fromLocalFile() exactly as before.
PDF_CACHE_FOLDER = "pdfs"


def _ensure_pdf_cache_folder():
    try:
        os.makedirs(
            PDF_CACHE_FOLDER,
            exist_ok=True
        )
    except Exception as error:
        print(
            f"Could not create PDF cache folder: {error}"
        )


def _safe_pdf_filename(
    notice
):
    pdf_name = notice.get(
        "pdf_name"
    )

    if pdf_name:
        return os.path.basename(
            str(pdf_name)
        )

    pdf_value = notice.get(
        "pdf"
    )

    if pdf_value:
        parsed = urlparse(
            str(pdf_value)
        )

        name = os.path.basename(
            parsed.path
        )

        if name:
            return name

    return "notice_attachment.pdf"


def _materialize_notice_pdfs(
    cloud_data
):
    """
    Keep the cloud URL in pdf_url, but make pdf point to a local
    cached copy so the existing test.py NoticeCard can open it
    with QDesktopServices.fromLocalFile() without changing test.py.
    """
    if not isinstance(
        cloud_data,
        dict
    ):
        return cloud_data

    _ensure_pdf_cache_folder()

    notices = cloud_data.get(
        "notices",
        []
    )

    if not isinstance(
        notices,
        list
    ):
        return cloud_data

    for notice in notices:

        if not isinstance(
            notice,
            dict
        ):
            continue

        pdf_value = notice.get(
            "pdf"
        )

        if not isinstance(
            pdf_value,
            str
        ):
            continue

        if not pdf_value.startswith(
            (
                "http://",
                "https://"
            )
        ):
            continue

        try:

            file_name = _safe_pdf_filename(
                notice
            )

            destination = os.path.join(
                PDF_CACHE_FOLDER,
                file_name
            )

            # Add a collision-safe prefix using the URL path so two
            # different cloud objects with the same filename do not
            # overwrite one another.
            parsed = urlparse(
                pdf_value
            )

            cloud_basename = os.path.basename(
                parsed.path
            )

            if cloud_basename:
                file_name = os.path.basename(
                    cloud_basename
                )

            destination = os.path.join(
                PDF_CACHE_FOLDER,
                file_name
            )

            should_download = True

            if os.path.isfile(
                destination
            ):

                try:

                    should_download = (
                        os.path.getsize(
                            destination
                        ) == 0
                    )

                except Exception:

                    should_download = True

            if should_download:

                request = Request(
                    pdf_value,
                    headers={
                        "User-Agent":
                            "SOS-School-PDF-Cache/1.0"
                    }
                )

                with urlopen(
                    request,
                    timeout=30
                ) as response:

                    content = response.read()

                if not content:
                    raise ValueError(
                        "Cloud PDF response was empty."
                    )

                with open(
                    destination,
                    "wb"
                ) as pdf_file:

                    pdf_file.write(
                        content
                    )

            notice["pdf_url"] = pdf_value
            notice["pdf_local"] = os.path.abspath(
                destination
            )
            notice["pdf_name"] = (
                notice.get(
                    "pdf_name"
                )
                or os.path.basename(
                    destination
                )
            )

            # IMPORTANT:
            # test.py already expects notice["pdf"] to be a local path.
            notice["pdf"] = os.path.abspath(
                destination
            )

        except Exception as error:

            print(
                "Could not cache notice PDF "
                f"{pdf_value}: {error}"
            )

    return cloud_data

_realtime_stop_events = []


# ============================================================
# EXISTING SCHOOL DATA FUNCTIONS
# ============================================================

def upload_notice_pdf(pdf_path):

    if not pdf_path:
        return None

    if not os.path.isfile(pdf_path):

        print(
            f"PDF file not found: {pdf_path}"
        )

        return None

    if not supabase:

        print(
            "Supabase unavailable. PDF upload skipped."
        )

        return None

    try:

        original_name = os.path.basename(
            pdf_path
        )

        unique_name = (
            f"{uuid.uuid4().hex}_{original_name}"
        )

        storage_path = (
            f"notices/{unique_name}"
        )

        with open(
            pdf_path,
            "rb"
        ) as pdf_file:

            pdf_bytes = pdf_file.read()

        if not pdf_bytes:

            print(
                "PDF upload failed: selected PDF is empty."
            )

            return None

        upload_result = (
            supabase
            .storage
            .from_(NOTICE_BUCKET)
            .upload(
                storage_path,
                pdf_bytes,
                {
                    "content-type": "application/pdf",
                    "upsert": "false"
                }
            )
        )

        print(
            "PDF upload result:",
            upload_result
        )

        public_url = (
            supabase
            .storage
            .from_(NOTICE_BUCKET)
            .get_public_url(
                storage_path
            )
        )

        print(
            "PDF uploaded successfully."
        )

        print(
            "Bucket:",
            NOTICE_BUCKET
        )

        print(
            "Storage path:",
            storage_path
        )

        print(
            "Public URL:",
            public_url
        )

        return public_url

    except Exception as e:

        print(
            "========================================"
        )
        print(
            "PDF UPLOAD FAILED"
        )
        print(
            "========================================"
        )
        print(
            f"Bucket: {NOTICE_BUCKET}"
        )
        print(
            f"PDF path: {pdf_path}"
        )
        print(
            f"Error: {e}"
        )
        print(
            "========================================"
        )

        return None


def push_cloud_data(data_dict):

    try:

        cloud_data = json.loads(
            json.dumps(data_dict)
        )

        notices = cloud_data.get(
            "notices",
            []
        )

        for notice in notices:

            if not isinstance(
                notice,
                dict
            ):
                continue

            pdf_value = notice.get(
                "pdf"
            )

            if not pdf_value:
                continue

            if (
                isinstance(pdf_value, str)
                and pdf_value.startswith(
                    ("http://", "https://")
                )
            ):
                continue

            if (
                isinstance(pdf_value, str)
                and os.path.isfile(pdf_value)
            ):

                pdf_url = upload_notice_pdf(
                    pdf_value
                )

                if pdf_url:

                    notice["pdf"] = (
                        pdf_url
                    )

                    notice["pdf_name"] = (
                        os.path.basename(
                            pdf_value
                        )
                    )

        for notice in notices:

            if not isinstance(
                notice,
                dict
            ):
                continue

            pdf_local = notice.get(
                "pdf_local"
            )

            current_pdf = notice.get(
                "pdf"
            )

            current_is_url = (
                isinstance(
                    current_pdf,
                    str
                )
                and current_pdf.startswith(
                    ("http://", "https://")
                )
            )

            if (
                not current_is_url
                and pdf_local
                and isinstance(pdf_local, str)
                and os.path.isfile(pdf_local)
            ):

                pdf_url = upload_notice_pdf(
                    pdf_local
                )

                if pdf_url:

                    notice["pdf"] = (
                        pdf_url
                    )

                    notice["pdf_name"] = (
                        os.path.basename(
                            pdf_local
                        )
                    )

        try:

            with open(
                local_cache_file,
                "w",
                encoding="utf-8"
            ) as f:

                json.dump(
                    cloud_data,
                    f,
                    indent=4,
                    ensure_ascii=False
                )

        except Exception as e:

            print(
                f"Local cache save failed: {e}"
            )

        if supabase:

            try:

                (
                    supabase
                    .table("school_data")
                    .upsert(
                        {
                            "id": 1,
                            "payload": cloud_data
                        }
                    )
                    .execute()
                )

                print(
                    "Cloud data pushed successfully."
                )

            except Exception as e:

                print(
                    "Cloud push failed, saved locally only: "
                    f"{e}"
                )

    except Exception as e:

        print(
            f"Cloud data processing failed: {e}"
        )


def fetch_network_data(
    data_filename="data.json"
):

    if supabase:

        try:

            response = (
                supabase
                .table("school_data")
                .select("payload")
                .eq("id", 1)
                .execute()
            )

            if (
                response.data
                and len(response.data) > 0
            ):

                cloud_data = (
                    response
                    .data[0]
                    .get("payload")
                )

                if cloud_data is not None:

                    cloud_data = _materialize_notice_pdfs(cloud_data)

                    try:

                        with open(
                            data_filename,
                            "w",
                            encoding="utf-8"
                        ) as f:

                            json.dump(
                                cloud_data,
                                f,
                                indent=4,
                                ensure_ascii=False
                            )

                    except Exception as e:

                        print(
                            "Error saving cloud cache: "
                            f"{e}"
                        )

                    return cloud_data

        except Exception as e:

            print(
                "Cloud fetch failed, using local cache: "
                f"{e}"
            )

    if os.path.exists(
        data_filename
    ):

        try:

            with open(
                data_filename,
                "r",
                encoding="utf-8"
            ) as f:

                return json.load(f)

        except Exception as e:

            print(
                f"Local cache read failed: {e}"
            )

    return {}


# ============================================================
# EXISTING SCHOOL DATA REALTIME
# Now implemented with Supabase async client.
# Public function names are unchanged.
# ============================================================

def _extract_realtime_record(payload):

    if not payload:
        return {}

    if hasattr(
        payload,
        "get"
    ):

        data = (
            payload.get(
                "data",
                {}
            )
            or {}
        )

        if isinstance(
            data,
            dict
        ):

            record = data.get(
                "record"
            )

            if isinstance(
                record,
                dict
            ):

                return record

        new_record = (
            payload.get(
                "new",
                {}
            )
            or {}
        )

        if isinstance(
            new_record,
            dict
        ):

            return new_record

    return {}


async def _school_data_realtime_loop(
    on_update_callback,
    data_filename,
    stop_event
):

    client = None
    channel = None

    try:

        client: AsyncClient = (
            await acreate_client(
                SUPABASE_URL,
                SUPABASE_KEY
            )
        )

        async def handle_change(
            payload
        ):

            try:

                new_record = (
                    _extract_realtime_record(
                        payload
                    )
                )

                if not new_record:
                    return

                record_id = (
                    new_record.get(
                        "id"
                    )
                )

                if str(
                    record_id
                ) != "1":

                    return

                cloud_data = (
                    new_record.get(
                        "payload"
                    )
                )

                if cloud_data is None:
                    return

                try:

                    with open(
                        data_filename,
                        "w",
                        encoding="utf-8"
                    ) as f:

                        json.dump(
                            cloud_data,
                            f,
                            indent=4,
                            ensure_ascii=False
                        )

                except Exception as e:

                    print(
                        "Error saving realtime cache: "
                        f"{e}"
                    )

                try:

                    on_update_callback(
                        cloud_data
                    )

                except Exception as e:

                    print(
                        "Realtime UI callback failed: "
                        f"{e}"
                    )

            except Exception as e:

                print(
                    "Error processing realtime update: "
                    f"{e}"
                )

        channel = (
            client
            .channel(
                "school_data_realtime"
            )
        )

        channel = (
            channel
            .on_postgres_changes(
                event="*",
                schema="public",
                table="school_data",
                callback=handle_change
            )
        )

        await channel.subscribe()

        print(
            "Listening for real-time "
            "notice/substitution updates..."
        )

        while not stop_event.is_set():

            await asyncio.sleep(
                1
            )

    except Exception as e:

        print(
            "Failed to start realtime listener: "
            f"{e}"
        )

    finally:

        if channel is not None:

            try:

                await channel.unsubscribe()

            except Exception:

                pass

        if client is not None:

            try:

                await client.close()

            except Exception:

                pass


def _run_school_data_realtime(
    on_update_callback,
    data_filename,
    stop_event
):

    try:

        asyncio.run(
            _school_data_realtime_loop(
                on_update_callback,
                data_filename,
                stop_event
            )
        )

    except Exception as e:

        print(
            "School realtime thread error: "
            f"{e}"
        )


def listen_for_updates(
    on_update_callback,
    data_filename="data.json"
):

    stop_event = threading.Event()

    thread = threading.Thread(
        target=_run_school_data_realtime,
        args=(
            on_update_callback,
            data_filename,
            stop_event
        ),
        daemon=True,
        name="SchoolSupabaseRealtime"
    )

    _realtime_stop_events.append(
        stop_event
    )

    _realtime_threads.append(
        thread
    )

    thread.start()

    print(
        "Supabase async school-data "
        "realtime listener started."
    )


# ============================================================
# ATTENDANCE SYNCHRONIZATION
# ============================================================

def _load_last_attendance_sync():

    try:

        if os.path.exists(
            attendance_sync_file
        ):

            with open(
                attendance_sync_file,
                "r",
                encoding="utf-8"
            ) as f:

                data = json.load(
                    f
                )

                return data.get(
                    "last_sync"
                )

    except Exception as e:

        print(
            "Could not read attendance "
            f"sync timestamp: {e}"
        )

    return None


def _save_last_attendance_sync(
    timestamp
):

    try:

        with open(
            attendance_sync_file,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                {
                    "last_sync":
                        timestamp
                },
                f,
                indent=4
            )

    except Exception as e:

        print(
            "Could not save attendance "
            f"sync timestamp: {e}"
        )


def fetch_attendance_catchup():

    if not supabase:

        print(
            "Supabase unavailable. "
            "Attendance catch-up skipped."
        )

        return []

    try:

        last_sync = (
            _load_last_attendance_sync()
        )

        query = (
            supabase
            .table("attendance")
            .select("*")
            .order(
                "created_at",
                desc=False
            )
        )

        if last_sync:

            query = query.gt(
                "created_at",
                last_sync
            )

            print(
                "Fetching attendance created "
                f"after {last_sync}"
            )

        else:

            today = (
                datetime.datetime
                .now()
                .date()
                .isoformat()
            )

            query = query.eq(
                "attendance_date",
                today
            )

            print(
                "First attendance sync. "
                "Fetching today's attendance: "
                f"{today}"
            )

        response = (
            query.execute()
        )

        records = (
            response.data or []
        )

        now_utc = (
            datetime.datetime
            .now(
                datetime.timezone.utc
            )
            .isoformat()
        )

        _save_last_attendance_sync(
            now_utc
        )

        print(
            "Attendance catch-up complete: "
            f"{len(records)} record(s)"
        )

        return records

    except Exception as e:

        print(
            f"Attendance catch-up failed: {e}"
        )

        return []


def fetch_today_attendance():

    if not supabase:

        return []

    try:

        today = (
            datetime.datetime
            .now()
            .date()
            .isoformat()
        )

        response = (
            supabase
            .table("attendance")
            .select("*")
            .eq(
                "attendance_date",
                today
            )
            .order(
                "created_at",
                desc=False
            )
            .execute()
        )

        return response.data or []

    except Exception as e:

        print(
            f"Today's attendance fetch failed: {e}"
        )

        return []


# ============================================================
# ATTENDANCE REALTIME
# Now implemented with Supabase async client.
# Public function name is unchanged.
# ============================================================

async def _attendance_realtime_loop(
    on_update_callback,
    stop_event
):

    client = None
    channel = None

    try:

        client: AsyncClient = (
            await acreate_client(
                SUPABASE_URL,
                SUPABASE_KEY
            )
        )

        async def handle_attendance_change(
            payload
        ):

            try:

                new_record = (
                    _extract_realtime_record(
                        payload
                    )
                )

                if not new_record:
                    return

                try:

                    on_update_callback(
                        new_record
                    )

                except Exception as e:

                    print(
                        "Attendance UI callback failed: "
                        f"{e}"
                    )

            except Exception as e:

                print(
                    "Attendance realtime processing error: "
                    f"{e}"
                )

        channel = (
            client
            .channel(
                "attendance_realtime"
            )
        )

        channel = (
            channel
            .on_postgres_changes(
                event="*",
                schema="public",
                table="attendance",
                callback=handle_attendance_change
            )
        )

        await channel.subscribe()

        print(
            "Listening for real-time "
            "attendance updates..."
        )

        while not stop_event.is_set():

            await asyncio.sleep(
                1
            )

    except Exception as e:

        print(
            "Failed to start attendance "
            f"realtime listener: {e}"
        )

    finally:

        if channel is not None:

            try:

                await channel.unsubscribe()

            except Exception:

                pass

        if client is not None:

            try:

                await client.close()

            except Exception:

                pass


def _run_attendance_realtime(
    on_update_callback,
    stop_event
):

    try:

        asyncio.run(
            _attendance_realtime_loop(
                on_update_callback,
                stop_event
            )
        )

    except Exception as e:

        print(
            "Attendance realtime thread error: "
            f"{e}"
        )


def listen_for_attendance_updates(
    on_update_callback
):

    stop_event = threading.Event()

    thread = threading.Thread(
        target=_run_attendance_realtime,
        args=(
            on_update_callback,
            stop_event
        ),
        daemon=True,
        name="AttendanceSupabaseRealtime"
    )

    _realtime_stop_events.append(
        stop_event
    )

    _realtime_threads.append(
        thread
    )

    thread.start()

    print(
        "Supabase async attendance "
        "realtime listener started."
    )
