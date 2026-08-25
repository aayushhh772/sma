import re
from datetime import datetime, date
from zoneinfo import ZoneInfo

from school_calendar import is_school_holidayimport re
from datetime import datetime, date
from zoneinfo import ZoneInfo

from school_calendar import is_school_holiday
from supabase import create_client


# ============================================================
# SUPABASE CONFIGURATION
# ============================================================

SUPABASE_URL = "https://bnhpestcxuisikkbhwkc.supabase.co"

# IMPORTANT:
# Replace this with your NEW Supabase key after rotating the
# exposed key.
SUPABASE_KEY = "sb_publishable_LjCEE0ik3tcJBPpPqcESPw_31ImMTle"

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)


# ============================================================
# SYSTEM CONFIGURATION
# ============================================================

STUDENT_ID_PATTERN = re.compile(
    r"^[A-Z0-9]+$"
)

NEPAL_TIMEZONE = ZoneInfo(
    "Asia/Kathmandu"
)

# Students are automatically considered absent from 1 PM.
ABSENT_AFTER_HOUR = 13


VALID_CLASS_SECTIONS = {
    "6": ["A", "B"],
    "7": ["A", "B"],
    "8": ["A", "B"],
    "9": ["A", "B"],
    "10": ["A", "B"],
    "11": ["A", "B", "C", "D"],
    "12": ["A", "B", "C", "D"]
}


# ============================================================
# NORMALIZATION FUNCTIONS
# ============================================================

def normalize_student_id(student_id):

    return (
        str(student_id)
        .strip()
        .upper()
        .replace(" ", "")
    )


def normalize_class_number(class_number):

    return str(
        class_number
    ).strip()


def normalize_section(section):

    return (
        str(section)
        .strip()
        .upper()
    )


# ============================================================
# VALIDATION FUNCTIONS
# ============================================================

def validate_student_id(student_id):

    student_id = normalize_student_id(
        student_id
    )

    return bool(
        STUDENT_ID_PATTERN.fullmatch(
            student_id
        )
    )


def validate_class_section(
    class_number,
    section
):

    class_number = normalize_class_number(
        class_number
    )

    section = normalize_section(
        section
    )

    return (
        class_number in VALID_CLASS_SECTIONS
        and
        section in VALID_CLASS_SECTIONS[
            class_number
        ]
    )


# ============================================================
# DATE / TIME FUNCTIONS
# ============================================================

def get_nepal_now():

    return datetime.now(
        NEPAL_TIMEZONE
    )


def get_nepal_today():

    return get_nepal_now().date()


def normalize_attendance_date(
    attendance_date
):

    if attendance_date is None:

        return get_nepal_today().isoformat()

    if isinstance(
        attendance_date,
        datetime
    ):

        return attendance_date.date().isoformat()

    if isinstance(
        attendance_date,
        date
    ):

        return attendance_date.isoformat()

    return str(
        attendance_date
    ).strip()


# ============================================================
# SCHOOL CALENDAR
# ============================================================

def check_school_holiday(
    attendance_date
):

    attendance_date = normalize_attendance_date(
        attendance_date
    )

    try:

        parsed_date = datetime.strptime(
            attendance_date,
            "%Y-%m-%d"
        ).date()

        return bool(
            is_school_holiday(
                parsed_date
            )
        )

    except Exception:

        return False


# ============================================================
# CHECK WHETHER TODAY IS A SCHOOL DAY
# ============================================================

def is_school_day(
    attendance_date=None
):

    if attendance_date is None:

        attendance_date = get_nepal_today()

    if isinstance(
        attendance_date,
        str
    ):

        try:

            attendance_date = datetime.strptime(
                attendance_date,
                "%Y-%m-%d"
            ).date()

        except ValueError:

            return False

    return not is_school_holiday(
        attendance_date
    )


# ============================================================
# GET ALL ENROLLED STUDENTS
# ============================================================

def get_students(
    class_number=None,
    section=None
):

    # Get all students first.
    # We normalize class and section in Python so that
    # values such as 10 / "10" and a / A do not cause
    # an enrolled student to disappear.

    response = (
        supabase
        .table("students")
        .select("*")
        .execute()
    )

    students = response.data or []

    requested_class = None
    requested_section = None

    if class_number is not None:
        requested_class = normalize_class_number(
            class_number
        )

    if section is not None:
        requested_section = normalize_section(
            section
        )

    valid_students = []

    for student in students:

        if not isinstance(
            student,
            dict
        ):
            continue

        student_id = normalize_student_id(
            student.get(
                "student_id",
                ""
            )
        )

        if not student_id:
            continue

        student_class = normalize_class_number(
            student.get(
                "class_number",
                ""
            )
        )

        student_section = normalize_section(
            student.get(
                "section",
                ""
            )
        )

        # Filter class in Python
        if (
            requested_class is not None
            and student_class != requested_class
        ):
            continue

        # Filter section in Python
        if (
            requested_section is not None
            and student_section != requested_section
        ):
            continue

        valid_students.append(
            student
        )

    valid_students.sort(
        key=lambda student:
        normalize_student_id(
            student.get(
                "student_id",
                ""
            )
        )
    )

    return valid_students

