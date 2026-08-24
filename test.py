import sys
import os
import subprocess
import datetime
import json
import re
import math
import random

from network_sync import (
    fetch_network_data,
    listen_for_updates,
    fetch_attendance_catchup,
    fetch_today_attendance,
    listen_for_attendance_updates
)

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QTableWidget, QTableWidgetItem, QHeaderView, QFrame, QPushButton,
    QMessageBox, QDialog, QScrollArea, QLineEdit
)

from PyQt6.QtCore import (
    Qt, QThread, pyqtSignal, QTimer, QTime, QUrl, QPointF
)

from PyQt6.QtGui import (
    QFont, QDesktopServices, QPainter, QPainterPath,
    QColor, QBrush, QIcon
)

from help import HelpWindow
from enrollment import EnrollmentWindow
from facial_attendance import FacialAttendanceWindow
from cal import CalendarWindow
from attendancedisplaytest import AttendanceDisplayTest


try:
    from database import process_scan
except ImportError:
    def process_scan(code):
        pass


DATA_FILE = "data.json"
EXPIRATION_HOURS = 12


def parse_iso_timestamp(ts_str):
    if not ts_str:
        return None

    try:
        return datetime.datetime.fromisoformat(ts_str)
    except Exception:
        return None


def is_recent(ts_str, max_hours=EXPIRATION_HOURS):
    dt = parse_iso_timestamp(ts_str)

    if not dt:
        return True

    now = datetime.datetime.now()

    return (now - dt).total_seconds() < (max_hours * 3600)


# ============================================================
# REALTIME ADMIN DATA LISTENER
# ============================================================

class RealtimeListenerThread(QThread):
    data_updated = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.running = True

    def run(self):
        try:
            listen_for_updates(
                self._on_cloud_change,
                DATA_FILE
            )
        except Exception as e:
            print(f"Realtime listener error: {e}")

        while self.running:
            self.msleep(1000)

    def _on_cloud_change(self, cloud_data):
        if self.running:
            self.data_updated.emit()

    def stop(self):
        self.running = False
        self.quit()


# ============================================================
# ENROLLMENT LOGIN
# ============================================================

class LoginDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Enrollment Login")
        self.resize(380, 260)

        self.setStyleSheet(
            "background-color: #E0F2FE; "
            "font-family: 'Segoe UI', sans-serif;"
        )

        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            24, 24, 24, 24
        )

        layout.setSpacing(16)

        title_lbl = QLabel(
            "Enrollment Authentication"
        )

        title_lbl.setFont(
            QFont(
                "Segoe UI",
                14,
                QFont.Weight.Bold
            )
        )

        title_lbl.setStyleSheet(
            "color: #0284C7; "
            "background: transparent;"
        )

        layout.addWidget(title_lbl)

        self.user_input = QLineEdit()

        self.user_input.setPlaceholderText(
            "Username"
        )

        self.user_input.setStyleSheet("""
            QLineEdit {
                background-color: rgba(255, 255, 255, 0.9);
                border: 1.5px solid #7DD3FC;
                border-radius: 8px;
                padding: 10px;
                font-size: 13px;
                color: #0F172A;
            }

            QLineEdit:focus {
                border-color: #0284C7;
            }
        """)

        layout.addWidget(
            self.user_input
        )

        self.pass_input = QLineEdit()

        self.pass_input.setPlaceholderText(
            "Password"
        )

        self.pass_input.setEchoMode(
            QLineEdit.EchoMode.Password
        )

        self.pass_input.setStyleSheet("""
            QLineEdit {
                background-color: rgba(255, 255, 255, 0.9);
                border: 1.5px solid #7DD3FC;
                border-radius: 8px;
                padding: 10px;
                font-size: 13px;
                color: #0F172A;
            }

            QLineEdit:focus {
                border-color: #0284C7;
            }
        """)

        layout.addWidget(
            self.pass_input
        )

        btn_login = QPushButton(
            "Login to Enroll"
        )

        btn_login.setCursor(
            Qt.CursorShape.PointingHandCursor
        )

        btn_login.setStyleSheet("""
            QPushButton {
                background-color: #0284C7;
                color: #FFFFFF;
                border-radius: 8px;
                padding: 12px;
                font-weight: 700;
                font-size: 13px;
                border: none;
            }

            QPushButton:hover {
                background-color: #0369A1;
            }
        """)

        btn_login.clicked.connect(
            self.verify_credentials
        )

        layout.addWidget(btn_login)

    def verify_credentials(self):

        username = self.user_input.text().strip()
        password = self.pass_input.text().strip()

        if (
            username == "enrollment123"
            and password == "sameasabove123"
        ):
            self.accept()

        else:
            QMessageBox.warning(
                self,
                "Access Denied",
                "Invalid credentials. Please check username and password."
            )


# ============================================================
# ANIMATED BACKGROUND
# ============================================================

class BubbleParticle:

    def __init__(self, w, h):
        self.reset(
            w,
            h,
            initial=True
        )

    def reset(
        self,
        w,
        h,
        initial=False
    ):

        self.x = random.uniform(
            0,
            max(1, w)
        )

        self.y = (
            random.uniform(
                0,
                max(1, h)
            )
            if initial
            else h + random.uniform(10, 50)
        )

        self.radius = random.uniform(
            12,
            45
        )

        self.speed = random.uniform(
            0.4,
            1.2
        )

        self.drift = random.uniform(
            -0.3,
            0.3
        )

        self.alpha = random.randint(
            40,
            110
        )

        colors = [
            "#38BDF8",
            "#0284C7",
            "#7DD3FC",
            "#0EA5E9",
            "#BAE6FD"
        ]

        self.color = QColor(
            random.choice(colors)
        )

        self.color.setAlpha(
            self.alpha
        )

    def move(self, w, h):

        self.y -= self.speed

        self.x += (
            math.sin(
                self.y * 0.02
            ) * 0.4
            + self.drift
        )

        if self.y < -self.radius * 2:

            self.reset(
                w,
                h,
                initial=False
            )


