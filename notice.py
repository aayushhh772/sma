import sys
import os
import json
import datetime
import subprocess
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox
)
from PyQt6.QtCore import Qt, QDateTime
from PyQt6.QtGui import QFont
from network_sync import fetch_network_data

DATA_FILE = "data.json"
RECOGNITION_COOLDOWN_SECONDS = 15

class NoticeHistoryWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("SOS School - Notice Archives & Cloud Audit Log")
        self.resize(900, 550)
        self.setStyleSheet("background-color: #eaf5fc;")

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 25, 25, 25)
        main_layout.setSpacing(15)

        # Title Header with Back Button
        header_layout = QHBoxLayout()

        btn_back = QPushButton("⬅ Back to Admin Panel")
        btn_back.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_back.setFixedHeight(34)
        btn_back.setStyleSheet("""
            QPushButton {
                background-color: #e1f0fa;
                color: #0066b2;
                border-radius: 6px;
                font-weight: bold;
                padding: 0 12px;
                border: 1px solid #b2d4ee;
            }
            QPushButton:hover {
                background-color: #cbe3f5;
            }
        """)
        btn_back.clicked.connect(self.return_to_admin)

        title_lbl = QLabel("📚 Managed Notice Archive (Cloud Synced)")
        title_lbl.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title_lbl.setStyleSheet("color: #004080; background: transparent;")

        self.refresh_btn = QPushButton("🔄 Refresh Archives")
        self.refresh_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.refresh_btn.setFixedHeight(34)
        self.refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #0077c8;
                color: #ffffff;
                border-radius: 6px;
                font-weight: bold;
                padding: 0 15px;
                border: none;
            }
            QPushButton:hover {
                background-color: #005fa3;
            }
        """)
        self.refresh_btn.clicked.connect(self.load_archive_data)

        header_layout.addWidget(btn_back)
        header_layout.addSpacing(15)
        header_layout.addWidget(title_lbl)
        header_layout.addStretch()
        header_layout.addWidget(self.refresh_btn)
        main_layout.addLayout(header_layout)

        # Card container for data view
        card_frame = QFrame()
        card_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.95);
                border-radius: 12px;
                border: 1px solid #cbe3f5;
                padding: 15px;
            }
        """)
        card_layout = QVBoxLayout(card_frame)
        card_layout.setContentsMargins(10, 10, 10, 10)

        # Data Table displaying well-managed historical notices payload fields
        self.table_archive = QTableWidget(0, 5)
        self.table_archive.setHorizontalHeaderLabels(
            ["Target Group", "Notice Title", "Content Body", "PDF Attachment", "Timestamp"])
        self.table_archive.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_archive.setStyleSheet("""
            QTableWidget {
                background-color: #ffffff;
                color: #1a2a3a;
                border-radius: 8px;
                border: 1px solid #b2d4ee;
                gridline-color: #e1f0fa;
            }
            QHeaderView::section {
                background-color: #0077c8;
                color: #ffffff;
                border: none;
                padding: 8px;
                font-weight: bold;
            }
        """)
        card_layout.addWidget(self.table_archive)
        main_layout.addWidget(card_frame)

        self.load_archive_data()

    def return_to_admin(self):
        """Closes notice window and re-opens admin_panel.py."""
        admin_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "admin_panel.py")
        if os.path.exists(admin_path):
            subprocess.Popen([sys.executable, admin_path], cwd=os.path.dirname(admin_path))
            self.close()
        else:
            QMessageBox.warning(self, "File Missing", "Could not find admin_panel.py in the current directory.")

    def load_archive_data(self):
        """Fetches all notice records, including full archives, from network or local JSON fallback."""
        try:
            # Pass ignore_expiration=True if supported by fetch_network_data,
            # or read directly from data.json without running is_recent()
            data = fetch_network_data(DATA_FILE)
            if not data and os.path.exists(DATA_FILE):
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)

            # Do NOT filter by is_recent() here — load every notice
            notices = data.get("notices", []) if isinstance(data, dict) else []

            self.table_archive.setRowCount(len(notices))
            for row, n in enumerate(notices):
                target_str = f"{n.get('target', 'All')} ({n.get('section', '')})"
                title = n.get("title", "")
                content = n.get("content", "No body text")
                pdf_val = os.path.basename(n.get("pdf")) if n.get("pdf") else "None"

                ts_str = n.get("timestamp", "")
                try:
                    dt_obj = datetime.datetime.fromisoformat(ts_str)
                    time_display = dt_obj.strftime("%b %d, %Y - %I:%M %p")
                except Exception:
                    time_display = ts_str or "N/A"

                self.table_archive.setItem(row, 0, QTableWidgetItem(target_str))
                self.table_archive.setItem(row, 1, QTableWidgetItem(title))
                self.table_archive.setItem(row, 2, QTableWidgetItem(content))
                self.table_archive.setItem(row, 3, QTableWidgetItem(pdf_val))
                self.table_archive.setItem(row, 4, QTableWidgetItem(time_display))
        except Exception as e:
            QMessageBox.warning(self, "Sync Error", f"Could not parse cloud payload data securely:\n{e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = NoticeHistoryWindow()
    window.show()
    sys.exit(app.exec())
