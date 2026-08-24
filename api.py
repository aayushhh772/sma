import os
import json
import tempfile

from fastapi import (
    FastAPI,
    HTTPException,
    UploadFile,
    File,
    Request,
)

from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

import database
import network_sync


BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

DATA_FILE = os.path.join(
    BASE_DIR,
    "data.json"
)

CREDENTIALS_FILE = os.path.join(
    BASE_DIR,
    "admin_credentials.json"
)


app = FastAPI(
    title="SOS School API",
    version="1.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# LOCAL DATA HELPERS
# ============================================================

def read_local_data():

    if not os.path.exists(DATA_FILE):
        return {}

    try:

        with open(
            DATA_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            return json.load(f)

    except Exception:

        return {}


# ============================================================
# HEALTH
# ============================================================

@app.get("/api/health")
def health():

    return {
        "success": True,
        "service": "SOS School API",
        "database": (
            "available"
            if database.supabase
            else "unavailable"
        ),
        "network_sync": (
            "available"
            if network_sync.supabase
            else "unavailable"
        )
    }


# ============================================================
# SCHOOL DATA
#
# Accept BOTH:
#   {"payload": {...}}
# and:
#   {"data": {...}}
#
# This keeps compatibility with both old and new frontends.
# ============================================================

@app.get("/api/admin/data")
def get_admin_data():

    try:

        data = network_sync.fetch_network_data(
            DATA_FILE
        )

        return {
            "success": True,
            "data": data or {}
        }

    except Exception as error:

        return {
            "success": True,
            "data": read_local_data(),
            "fallback": True,
            "error": str(error)
        }


@app.post("/api/admin/data")
async def save_admin_data(
    request: Request
):

    try:

        body = await request.json()

    except Exception as error:

        raise HTTPException(
            status_code=400,
            detail=f"Invalid JSON body: {error}"
        )


    if not isinstance(body, dict):

        raise HTTPException(
            status_code=400,
            detail="Request body must be a JSON object."
        )


    # Preferred schema.
    data = body.get("payload")

    # Backward-compatible schema.
    if data is None:
        data = body.get("data")


    if not isinstance(data, dict):

        raise HTTPException(
            status_code=422,
            detail=(
                "Missing school data. "
                "Send JSON as {\"payload\": {...}}."
            )
        )


    try:

        # This is the same cloud synchronization path
        # used by the original Python admin panel.
        network_sync.push_cloud_data(
            data
        )


        # Read the actual cloud/cache copy back so the
        # response contains the synchronized representation.
        synchronized = (
            network_sync.fetch_network_data(
                DATA_FILE
            )
            or
            data
        )


        return {
            "success": True,
            "message":
                "School data synchronized to Supabase.",
            "data":
                synchronized
        }


    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )


# ============================================================
# PDF UPLOAD
# ============================================================

@app.post("/api/admin/upload-pdf")
async def upload_pdf(
    file: UploadFile = File(...)
):

    if not file.filename:

        raise HTTPException(
            status_code=400,
            detail="No PDF file supplied."
        )


    if not file.filename.lower().endswith(".pdf"):

        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed."
        )


    temporary_path = None


    try:

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".pdf"
        ) as temp_file:

            temporary_path = temp_file.name

            content = await file.read()

            if not content:

                raise ValueError(
                    "Uploaded PDF is empty."
                )

            temp_file.write(
                content
            )


        pdf_url = (
            network_sync
            .upload_notice_pdf(
                temporary_path
            )
        )


        if not pdf_url:

            raise RuntimeError(
                "network_sync.upload_notice_pdf() returned None. "
                "Check the Supabase Storage bucket and permissions."
            )


        return {
            "success": True,
            "filename": file.filename,
            "pdf_name": file.filename,
            "url": pdf_url
        }


    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )


    finally:

        if (
            temporary_path
            and
            os.path.exists(
                temporary_path
            )
        ):

            try:
                os.remove(
                    temporary_path
                )
            except Exception:
                pass


# ============================================================
# CREDENTIALS
# ============================================================

@app.get("/api/admin/credentials")
def get_credentials():

    if os.path.exists(
        CREDENTIALS_FILE
    ):

        try:

            with open(
                CREDENTIALS_FILE,
                "r",
                encoding="utf-8"
            ) as f:

                return json.load(f)

        except Exception:
            pass


    return {
        "admin_id": "SOSADMIN1",
        "password": "ADMIN404"
    }


@app.post("/api/admin/credentials")
async def save_credentials(
    request: Request
):

    try:

        data = await request.json()

    except Exception as error:

        raise HTTPException(
            status_code=400,
            detail=f"Invalid JSON body: {error}"
        )


    admin_id = str(
        data.get(
            "admin_id",
            ""
        )
    ).strip()


    password = str(
        data.get(
            "password",
            ""
        )
    ).strip()


    if not admin_id or not password:

        raise HTTPException(
            status_code=400,
            detail=(
                "Admin ID and Password cannot be empty."
            )
        )


    with open(
        CREDENTIALS_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            {
                "admin_id": admin_id,
                "password": password
            },
            f,
            indent=4
        )


    return {
        "success": True
    }


# ============================================================
# ATTENDANCE DISPLAY
# ============================================================

@app.get("/api/attendance/display")
def attendance_display(
    class_number: str,
    section: str,
    attendance_date: str
):

    try:

        result = (
            database
            .get_attendance_for_display(
                class_number,
                section,
                attendance_date
            )
        )


        return {
            "success": True,
            "data": result
        }


    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )


# ============================================================
# ATTENDANCE HISTORY
# ============================================================

@app.get("/api/attendance/history")
def attendance_history(
    class_number: str | None = None,
    section: str | None = None,
    attendance_date: str | None = None
):

    try:

        result = (
            database
            .get_attendance_history(
                class_number=class_number,
                section=section,
                attendance_date=attendance_date
            )
        )


        return {
            "success": True,
            "data": result
        }


    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )


# ============================================================
# STUDENTS
# ============================================================

@app.get("/api/students")
def students(
    class_number: str | None = None,
    section: str | None = None
):

    try:

        result = (
            database
            .get_students(
                class_number=class_number,
                section=section
            )
        )


        return {
            "success": True,
            "data": result
        }


    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )


# ============================================================
# ONE STUDENT
# ============================================================

@app.get("/api/students/{student_id}")
def student(
    student_id: str
):

    try:

        result = (
            database
            .get_student(
                student_id
            )
        )


        return {
            "success": True,
            "data": result
        }


    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )


# ============================================================
# DATABASE TEST
# ============================================================

@app.get("/api/database/test")
def database_test():

    try:

        database.test_database_connection()

        return {
            "success": True,
            "message":
                "Supabase connection successful."
        }


    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )



# ============================================================
# PORTAL ENTRY
# ============================================================

@app.get("/")
def portal_entry():

    portal_path = os.path.join(
        BASE_DIR,
        "adminpage.html"
    )

    if os.path.isfile(
        portal_path
    ):

        from fastapi.responses import FileResponse

        return FileResponse(
            portal_path,
            media_type="text/html"
        )

    admin_panel_path = os.path.join(
        BASE_DIR,
        "admin_panel.html"
    )

    if os.path.isfile(
        admin_panel_path
    ):

        from fastapi.responses import FileResponse

        return FileResponse(
            admin_panel_path,
            media_type="text/html"
        )

    return {
        "success": True,
        "service": "SOS School API"
    }


# ============================================================
# STATIC WEBSITE
# MUST BE LAST
# ============================================================

app.mount(
    "/",
    StaticFiles(
        directory=BASE_DIR,
        html=True
    ),
    name="website"
)