# ============================================================
# GET ONE STUDENT
# ============================================================

def get_student(student_id):

    student_id = normalize_student_id(
        student_id
    )

    if not student_id:

        return None

    response = (
        supabase
        .table("students")
        .select("*")
        .eq(
            "student_id",
            student_id
        )
        .limit(1)
        .execute()
    )

    if not response.data:

        return None

    return response.data[0]


# ============================================================
# SAVE / UPDATE STUDENT
# ============================================================

def save_student_embedding(
    student_id,
    class_number,
    section,
    embeddings,
    name=""
):

    student_id = normalize_student_id(
        student_id
    )

    class_number = normalize_class_number(
        class_number
    )

    section = normalize_section(
        section
    )

    if not validate_student_id(
        student_id
    ):

        raise ValueError(
            "Invalid student ID format."
        )

    if not validate_class_section(
        class_number,
        section
    ):

        raise ValueError(
            "Invalid class or section."
        )

    if not isinstance(
        embeddings,
        list
    ):

        raise ValueError(
            "Embeddings must be a list."
        )

    if len(embeddings) == 0:

        raise ValueError(
            "At least one embedding is required."
        )

    now = get_nepal_now().isoformat()

    data = {

        "student_id":
            student_id,

        "name":
            str(name).strip(),

        "class_number":
            class_number,

        "section":
            section,

        "embeddings":
            embeddings,

        "enrolled_at":
            now,

        "updated_at":
            now
    }

    response = (
        supabase
        .table("students")
        .upsert(
            data,
            on_conflict="student_id"
        )
        .execute()
    )

    return response.data


# ============================================================
# GET ATTENDANCE RECORDS FOR A DATE
# ============================================================

def get_attendance_records(
    class_number,
    section,
    attendance_date
):

    class_number = normalize_class_number(
        class_number
    )

    section = normalize_section(
        section
    )

    attendance_date = normalize_attendance_date(
        attendance_date
    )

    response = (
        supabase
        .table("attendance")
        .select("*")
        .eq(
            "class_number",
            class_number
        )
        .eq(
            "section",
            section
        )
        .eq(
            "attendance_date",
            attendance_date
        )
        .execute()
    )

    return response.data or []


# ============================================================
# AUTOMATIC ABSENCE CREATION
# ============================================================

def mark_absent_students_if_due():

    now_nepal = get_nepal_now()

    today_nepal = now_nepal.date()

    today_string = today_nepal.isoformat()


    # --------------------------------------------------------
    # BEFORE 1 PM
    # --------------------------------------------------------

    if now_nepal.hour < ABSENT_AFTER_HOUR:

        return {
            "marked": False,
            "reason": "Before 1:00 PM Nepal time",
            "date": today_string,
            "absent_students": 0
        }


    # --------------------------------------------------------
    # HOLIDAY / SATURDAY / SUNDAY
    # --------------------------------------------------------

    if is_school_holiday(
        today_nepal
    ):

        return {
            "marked": False,
            "reason": "Holiday / weekend",
            "date": today_string,
            "absent_students": 0
        }


    total_marked = 0


    # --------------------------------------------------------
    # PROCESS EVERY CLASS AND SECTION
    # --------------------------------------------------------

    for class_number, sections in VALID_CLASS_SECTIONS.items():

        for section in sections:

            students = get_students(
                class_number,
                section
            )

            if not students:
                continue


            existing_records = get_attendance_records(
                class_number,
                section,
                today_string
            )


            existing_ids = set()

            for record in existing_records:

                if not isinstance(
                    record,
                    dict
                ):
                    continue

                sid = normalize_student_id(
                    record.get(
                        "student_id",
                        ""
                    )
                )

                if sid:
                    existing_ids.add(
                        sid
                    )


            # ------------------------------------------------
            # CREATE ABSENT RECORD FOR EVERY STUDENT
            # WHO HAS NOT MARKED ATTENDANCE
            # ------------------------------------------------

            for student in students:

                student_id = normalize_student_id(
                    student.get(
                        "student_id",
                        ""
                    )
                )

                if not student_id:
                    continue

                if student_id in existing_ids:
                    continue


                data = {

                    "student_id":
                        student_id,

                    "name":
                        str(
                            student.get(
                                "name",
                                ""
                            )
                        ).strip(),

                    "class_number":
                        class_number,

                    "section":
                        section,

                    "attendance_date":
                        today_string,

                    "attendance_time":
                        now_nepal.strftime(
                            "%H:%M:%S"
                        ),

                    "similarity":
                        0.0,

                    "status":
                        "Absent"
                }


                try:

                    (
                        supabase
                        .table("attendance")
                        .insert(data)
                        .execute()
                    )

                    total_marked += 1

                    existing_ids.add(
                        student_id
                    )

                except Exception as error:

                    print(
                        "Could not create absent "
                        f"record for {student_id}: "
                        f"{error}"
                    )


    return {

        "marked":
            True,

        "reason":
            "Absence check completed",

        "date":
            today_string,

        "absent_students":
            total_marked
    }


