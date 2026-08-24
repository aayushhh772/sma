import sys
import re

from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QMessageBox,
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor, QFont

from database import supabase


class AttendanceDisplayTest(QWidget):
    """Simple attendance-history window for test.py.

    It intentionally contains only the attendance table. The existing
    facial-recognition/database backend is not modified.
    """

    def __init__(self, selected_class="Class 6 A", parent=None):
        super().__init__(parent)

        self.previous_window = parent

        # Set standalone window flags
        self.setWindowFlags(Qt.WindowType.Window)
        
        self.selected_class = str(selected_class).strip()
        self.class_number, self.section = self.extract_class_section(
            self.selected_class
        )

        self.setWindowTitle(f"Attendance - {self.selected_class}")
        self.resize(900, 560)
        self.setMinimumSize(700, 400)

        self.build_ui()
        self.load_attendance()

        # Refresh periodically so attendance marked by facial recognition
        # appears without having to close and reopen this window.
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.load_attendance)
        self.refresh_timer.start(3000)

    @staticmethod
    def extract_class_section(class_text):
        """Convert 'Class 9 A' into ('9', 'A')."""
        text = str(class_text).strip()

        match = re.search(r"Class\s+(\d+)\s+([A-D])\b", text, re.IGNORECASE)
        if match:
            return match.group(1), match.group(2).upper()

        match = re.search(r"^(\d+)\s+([A-D])\b", text, re.IGNORECASE)
        if match:
            return match.group(1), match.group(2).upper()

        class_match = re.search(r"(\d+)", text)
        section_match = re.search(r"\b([A-D])\b", text, re.IGNORECASE)
        return (
            class_match.group(1) if class_match else text,
            section_match.group(1).upper() if section_match else "A",
        )

    def build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 24)
        root.setSpacing(16)

        header = QHBoxLayout()
        header.setSpacing(12)

        self.back_button = QPushButton("←  Back")
        self.back_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.back_button.setFixedSize(110, 44)
        self.back_button.clicked.connect(self.go_back)
        self.back_button.setStyleSheet("""
            QPushButton {
                background: #0F172A;
                color: white;
                border: none;
                border-radius: 12px;
                font-size: 14px;
                font-weight: 700;
            }
            QPushButton:hover { background: #1E293B; }
            QPushButton:pressed { background: #334155; }
        """)
        header.addWidget(self.back_button)

        title_box = QVBoxLayout()
        title = QLabel("Attendance Overview")
        title.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        title.setStyleSheet("color: #0F172A;")
        subtitle = QLabel(
            f"{self.selected_class}  •  Live facial-recognition attendance"
        )
        subtitle.setFont(QFont("Segoe UI", 10))
        subtitle.setStyleSheet("color: #64748B;")
        title_box.addWidget(title)
        title_box.addWidget(subtitle)
        header.addLayout(title_box)
        header.addStretch()

        self.refresh_label = QLabel("● LIVE")
        self.refresh_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self.refresh_label.setStyleSheet(
            "color:#16A34A; background:#DCFCE7; padding:9px 14px; border-radius:12px;"
        )
        header.addWidget(self.refresh_label)
        root.addLayout(header)

        cards = QHBoxLayout()
        cards.setSpacing(12)

        self.total_value, total_card = self.make_stat_card(
            "TOTAL STUDENTS", "0", "#0284C7", "#E0F2FE"
        )
        self.present_value, present_card = self.make_stat_card(
            "PRESENT", "0", "#16A34A", "#DCFCE7"
        )
        self.absent_value, absent_card = self.make_stat_card(
            "ABSENT", "0", "#DC2626", "#FEE2E2"
        )

        cards.addWidget(total_card)
        cards.addWidget(present_card)
        cards.addWidget(absent_card)
        root.addLayout(cards)

        self.table = QTableWidget(0, 4, self)
        self.table.setHorizontalHeaderLabels(
            ["Student ID", "Student Name", "Time Marked", "Status"]
        )

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Interactive)
        self.table.setColumnWidth(0, 150)
        self.table.setColumnWidth(3, 120)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSortingEnabled(True)

        self.table.setStyleSheet("""
            QTableWidget {
                background: white;
                color: #0F172A;
                border: 1px solid #E2E8F0;
                border-radius: 14px;
                gridline-color: #E2E8F0;
                font-size: 13px;
                selection-background-color: #E0F2FE;
            }
            QHeaderView::section {
                background: #0369A1;
                color: white;
                border: none;
                padding: 13px;
                font-size: 13px;
                font-weight: 700;
            }
            QTableWidget::item { padding: 10px; }
        """)

        root.addWidget(self.table, 1)
        self.setStyleSheet("""
            AttendanceDisplayTest {
                background-color: #F8FAFC;
            }
            QWidget {
                font-family: 'Segoe UI', sans-serif;
            }
        """)

    def make_stat_card(self, label, value, accent, background):
        card = QWidget()
        card.setMinimumHeight(105)
        card.setStyleSheet(
            f"QWidget {{ background:{background}; border-radius:16px; "
            f"border:1px solid {accent}33; }}"
        )

        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 14, 18, 14)

        lbl = QLabel(label)
        lbl.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        lbl.setStyleSheet(f"color:{accent}; border:none;")

        val = QLabel(value)
        val.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        val.setStyleSheet(f"color:{accent}; border:none;")

        layout.addWidget(lbl)
        layout.addWidget(val)
        return val, card

    def go_back(self):
        self.close()
        prev = getattr(self, "previous_window", None) or self.parent()
        if prev is not None:
            prev.show()
            prev.raise_()
            prev.activateWindow()

    def load_attendance(self):
        """Load attendance records directly from the existing Supabase table."""
        try:
            response = (
                supabase
                .table("attendance")
                .select("*")
                .eq("class_number", self.class_number)
                .eq("section", self.section)
                .execute()
            )

            records = response.data or []

            display_records = []
            for record in records:
                status = str(record.get("status", "")).strip().upper()
                if status not in ("PRESENT", "ABSENT"):
                    continue

                student_id = str(record.get("student_id", "")).strip()
                name = str(record.get("name", "")).strip()

                time_marked = str(
                    record.get(
                        "attendance_time",
                        record.get(
                            "time",
                            record.get("created_at", record.get("attendance_date", "")),
                        ),
                    )
                ).strip()

                attendance_date = str(
                    record.get("attendance_date", "")
                ).strip()

                display_records.append(
                    {
                        "student_id": student_id,
                        "name": name,
                        "time_marked": time_marked,
                        "status": status,
                        "attendance_date": attendance_date,
                    }
                )

            display_records.sort(
                key=lambda r: (
                    r.get("attendance_date", ""),
                    r.get("time_marked", ""),
                ),
                reverse=True,
            )

            sorting = self.table.isSortingEnabled()
            self.table.setSortingEnabled(False)
            self.table.setRowCount(len(display_records))

            for row, record in enumerate(display_records):
                values = (
                    record["student_id"],
                    record["name"],
                    record["time_marked"],
                    record["status"],
                )

                for column, value in enumerate(values):
                    item = QTableWidgetItem(value)
                    item.setFont(QFont("Segoe UI", 10))
                    self.table.setItem(row, column, item)

                status_item = self.table.item(row, 3)
                if status_item:
                    if record["status"] == "PRESENT":
                        status_item.setForeground(QColor("#16A34A"))
                    else:
                        status_item.setForeground(QColor("#DC2626"))
                    status_item.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))

            self.table.setSortingEnabled(sorting)

            present_count = sum(
                1 for r in display_records if r["status"] == "PRESENT"
            )
            absent_count = sum(
                1 for r in display_records if r["status"] == "ABSENT"
            )
            total_count = present_count + absent_count

            self.total_value.setText(str(total_count))
            self.present_value.setText(str(present_count))
            self.absent_value.setText(str(absent_count))

        except Exception as error:
            if not hasattr(self, "_last_error") or self._last_error != str(error):
                self._last_error = str(error)
                QMessageBox.critical(
                    self,
                    "Attendance Display Error",
                    f"Could not load attendance data:\n\n{error}",
                )
            print("ATTENDANCE DISPLAY ERROR:", error)

    def closeEvent(self, event):
        if hasattr(self, "refresh_timer"):
            self.refresh_timer.stop()
        prev = getattr(self, "previous_window", None) or self.parent()
        if prev is not None:
            prev.show()
            prev.raise_()
            prev.activateWindow()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AttendanceDisplayTest("Class 10 B")
    window.show()
    sys.exit(app.exec())