class AnimatedBubbleBackground(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.bubbles = []
        self.num_bubbles = 35

        self.animation_timer = QTimer(self)

        self.animation_timer.timeout.connect(
            self.animate
        )

        self.animation_timer.start(25)

    def resizeEvent(self, event):

        w = self.width()
        h = self.height()

        if not self.bubbles:

            self.bubbles = [
                BubbleParticle(w, h)
                for _ in range(self.num_bubbles)
            ]

        super().resizeEvent(event)

    def animate(self):

        w = self.width()
        h = self.height()

        for b in self.bubbles:
            b.move(w, h)

        self.update()

    def paintEvent(self, event):

        painter = QPainter(self)

        painter.setRenderHint(
            QPainter.RenderHint.Antialiasing
        )

        w = self.width()
        h = self.height()

        painter.fillRect(
            0,
            0,
            w,
            h,
            QColor("#E0F2FE")
        )

        for b in self.bubbles:

            painter.setPen(
                Qt.PenStyle.NoPen
            )

            painter.setBrush(
                QBrush(b.color)
            )

            painter.drawEllipse(
                QPointF(
                    b.x,
                    b.y
                ),
                b.radius,
                b.radius
            )


# ============================================================
# BARCODE LISTENER
# ============================================================

class BarcodeListenerThread(QThread):

    scan_received = pyqtSignal(str)

    def run(self):

        while True:

            try:

                scanned_code = (
                    sys.stdin.readline()
                    .strip()
                )

                if scanned_code:

                    process_scan(
                        scanned_code
                    )

                    self.scan_received.emit(
                        scanned_code
                    )

            except Exception:
                break


# ============================================================
# NOTICE CARD
# ============================================================

class NoticeCard(QFrame):

    def __init__(
        self,
        notice_data,
        parent=None
    ):

        super().__init__(parent)

        self.notice_data = notice_data

        self.init_ui()

    def init_ui(self):

        self.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.92);
                border-radius: 12px;
                border: 1px solid #7DD3FC;
            }
        """)

        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            18,
            16,
            18,
            16
        )

        layout.setSpacing(10)

        target = self.notice_data.get(
            "target",
            "All"
        )

        section = self.notice_data.get(
            "section",
            "All Sections"
        )

        title = self.notice_data.get(
            "title",
            "Untitled Announcement"
        )

        header_lbl = QLabel(
            f"[{target} - {section}] {title}"
        )

        header_lbl.setFont(
            QFont(
                "Segoe UI",
                12,
                QFont.Weight.Bold
            )
        )

        header_lbl.setWordWrap(True)

        header_lbl.setStyleSheet(
            "color: #0369A1; "
            "border: none; "
            "background: transparent;"
        )

        layout.addWidget(header_lbl)

        content = self.notice_data.get(
            "content",
            ""
        ).strip()

        if content:

            body_lbl = QLabel(
                content
            )

            body_lbl.setFont(
                QFont(
                    "Segoe UI",
                    11
                )
            )

            body_lbl.setWordWrap(True)

            body_lbl.setStyleSheet(
                "color: #334155; "
                "border: none; "
                "background: transparent;"
            )

            layout.addWidget(
                body_lbl
            )

        pdf_path = self.notice_data.get(
            "pdf"
        )

        if (
            pdf_path
            and os.path.exists(pdf_path)
        ):

            pdf_btn = QPushButton(
                f"Attachment: {os.path.basename(pdf_path)}"
            )

            pdf_btn.setCursor(
                Qt.CursorShape.PointingHandCursor
            )

            pdf_btn.setStyleSheet("""
                QPushButton {
                    background-color: #0284C7;
                    color: #FFFFFF;
                    border-radius: 6px;
                    padding: 8px 14px;
                    font-size: 11px;
                    font-weight: 700;
                    border: none;
                }

                QPushButton:hover {
                    background-color: #0369A1;
                }
            """)

            pdf_btn.clicked.connect(
                lambda:
                QDesktopServices.openUrl(
                    QUrl.fromLocalFile(
                        pdf_path
                    )
                )
            )

            layout.addWidget(
                pdf_btn
            )

        ts_str = self.notice_data.get(
            "timestamp",
            ""
        )

        dt_obj = parse_iso_timestamp(
            ts_str
        )

        time_display = (
            dt_obj.strftime(
                "%b %d, %Y %I:%M%p"
            )
            if dt_obj
            else "Recently"
        )

        ts_lbl = QLabel(
            f"Posted: {time_display}"
        )

        ts_lbl.setFont(
            QFont(
                "Segoe UI",
                10
            )
        )

        ts_lbl.setStyleSheet(
            "color: #64748B; "
            "border: none; "
            "background: transparent;"
        )

        layout.addWidget(
            ts_lbl
        )


# ============================================================
# NOTIFICATION DIALOG
# ============================================================

class NotificationDialog(QDialog):

    def __init__(
        self,
        notices,
        parent=None
    ):

        super().__init__(parent)

        self.setWindowTitle(
            "Official Bulletins & Notices"
        )

        self.resize(
            620,
            550
        )

        self.setStyleSheet(
            "background-color: #E0F2FE; "
            "font-family: 'Segoe UI', sans-serif;"
        )

        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            22,
            22,
            22,
            22
        )

        layout.setSpacing(16)

        title_label = QLabel(
            "Official Bulletins & Notices"
        )

        title_label.setFont(
            QFont(
                "Segoe UI",
                16,
                QFont.Weight.Bold
            )
        )

        title_label.setStyleSheet(
            "color: #0284C7; "
            "background: transparent;"
        )

        layout.addWidget(
            title_label
        )

        scroll = QScrollArea()

        scroll.setWidgetResizable(
            True
        )

        scroll.setStyleSheet(
            "QScrollArea { "
            "border: none; "
            "background: transparent; "
            "}"
        )

        container = QWidget()

        container.setStyleSheet(
            "background: transparent;"
        )

        cards_layout = QVBoxLayout(
            container
        )

        cards_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        cards_layout.setSpacing(14)

        if not notices:

            empty_lbl = QLabel(
                "No active bulletins present for this class."
            )

            empty_lbl.setStyleSheet(
                "color: #64748B; "
                "font-size: 13px;"
            )

            cards_layout.addWidget(
                empty_lbl
            )

        else:

            for n in notices:

                cards_layout.addWidget(
                    NoticeCard(n)
                )

        cards_layout.addStretch()

        scroll.setWidget(
            container
        )

        layout.addWidget(
            scroll
        )


# ============================================================
# CLASSROOM DASHBOARD
# ============================================================

class ClassroomDashboard(QWidget):

    seen_notices_counts = {}

    def __init__(
        self,
        current_class_name="Class 6 A",
        previous_window=None
    ):

        super().__init__()

        self.previous_window = previous_window

        self.help_window = None
        self.attendance_window = None
        self.attendance_display_window = None
        self.calendar_window = None

        self.selected_class_name = (
            current_class_name
        )

        self.current_notices = []

        # ----------------------------------------------------
        # CLASS / SECTION
        # ----------------------------------------------------

        match = re.search(
            r"Class\s+(\d+)\s+([A-D])",
            current_class_name
        )

        if match:

            self.class_num = int(
                match.group(1)
            )

            self.section_letter = (
                match.group(2)
            )

        else:

            self.class_num = 6
            self.section_letter = "A"

        # ----------------------------------------------------
        # PERIOD 1
        # ----------------------------------------------------

        if (
            self.class_num == 11
            and self.section_letter in ["A", "C"]
        ):

            p1_start = QTime(
                10,
                0
            )

            p1_end = QTime(
                10,
                45
            )

            p1_str = (
                "10:00 AM - 10:45 AM"
            )

        else:

            p1_start = QTime(
                10,
                15
            )

            p1_end = QTime(
                11,
                0
            )

            p1_str = (
                "10:15 AM - 11:00 AM"
            )

        # ----------------------------------------------------
        # PERIOD 4
        # ----------------------------------------------------

        if (
            self.class_num == 11
            and self.section_letter in ["B", "D"]
        ):

            p4_start = QTime(
                12,
                25
            )

            p4_end = QTime(
                13,
                25
            )

            p4_str = (
                "12:25 PM - 01:25 PM"
            )

        else:

            p4_start = QTime(
                12,
                25
            )

            p4_end = QTime(
                13,
                5
            )

            p4_str = (
                "12:25 PM - 01:05 PM"
            )

        # ----------------------------------------------------
        # PERIOD 5
        # ----------------------------------------------------

        if (
            self.class_num == 12
            and self.section_letter in ["A", "C"]
        ):

            p5_start = QTime(
                13,
                25
            )

            p5_end = QTime(
                14,
                25
            )

            p5_str = (
                "01:25 PM - 02:25 PM"
            )

        else:

            p5_start = QTime(
                13,
                45
            )

            p5_end = QTime(
                14,
                25
            )

            p5_str = (
                "01:45 PM - 02:25 PM"
            )

        # ----------------------------------------------------
        # PERIOD 9
        # ----------------------------------------------------

        if (
            self.class_num == 12
            and self.section_letter in ["B", "D"]
        ):

            p9_start = QTime(
                16,
                30
            )

            p9_end = QTime(
                17,
                30
            )

            p9_str = (
                "04:30 PM - 05:30 PM"
            )

        else:

            p9_start = QTime(
                16,
                30
            )

            p9_end = QTime(
                17,
                10
            )

            p9_str = (
                "04:30 PM - 05:10 PM"
            )

        # ----------------------------------------------------
        # COMPLETE DAILY SCHEDULE
        # ----------------------------------------------------

        self.full_schedule_structure = [

            (
                "1",
                p1_str,
                p1_start,
                p1_end,
                False,
                1
            ),

            (
                "2",
                "11:00 AM - 11:40 AM",
                QTime(11, 0),
                QTime(11, 40),
                False,
                2
            ),

            (
                "-",
                "11:40 AM - 11:45 AM",
                QTime(11, 40),
                QTime(11, 45),
                True,
                None
            ),

            (
                "3",
                "11:45 AM - 12:25 PM",
                QTime(11, 45),
                QTime(12, 25),
                False,
                3
            ),

            (
                "4",
                p4_str,
                p4_start,
                p4_end,
                False,
                4
            ),

            (
                "-",
                "01:05 PM - 01:45 PM",
                QTime(13, 5),
                QTime(13, 45),
                True,
                None
            ),

            (
                "5",
                p5_str,
                p5_start,
                p5_end,
                False,
                5
            ),

            (
                "6",
                "02:25 PM - 03:05 PM",
                QTime(14, 25),
                QTime(15, 5),
                False,
                6
            ),

            (
                "-",
                "03:05 PM - 03:10 PM",
                QTime(15, 5),
                QTime(15, 10),
                True,
                None
            ),

            (
                "7",
                "03:10 PM - 03:50 PM",
                QTime(15, 10),
                QTime(15, 50),
                False,
                7
            ),

            (
                "8",
                "03:50 PM - 04:30 PM",
                QTime(15, 50),
                QTime(16, 30),
                False,
                8
            )
        ]

        if self.class_num >= 11:
            self.full_schedule_structure.append(("9", p9_str, p9_start, p9_end, False, 9))
        self.all_routines = {
            # --- CLASS 6 ---
            "Class 6 A": {1: {},
                          2: {1: ("English", "SP"), 2: ("Science", "YS"), 3: ("Maths", "GB"), 4: ("Social", "MB"),
                              5: ("English II", "BSP"), 6: ("Nepali", "SRP"), 7: ("Computer", "PL"), 8: ("HPE", "DN")},
                          3: {1: ("English", "SP"), 2: ("Science", "YS"), 3: ("Nepali", "SRP"),
                              4: ("English II", "BSP"), 5: ("Social", "MB"), 6: ("Nepali", "SPG"),
                              7: ("Computer", "PL"), 8: ("Maths", "GB")},
                          4: {1: ("English", "SP"), 2: ("Science", "YS"), 3: ("Nepali", "SRP"), 4: ("Music", "RBJ"),
                              5: ("Social", "MB"), 6: ("Maths", "GB"), 7: ("Maths", "GB"), 8: ("Computer", "PL")},
                          5: {1: ("English", "SP"), 2: ("Science", "YS"), 3: ("Science", "YS"), 4: ("Social", "MB"),
                              5: ("English II", "BSP"), 6: ("Nepali", "SPG"), 7: ("HPE", "DN"), 8: ("Maths", "GB")},
                          6: {1: ("English", "SP"), 2: ("Science", "YS"), 3: ("Drama", "RBT"), 4: ("Arts", "HKG"),
                              5: ("Social", "MB"), 6: ("Nepali", "SRP"), 7: ("HPE", "DN"), 8: ("Maths", "GB")}, 7: {}},
            "Class 6 B": {1: {}, 2: {1: ("Social", "MB"), 2: ("English", "SP"), 3: ("HPE", "DN"), 4: ("Maths", "GB"),
                                     5: ("Computer", "PL"), 6: ("English II", "SS"), 7: ("Nepali", "SPG"),
                                     8: ("Science", "PG")},
                          3: {1: ("Social", "MB"), 2: ("English", "SP"), 3: ("Maths", "GB"), 4: ("Maths", "GB"),
                              5: ("Science", "PG"), 6: ("Science", "PG"), 7: ("English", "SS"), 8: ("Nepali", "SK")},
                          4: {1: ("Social", "MB"), 2: ("English", "SP"), 3: ("HPE", "DN"), 4: ("Maths", "GB"),
                              5: ("Science", "PG"), 6: ("Computer", "PL"), 7: ("English", "SS"), 8: ("Nepali", "SK")},
                          5: {1: ("Social", "MB"), 2: ("English", "SP"), 3: ("Music", "RBJ"), 4: ("Maths", "GB"),
                              5: ("Computer", "PL"), 6: ("Nepali", "SK"), 7: ("Arts", "HKG"), 8: ("Science", "PG")},
                          6: {1: ("Social", "MB"), 2: ("English", "SP"), 3: ("Maths", "GB"), 4: ("Drama", "RBT"),
                              5: ("HPE", "DN"), 6: ("Nepali", "SK"), 7: ("Nepali", "SPG"), 8: ("Science", "PG")},
                          7: {}},
            # --- CLASS 7 ---
            "Class 7 A": {1: {}, 2: {1: ("Nepali", "SPG"), 2: ("English", "BSP"), 3: ("English II", "SS"),
                                     4: ("Science", "YS"), 5: ("Social", "TPK"), 6: ("HPE", "DN"), 7: ("Maths", "GB"),
                                     8: ("Maths", "GB")},
                          3: {1: ("Nepali", "SPG"), 2: ("Nepali", "SPG"), 3: ("Computer", "PL"), 4: ("Science", "YS"),
                              5: ("Social", "TPK"), 6: ("Maths", "GB"), 7: ("HPE", "DN"), 8: ("English", "BSP")},
                          4: {1: ("Nepali", "SPG"), 2: ("Maths", "GB"), 3: ("English II", "SS"), 4: ("Science", "YS"),
                              5: ("Social", "TPK"), 6: ("HPE", "DN"), 7: ("Arts", "HKG"), 8: ("English", "BSP")},
                          5: {1: ("Nepali", "SPG"), 2: ("Science", "PG"), 3: ("Computer", "PL"), 4: ("Music", "RBJ"),
                              5: ("Social", "TPK"), 6: ("Maths", "GB"), 7: ("English II", "SS"), 8: ("English", "BSP")},
                          6: {1: ("Nepali", "SPG"), 2: ("Science", "PG"), 3: ("English", "BSP"), 4: ("Science", "YS"),
                              5: ("Drama", "RBT"), 6: ("Maths", "GB"), 7: ("Computer", "PL"), 8: ("Social", "TPK")},
                          7: {}},
            "Class 7 B": {1: {},
                          2: {1: ("Science", "SM"), 2: ("Science", "SM"), 3: ("Nepali", "SK"), 4: ("Maths", "DRP"),
                              5: ("HPE", "DN"), 6: ("English", "SP"), 7: ("Social", "TNS"), 8: ("English II", "SS")},
                          3: {1: ("Science", "SM"), 2: ("Maths", "DRP"), 3: ("Maths", "DRP"), 4: ("English", "SP"),
                              5: ("Nepali", "SK"), 6: ("Nepali", "SK"), 7: ("Social", "TNS"), 8: ("Computer", "PL")},
                          4: {1: ("Science", "SM"), 2: ("Music", "RBJ"), 3: ("Nepali", "SK"), 4: ("Maths", "DRP"),
                              5: ("English II", "SS"), 6: ("English", "SP"), 7: ("Social", "TNS"),
                              8: ("Nepali", "SPG")},
                          5: {1: ("Science", "SM"), 2: ("HPE", "DN"), 3: ("Nepali", "SK"), 4: ("Maths", "DRP"),
                              5: ("Arts", "HKG"), 6: ("English", "SP"), 7: ("Social", "TNS"), 8: ("Computer", "PL")},
                          6: {1: ("Science", "SM"), 2: ("Nepali", "SK"), 3: ("Computer", "PL"), 4: ("English II", "SS"),
                              5: ("Maths", "DRP"), 6: ("Drama", "RBT"), 7: ("Social", "TNS"), 8: ("English", "SP")},
                          7: {}},
            # --- CLASS 8 ---
            "Class 8 A": {1: {},
                          2: {1: ("Maths", "GB"), 2: ("Nepali", "SPG"), 3: ("Health", "SD"), 4: ("Science", "SM"),
                              5: ("Local Cu", "TNS"), 6: ("Social", "TPK"), 7: ("English", "BSP"),
                              8: ("Local Cu", "PL")},
                          3: {1: ("Maths", "GB"), 2: ("Science", "PG"), 3: ("English", "BSP"), 4: ("Science", "SM"),
                              5: ("English II", "SS"), 6: ("Social", "TPK"), 7: ("Health", "SD"), 8: ("Nepali", "SPG")},
                          4: {1: ("Maths", "GB"), 2: ("Science", "PG"), 3: ("Music", "RBJ"), 4: ("Social", "TPK"),
                              5: ("Computer", "PL"), 6: ("Local Cu", "TNS"), 7: ("English", "BSP"),
                              8: ("Nepali", "SPG")},
                          5: {1: ("Maths", "GB"), 2: ("Maths", "GB"), 3: ("English", "BSP"), 4: ("Science", "SM"),
                              5: ("English II", "SS"), 6: ("Social", "TPK"), 7: ("Health", "SD"), 8: ("Nepali", "SPG")},
                          6: {1: ("Maths", "GB"), 2: ("Drama", "RBT"), 3: ("PE", "DN"), 4: ("Social", "TPK"),
                              5: ("Science", "PG"), 6: ("Nepali", "SPG"), 7: ("English", "BSP"),
                              8: ("English II", "SS")}, 7: {}},
            "Class 8 B": {1: {}, 2: {1: ("Social", "TNS"), 2: ("PE", "DN"), 3: ("Music", "RBJ"), 4: ("Science", "PG"),
                                     5: ("Nepali", "SK"), 6: ("Maths", "NA"), 7: ("English", "SP"),
                                     8: ("Local Cu", "TPK")},
                          3: {1: ("Social", "TNS"), 2: ("Health", "SD"), 3: ("Science", "PG"), 4: ("Nepali", "SK"),
                              5: ("Maths", "DRP"), 6: ("English II", "BSP"), 7: ("English", "SP"),
                              8: ("Local Cu", "TPK")},
                          4: {1: ("Social", "TNS"), 2: ("Local Cu", "PL"), 3: ("Science", "PG"), 4: ("Nepali", "SK"),
                              5: ("English II", "BSP"), 6: ("Maths", "NA"), 7: ("English", "SP"), 8: ("Math", "DRP")},
                          5: {1: ("Social", "TNS"), 2: ("Local Cu", "PL"), 3: ("Science", "PG"), 4: ("English", "DRG"),
                              5: ("Nepali", "SK"), 6: ("Health", "SD"), 7: ("Computer", "PL"), 8: ("Math", "DRP")},
                          6: {1: ("Social", "TNS"), 2: ("Health", "SD"), 3: ("Science", "PG"), 4: ("English", "SP"),
                              5: ("Nepali", "SK"), 6: ("English II", "BSP"), 7: ("Drama", "RBT"), 8: ("Math", "DRP")},
                          7: {}},
            # --- CLASS 9 ---
            "Class 9 A": {1: {},
                          2: {1: ("Maths", "NA"), 2: ("Science", "PA"), 3: ("Social", "TPK"), 4: ("Nepali", "SPG"),
                              5: ("English", "DRG"), 6: ("English", "DRG"), 7: ("Computer, Account", "PKC, HD"),
                              8: ("Opt.Math, Economics", "LBR,YS")},
                          3: {1: ("Maths", "NA"), 2: ("Science", "PA"), 3: ("Social", "TPK"), 4: ("Nepali", "SPG"),
                              5: ("Maths", "IPG"), 6: ("English", "DRG"), 7: ("Computer, Account", "PKC, HD"),
                              8: ("Opt.Math, Economics", "LBR,YS")},
                          4: {1: ("Maths", "NA"), 2: ("English", "DRG"), 3: ("Nepali", "SPG"), 4: ("Nepali", "SPG"),
                              5: ("Science", "YS"), 6: ("Social", "TPK"), 7: ("Computer, Account", "PKC, HD"),
                              8: ("Opt.Math, Economics", "LBR,YS")},
                          5: {1: ("Maths", "NA"), 2: ("English", "DRG"), 3: ("Social", "TPK"), 4: ("Nepali", "SPG"),
                              5: ("Science", "YS"), 6: ("Science", "PA"), 7: ("Computer, Account", "KKC, HD"),
                              8: ("Opt.Math, Economics", "LBR,YS")},
                          6: {1: ("Maths", "NA"), 2: ("English", "DRG"), 3: ("Science", "PA"), 4: ("Nepali", "SPG"),
                              5: ("Social", "TPK"), 6: ("Social", "TPK"), 7: ("Computer, Account", "KKC, HD"),
                              8: ("Opt.Math, Economics", "LBR,YS")}, 7: {}},
            "Class 9 B": {1: {},
                          2: {1: ("English", "PRT"), 2: ("English", "PRT"), 3: ("Maths", "NA"), 4: ("Social", "TNS"),
                              5: ("Nepali", "KK"), 6: ("Science", "SM"), 7: ("Computer, Account", "KKC, HD"),
                              8: ("Opt.Math, Economics", "NA,YS")},
                          3: {1: ("English", "PRT"), 2: ("Nepali", "KK"), 3: ("Maths", "NA"), 4: ("Maths", "NA"),
                              5: ("Social", "TNS"), 6: ("Science", "SD"), 7: ("Computer, Account", "KKC, HD"),
                              8: ("Opt.Math, Economics", "NA,YS")},
                          4: {1: ("English", "PRT"), 2: ("Nepali", "KK"), 3: ("Science", "SD"), 4: ("Social", "TNS"),
                              5: ("Maths", "NA"), 6: ("Science", "SM"), 7: ("Computer, Account", "KKC, HD"),
                              8: ("Opt.Math, Economics", "NA,YS")},
                          5: {1: ("English", "PRT"), 2: ("Nepali", "KK"), 3: ("Social", "TNS"), 4: ("Social", "TNS"),
                              5: ("Maths", "NA"), 6: ("Science", "SM"), 7: ("Computer, Account", "PKC, HD"),
                              8: ("Opt.Math, Economics", "NA,YS")},
                          6: {1: ("English", "PRT"), 2: ("Nepali", "KK"), 3: ("Nepali", "KK"), 4: ("Social", "TNS"),
                              5: ("Maths", "NA"), 6: ("Science", "SD"), 7: ("Computer, Account", "PKC, HD"),
                              8: ("Opt.Math, Economics", "NA,YS")}, 7: {}},
            # --- CLASS 10 ---
            "Class 10 A": {1: {},
                           2: {1: ("English", "DRG"), 2: ("English", "DRG"), 3: ("Social", "TNS"), 4: ("Maths", "NA"),
                               5: ("Nepali", "SPG"), 6: ("Science", "TRS"), 7: ("Opt.Math, Economics", "IPG,YS"),
                               8: ("Computer, Account", "PKC, HD")},
                           3: {1: ("English", "DRG"), 2: ("Nepali", "SRG"), 3: ("Social", "TNS"), 4: ("Social", "TNS"),
                               5: ("Science", "YS"), 6: ("Maths", "NA"), 7: ("Opt.Math, Economics", "IPG,YS"),
                               8: ("Computer, Account", "PKC, HD")},
                           4: {1: ("English", "DRG"), 2: ("Nepali", "SRG"), 3: ("Social", "TNS"), 4: ("Maths", "NA"),
                               5: ("Nepali", "SPG"), 6: ("Science", "TRS"), 7: ("Opt.Math, Economics", "IPG,YS"),
                               8: ("Computer, Account", "PKC, HD")},
                           5: {1: ("English", "DRG"), 2: ("Nepali", "SRG"), 3: ("Maths", "NA"), 4: ("Maths", "NA"),
                               5: ("Social", "TNS"), 6: ("Science", "TRS"), 7: ("Opt.Math, Economics", "IPG,YS"),
                               8: ("Computer, Account", "KKC, HD")},
                           6: {1: ("English", "DRG"), 2: ("Nepali", "SPG"), 3: ("Social", "TNS"), 4: ("Maths", "NA"),
                               5: ("Science", "YS"), 6: ("Science", "TRS"), 7: ("Opt.Math, Economics", "IPG,YS"),
                               8: ("Computer, Account", "KKC, HD")}, 7: {}},
            "Class 10 B": {1: {},
                           2: {1: ("Social", "TPK"), 2: ("Nepali", "SRG"), 3: ("Nepali", "KK"), 4: ("Maths", "IPG"),
                               5: ("English", "PRT"), 6: ("Science", "PG"), 7: ("Opt.Math, Economics", "LBR,YS"),
                               8: ("Computer, Account", "KKC, HD")},
                           3: {1: ("Social", "TPK"), 2: ("Science", "SM"), 3: ("Nepali", "KK"), 4: ("Maths", "IPG"),
                               5: ("English", "PRT"), 6: ("English", "PRT"), 7: ("Opt.Math, Economics", "LBR,YS"),
                               8: ("Computer, Account", "KKC, HD")},
                           4: {1: ("Social", "TPK"), 2: ("Social", "TPK"), 3: ("English", "PRT"), 4: ("Maths", "LBR"),
                               5: ("Nepali", "KK"), 6: ("Science", "PG"), 7: ("Opt.Math, Economics", "LBR,YS"),
                               8: ("Computer, Account", "KKC, HD")},
                           5: {1: ("Social", "TPK"), 2: ("Science", "SM"), 3: ("Nepali", "KK"), 4: ("Maths", "IPG"),
                               5: ("English", "PRT"), 6: ("Science", "PG"), 7: ("Opt.Math, Economics", "LBR,YS"),
                               8: ("Computer, Account", "PKC, HD")},
                           6: {1: ("Social", "TPK"), 2: ("Nepali", "SRG"), 3: ("Maths", "LBR"), 4: ("English", "PRT"),
                               5: ("Maths", "IPG"), 6: ("Science", "PG"), 7: ("Opt.Math, Economics", "LBR,YS"),
                               8: ("Computer, Account", "PKC, HD")}, 7: {}},
            # --- CLASS 11 ---
            "Class 11 A": {1: {}, 2: {1: ("PHy PR, Bot PR", "SB, SD"), 2: ("Maths", "LBR"), 3: ("Physics", "PA"),
                                      4: ("Physics", "SB"), 5: ("Botany", "SD"), 6: ("Chemistry", "AP"),
                                      7: ("Zoology", "SH"), 8: ("Maths", "KB"), 9: ("English", "BSB")},
                           3: {1: ("Botany", "SD"), 2: ("Chemistry", "PS"), 3: ("Maths", "IPG"), 4: ("English", "PRT"),
                               5: ("Nepali", "KK"), 6: ("Chemistry", "MK"), 7: ("Zoology", "SH"), 8: ("Maths", "KB"),
                               9: ("Physics", "TRS")},
                           4: {1: ("Che PR, PHy PR", "PS, SB"), 2: ("Botany", "SD"), 3: ("Maths", "LBR"),
                               4: ("Nepali", "KK"), 5: ("Maths", "IPG"), 6: ("Chemistry", "AP"), 7: ("Physics", "SB"),
                               8: ("English", "PRT"), 9: ("Physics", "PA")},
                           5: {1: ("Nepali", "SRG"), 2: ("Physics", "PA"), 3: ("Chemistry", "AP"), 4: ("Botany", "SD"),
                               5: ("Maths", "IPG"), 6: ("MCQ's", "GR"), 7: ("Physics", "SB"), 8: ("Nepali", "SRG"),
                               9: ("Zoology", "SH")},
                           6: {1: ("Zol PR, Che PR", "SH, PS"), 2: ("Chemistry", "PS"), 3: ("Physics", "TRS"),
                               4: ("Chemistry", "MK"), 5: ("Maths", "LBR"), 6: ("English", "BSB"), 7: ("Maths", "IPG"),
                               8: ("Nepali", "SRG"), 9: ("Physics", "PA")}, 7: {}},
            "Class 11 B": {1: {}, 2: {1: ("Nepali", "KK"), 2: ("Physics", "SP"), 3: ("Physics", "TRS"),
                                      4: ("PHy PR, Che PR", "TRS, PB"), 5: ("Maths", "LBR"), 6: ("Botany", "SD"),
                                      7: ("Chemistry", "PS"), 8: ("English", "PRT"), 9: ("Zoology", "SH")},
                           3: {1: ("Maths", "IPG"), 2: ("Physics", "TRS"), 3: ("Maths", "LBR"),
                               4: ("Bot PR, PHy PR", "SD, PA"), 5: ("Chemistry", "PS"), 6: ("Physics", "PA"),
                               7: ("Chemistry", "PB"), 8: ("Nepali", "SRG"), 9: ("Zoology", "SH")},
                           4: {1: ("Maths", "IPG"), 2: ("MCQ's", "GR"), 3: ("Zoology", "SH"),
                               4: ("Chem PR, Zol PR", "AP, SH"), 5: ("Botany", "SD"), 6: ("Physics", "PA"),
                               7: ("Math", "KB"), 8: ("English", "BSB"), 9: ("Chemistry", "AP")},
                           5: {1: ("Botany", "SD"), 2: ("Maths", "LBR"), 3: ("Chemistry", "PB"), 4: ("Chemistry", "PS"),
                               5: ("Zoology", "SH"), 6: ("Maths", "PA"), 7: ("Nepali", "SRG"), 8: ("Physics", "PA"),
                               9: ("English", "BSB")},
                           6: {1: ("Nepali", "KK"), 2: ("Chemistry", "AP"), 3: ("Maths", "IPG"), 4: ("Physics", "PA"),
                               5: ("Math", "KB"), 6: ("Chemistry", "PB"), 7: ("Botany", "SD"), 8: ("English", "PRT"),
                               9: ("Physics", "TRS")}, 7: {}},
            "Class 11 C": {1: {}, 2: {1: ("Chemistry", "PS"), 2: ("Maths", "IPG"), 3: ("Chemistry", "PB"),
                                      4: ("Computer", "KKC"), 5: ("Maths", "KB"), 6: ("Nepali", "KK"),
                                      7: ("MCQ's", "GR"), 8: ("Physics", "RK"), 9: ("Physics", "PA")},
                           3: {1: ("PHy PR, Chem PR", "TRS, PB"), 2: ("English", "BSB"), 3: ("Computer PR", "KKC"),
                               4: ("Computer", "PKC"), 5: ("Maths", "LBR"), 6: ("Nepali", "KK"), 7: ("Physics", "PR"),
                               8: ("Chemistry", "BP"), 9: ("Chemistry", "AP")},
                           4: {1: ("Computer", "PKC"), 2: ("Maths", "IPG"), 3: ("Chemistry", "PB"),
                               4: ("Chemistry", "PS"), 5: ("Nepali", "SRG"), 6: ("Maths", "KB"), 7: ("English", "PRT"),
                               8: ("Physics", "RK"), 9: ("Physics", "TRS")},
                           5: {1: ("Che PR, PHy PR", "PB, TRS"), 2: ("Chemistry", "AP"), 3: ("Maths", "IPG"),
                               4: ("Maths", "LBR"), 5: ("Computer", "KKC"), 6: ("Nepali", "SRG"), 7: ("Physics", "TRS"),
                               8: ("English", "PRT"), 9: ("Physics", "PA")},
                           6: {1: ("Computer", "PKC"), 2: ("Maths", "LBR"), 3: ("Computer", "KKC"), 4: ("Maths", "IPG"),
                               5: ("Physics", "PA"), 6: ("Chemistry", "PS"), 7: ("Physics", "TRS"),
                               8: ("Chemistry", "AP"), 9: ("English", "BSB")}, 7: {}},
            "Class 11 D": {1: {},
                           2: {1: ("Maths", "IPG"), 2: ("Maths", "PP"), 3: ("Maths", "PP"), 4: ("English", "PRT"),
                               5: ("Nepali", "SRG"), 6: ("Physics", "SB"), 7: ("Physics", "PA"), 8: ("Chemistry", "PS"),
                               9: ("Chemistry", "AP")},
                           3: {1: ("Maths", "LBR"), 2: ("Chemistry", "MK"), 3: ("Computer", "PKC"),
                               4: ("Computer", "KKC"), 5: ("Physics", "SB"), 6: ("Nepali", "SRG"),
                               7: ("Chemistry", "PA"), 8: ("English", "DRG"), 9: ("Physics", "PA")},
                           4: {1: ("Maths", "LBR"), 2: ("Computer", "PKC"), 3: ("Computer PR", "KKC"),
                               4: ("Maths", "IPG"), 5: ("Computer", "KKC"), 6: ("Chemistry", "MK"),
                               7: ("Chemistry", "PS"), 8: ("Nepali", "SRG"), 9: ("Physics", "RK")},
                           5: {1: ("Maths", "IPG"), 2: ("Physics", "SB"), 3: ("Nepali", "SRG"),
                               4: ("Che PR, PHy PR", "AP, SB"), 5: ("Computer", "KKC"), 6: ("Chemistry", "PS"),
                               7: ("English", "PRT"), 8: ("Physics", "RK"), 9: ("Chemistry", "MK")},
                           6: {1: ("Maths", "IPG"), 2: ("Computer", "KKC"), 3: ("Computer", "PKC"),
                               4: ("PHy PR, Che", "PA, PS"), 5: ("Chemistry", "PB"), 6: ("English", "DRG"),
                               7: ("Chemistry", "PA"), 8: ("Physics", "RK"), 9: ("Maths", "PP")}, 7: {}},
            # --- CLASS 12 ---
            "Class 12 A": {1: {},
                           2: {1: ("Maths", "KB"), 2: ("Maths", "PP"), 3: ("Chemistry", "MK"), 4: ("English", "BSB"),
                               5: ("Zoology", "SH"), 6: ("Nepali", "SRG"), 7: ("Physics", "JR"), 8: ("Botany", "BPP"),
                               9: ("Botany", "BPP")},
                           3: {1: ("Physics", "SB"), 2: ("Zoology", "SH"), 3: ("Maths", "KB"), 4: ("English", "BSB"),
                               5: ("Zol PR, Che PR", "SH, BP"), 6: ("Chemistry", "PS"), 7: ("Physics", "PA"),
                               8: ("Nepali", "KK"), 9: ("Maths", "PP")},
                           4: {1: ("Maths", "KB"), 2: ("Maths", "PP"), 3: ("Nepali", "SRG"), 4: ("Chemistry", "MK"),
                               5: ("Che PR, PHy PR", "PS, SB"), 6: ("English", "DRG"), 7: ("Zoology", "SH"),
                               8: ("Chemistry", "PB"), 9: ("Physics", "JR")},
                           5: {1: ("Physics", "SB"), 2: ("Phy PR, Bot PR", "PA, BPP"), 3: ("Maths", "KB"),
                               4: ("English", "DRG"), 5: ("Bot PR, PHy PR", "PA, BPP"), 6: ("Chemistry", "MK"),
                               7: ("Physics", "JR"), 8: ("Botany", "BPP"), 9: ("Maths", "PP")},
                           6: {1: ("Physics", "SB"), 2: ("Zoology", "SH"), 3: ("Maths", "KB"), 4: ("Botany", "BPP"),
                               5: ("Chemistry", "PB"), 6: ("MCQ's", "GR"), 7: ("Nepali", "KK"), 8: ("Chemistry", "PS"),
                               9: ("Physics", "PA")}, 7: {}},
            "Class 12 B": {1: {},
                           2: {1: ("Nepali", "SRG"), 2: ("Chemistry", "MK"), 3: ("Chemistry", "PS"), 4: ("Maths", "KB"),
                               5: ("Physics", "TRS"), 6: ("Maths", "PP"), 7: ("Botany", "BPP"), 8: ("Chemistry", "PB"),
                               9: ("PHy PR, Che PR", "JR, MK")},
                           3: {1: ("Chemistry", "PS"), 2: ("Maths", "PP"), 3: ("MCQ's", "GR"), 4: ("Maths", "KB"),
                               5: ("Chemistry", "MK"), 6: ("Zoology", "SH"), 7: ("Physics", "JR"), 8: ("Physics", "SB"),
                               9: ("English", "BSB")},
                           4: {1: ("Nepali", "KK"), 2: ("Chemistry", "PS"), 3: ("Physics", "SB"), 4: ("Maths", "KB"),
                               5: ("Physics", "TRS"), 6: ("Zoology", "SH"), 7: ("Maths", "PP"), 8: ("English", "DRG"),
                               9: ("Che PR, Zol PR", "MK, SH")},
                           5: {1: ("Maths", "KB"), 2: ("Zoology", "SH"), 3: ("English", "BSB"), 4: ("Chemistry", "PB"),
                               5: ("Nepali", "KK"), 6: ("Botany", "BPP"), 7: ("Botany", "BPP"), 8: ("Physics", "JR"),
                               9: ("Bot PR, PHy PR", "BPP, JR")},
                           6: {1: ("Maths", "KB"), 2: ("Maths", "PP"), 3: ("Zoology", "SH"), 4: ("Nepali", "SRG"),
                               5: ("Botany", "BPP"), 6: ("Physics", "JR"), 7: ("Physics", "SB"), 8: ("English", "DRG"),
                               9: ("Chemistry", "MK")}, 7: {}},
            "Class 12 C": {1: {}, 2: {1: ("Computer", "KKC"), 2: ("Computer PR", "PKC"), 3: ("Computer", "PKC"),
                                      4: ("Chemistry", "AP"), 5: ("PHy PR, Che PR", "JR, AP"), 6: ("Maths", "KB"),
                                      7: ("Chemistry", "PB"), 8: ("English", "BSB"), 9: ("Maths", "PP")},
                           3: {1: ("Computer", "PKC"), 2: ("Chemistry", "PB"), 3: ("Chemistry", "MK"),
                               4: ("Maths", "PP"), 5: ("Nepali", "SRG"), 6: ("Maths", "KB"), 7: ("Physics", "TRS"),
                               8: ("Physics", "RK"), 9: ("Physics", "JR")},
                           4: {1: ("Computer", "KKC"), 2: ("Chemistry", "MK"), 3: ("MCQ's", "GR"),
                               4: ("Physics", "TRS"), 5: ("English", "DRG"), 6: ("Nepali", "KK"), 7: ("Physics", "JR"),
                               8: ("Maths", "KB"), 9: ("Maths", "PP")},
                           5: {1: ("Computer", "KKC"), 2: ("Maths", "PP"), 3: ("Computer", "PKC"),
                               4: ("Physics", "TRS"), 5: ("Nepali", "SRG"), 6: ("Maths", "KB"), 7: ("Chemistry", "AP"),
                               8: ("Maths", "KB"), 9: ("Physics", "RK")},
                           6: {1: ("Chemistry", "PB"), 2: ("Chemistry", "MK"), 3: ("Chemistry", "AP"),
                               4: ("English", "BSB"), 5: ("Che PR, PHy PR", "MK, RK"), 6: ("Maths", "KB"),
                               7: ("Physics", "RK"), 8: ("Nepali", "KK"), 9: ("Physics", "JR")}, 7: {}},
            "Class 12 D": {1: {}, 2: {1: ("Chemistry", "PB"), 2: ("Maths", "KB"), 3: ("Computer", "KKC"),
                                      4: ("Nepali II", "KK"), 5: ("Computer", "PKC"), 6: ("Physics", "JR"),
                                      7: ("Chemistry", "MK"), 8: ("English", "DRG"), 9: ("Physics", "RK")},
                           3: {1: ("Computer", "KKC"), 2: ("Maths", "KB"), 3: ("Physics", "SB"),
                               4: ("Nepali II", "SRG"), 5: ("English", "DRG"), 6: ("Chemistry", "AP"),
                               7: ("Maths", "PP"), 8: ("PHy PR, Che PR", "RK, MK")},
                           4: {1: ("Chemistry", "PB"), 2: ("Maths", "KB"), 3: ("Chemistry", "AP"), 4: ("Maths", "PP"),
                               5: ("Computer", "PKC"), 6: ("Physics", "RK"), 7: ("Nepali", "SRG"), 8: ("Physics", "SB"),
                               9: ("English", "BSB")},
                           5: {1: ("Computer PR", "PKC"), 2: ("Maths", "KB"), 3: ("Maths", "PP"), 4: ("English", "BSB"),
                               5: ("Chemistry", "MK"), 6: ("Physics", "RK"), 7: ("MCQ's", "GR"), 8: ("Nepali", "KK"),
                               9: ("Chemistry", "AP")},
                           6: {1: ("Computer", "KKC"), 2: ("Maths", "KB"), 3: ("Chemistry", "PB"), 4: ("Maths", "PP"),
                               5: ("Computer", "PKC"), 6: ("Physics", "SB"), 7: ("Physics", "JR"),
                               8: ("Chemistry", "MK"), 9: ("Che PR, Phy PR", "AP, RK")}, 7: {}}
        }




        # ----------------------------------------------------
        # INITIALIZE UI
        # ----------------------------------------------------

        self.init_ui()

        self.start_listener()

        # ====================================================
        # SUPABASE STARTUP SYNCHRONIZATION
        # ====================================================

        try:

            self.startup_attendance_data = (
                fetch_attendance_catchup()
            )

            self.today_attendance_data = (
                fetch_today_attendance()
            )

            print(
                "APK startup sync complete. "
                f"Today's attendance: "
                f"{len(self.today_attendance_data)} record(s)"
            )

        except Exception as e:

            print(
                "APK attendance startup sync failed: "
                f"{e}"
            )

            self.startup_attendance_data = []
            self.today_attendance_data = []

        # ====================================================
        # MAIN CLOCK TIMER
        # ====================================================

        self.timer = QTimer(self)

        self.timer.timeout.connect(
            self.update_live_time_and_status
        )

        self.timer.start(1000)

        # ====================================================
        # ADMIN DATA SYNCHRONIZATION
        # ====================================================

        self.sync_admin_data()

        self.realtime_thread = (
            RealtimeListenerThread(self)
        )

        self.realtime_thread.data_updated.connect(
            self.sync_admin_data
        )

        self.realtime_thread.start()

        # ====================================================
        # ATTENDANCE REALTIME
        # ====================================================

        try:

            listen_for_attendance_updates(
                self.handle_live_attendance_update
            )

        except Exception as e:

            print(
                "Could not start attendance realtime: "
                f"{e}"
            )

        # ====================================================
        # PERIODIC CLOUD SYNC
        # ====================================================

        self.cloud_sync_timer = QTimer(self)

        self.cloud_sync_timer.timeout.connect(
            self.sync_admin_data
        )

        self.cloud_sync_timer.start(
            1000
        )

        # ====================================================
        # NOTICE EXPIRATION TIMER
        # ====================================================

        self.expiration_timer = QTimer(self)

        self.expiration_timer.timeout.connect(
            self.sync_admin_data
        )

        self.expiration_timer.start(
            60000
        )

    # ========================================================
    # CLOSE
    # ========================================================

    def closeEvent(self, event):

        if hasattr(
            self,
            "cloud_sync_timer"
        ):

            self.cloud_sync_timer.stop()

        if hasattr(
            self,
            "expiration_timer"
        ):

            self.expiration_timer.stop()

        if (
            hasattr(
                self,
                "realtime_thread"
            )
            and self.realtime_thread.isRunning()
        ):

            self.realtime_thread.stop()

            self.realtime_thread.wait(
                2000
            )

        if (
            hasattr(
                self,
                "listener_thread"
            )
            and self.listener_thread.isRunning()
        ):

            self.listener_thread.terminate()

            self.listener_thread.wait(
                1000
            )

        event.accept()

    # ========================================================
    # BACK
    # ========================================================

    def go_back(self):

        if self.previous_window is not None:

            self.previous_window.show()
            self.previous_window.raise_()
            self.previous_window.activateWindow()

            self.close()

    # ========================================================
    # BARCODE LISTENER
    # ========================================================

    def start_listener(self):

        self.listener_thread = (
            BarcodeListenerThread()
        )

        self.listener_thread.start()

    # ========================================================
    # CALENDAR
    # ========================================================

    def open_cal(self):

        try:

            self.hide()

            self.calendar_window = CalendarWindow(
                previous_window=self
            )

            self.calendar_window.show()
            self.calendar_window.raise_()
            self.calendar_window.activateWindow()

        except TypeError:

            self.calendar_window = CalendarWindow()

            if hasattr(
                self.calendar_window,
                "previous_window"
            ):

                self.calendar_window.previous_window = self

            self.calendar_window.show()
            self.calendar_window.raise_()
            self.calendar_window.activateWindow()

        except Exception as e:

            self.show()

            QMessageBox.warning(
                self,
                "Calendar Error",
                "Could not open the Academic Calendar.\n\n"
                f"{e}"
            )

    # ========================================================
    # DATABASE
    # ========================================================

    def open_db(self):

        db_path = os.path.join(
            os.path.dirname(
                os.path.abspath(__file__)
            ),
            "database.py"
        )

        if os.path.exists(db_path):

            subprocess.Popen(
                [
                    sys.executable,
                    db_path
                ]
            )

            self.close()

    # ========================================================
    # FACIAL ATTENDANCE
    # ========================================================

    def open_facial_attendance(self):

        self.hide()

        self.attendance_window = (
            FacialAttendanceWindow(
                back_callback=
                self.return_from_facial_attendance,
                source_class=
                self.selected_class_name
            )
        )

        self.attendance_window.show()

    # ========================================================
    # ATTENDANCE HISTORY
    #
    # IMPORTANT:
    # Attendance history is now handled entirely by
    # attendancedisplaytest.py.
    # ========================================================

    def open_attendance_history(self):

        try:

            self.hide()

            # Close an old instance if one exists.
            if (
                self.attendance_display_window
                is not None
            ):

                try:
                    self.attendance_display_window.close()
                except Exception:
                    pass

                self.attendance_display_window = None

            # Open the new attendance history window.
            self.attendance_display_window = (
                AttendanceDisplayTest(
                    selected_class=
                    self.selected_class_name,
                    parent=None
                )
            )

            # Give the attendance window a reference
            # back to this dashboard.
            self.attendance_display_window.previous_window = (
                self
            )

            self.attendance_display_window.show()
            self.attendance_display_window.raise_()
            self.attendance_display_window.activateWindow()

        except Exception as e:

            self.show()

            QMessageBox.critical(
                self,
                "Attendance Display Error",
                "Could not open attendance display:\n\n"
                f"{e}"
            )

    # ========================================================
    # RETURN FROM FACIAL ATTENDANCE
    # ========================================================

    def return_from_facial_attendance(
        self,
        source_class
    ):

        if (
            hasattr(
                self,
                "attendance_window"
            )
            and self.attendance_window
        ):

            self.attendance_window.close()

            self.attendance_window = None

        if source_class:

            self.selected_class_name = (
                source_class
            )

            self.class_title.setText(
                f"Classroom Portal - "
                f"{self.selected_class_name}"
            )

            self.update_live_time_and_status()

            self.sync_admin_data()

            self.show()

    # ========================================================
    # ENROLLMENT
    # ========================================================

    def open_enrollment(self):

        login_dialog = LoginDialog(
            self
        )

        if (
            login_dialog.exec()
            == QDialog.DialogCode.Accepted
        ):

            try:

                if self.attendance_window is not None:

                    self.attendance_window.close()
                    self.attendance_window = None

                if self.calendar_window is not None:

                    self.calendar_window.close()
                    self.calendar_window = None

                if self.help_window is not None:

                    self.help_window.close()
                    self.help_window = None

                self.hide()

                self.enrollment_window = (
                    EnrollmentWindow(
                        previous_window=self
                    )
                )

                self.enrollment_window.show()
                self.enrollment_window.raise_()
                self.enrollment_window.activateWindow()

            except Exception as e:

                self.show()

                QMessageBox.warning(
                    self,
                    "Enrollment Error",
                    "Could not open the Student Enrollment page.\n\n"
                    f"{e}"
                )

    # ========================================================
    # HELP
    # ========================================================

    def open_help(self):

        if self.help_window is None:

            self.help_window = HelpWindow(
                self
            )

            self.hide()

            self.help_window.show()
            self.help_window.raise_()
            self.help_window.activateWindow()

    # ========================================================
    # LOGOUT
    # ========================================================

    def handle_logout(self):

        reply = QMessageBox.question(
            self,
            "Confirm Session Exit",
            "Are you sure you want to log out of the classroom system?",
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if (
            reply
            == QMessageBox.StandardButton.Yes
        ):

            admin_path = os.path.join(
                os.path.dirname(
                    os.path.abspath(__file__)
                ),
                "classroom.py"
            )

            if os.path.exists(
                admin_path
            ):

                subprocess.Popen(
                    [
                        sys.executable,
                        admin_path
                    ],
                    cwd=os.path.dirname(
                        admin_path
                    )
                )

            self.close()

            QApplication.quit()

    # ========================================================
    # NOTIFICATIONS
    # ========================================================

    def show_notifications(self):

        dialog = NotificationDialog(
            self.current_notices,
            self
        )

        dialog.exec()

        ClassroomDashboard.seen_notices_counts[
            self.selected_class_name
        ] = len(
            self.current_notices
        )

        self.update_notices_button_style()

    # ========================================================
    # NOTICE FILTER
    # ========================================================

    def is_notice_relevant(
        self,
        notice
    ):

        if not is_recent(
            notice.get("timestamp")
        ):

            return False

        target = notice.get(
            "target",
            ""
        )

        sec_str = notice.get(
            "section",
            "All Sections"
        )

        if sec_str != "All Sections":

            expected_sec = (
                f"Section {self.section_letter}"
            )

            if sec_str != expected_sec:
                return False

        if "Class 6-12" in target:
            return True

        if (
            "Class 6-10" in target
            and 6 <= self.class_num <= 10
        ):
            return True

        if (
            "Class 11-12" in target
            and 11 <= self.class_num <= 12
        ):
            return True

        match_range = re.search(
            r"Class\s+(\d+)(?:-(\d+))?",
            target
        )

        if match_range:

            start_g = int(
                match_range.group(1)
            )

            end_g = (
                int(match_range.group(2))
                if match_range.group(2)
                else start_g
            )

            if (
                start_g
                <= self.class_num
                <= end_g
            ):

                return True

        match_exact = re.search(
            r"Class\s+(\d+)",
            target
        )

        if (
            match_exact
            and int(match_exact.group(1))
            == self.class_num
        ):

            return True

        return False

    # ========================================================
    # NOTICE BUTTON
    # ========================================================

    def update_notices_button_style(self):

        notice_count = len(
            self.current_notices
        )

        seen_count = (
            ClassroomDashboard
            .seen_notices_counts
            .get(
                self.selected_class_name,
                0
            )
        )

        unseen_count = (
            notice_count
            - seen_count
        )

        if unseen_count > 0:

            self.btn_notices.setText(
                f"Notices ({unseen_count} New)"
            )

            self.btn_notices.setStyleSheet("""
                QPushButton {
                    background-color: #0284C7;
                    color: #FFFFFF;
                    border-radius: 10px;
                    font-size: 14px;
                    font-weight: 700;
                    padding: 12px 18px;
                    border: none;
                    text-align: left;
                }
            """)

        else:

            self.btn_notices.setText(
                "Notices"
            )

            self.btn_notices.setStyleSheet("""
                QPushButton {
                    background-color: rgba(255, 255, 255, 0.85);
                    color: #0284C7;
                    border-radius: 10px;
                    padding: 12px 18px;
                    font-size: 14px;
                    font-weight: 700;
                    border: 1px solid #7DD3FC;
                    text-align: left;
                }

                QPushButton:hover {
                    background-color: #0284C7;
                    color: #FFFFFF;
                }
            """)

    # ========================================================
    # ADMIN DATA SYNC
    # ========================================================

    def sync_admin_data(self):

        data = fetch_network_data(
            DATA_FILE
        )

        if not data:
            return

        # ----------------------------------------------------
        # NOTICES
        # ----------------------------------------------------

        all_notices = data.get(
            "notices",
            []
        )

        self.current_notices = [
            n
            for n in all_notices
            if self.is_notice_relevant(n)
        ]

        self.update_notices_button_style()

        # ----------------------------------------------------
        # FACULTY SUBSTITUTIONS
        # ----------------------------------------------------

        all_substitutions = data.get(
            "substitutions",
            []
        )

        matching_subs = []

        for sub in all_substitutions:

            if not is_recent(
                sub.get("timestamp")
            ):
                continue

            sub_c = str(
                sub.get(
                    "class",
                    ""
                )
            ).strip()

            sub_s = str(
                sub.get(
                    "section",
                    ""
                )
            ).strip()

            if (
                sub_c
                == str(self.class_num)
                and
                sub_s.upper()
                == self.section_letter.upper()
            ):

                matching_subs.append(
                    sub
                )

        # ----------------------------------------------------
        # CLEAR OLD SUBSTITUTIONS
        # ----------------------------------------------------

        while (
            self.sub_content_layout.count()
        ):

            child = (
                self.sub_content_layout.takeAt(0)
            )

            if child.widget():

                child.widget().deleteLater()

        # ----------------------------------------------------
        # DISPLAY SUBSTITUTIONS
        # ----------------------------------------------------

        if not matching_subs:

            sub_msg1 = QLabel(
                "No faculty substitutions recorded for today."
            )

            sub_msg1.setAlignment(
                Qt.AlignmentFlag.AlignLeft
            )

            sub_msg1.setStyleSheet(
                "color: #64748B; "
                "font-size: 13px; "
                "border: none; "
                "background: transparent; "
                "padding-top: 8px;"
            )

            self.sub_content_layout.addWidget(
                sub_msg1
            )

        else:

            for sub in matching_subs:

                p = sub.get(
                    "period",
                    "-"
                )

                absent = sub.get(
                    "absent",
                    "-"
                )

                substitute = sub.get(
                    "substitute",
                    "-"
                )

                sub_label = QLabel(
                    f"<b>Period {p}:</b> "
                    f"{substitute} "
                    f"<span style='color:#64748B;'>"
                    f"(Replacing {absent})"
                    f"</span>"
                )

                sub_label.setStyleSheet(
                    "color: #0F172A; "
                    "font-size: 13px; "
                    "margin-top: 6px; "
                    "border: none; "
                    "background: transparent;"
                )

                self.sub_content_layout.addWidget(
                    sub_label
                )

    # ========================================================
    # LIVE ATTENDANCE UPDATE
    #
    # Attendance history is no longer displayed here.
    # The actual history UI belongs to AttendanceDisplayTest.
    # ========================================================

    def handle_live_attendance_update(
        self,
        attendance_record
    ):

        try:

            today = (
                datetime.datetime
                .now()
                .date()
                .isoformat()
            )

            record_date = str(
                attendance_record.get(
                    "attendance_date",
                    ""
                )
            )

            # Ignore records belonging to another date.
            if record_date != today:
                return

            # Make sure today's attendance list exists.
            if not hasattr(
                self,
                "today_attendance_data"
            ):

                self.today_attendance_data = []

            record_id = (
                attendance_record.get("id")
            )

            replaced = False

            # Update an existing record.
            for index, existing in enumerate(
                self.today_attendance_data
            ):

                if (
                    existing.get("id")
                    == record_id
                ):

                    self.today_attendance_data[
                        index
                    ] = attendance_record

                    replaced = True

                    break

            # Add a new record.
            if not replaced:

                self.today_attendance_data.append(
                    attendance_record
                )

            print(
                "Live attendance update received:",
                attendance_record
            )

            # ------------------------------------------------
            # IMPORTANT:
            # Do NOT access the old
            # AttendanceHistoryDialog here.
            #
            # AttendanceDisplayTest is now responsible for
            # displaying attendance history.
            # ------------------------------------------------

        except Exception as e:

            print(
                "Live attendance UI update failed: "
                f"{e}"
            )

    # ========================================================
    # LIVE CLOCK + STATUS
    # ========================================================

    def update_live_time_and_status(self):

        now = datetime.datetime.now()

        self.clock_lbl.setText(
            now.strftime("%I:%M%p")
        )

        self.date_lbl.setText(
            now.strftime(
                "%A, %B %d, %Y"
            )
        )

        py_weekday = now.weekday()

        day_map = {
            6: 1,
            0: 2,
            1: 3,
            2: 4,
            3: 5,
            4: 6,
            5: 7
        }

        current_routine_day = (
            day_map[py_weekday]
        )

        selected_routine = (
            self.all_routines.get(
                self.selected_class_name,
                {}
            )
        )

        today_classes = (
            selected_routine.get(
                current_routine_day,
                {}
            )
        )

        if current_routine_day in [1, 7]:

            self.badge.setText(
                "SCHEDULED OFF"
            )

            self.badge.setStyleSheet(
                "background-color: #CBD5E1; "
                "color: #475569; "
                "border-radius: 6px; "
                "padding: 6px 12px; "
                "font-weight: 800; "
                "font-size: 11px;"
            )

            self.period_lbl.setText(
                "Weekend Non-Instructional Day"
            )

            self.subj_lbl.setText(
                "Weekend Recess"
            )

            self.teacher_lbl.setText(
                "Faculty: Unassigned"
            )

        else:

            current_qtime = (
                QTime.currentTime()
            )

            active_block = None

            for (
                p_num,
                time_str,
                start_t,
                end_t,
                is_break,
                p_idx
            ) in self.full_schedule_structure:

                if (
                    start_t
                    <= current_qtime
                    <= end_t
                ):

                    active_block = (
                        p_num,
                        time_str,
                        is_break,
                        p_idx
                    )

                    break

            if active_block:

                (
                    p_num,
                    time_str,
                    is_break,
                    p_idx
                ) = active_block

                if is_break:

                    self.badge.setText(
                        "RECESS / BREAK"
                    )

                    self.badge.setStyleSheet(
                        "background-color: #FEF3C7; "
                        "color: #D97706; "
                        "border-radius: 6px; "
                        "padding: 6px 12px; "
                        "font-weight: 800; "
                        "font-size: 11px;"
                    )

                    self.period_lbl.setText(
                        f"Break Interval "
                        f"({time_str})"
                    )

                    self.subj_lbl.setText(
                        "Recess Period"
                    )

                    self.teacher_lbl.setText(
                        "Faculty: Standard Supervision"
                    )

                else:

                    subj, teacher = (
                        today_classes.get(
                            p_idx,
                            (
                                "Free Period",
                                "N/A"
                            )
                        )
                    )

                    self.badge.setText(
                        "IN PROGRESS"
                    )

                    self.badge.setStyleSheet(
                        "background-color: #DCFCE7; "
                        "color: #15803D; "
                        "border-radius: 6px; "
                        "padding: 6px 12px; "
                        "font-weight: 800; "
                        "font-size: 11px;"
                    )

                    self.period_lbl.setText(
                        f"Period {p_num} "
                        f"({time_str})"
                    )

                    self.subj_lbl.setText(
                        subj
                    )

                    self.teacher_lbl.setText(
                        f"Instructor: {teacher}"
                    )

            else:

                self.badge.setText(
                    "INACTIVE"
                )

                self.badge.setStyleSheet(
                    "background-color: #E2E8F0; "
                    "color: #64748B; "
                    "border-radius: 6px; "
                    "padding: 6px 12px; "
                    "font-weight: 800; "
                    "font-size: 11px;"
                )

                self.period_lbl.setText(
                    "Academic Hours Concluded"
                )

                self.subj_lbl.setText(
                    "No Active Class"
                )

                self.teacher_lbl.setText(
                    "Instructor: Unassigned"
                )

        self.update_schedule_table()

    # ========================================================
    # SCHEDULE TABLE
    # ========================================================

    def update_schedule_table(self):

        py_weekday = (
            datetime.datetime.now()
            .weekday()
        )

        day_map = {
            6: 1,
            0: 2,
            1: 3,
            2: 4,
            3: 5,
            4: 6,
            5: 7
        }

        current_routine_day = (
            day_map[py_weekday]
        )

        selected_routine = (
            self.all_routines.get(
                self.selected_class_name,
                {}
            )
        )

        today_classes = (
            selected_routine.get(
                current_routine_day,
                {}
            )
        )

        data = []

        if current_routine_day in [1, 7]:

            data.append(
                (
                    "-",
                    "All Day",
                    "Weekend Recess",
                    "-"
                )
            )

        else:

            for (
                p_num,
                time_str,
                _,
                _,
                is_break,
                p_idx
            ) in self.full_schedule_structure:

                if is_break:

                    data.append(
                        (
                            p_num,
                            time_str,
                            "Intermission / Recess",
                            "-"
                        )
                    )

                else:

                    subj, teacher = (
                        today_classes.get(
                            p_idx,
                            (
                                "-",
                                "-"
                            )
                        )
                    )

                    data.append(
                        (
                            p_num,
                            time_str,
                            subj,
                            teacher
                        )
                    )

        self.table.setRowCount(
            len(data)
        )

        for row, period in enumerate(data):

            for col, item in enumerate(
                period
            ):

                item_widget = (
                    QTableWidgetItem(item)
                )

                if period[2] in [
                    "Intermission / Recess",
                    "Weekend Recess"
                ]:

                    item_widget.setForeground(
                        QColor("#94A3B8")
                    )

                else:

                    item_widget.setForeground(
                        QColor("#0F172A")
                    )

                self.table.setItem(
                    row,
                    col,
                    item_widget
                )

    # ========================================================
    # UI
    # ========================================================

    def init_ui(self):

        self.setWindowTitle(
            "SOS Hermann Gmeiner School Gandaki - "
            f"Portal ({self.selected_class_name})"
        )

        self.resize(
            1200,
            720
        )

        root_layout = QVBoxLayout(self)

        root_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        bg_widget = AnimatedBubbleBackground(
            self
        )

        root_layout.addWidget(
            bg_widget
        )

        app_layout = QHBoxLayout(
            bg_widget
        )

        app_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        app_layout.setSpacing(0)

        # ====================================================
        # SIDEBAR
        # ====================================================

        sidebar = QWidget()

        sidebar.setFixedWidth(
            260
        )

        sidebar.setStyleSheet(
            "background-color: "
            "rgba(255, 255, 255, 0.85); "
            "border-right: "
            "1px solid #7DD3FC;"
        )

        sidebar_layout = QVBoxLayout(
            sidebar
        )

        sidebar_layout.setContentsMargins(
            22,
            26,
            22,
            26
        )

        sidebar_layout.setSpacing(
            16
        )

        brand_container = QFrame()

        brand_container.setStyleSheet(
            "background-color: #0284C7; "
            "border-radius: 12px; "
            "padding: 12px;"
        )

        brand_box = QVBoxLayout(
            brand_container
        )

        brand_box.setSpacing(
            2
        )

        main_title = QLabel(
            "SOS HGS"
        )

        main_title.setFont(
            QFont(
                "Segoe UI",
                18,
                QFont.Weight.Black
            )
        )

        main_title.setStyleSheet(
            "color: #FFFFFF; "
            "background: transparent;"
        )

        sub_title = QLabel(
            "GANDAKI PORTAL"
        )

        sub_title.setFont(
            QFont(
                "Segoe UI",
                10,
                QFont.Weight.Bold
            )
        )

        sub_title.setStyleSheet(
            "color: #BAE6FD; "
            "background: transparent; "
            "letter-spacing: 1px;"
        )

        brand_box.addWidget(
            main_title
        )

        brand_box.addWidget(
            sub_title
        )

        sidebar_layout.addWidget(
            brand_container
        )

        sidebar_layout.addSpacing(
            16
        )

        # ====================================================
        # HOME
        # ====================================================

        self.btn_home = QPushButton(
            "Home Dashboard"
        )

        self.btn_home.setCursor(
            Qt.CursorShape.PointingHandCursor
        )

        self.btn_home.setStyleSheet("""
            QPushButton {
                background-color: #0284C7;
                color: #FFFFFF;
                border-radius: 10px;
                padding: 12px 18px;
                font-size: 14px;
                font-weight: 700;
                border: none;
                text-align: left;
            }
        """)

        # ====================================================
        # CALENDAR
        # ====================================================

        btn_cal = QPushButton(
            "Academic Calendar"
        )

        btn_cal.setCursor(
            Qt.CursorShape.PointingHandCursor
        )

        btn_cal.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.85);
                color: #0284C7;
                border-radius: 10px;
                padding: 12px 18px;
                font-size: 14px;
                font-weight: 700;
                border: 1px solid #7DD3FC;
                text-align: left;
            }

            QPushButton:hover {
                background-color: #0284C7;
                color: #FFFFFF;
            }
        """)

        btn_cal.clicked.connect(
            self.open_cal
        )

        # ====================================================
        # NOTICES
        # ====================================================

        self.btn_notices = QPushButton(
            "Notices"
        )

        self.btn_notices.setCursor(
            Qt.CursorShape.PointingHandCursor
        )

        self.btn_notices.clicked.connect(
            self.show_notifications
        )

        sidebar_layout.addWidget(
            self.btn_home
        )

        sidebar_layout.addWidget(
            btn_cal
        )

        sidebar_layout.addWidget(
            self.btn_notices
        )

        sidebar_layout.addStretch()

        # ====================================================
        # ENROLL
        # ====================================================

        btn_enroll = QPushButton(
            "Enroll"
        )

        btn_enroll.setCursor(
            Qt.CursorShape.PointingHandCursor
        )

        btn_enroll.setStyleSheet("""
            QPushButton {
                background-color: #0284C7;
                color: #FFFFFF;
                border-radius: 10px;
                padding: 14px 18px;
                font-weight: 700;
                font-size: 14px;
                border: none;
            }

            QPushButton:hover {
                background-color: #0369A1;
            }
        """)

        camera_icon = self.style().standardIcon(
            QApplication.style().StandardPixmap.SP_FileDialogDetailedView
        )

        if not camera_icon.isNull():
            btn_enroll.setIcon(
                camera_icon
            )

        btn_enroll.clicked.connect(
            self.open_enrollment
        )

        sidebar_layout.addWidget(
            btn_enroll
        )

        # ====================================================
        # ATTENDANCE BUTTONS
        # ====================================================

        attendance_btn_layout = QHBoxLayout()

        attendance_btn_layout.setSpacing(
            6
        )

        btn_attendance = QPushButton(
            "Mark Attendance"
        )

        btn_attendance.setCursor(
            Qt.CursorShape.PointingHandCursor
        )

        btn_attendance.setStyleSheet("""
            QPushButton {
                background-color: #0284C7;
                color: #FFFFFF;
                border-radius: 10px;
                padding: 14px 18px;
                font-weight: 700;
                font-size: 14px;
                border: none;
            }

            QPushButton:hover {
                background-color: #0369A1;
            }
        """)

        btn_attendance.clicked.connect(
            self.open_facial_attendance
        )

        attendance_btn_layout.addWidget(
            btn_attendance,
            1
        )

        # ====================================================
        # ATTENDANCE HISTORY
        # ====================================================

        btn_history = QPushButton()

        btn_history.setCursor(
            Qt.CursorShape.PointingHandCursor
        )

        history_icon = self.style().standardIcon(
            QApplication.style().StandardPixmap.SP_FileDialogListView
        )

        if not history_icon.isNull():

            btn_history.setIcon(
                history_icon
            )

        else:

            btn_history.setText(
                "H"
            )

        btn_history.setToolTip(
            "View Attendance History"
        )

        btn_history.setStyleSheet("""
            QPushButton {
                background-color: #0284C7;
                color: #FFFFFF;
                border-radius: 10px;
                padding: 14px;
                border: none;
            }

            QPushButton:hover {
                background-color: #0369A1;
            }
        """)

        btn_history.clicked.connect(
            self.open_attendance_history
        )

        attendance_btn_layout.addWidget(
            btn_history
        )

        sidebar_layout.addLayout(
            attendance_btn_layout
        )

        app_layout.addWidget(
            sidebar
        )

        # ====================================================
        # MAIN CONTENT
        # ====================================================

        main_content = QWidget()

        main_content.setStyleSheet(
            "background: transparent;"
        )

        main_layout = QVBoxLayout(
            main_content
        )

        main_layout.setContentsMargins(
            32,
            24,
            32,
            24
        )

        main_layout.setSpacing(
            20
        )

        # ====================================================
        # TOP BAR
        # ====================================================

        top_bar = QHBoxLayout()

        self.class_title = QLabel(
            f"Classroom Portal - "
            f"{self.selected_class_name}"
        )

        self.class_title.setFont(
            QFont(
                "Segoe UI",
                20,
                QFont.Weight.Bold
            )
        )

        self.class_title.setStyleSheet(
            "color: #0369A1; "
            "background: transparent;"
        )

        time_box = QVBoxLayout()

        time_box.setSpacing(
            2
        )

        time_box.setAlignment(
            Qt.AlignmentFlag.AlignRight
        )

        self.clock_lbl = QLabel(
            ""
        )

        self.clock_lbl.setFont(
            QFont(
                "Segoe UI",
                16,
                QFont.Weight.Bold
            )
        )

        self.clock_lbl.setStyleSheet(
            "color: #0284C7; "
            "background: transparent;"
        )

        self.date_lbl = QLabel(
            ""
        )

        self.date_lbl.setFont(
            QFont(
                "Segoe UI",
                11,
                QFont.Weight.DemiBold
            )
        )

        self.date_lbl.setStyleSheet(
            "color: #475569; "
            "background: transparent;"
        )

        time_box.addWidget(
            self.clock_lbl
        )

        time_box.addWidget(
            self.date_lbl
        )

        top_bar.addWidget(
            self.class_title
        )

        top_bar.addStretch()

        top_bar.addLayout(
            time_box
        )

        main_layout.addLayout(
            top_bar
        )

        # ====================================================
        # TOP CARDS
        # ====================================================

        top_cards_layout = QHBoxLayout()

        top_cards_layout.setSpacing(
            20
        )

        self.curr_card = QFrame()

        self.curr_card.setStyleSheet(
            "background-color: "
            "rgba(255, 255, 255, 0.88); "
            "border-radius: 16px; "
            "border: 1.5px solid #7DD3FC;"
        )

        curr_layout = QVBoxLayout(
            self.curr_card
        )

        curr_layout.setContentsMargins(
            24,
            20,
            24,
            20
        )

        curr_head = QHBoxLayout()

        curr_title = QLabel(
            "CURRENT INSTRUCTIONAL STATUS"
        )

        curr_title.setFont(
            QFont(
                "Segoe UI",
                10,
                QFont.Weight.Bold
            )
        )

        curr_title.setStyleSheet(
            "color: #0284C7; "
            "border: none; "
            "background: transparent; "
            "letter-spacing: 0.8px;"
        )

        self.badge = QLabel(
            "IN PROGRESS"
        )

        self.badge.setStyleSheet(
            "background-color: #DCFCE7; "
            "color: #15803D; "
            "border-radius: 6px; "
            "padding: 6px 12px; "
            "font-weight: 800; "
            "font-size: 11px;"
        )

        curr_head.addWidget(
            curr_title
        )

        curr_head.addStretch()

        curr_head.addWidget(
            self.badge
        )

        self.period_lbl = QLabel(
            "-"
        )

        self.period_lbl.setStyleSheet(
            "color: #64748B; "
            "font-size: 13px; "
            "font-weight: 600; "
            "margin-top: 4px; "
            "border: none; "
            "background: transparent;"
        )

        self.subj_lbl = QLabel(
            "-"
        )

        self.subj_lbl.setFont(
            QFont(
                "Segoe UI",
                22,
                QFont.Weight.Bold
            )
        )

        self.subj_lbl.setStyleSheet(
            "color: #0F172A; "
            "border: none; "
            "background: transparent;"
        )

        self.teacher_lbl = QLabel(
            "Instructor: -"
        )

        self.teacher_lbl.setStyleSheet(
            "color: #334155; "
            "font-size: 14px; "
            "font-weight: 600; "
            "border: none; "
            "background: transparent;"
        )

        curr_layout.addLayout(
            curr_head
        )

        curr_layout.addWidget(
            self.period_lbl
        )

        curr_layout.addWidget(
            self.subj_lbl
        )

        curr_layout.addWidget(
            self.teacher_lbl
        )

        # ====================================================
        # SUBSTITUTIONS
        # ====================================================

        sub_card = QFrame()

        sub_card.setStyleSheet(
            "background-color: "
            "rgba(255, 255, 255, 0.88); "
            "border-radius: 16px; "
            "border: 1.5px solid #7DD3FC;"
        )

        sub_layout = QVBoxLayout(
            sub_card
        )

        sub_layout.setContentsMargins(
            24,
            20,
            24,
            20
        )

        sub_title = QLabel(
            "FACULTY SUBSTITUTIONS"
        )

        sub_title.setFont(
            QFont(
                "Segoe UI",
                10,
                QFont.Weight.Bold
            )
        )

        sub_title.setStyleSheet(
            "color: #0284C7; "
            "border: none; "
            "background: transparent; "
            "letter-spacing: 0.8px;"
        )

        sub_layout.addWidget(
            sub_title
        )

        self.sub_content_layout = (
            QVBoxLayout()
        )

        sub_layout.addLayout(
            self.sub_content_layout
        )

        sub_layout.addStretch()

        top_cards_layout.addWidget(
            self.curr_card,
            1
        )

        top_cards_layout.addWidget(
            sub_card,
            1
        )

        main_layout.addLayout(
            top_cards_layout
        )

        # ====================================================
        # DAILY SCHEDULE TABLE
        # ====================================================

        table_container = QFrame()

        table_container.setStyleSheet(
            "background-color: "
            "rgba(255, 255, 255, 0.88); "
            "border-radius: 16px; "
            "border: 1.5px solid #7DD3FC;"
        )

        table_box_layout = QVBoxLayout(
            table_container
        )

        table_box_layout.setContentsMargins(
            24,
            20,
            24,
            20
        )

        table_head = QHBoxLayout()

        routine_lbl = QLabel(
            "Daily Academic Schedule"
        )

        routine_lbl.setFont(
            QFont(
                "Segoe UI",
                14,
                QFont.Weight.Bold
            )
        )

        routine_lbl.setStyleSheet(
            "color: #0F172A; "
            "border: none; "
            "background: transparent;"
        )

        table_head.addWidget(
            routine_lbl
        )

        table_head.addStretch()

        table_box_layout.addLayout(
            table_head
        )

        self.table = QTableWidget(
            0,
            4
        )

        self.table.setHorizontalHeaderLabels(
            [
                "Period",
                "Time Interval",
                "Subject / Activity",
                "Instructor"
            ]
        )

        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )

        self.table.verticalHeader().setVisible(
            False
        )

        self.table.setShowGrid(
            False
        )

        self.table.setStyleSheet("""
            QTableWidget {
                background-color: transparent;
                color: #0F172A;
                font-size: 13px;
                border: none;
            }

            QHeaderView::section {
                background-color: #E0F2FE;
                color: #0284C7;
                font-weight: 800;
                font-size: 12px;
                border: none;
                padding: 10px;
                border-bottom: 2px solid #38BDF8;
            }

            QTableWidget::item {
                padding: 10px;
                border-bottom: 1px solid #E2E8F0;
            }

            QTableWidget::item:selected {
                background-color: #BAE6FD;
                color: #0284C7;
            }
        """)

        table_box_layout.addWidget(
            self.table
        )

        main_layout.addWidget(
            table_container
        )

        # ====================================================
        # FOOTER
        # ====================================================

        footer = QFrame()

        footer.setStyleSheet(
            "background-color: "
            "rgba(255, 255, 255, 0.88); "
            "border-radius: 12px; "
            "border: 1px solid #7DD3FC;"
        )

        footer_layout = QHBoxLayout(
            footer
        )

        footer_layout.setContentsMargins(
            20,
            10,
            20,
            10
        )

        quote_lbl = QLabel(
            "SOS Hermann Gmeiner School Gandaki - "
            "Excellence & Character in Education"
        )

        quote_lbl.setStyleSheet(
            "color: #475569; "
            "font-size: 12px; "
            "font-weight: 600; "
            "border: none; "
            "background: transparent;"
        )

        actions_layout = QHBoxLayout()

        actions_layout.setSpacing(
            10
        )

        # ====================================================
        # HELP BUTTON
        # ====================================================

        btn_help = QPushButton(
            "System Guide"
        )

        btn_help.setCursor(
            Qt.CursorShape.PointingHandCursor
        )

        btn_help.setStyleSheet("""
            QPushButton {
                background-color: #E0F2FE;
                color: #0284C7;
                border-radius: 6px;
                padding: 6px 14px;
                font-size: 12px;
                border: 1px solid #7DD3FC;
                font-weight: 700;
            }

            QPushButton:hover {
                background-color: #BAE6FD;
            }
        """)

        btn_help.clicked.connect(
            self.open_help
        )

        # ====================================================
        # LOGOUT BUTTON
        # ====================================================

        btn_logout = QPushButton(
            "Logout"
        )

        btn_logout.setCursor(
            Qt.CursorShape.PointingHandCursor
        )

        btn_logout.setStyleSheet("""
            QPushButton {
                background-color: #EF4444;
                color: #FFFFFF;
                border-radius: 6px;
                padding: 6px 14px;
                font-size: 12px;
                border: none;
                font-weight: 700;
            }

            QPushButton:hover {
                background-color: #DC2626;
            }
        """)

        btn_logout.clicked.connect(
            self.handle_logout
        )

        actions_layout.addWidget(
            btn_help
        )

        actions_layout.addWidget(
            btn_logout
        )

        footer_layout.addWidget(
            quote_lbl
        )

        footer_layout.addStretch()

        footer_layout.addLayout(
            actions_layout
        )

        main_layout.addWidget(
            footer
        )

        app_layout.addWidget(
            main_content
        )


# ============================================================
# PROGRAM START
# ============================================================

if __name__ == "__main__":

    app = QApplication(
        sys.argv
    )

    if len(sys.argv) >= 3:

        target_class = (
            f"Class {sys.argv[1]} "
            f"{sys.argv[2]}"
        )

    elif len(sys.argv) == 2:

        raw_arg = sys.argv[1]

        target_class = (
            raw_arg
            if raw_arg.startswith("Class ")
            else f"Class {raw_arg}"
        )

    else:

        target_class = (
            "Class 10 A"
        )

    window = ClassroomDashboard(
        target_class
    )

    window.show()

    sys.exit(
        app.exec()
    )