# ============================================================
# ATTENDANCE DISPLAY
# ============================================================

def get_attendance_for_display(
    class_number,
    section,
    attendance_date=None
):

    class_number = normalize_class_number(
        class_number
    )

    section = normalize_section(
        section
    )

    attendance_date = normalize_attendance_date(
        attendance_date
    )


    if not validate_class_section(
        class_number,
        section
    ):

        raise ValueError(
            "Invalid class or section."
        )


    today = get_nepal_today()

    today_string = today.isoformat()

    is_today = (
        attendance_date == today_string
    )


    now_nepal = get_nepal_now()

    after_absent_time = (
        now_nepal.hour >= ABSENT_AFTER_HOUR
    )


    # --------------------------------------------------------
    # GET ENROLLED STUDENTS
    # --------------------------------------------------------

    students = get_students(
        class_number,
        section
    )

    total_students = len(
        students
    )


    # --------------------------------------------------------
    # HOLIDAY
    # --------------------------------------------------------

    holiday = check_school_holiday(
        attendance_date
    )

    if holiday:

        return {

            "date":
                attendance_date,

            "class_number":
                class_number,

            "section":
                section,

            "holiday":
                True,

            "total_students":
                total_students,

            "present_students":
                0,

            "absent_students":
                0,

            "students":
                []
        }


    # --------------------------------------------------------
    # AFTER 1 PM:
    # CREATE MISSING ABSENCES
    # --------------------------------------------------------

    if is_today and after_absent_time:

        try:

            mark_absent_students_if_due()

        except Exception as error:

            print(
                "Automatic absence check error:",
                error
            )


    # --------------------------------------------------------
    # GET ALL ATTENDANCE RECORDS
    #
    # IMPORTANT:
    # THERE IS NO 12-HOUR FILTER ANYMORE.
    #
    # Records remain visible permanently.
    # --------------------------------------------------------

    attendance_records = get_attendance_records(
        class_number,
        section,
        attendance_date
    )


    attendance_by_student = {}


    for record in attendance_records:

        if not isinstance(
            record,
            dict
        ):
            continue

        student_id = normalize_student_id(
            record.get(
                "student_id",
                ""
            )
        )

        if not student_id:
            continue

        attendance_by_student[
            student_id
        ] = record


    # --------------------------------------------------------
    # BUILD DISPLAY TABLE
    # --------------------------------------------------------

    display_students = []

    present_count = 0

    absent_count = 0


    for student in students:

        student_id = normalize_student_id(
            student.get(
                "student_id",
                ""
            )
        )

        name = str(
            student.get(
                "name",
                ""
            )
        ).strip()


        attendance = attendance_by_student.get(
            student_id
        )


        # ----------------------------------------------------
        # ATTENDANCE RECORD EXISTS
        # ----------------------------------------------------

        if attendance:

            status = str(
                attendance.get(
                    "status",
                    ""
                )
            ).strip().upper()

            time_marked = str(
                attendance.get(
                    "attendance_time",
                    ""
                )
            )


            if status == "PRESENT":

                display_students.append({

                    "student_id":
                        student_id,

                    "name":
                        name,

                    "status":
                        "Present",

                    "time_marked":
                        time_marked
                })

                present_count += 1

                continue


            if status == "ABSENT":

                display_students.append({

                    "student_id":
                        student_id,

                    "name":
                        name,

                    "status":
                        "Absent",

                    "time_marked":
                        time_marked
                })

                absent_count += 1

                continue


        # ----------------------------------------------------
        # TODAY BEFORE 1 PM
        # ----------------------------------------------------

        if is_today and not after_absent_time:

            display_students.append({

                "student_id":
                    student_id,

                "name":
                    name,

                "status":
                    "Not Marked",

                "time_marked":
                    "-"
            })

            continue


        # ----------------------------------------------------
        # TODAY AFTER 1 PM
        #
        # This is a safety fallback.
        # Normally mark_absent_students_if_due()
        # has already created the database record.
        # ----------------------------------------------------

        if is_today and after_absent_time:

            display_students.append({

                "student_id":
                    student_id,

                "name":
                    name,

                "status":
                    "Absent",

                "time_marked":
                    "-"
            })

            absent_count += 1

            continue


        # ----------------------------------------------------
        # PAST DATE
        #
        # If no record exists, leave them unmarked.
        # We DO NOT invent historical attendance.
        # ----------------------------------------------------

        display_students.append({

            "student_id":
                student_id,

            "name":
                name,

            "status":
                "Not Marked",

            "time_marked":
                "-"
        })


    return {

        "date":
            attendance_date,

        "class_number":
            class_number,

        "section":
            section,

        "holiday":
            False,

        "total_students":
            total_students,

        "present_students":
            present_count,

        "absent_students":
            absent_count,

        "students":
            display_students
    }


# ============================================================
# MARK FACIAL ATTENDANCE
# ============================================================

