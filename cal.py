import sys
import calendar
import subprocess
from datetime import datetime

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
    QGridLayout, QLabel, QPushButton, QFrame
)


class CalendarCell(QLabel):
    """Custom Label Widget to mimic themed calendar grid cells."""
    def __init__(self, text="", bg_color="#172945", text_color="#FFFFFF", border_color="#243B5C", font_size=14):
        super().__init__(text)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet(f"""
            QLabel {{
                background-color: {bg_color};
                color: {text_color};
                border: 1px solid {border_color};
                border-radius: 4px;
                font-weight: bold;
                font-size: {font_size}px;
            }}
        """)


class CalendarWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.year = datetime.now().year
        self.month = datetime.now().month
        
        self.setWindowTitle("Calendar")
        self.resize(700, 500)
        self.setStyleSheet("""
            QWidget {
                background-color: #0A121C;
            }
        """)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(0)

        self.card_frame = QFrame()
        self.card_frame.setStyleSheet("""
            QFrame {
                background-color: #0A121C;
                border: 2px solid #243B5C;
                border-radius: 18px;
            }
        """)
        
        # Reduced padding and layout spacing inside card_frame
        self.card_layout = QVBoxLayout(self.card_frame)
        self.card_layout.setContentsMargins(10, 10, 10, 10)
        self.card_layout.setSpacing(2)  # Tightened gap between header and grid

        self.main_layout.addWidget(self.card_frame)
        
        self.show_calendar()

    def go_to_test(self):
        subprocess.Popen([sys.executable, 'test.py'])
        QApplication.quit()

    def show_calendar(self):
        while self.card_layout.count():
            child = self.card_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # -------------------------
        # TITLE BAR
        # -------------------------
        title_container = QWidget()
        title_layout = QHBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 0)

        title_text = f"{calendar.month_name[self.month]} {self.year}"
        title_label = QLabel(title_text)
        title_label.setFixedHeight(50)  # Slightly compact height
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                background-color: #40050D;
                color: #FFE6E6;
                border: 1px solid #660D1A;
                border-radius: 14px;
                font-size: 22px;
                font-weight: bold;
            }
        """)

        back_button = QPushButton("<--", title_label)
        back_button.setGeometry(10, 8, 70, 34)
        back_button.setCursor(Qt.CursorShape.PointingHandCursor)
        back_button.setStyleSheet("""
            QPushButton {
                background-color: #40050D;
                color: #FFCDCD;
                border: none;
                font-size: 15px;
                font-weight: bold;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #660D1A;
            }
        """)
        back_button.clicked.connect(self.go_to_test)

        title_layout.addWidget(title_label)
        self.card_layout.addWidget(title_container)

        # -------------------------
        # CALENDAR GRID
        # -------------------------
        grid_layout = QGridLayout()
        grid_layout.setSpacing(2)

        weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        for col, day in enumerate(weekdays):
            header_cell = CalendarCell(
                text=day,
                bg_color="#0F1F33",
                text_color="#99C0E6",
                border_color="#243B5C",
                font_size=13
            )
            grid_layout.addWidget(header_cell, 0, col)

        month_matrix = calendar.monthcalendar(self.year, self.month)
        while len(month_matrix) < 6:
            month_matrix.append([0] * 7)

        today = datetime.now()
        current_year, current_month, current_day = today.year, today.month, today.day

        for row_idx, week in enumerate(month_matrix, start=1):
            for col_idx, day in enumerate(week):
                if day == 0:
                    cell = CalendarCell(
                        text="",
                        bg_color="#050A14",
                        text_color="#334D66",
                        border_color="#0F1A29"
                    )
                elif self.year == current_year and self.month == current_month and day == current_day:
                    cell = CalendarCell(
                        text=str(day),
                        bg_color="#032E0F",
                        text_color="#CCFFCC",
                        border_color="#054D1A",
                        font_size=18
                    )
                elif col_idx >= 5:
                    cell = CalendarCell(
                        text=str(day),
                        bg_color="#380308",
                        text_color="#FFD9D9",
                        border_color="#59080F",
                        font_size=18
                    )
                else:
                    cell = CalendarCell(
                        text=str(day),
                        bg_color="#172945",
                        text_color="#F2F7FF",
                        border_color="#243B5C",
                        font_size=18
                    )

                grid_layout.addWidget(cell, row_idx, col_idx)

        self.card_layout.addLayout(grid_layout)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CalendarWidget()
    window.show()
    sys.exit(app.exec())
