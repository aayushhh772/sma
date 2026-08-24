import sys
import os
import argparse
import subprocess
from datetime import datetime, date
from zoneinfo import ZoneInfo

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QPushButton, QTableWidget, QHeaderView, QMessageBox,
    QDateEdit, QTableWidgetItem
)
from PyQt6.QtCore import Qt, QDateTime, QDate, QTimer
from PyQt6.QtGui import QFont, QPixmap

from school_calendar import is_school_holiday

# Import your Supabase connection
try:
    from database import supabase
except ImportError:
    from database import supabase

from database import (
    get_attendance_for_display
)


LOGO_FILENAME = "logo.png"

NEPAL_TIMEZONE = ZoneInfo("Asia/Kathmandu")


class AttendanceDisplay(QWidget):

    def __init__(
        self,
        selected_class="Class 6",
        selected_section="Section A"
    ):

        super().__init__()

        self.selected_class = selected_class
        self.selected_section = selected_section

        # Convert:
        # "Class 10" -> "10"
        # "Section A" -> "A"
        self.class_number = self.extract_class_number(
            selected_class
        )

        self.section = self.extract_section(
            selected_section
        )

        self.init_ui()

        # Load today's data immediately
        self.load_attendance_for_date(
            QDate.currentDate().toString("yyyy-MM-dd")
        )

    # =========================================================
    # CLASS / SECTION HELPERS
    # =========================================================

    def extract_class_number(self, class_text):

        class_text = str(class_text).strip()

        if class_text.lower().startswith("class "):

            return class_text[6:].strip()

        return class_text

    def extract_section(self, section_text):

        section_text = str(section_text).strip()

        if section_text.lower().startswith("section "):

            return section_text[8:].strip().upper()

        return section_text.upper()

    # =========================================================
    # USER INTERFACE
    # =========================================================

    def init_ui(self):

        self.setWindowTitle(
            "SOS Hermann Gmeiner School Gandaki - Attendance Display"
        )

        self.resize(1050, 700)

        self.setStyleSheet(
            "background-color: #eaf5fc;"
        )

        main_layout = QVBoxLayout(self)

        main_layout.setContentsMargins(
            20,
            15,
            20,
            15
        )

        main_layout.setSpacing(15)

        # =====================================================
        # TOP HEADER BAR
        # =====================================================

        header_card = QFrame()

        header_card.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border-radius: 10px;
                border: 1px solid #cbe3f5;
                padding: 10px;
            }
        """)

        header_layout = QHBoxLayout(
            header_card
        )

        # =====================================================
        # SCHOOL LOGO
        # =====================================================

        logo_lbl = QLabel()

        logo_path = os.path.join(
            os.path.dirname(
                os.path.abspath(__file__)
            ),
            LOGO_FILENAME
        )

        if not os.path.exists(logo_path):

            logo_path = os.path.join(
                os.path.dirname(
                    os.path.abspath(__file__)
                ),
                "486624203_601802256148254_3403736131493055483_n.png"
            )

        if os.path.exists(logo_path):

            pix = QPixmap(
                logo_path
            ).scaled(
                50,
                50,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )

            logo_lbl.setPixmap(pix)

        header_layout.addWidget(
            logo_lbl
        )

        # =====================================================
        # TITLE
        # =====================================================

        title_box = QVBoxLayout()

        self.title_label = QLabel(
            f"Attendance Register: "
            f"{self.selected_class} - "
            f"{self.selected_section}"
        )

        self.title_label.setFont(
            QFont(
                "Segoe UI",
                15,
                QFont.Weight.Bold
            )
        )

        self.title_label.setStyleSheet(
            "color: #004080; "
            "border: none; "
            "background: transparent;"
        )

        self.date_label = QLabel()

        self.date_label.setFont(
            QFont(
                "Segoe UI",
                10
            )
        )

        self.date_label.setStyleSheet(
            "color: #555555; "
            "border: none; "
            "background: transparent;"
        )

        title_box.addWidget(
            self.title_label
        )

        title_box.addWidget(
            self.date_label
        )

        header_layout.addLayout(
            title_box
        )

        header_layout.addStretch()

        # =====================================================
        # DATE PICKER
        # =====================================================

        date_box = QHBoxLayout()

        date_box.setSpacing(8)

        lbl_select_date = QLabel(
            "📅 Select Date:"
        )

        lbl_select_date.setFont(
            QFont(
                "Segoe UI",
                10,
                QFont.Weight.Bold
            )
        )

        lbl_select_date.setStyleSheet(
            "color: #004080; "
            "border: none; "
            "background: transparent;"
        )

        self.date_picker = QDateEdit()

        self.date_picker.setCalendarPopup(
            True
        )

        self.date_picker.setDate(
            QDate.currentDate()
        )

        self.date_picker.setDisplayFormat(
            "yyyy-MM-dd"
        )

        self.date_picker.setFixedSize(
            120,
            35
        )

        self.date_picker.setStyleSheet("""
            QDateEdit {
                background-color: #ffffff;
                color: #1a2a3a;
                border: 1px solid #b2d4ee;
                border-radius: 6px;
                padding-left: 8px;
                font-size: 13px;
                font-weight: bold;
            }

            QDateEdit::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left-width: 1px;
                border-left-color: #b2d4ee;
                border-left-style: solid;
            }
        """)

        btn_fetch = QPushButton(
            "Fetch"
        )

        btn_fetch.setFixedSize(
            70,
            35
        )

        btn_fetch.setCursor(
            Qt.CursorShape.PointingHandCursor
        )

        btn_fetch.setStyleSheet("""
            QPushButton {
                background-color: #0077c8;
                color: #ffffff;
                border-radius: 6px;
                font-weight: bold;
                font-size: 12px;
                border: none;
            }

            QPushButton:hover {
                background-color: #005a9e;
            }
        """)

        btn_fetch.clicked.connect(
            self.on_date_changed
        )

        date_box.addWidget(
            lbl_select_date
        )

        date_box.addWidget(
            self.date_picker
        )

        date_box.addWidget(
            btn_fetch
        )

        header_layout.addLayout(
            date_box
        )

        header_layout.addSpacing(
            15
        )

        # =====================================================
        # BACK TO ADMIN
        # =====================================================

        btn_back = QPushButton(
            "⬅️ Back to Admin Panel"
        )

        btn_back.setFixedSize(
            160,
            35
        )

        btn_back.setCursor(
            Qt.CursorShape.PointingHandCursor
        )

        btn_back.setStyleSheet("""
            QPushButton {
                background-color: #e1f0fa;
                color: #0066b2;
                border: 1px solid #b2d4ee;
                border-radius: 6px;
                font-weight: bold;
                font-size: 12px;
            }

            QPushButton:hover {
                background-color: #0077c8;
                color: #ffffff;
            }
        """)

        btn_back.clicked.connect(
            self.return_to_admin
        )

        header_layout.addWidget(
            btn_back
        )

        main_layout.addWidget(
            header_card
        )

        # =====================================================
        # STATISTICS
        # =====================================================

        stats_layout = QHBoxLayout()

        self.lbl_total = self.create_stat_card(
            "Total Students",
            "0",
            "#0077c8"
        )

        self.lbl_present = self.create_stat_card(
            "Present",
            "0",
            "#27ae60"
        )

        self.lbl_absent = self.create_stat_card(
            "Absent",
            "0",
            "#e74c3c"
        )

        stats_layout.addWidget(
            self.lbl_total["card"]
        )

        stats_layout.addWidget(
            self.lbl_present["card"]
        )

        stats_layout.addWidget(
            self.lbl_absent["card"]
        )

        main_layout.addLayout(
            stats_layout
        )

        # =====================================================
        # ATTENDANCE TABLE
        # =====================================================

        self.table = QTableWidget(
            0,
            4
        )

        self.table.setHorizontalHeaderLabels(
            [
                "Student ID",
                "Student Name",
                "Status",
                "Time Marked"
            ]
        )

        header = self.table.horizontalHeader()

        header.setSectionResizeMode(
            0,
            QHeaderView.ResizeMode.Interactive
        )

        header.setSectionResizeMode(
            1,
            QHeaderView.ResizeMode.Stretch
        )

        header.setSectionResizeMode(
            2,
            QHeaderView.ResizeMode.Interactive
        )

        header.setSectionResizeMode(
            3,
            QHeaderView.ResizeMode.Interactive
        )

        self.table.setColumnWidth(
            0,
            140
        )

        self.table.setColumnWidth(
            2,
            130
        )

        self.table.setColumnWidth(
            3,
            260
        )

        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #ffffff;
                color: #1a2a3a;
                border-radius: 8px;
                border: 1px solid #cbe3f5;
                gridline-color: #e1f0fa;
            }

            QHeaderView::section {
                background-color: #0077c8;
                color: #ffffff;
                border: none;
                padding: 8px;
                font-weight: bold;
                font-size: 13px;
            }
        """)

        main_layout.addWidget(
            self.table
        )

        # =====================================================
        # LIVE CLOCK
        # =====================================================

        self.timer = QTimer(
            self
        )

        self.timer.timeout.connect(
            self.update_time_display
        )

        self.timer.start(
            1000
        )

        self.update_time_display()

    # =========================================================
    # STAT CARD
    # =========================================================

    def create_stat_card(
        self,
        title,
        default_val,
        color_hex
    ):

        card = QFrame()

        card.setStyleSheet(
            f"""
            QFrame {{
                background-color: #ffffff;
                border-radius: 8px;
                border-left: 5px solid {color_hex};
                border-top: 1px solid #cbe3f5;
                border-right: 1px solid #cbe3f5;
                border-bottom: 1px solid #cbe3f5;
            }}
            """
        )

        layout = QVBoxLayout(
            card
        )

        layout.setContentsMargins(
            15,
            8,
            15,
            8
        )

        t_lbl = QLabel(
            title
        )

        t_lbl.setFont(
            QFont(
                "Segoe UI",
                9,
                QFont.Weight.Bold
            )
        )

        t_lbl.setStyleSheet(
            "color: #7f8c8d; "
            "border: none; "
            "background: transparent;"
        )

        v_lbl = QLabel(
            default_val
        )

        v_lbl.setFont(
            QFont(
                "Segoe UI",
                16,
                QFont.Weight.Bold
            )
        )

        v_lbl.setStyleSheet(
            f"color: {color_hex}; "
            "border: none; "
            "background: transparent;"
        )

        layout.addWidget(
            t_lbl
        )

        layout.addWidget(
            v_lbl
        )

        return {
            "card": card,
            "val_label": v_lbl
        }

    # =========================================================
    # CLOCK
    # =========================================================

    def update_time_display(self):
        now_nepal = datetime.now(NEPAL_TIMEZONE)

        day = str(now_nepal.day)
        hour = now_nepal.strftime("%I").lstrip("0")

        now_str = now_nepal.strftime(
            "%A, %B "
        ) + day + now_nepal.strftime(
            ", %Y - "
        ) + hour + now_nepal.strftime(
            ":%M:%S %p"
        )

        self.date_label.setText(
            f"Date & Time: {now_str}"
        )

    # =========================================================
    # FETCH SELECTED DATE
    # =========================================================

    def on_date_changed(self):

        selected_date = (
            self.date_picker
            .date()
            .toString(
                "yyyy-MM-dd"
            )
        )

        self.load_attendance_for_date(
            selected_date
        )

    # =========================================================
    # LOAD ATTENDANCE
    # =========================================================

    def load_attendance_for_date(
        self,
        selected_date
    ):

        try:

            # -------------------------------------------------
            # 1. Get all enrolled students
            # -------------------------------------------------

            students_response = (
                supabase
                .table("students")
                .select(
                    "student_id, name"
                )
                .eq(
                    "class_number",
                    self.class_number
                )
                .eq(
                    "section",
                    self.section
                )
                .execute()
            )

            enrolled_students = (
                students_response.data
                or []
            )

            total_students = len(
                enrolled_students
            )

            # -------------------------------------------------
            # 2. Check whether selected date is a holiday
            # -------------------------------------------------

            selected_date_object = date.fromisoformat(
                selected_date
            )

            holiday = is_school_holiday(
                selected_date_object
            )

            # -------------------------------------------------
            # 3. Clear old table FIRST
            # -------------------------------------------------

            self.table.setRowCount(
                0
            )

            # -------------------------------------------------
            # 4. HOLIDAY
            # -------------------------------------------------

            if holiday:

                self.lbl_total[
                    "val_label"
                ].setText(
                    str(total_students)
                )

                self.lbl_present[
                    "val_label"
                ].setText(
                    "0"
                )

                self.lbl_absent[
                    "val_label"
                ].setText(
                    "0"
                )

                self.title_label.setText(
                    f"Attendance Register: "
                    f"{self.selected_class} - "
                    f"{self.selected_section} "
                    f"(HOLIDAY)"
                )

                self.date_label.setText(
                    f"Date: {selected_date} - HOLIDAY"
                )

                return

            # -------------------------------------------------
            # 5. SCHOOL DAY
            # -------------------------------------------------

            self.title_label.setText(
                f"Attendance Register: "
                f"{self.selected_class} - "
                f"{self.selected_section}"
            )

            # -------------------------------------------------
            # 6. Fetch actual attendance records for date
            # -------------------------------------------------

            attendance_response = (
                supabase
                .table("attendance")
                .select("*")
                .eq(
                    "class_number",
                    self.class_number
                )
                .eq(
                    "section",
                    self.section
                )
                .eq(
                    "attendance_date",
                    selected_date
                )
                .execute()
            )

            attendance_records = (
                attendance_response.data
                or []
            )

            # Map existing attendance by student_id
            attendance_map = {}
            for rec in attendance_records:
                sid = str(rec.get("student_id", "")).strip()
                if sid:
                    attendance_map[sid] = rec

            # -------------------------------------------------
            # 7. Merge enrolled students with attendance
            # -------------------------------------------------

            present_count = 0
            absent_count = 0
            display_records = []

            for student in enrolled_students:
                student_id = str(student.get("student_id", "")).strip()
                name = str(student.get("name", "")).strip()

                if student_id in attendance_map:
                    rec = attendance_map[student_id]
                    status = str(rec.get("status", "")).strip().upper()
                    time_marked = str(
                        rec.get(
                            "attendance_time",
                            rec.get("time", "--")
                        )
                    ).strip() or "--"
                else:
                    status = "ABSENT"
                    time_marked = "--"

                if status == "PRESENT":
                    present_count += 1
                else:
                    status = "ABSENT"
                    absent_count += 1

                display_records.append(
                    {
                        "student_id": student_id,
                        "name": name,
                        "status": status,
                        "time_marked": time_marked
                    }
                )

            # Sort records: Present first, then by Student ID
            display_records.sort(
                key=lambda r: (0 if r["status"] == "PRESENT" else 1, r["student_id"])
            )

            # -------------------------------------------------
            # 8. Update statistic cards
            # -------------------------------------------------

            self.lbl_total[
                "val_label"
            ].setText(
                str(total_students)
            )

            self.lbl_present[
                "val_label"
            ].setText(
                str(present_count)
            )

            self.lbl_absent[
                "val_label"
            ].setText(
                str(absent_count)
            )

            # -------------------------------------------------
            # 9. Populate Table with All Enrolled Students
            # -------------------------------------------------

            self.table.setRowCount(
                len(display_records)
            )

            for row, record in enumerate(
                display_records
            ):

                self.table.setItem(
                    row,
                    0,
                    QTableWidgetItem(
                        record["student_id"]
                    )
                )

                self.table.setItem(
                    row,
                    1,
                    QTableWidgetItem(
                        record["name"]
                    )
                )

                self.table.setItem(
                    row,
                    2,
                    QTableWidgetItem(
                        record["status"]
                    )
                )

                self.table.setItem(
                    row,
                    3,
                    QTableWidgetItem(
                        record["time_marked"]
                    )
                )

            if len(display_records) == 0:

                self.date_label.setText(
                    f"Date: {selected_date} "
                    f"- No enrolled students found"
                )

            else:

                self.date_label.setText(
                    f"Date: {selected_date}"
                )

        except Exception as error:

            QMessageBox.critical(
                self,
                "Database Error",
                f"Could not load attendance data:\n\n{error}"
            )

            print(
                "ATTENDANCE DISPLAY ERROR:"
            )

            print(error)

    # =========================================================
    # RETURN TO ADMIN
    # =========================================================

    def return_to_admin(self):

        admin_script = os.path.join(
            os.path.dirname(
                os.path.abspath(__file__)
            ),
            "admin_panel.py"
        )

        if os.path.exists(
            admin_script
        ):

            subprocess.Popen(
                [
                    sys.executable,
                    admin_script
                ],
                cwd=os.path.dirname(
                    admin_script
                )
            )

            self.close()

        else:

            QMessageBox.warning(
                self,
                "File Missing",
                "Could not find admin_panel.py "
                "in the directory."
            )


# =============================================================
# COMMAND LINE ARGUMENTS
# =============================================================

def parse_args():

    parser = argparse.ArgumentParser(
        description="Attendance Display Portal"
    )

    parser.add_argument(
        "--class",
        dest="cls",
        default="Class 6",
        help="Selected Class"
    )

    parser.add_argument(
        "--section",
        dest="sec",
        default="Section A",
        help="Selected Section"
    )

    return parser.parse_args()


# =============================================================
# MAIN
# =============================================================

if __name__ == "__main__":

    args = parse_args()

    app = QApplication(
        sys.argv
    )

    window = AttendanceDisplay(
        selected_class=args.cls,
        selected_section=args.sec
    )

    window.show()

    sys.exit(
        app.exec()
    )