def mark_attendance(
    student,
    similarity
):

    if not isinstance(
        student,
        dict
    ):

        raise ValueError(
            "Invalid student record."
        )


    student_id = normalize_student_id(
        student.get(
            "student_id",
            ""
        )
    )

    name = str(
        student.get(
            "name",
            ""
        )
    ).strip()

    class_number = normalize_class_number(
        student.get(
            "class_number",
            ""
        )
    )

    section = normalize_section(
        student.get(
            "section",
            ""
        )
    )


    if not student_id:

        raise ValueError(
            "Student ID is missing."
        )


    if not validate_student_id(
        student_id
    ):

        raise ValueError(
            "Invalid student ID."
        )


    if not validate_class_section(
        class_number,
        section
    ):

        raise ValueError(
            "Invalid class or section."
        )


    try:

        similarity = float(
            similarity
        )

    except (
        TypeError,
        ValueError
    ):

        similarity = 0.0


    now_nepal = get_nepal_now()

    today = now_nepal.date()


    # ========================================================
    # HOLIDAY / WEEKEND BLOCK
    # ========================================================

    if is_school_holiday(
        today
    ):

        return (
            False,
            today.isoformat(),
            "HOLIDAY"
        )


    # ========================================================
    # AFTER 1 PM BLOCK
    #
    # Students cannot mark themselves Present after 1 PM.
    # They are automatically handled as Absent.
    # ========================================================

    if now_nepal.hour >= ABSENT_AFTER_HOUR:

        return (
            False,
            today.isoformat(),
            "ATTENDANCE_CLOSED"
        )


    # ========================================================
    # SUPABASE RPC
    # ========================================================

    response = (
        supabase
        .rpc(
            "mark_facial_attendance",
            {

                "p_student_id":
                    student_id,

                "p_name":
                    name,

                "p_class_number":
                    class_number,

                "p_section":
                    section,

                "p_similarity":
                    similarity
            }
        )
        .execute()
    )


    result = response.data


    if isinstance(
        result,
        list
    ):

        result = (
            result[0]
            if result
            else {}
        )


    if not isinstance(
        result,
        dict
    ):

        raise RuntimeError(
            "Invalid attendance response "
            "from Supabase."
        )


    if result.get(
        "holiday",
        False
    ):

        return (
            False,
            str(
                result.get(
                    "attendance_date",
                    today.isoformat()
                )
            ),
            "HOLIDAY"
        )


    return (

        bool(
            result.get(
                "inserted",
                False
            )
        ),

        str(
            result.get(
                "attendance_date",
                today.isoformat()
            )
        ),

        str(
            result.get(
                "attendance_time",
                ""
            )
        )
    )


# ============================================================
# ATTENDANCE HISTORY
# ============================================================

def get_attendance_history(
    class_number=None,
    section=None,
    attendance_date=None
):

    if attendance_date is not None:

        attendance_date = normalize_attendance_date(
            attendance_date
        )


    response = (
        supabase
        .rpc(
            "get_attendance_history",
            {

                "p_class_number":
                    (
                        normalize_class_number(
                            class_number
                        )
                        if class_number is not None
                        else None
                    ),

                "p_section":
                    (
                        normalize_section(
                            section
                        )
                        if section is not None
                        else None
                    ),

                "p_attendance_date":
                    attendance_date
            }
        )
        .execute()
    )


    return response.data or []


# ============================================================
# CHECK WHETHER STUDENT IS MARKED TODAY
# ============================================================

def is_attendance_marked_today(
    student_id
):

    student_id = normalize_student_id(
        student_id
    )

    today = get_nepal_today()

    today_string = today.isoformat()


    if is_school_holiday(
        today
    ):

        return False


    response = (
        supabase
        .table("attendance")
        .select("id")
        .eq(
            "student_id",
            student_id
        )
        .eq(
            "attendance_date",
            today_string
        )
        .limit(1)
        .execute()
    )


    return bool(
        response.data
    )


# ============================================================
# DATABASE CONNECTION TEST
# ============================================================

def test_database_connection():

    response = (
        supabase
        .table("students")
        .select("student_id")
        .limit(1)
        .execute()
    )

    return True


# ============================================================
# SIMPLE DATABASE TEST
# ============================================================

if __name__ == "__main__":

    try:

        test_database_connection()

        print(
            "SUCCESS: Connected to Supabase!"
        )


        today = get_nepal_today()


        print()
        print(
            "DATE:",
            today.isoformat()
        )


        print(
            "TIME:",
            get_nepal_now().strftime(
                "%H:%M:%S"
            )
        )


        print(
            "HOLIDAY:",
            check_school_holiday(
                today
            )
        )


        result = get_attendance_for_display(
            "10",
            "A",
            today.isoformat()
        )


        print()
        print(
            "CLASS:",
            result["class_number"]
        )


        print(
            "SECTION:",
            result["section"]
        )


        print(
            "TOTAL:",
            result["total_students"]
        )


        print(
            "PRESENT:",
            result["present_students"]
        )


        print(
            "ABSENT:",
            result["absent_students"]
        )


        print()


        for student in result["students"]:

            print(
                student["student_id"],
                "|",
                student["name"],
                "|",
                student["status"],
                "|",
                student["time_marked"]
            )


        print()


        print(
            "DATABASE TEST COMPLETED SUCCESSFULLY."
        )


    except Exception as error:

        print()
        print(
            "DATABASE ERROR:"
        )

        print(error)
from supabase import create_client


# ============================================================
# SUPABASE CONFIGURATION
# ============================================================

SUPABASE_URL = "https://bnhpestcxuisikkbhwkc.supabase.co"

# IMPORTANT:
# Replace this with your NEW Supabase key after rotating the
# exposed key.
SUPABASE_KEY = "sb_publishable_LjCEE0ik3tcJBPpPqcESPw_31ImMTle"

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)


# ============================================================
# SYSTEM CONFIGURATION
# ============================================================

STUDENT_ID_PATTERN = re.compile(
    r"^[A-Z0-9]+$"
)

NEPAL_TIMEZONE = ZoneInfo(
    "Asia/Kathmandu"
)

# Students are automatically considered absent from 1 PM.
ABSENT_AFTER_HOUR = 13


VALID_CLASS_SECTIONS = {
    "6": ["A", "B"],
    "7": ["A", "B"],
    "8": ["A", "B"],
    "9": ["A", "B"],
    "10": ["A", "B"],
    "11": ["A", "B", "C", "D"],
    "12": ["A", "B", "C", "D"]
}


# ============================================================
# NORMALIZATION FUNCTIONS
# ============================================================

def normalize_student_id(student_id):

    return (
        str(student_id)
        .strip()
        .upper()
        .replace(" ", "")
    )


def normalize_class_number(class_number):

    return str(
        class_number
    ).strip()


def normalize_section(section):

    return (
        str(section)
        .strip()
        .upper()
    )


# ============================================================
# VALIDATION FUNCTIONS
# ============================================================

def validate_student_id(student_id):

    student_id = normalize_student_id(
        student_id
    )

    return bool(
        STUDENT_ID_PATTERN.fullmatch(
            student_id
        )
    )


def validate_class_section(
    class_number,
    section
):

    class_number = normalize_class_number(
        class_number
    )

    section = normalize_section(
        section
    )

    return (
        class_number in VALID_CLASS_SECTIONS
        and
        section in VALID_CLASS_SECTIONS[
            class_number
        ]
    )


# ============================================================
# DATE / TIME FUNCTIONS
# ============================================================

def get_nepal_now():

    return datetime.now(
        NEPAL_TIMEZONE
    )


def get_nepal_today():

    return get_nepal_now().date()


def normalize_attendance_date(
    attendance_date
):

    if attendance_date is None:

        return get_nepal_today().isoformat()

    if isinstance(
        attendance_date,
        datetime
    ):

        return attendance_date.date().isoformat()

    if isinstance(
        attendance_date,
        date
    ):

        return attendance_date.isoformat()

    return str(
        attendance_date
    ).strip()


# ============================================================
# SCHOOL CALENDAR
# ============================================================

def check_school_holiday(
    attendance_date
):

    attendance_date = normalize_attendance_date(
        attendance_date
    )

    try:

        parsed_date = datetime.strptime(
            attendance_date,
            "%Y-%m-%d"
        ).date()

        return bool(
            is_school_holiday(
                parsed_date
            )
        )

    except Exception:

        return False


# ============================================================
# CHECK WHETHER TODAY IS A SCHOOL DAY
# ============================================================

def is_school_day(
    attendance_date=None
):

    if attendance_date is None:

        attendance_date = get_nepal_today()

    if isinstance(
        attendance_date,
        str
    ):

        try:

            attendance_date = datetime.strptime(
                attendance_date,
                "%Y-%m-%d"
            ).date()

        except ValueError:

            return False

    return not is_school_holiday(
        attendance_date
    )


# ============================================================
# GET ALL ENROLLED STUDENTS
# ============================================================

def get_students(
    class_number=None,
    section=None
):

    # Get all students first.
    # We normalize class and section in Python so that
    # values such as 10 / "10" and a / A do not cause
    # an enrolled student to disappear.

    response = (
        supabase
        .table("students")
        .select("*")
        .execute()
    )

    students = response.data or []

    requested_class = None
    requested_section = None

    if class_number is not None:
        requested_class = normalize_class_number(
            class_number
        )

    if section is not None:
        requested_section = normalize_section(
            section
        )

    valid_students = []

    for student in students:

        if not isinstance(
            student,
            dict
        ):
            continue

        student_id = normalize_student_id(
            student.get(
                "student_id",
                ""
            )
        )

        if not student_id:
            continue

        student_class = normalize_class_number(
            student.get(
                "class_number",
                ""
            )
        )

        student_section = normalize_section(
            student.get(
                "section",
                ""
            )
        )

        # Filter class in Python
        if (
            requested_class is not None
            and student_class != requested_class
        ):
            continue

        # Filter section in Python
        if (
            requested_section is not None
            and student_section != requested_section
        ):
            continue

        valid_students.append(
            student
        )

    valid_students.sort(
        key=lambda student:
        normalize_student_id(
            student.get(
                "student_id",
                ""
            )
        )
    )

    return valid_students

# ============================================================
# GET ONE STUDENT
# ============================================================

def get_student(student_id):

    student_id = normalize_student_id(
        student_id
    )

    if not student_id:

        return None

    response = (
        supabase
        .table("students")
        .select("*")
        .eq(
            "student_id",
            student_id
        )
        .limit(1)
        .execute()
    )

    if not response.data:

        return None

    return response.data[0]


# ============================================================
# SAVE / UPDATE STUDENT
# ============================================================

def save_student_embedding(
    student_id,
    class_number,
    section,
    embeddings,
    name=""
):

    student_id = normalize_student_id(
        student_id
    )

    class_number = normalize_class_number(
        class_number
    )

    section = normalize_section(
        section
    )

    if not validate_student_id(
        student_id
    ):

        raise ValueError(
            "Invalid student ID format."
        )

    if not validate_class_section(
        class_number,
        section
    ):

        raise ValueError(
            "Invalid class or section."
        )

    if not isinstance(
        embeddings,
        list
    ):

        raise ValueError(
            "Embeddings must be a list."
        )

    if len(embeddings) == 0:

        raise ValueError(
            "At least one embedding is required."
        )

    now = get_nepal_now().isoformat()

    data = {

        "student_id":
            student_id,

        "name":
            str(name).strip(),

        "class_number":
            class_number,

        "section":
            section,

        "embeddings":
            embeddings,

        "enrolled_at":
            now,

        "updated_at":
            now
    }

    response = (
        supabase
        .table("students")
        .upsert(
            data,
            on_conflict="student_id"
        )
        .execute()
    )

    return response.data


# ============================================================
# GET ATTENDANCE RECORDS FOR A DATE
# ============================================================

def get_attendance_records(
    class_number,
    section,
    attendance_date
):

    class_number = normalize_class_number(
        class_number
    )

    section = normalize_section(
        section
    )

    attendance_date = normalize_attendance_date(
        attendance_date
    )

    response = (
        supabase
        .table("attendance")
        .select("*")
        .eq(
            "class_number",
            class_number
        )
        .eq(
            "section",
            section
        )
        .eq(
            "attendance_date",
            attendance_date
        )
        .execute()
    )

    return response.data or []


# ============================================================
# AUTOMATIC ABSENCE CREATION
# ============================================================

def mark_absent_students_if_due():

    now_nepal = get_nepal_now()

    today_nepal = now_nepal.date()

    today_string = today_nepal.isoformat()


    # --------------------------------------------------------
    # BEFORE 1 PM
    # --------------------------------------------------------

    if now_nepal.hour < ABSENT_AFTER_HOUR:

        return {
            "marked": False,
            "reason": "Before 1:00 PM Nepal time",
            "date": today_string,
            "absent_students": 0
        }


    # --------------------------------------------------------
    # HOLIDAY / SATURDAY / SUNDAY
    # --------------------------------------------------------

    if is_school_holiday(
        today_nepal
    ):

        return {
            "marked": False,
            "reason": "Holiday / weekend",
            "date": today_string,
            "absent_students": 0
        }


    total_marked = 0


    # --------------------------------------------------------
    # PROCESS EVERY CLASS AND SECTION
    # --------------------------------------------------------

    for class_number, sections in VALID_CLASS_SECTIONS.items():

        for section in sections:

            students = get_students(
                class_number,
                section
            )

            if not students:
                continue


            existing_records = get_attendance_records(
                class_number,
                section,
                today_string
            )


            existing_ids = set()

            for record in existing_records:

                if not isinstance(
                    record,
                    dict
                ):
                    continue

                sid = normalize_student_id(
                    record.get(
                        "student_id",
                        ""
                    )
                )

                if sid:
                    existing_ids.add(
                        sid
                    )


            # ------------------------------------------------
            # CREATE ABSENT RECORD FOR EVERY STUDENT
            # WHO HAS NOT MARKED ATTENDANCE
            # ------------------------------------------------

            for student in students:

                student_id = normalize_student_id(
                    student.get(
                        "student_id",
                        ""
                    )
                )

                if not student_id:
                    continue

                if student_id in existing_ids:
                    continue


                data = {

                    "student_id":
                        student_id,

                    "name":
                        str(
                            student.get(
                                "name",
                                ""
                            )
                        ).strip(),

                    "class_number":
                        class_number,

                    "section":
                        section,

                    "attendance_date":
                        today_string,

                    "attendance_time":
                        now_nepal.strftime(
                            "%H:%M:%S"
                        ),

                    "similarity":
                        0.0,

                    "status":
                        "Absent"
                }


                try:

                    (
                        supabase
                        .table("attendance")
                        .insert(data)
                        .execute()
                    )

                    total_marked += 1

                    existing_ids.add(
                        student_id
                    )

                except Exception as error:

                    print(
                        "Could not create absent "
                        f"record for {student_id}: "
                        f"{error}"
                    )


    return {

        "marked":
            True,

        "reason":
            "Absence check completed",

        "date":
            today_string,

        "absent_students":
            total_marked
    }


# ============================================================
# ATTENDANCE DISPLAY
# ============================================================

def get_attendance_for_display(
    class_number,
    section,
    attendance_date=None
):

    class_number = normalize_class_number(
        class_number
    )

    section = normalize_section(
        section
    )

    attendance_date = normalize_attendance_date(
        attendance_date
    )


    if not validate_class_section(
        class_number,
        section
    ):

        raise ValueError(
            "Invalid class or section."
        )


    today = get_nepal_today()

    today_string = today.isoformat()

    is_today = (
        attendance_date == today_string
    )


    now_nepal = get_nepal_now()

    after_absent_time = (
        now_nepal.hour >= ABSENT_AFTER_HOUR
    )


    # --------------------------------------------------------
    # GET ENROLLED STUDENTS
    # --------------------------------------------------------

    students = get_students(
        class_number,
        section
    )

    total_students = len(
        students
    )


    # --------------------------------------------------------
    # HOLIDAY
    # --------------------------------------------------------

    holiday = check_school_holiday(
        attendance_date
    )

    if holiday:

        return {

            "date":
                attendance_date,

            "class_number":
                class_number,

            "section":
                section,

            "holiday":
                True,

            "total_students":
                total_students,

            "present_students":
                0,

            "absent_students":
                0,

            "students":
                []
        }


    # --------------------------------------------------------
    # AFTER 1 PM:
    # CREATE MISSING ABSENCES
    # --------------------------------------------------------

    if is_today and after_absent_time:

        try:

            mark_absent_students_if_due()

        except Exception as error:

            print(
                "Automatic absence check error:",
                error
            )


    # --------------------------------------------------------
    # GET ALL ATTENDANCE RECORDS
    #
    # IMPORTANT:
    # THERE IS NO 12-HOUR FILTER ANYMORE.
    #
    # Records remain visible permanently.
    # --------------------------------------------------------

    attendance_records = get_attendance_records(
        class_number,
        section,
        attendance_date
    )


    attendance_by_student = {}


    for record in attendance_records:

        if not isinstance(
            record,
            dict
        ):
            continue

        student_id = normalize_student_id(
            record.get(
                "student_id",
                ""
            )
        )

        if not student_id:
            continue

        attendance_by_student[
            student_id
        ] = record


    # --------------------------------------------------------
    # BUILD DISPLAY TABLE
    # --------------------------------------------------------

    display_students = []

    present_count = 0

    absent_count = 0


    for student in students:

        student_id = normalize_student_id(
            student.get(
                "student_id",
                ""
            )
        )

        name = str(
            student.get(
                "name",
                ""
            )
        ).strip()


        attendance = attendance_by_student.get(
            student_id
        )


        # ----------------------------------------------------
        # ATTENDANCE RECORD EXISTS
        # ----------------------------------------------------

        if attendance:

            status = str(
                attendance.get(
                    "status",
                    ""
                )
            ).strip().upper()

            time_marked = str(
                attendance.get(
                    "attendance_time",
                    ""
                )
            )


            if status == "PRESENT":

                display_students.append({

                    "student_id":
                        student_id,

                    "name":
                        name,

                    "status":
                        "Present",

                    "time_marked":
                        time_marked
                })

                present_count += 1

                continue


            if status == "ABSENT":

                display_students.append({

                    "student_id":
                        student_id,

                    "name":
                        name,

                    "status":
                        "Absent",

                    "time_marked":
                        time_marked
                })

                absent_count += 1

                continue


        # ----------------------------------------------------
        # TODAY BEFORE 1 PM
        # ----------------------------------------------------

        if is_today and not after_absent_time:

            display_students.append({

                "student_id":
                    student_id,

                "name":
                    name,

                "status":
                    "Not Marked",

                "time_marked":
                    "-"
            })

            continue


        # ----------------------------------------------------
        # TODAY AFTER 1 PM
        #
        # This is a safety fallback.
        # Normally mark_absent_students_if_due()
        # has already created the database record.
        # ----------------------------------------------------

        if is_today and after_absent_time:

            display_students.append({

                "student_id":
                    student_id,

                "name":
                    name,

                "status":
                    "Absent",

                "time_marked":
                    "-"
            })

            absent_count += 1

            continue


        # ----------------------------------------------------
        # PAST DATE
        #
        # If no record exists, leave them unmarked.
        # We DO NOT invent historical attendance.
        # ----------------------------------------------------

        display_students.append({

            "student_id":
                student_id,

            "name":
                name,

            "status":
                "Not Marked",

            "time_marked":
                "-"
        })


    return {

        "date":
            attendance_date,

        "class_number":
            class_number,

        "section":
            section,

        "holiday":
            False,

        "total_students":
            total_students,

        "present_students":
            present_count,

        "absent_students":
            absent_count,

        "students":
            display_students
    }


# ============================================================
# MARK FACIAL ATTENDANCE
# ============================================================

def mark_attendance(
    student,
    similarity
):

    if not isinstance(
        student,
        dict
    ):

        raise ValueError(
            "Invalid student record."
        )


    student_id = normalize_student_id(
        student.get(
            "student_id",
            ""
        )
    )

    name = str(
        student.get(
            "name",
            ""
        )
    ).strip()

    class_number = normalize_class_number(
        student.get(
            "class_number",
            ""
        )
    )

    section = normalize_section(
        student.get(
            "section",
            ""
        )
    )


    if not student_id:

        raise ValueError(
            "Student ID is missing."
        )


    if not validate_student_id(
        student_id
    ):

        raise ValueError(
            "Invalid student ID."
        )


    if not validate_class_section(
        class_number,
        section
    ):

        raise ValueError(
            "Invalid class or section."
        )


    try:

        similarity = float(
            similarity
        )

    except (
        TypeError,
        ValueError
    ):

        similarity = 0.0


    now_nepal = get_nepal_now()

    today = now_nepal.date()


    # ========================================================
    # HOLIDAY / WEEKEND BLOCK
    # ========================================================

    if is_school_holiday(
        today
    ):

        return (
            False,
            today.isoformat(),
            "HOLIDAY"
        )


    # ========================================================
    # AFTER 1 PM BLOCK
    #
    # Students cannot mark themselves Present after 1 PM.
    # They are automatically handled as Absent.
    # ========================================================

    if now_nepal.hour >= ABSENT_AFTER_HOUR:

        return (
            False,
            today.isoformat(),
            "ATTENDANCE_CLOSED"
        )


    # ========================================================
    # SUPABASE RPC
    # ========================================================

    response = (
        supabase
        .rpc(
            "mark_facial_attendance",
            {

                "p_student_id":
                    student_id,

                "p_name":
                    name,

                "p_class_number":
                    class_number,

                "p_section":
                    section,

                "p_similarity":
                    similarity
            }
        )
        .execute()
    )


    result = response.data


    if isinstance(
        result,
        list
    ):

        result = (
            result[0]
            if result
            else {}
        )


    if not isinstance(
        result,
        dict
    ):

        raise RuntimeError(
            "Invalid attendance response "
            "from Supabase."
        )


    if result.get(
        "holiday",
        False
    ):

        return (
            False,
            str(
                result.get(
                    "attendance_date",
                    today.isoformat()
                )
            ),
            "HOLIDAY"
        )


    return (

        bool(
            result.get(
                "inserted",
                False
            )
        ),

        str(
            result.get(
                "attendance_date",
                today.isoformat()
            )
        ),

        str(
            result.get(
                "attendance_time",
                ""
            )
        )
    )


# ============================================================
# ATTENDANCE HISTORY
# ============================================================

def get_attendance_history(
    class_number=None,
    section=None,
    attendance_date=None
):

    if attendance_date is not None:

        attendance_date = normalize_attendance_date(
            attendance_date
        )


    response = (
        supabase
        .rpc(
            "get_attendance_history",
            {

                "p_class_number":
                    (
                        normalize_class_number(
                            class_number
                        )
                        if class_number is not None
                        else None
                    ),

                "p_section":
                    (
                        normalize_section(
                            section
                        )
                        if section is not None
                        else None
                    ),

                "p_attendance_date":
                    attendance_date
            }
        )
        .execute()
    )


    return response.data or []


# ============================================================
# CHECK WHETHER STUDENT IS MARKED TODAY
# ============================================================

def is_attendance_marked_today(
    student_id
):

    student_id = normalize_student_id(
        student_id
    )

    today = get_nepal_today()

    today_string = today.isoformat()


    if is_school_holiday(
        today
    ):

        return False


    response = (
        supabase
        .table("attendance")
        .select("id")
        .eq(
            "student_id",
            student_id
        )
        .eq(
            "attendance_date",
            today_string
        )
        .limit(1)
        .execute()
    )


    return bool(
        response.data
    )


# ============================================================
# DATABASE CONNECTION TEST
# ============================================================

def test_database_connection():

    response = (
        supabase
        .table("students")
        .select("student_id")
        .limit(1)
        .execute()
    )

    return True


# ============================================================
# SIMPLE DATABASE TEST
# ============================================================

if __name__ == "__main__":

    try:

        test_database_connection()

        print(
            "SUCCESS: Connected to Supabase!"
        )


        today = get_nepal_today()


        print()
        print(
            "DATE:",
            today.isoformat()
        )


        print(
            "TIME:",
            get_nepal_now().strftime(
                "%H:%M:%S"
            )
        )


        print(
            "HOLIDAY:",
            check_school_holiday(
                today
            )
        )


        result = get_attendance_for_display(
            "10",
            "A",
            today.isoformat()
        )


        print()
        print(
            "CLASS:",
            result["class_number"]
        )


        print(
            "SECTION:",
            result["section"]
        )


        print(
            "TOTAL:",
            result["total_students"]
        )


        print(
            "PRESENT:",
            result["present_students"]
        )


        print(
            "ABSENT:",
            result["absent_students"]
        )


        print()


        for student in result["students"]:

            print(
                student["student_id"],
                "|",
                student["name"],
                "|",
                student["status"],
                "|",
                student["time_marked"]
            )


        print()


        print(
            "DATABASE TEST COMPLETED SUCCESSFULLY."
        )


    except Exception as error:

        print()
        print(
            "DATABASE ERROR:"
        )

        print(error)
