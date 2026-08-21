import sys
import os
import json
import math
import random
import datetime
import subprocess

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QPushButton, QLineEdit, QTextEdit, QComboBox,
    QFileDialog, QMessageBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QStackedWidget, QInputDialog
)
from PyQt6.QtCore import Qt, QTimer, QPointF, QDateTime
from PyQt6.QtGui import QFont, QPixmap, QPainter, QPainterPath, QColor, QPen, QBrush

from network_sync import push_cloud_data, fetch_network_data

DATA_FILE = "data.json"
CREDENTIALS_FILE = "admin_credentials.json"
LOGO_FILENAME = "logo.png"
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


def load_credentials():
    if os.path.exists(CREDENTIALS_FILE):
        try:
            with open(CREDENTIALS_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {"admin_id": "SOSADMIN1", "password": "ADMIN404"}


def save_credentials(admin_id, password):
    with open(CREDENTIALS_FILE, "w") as f:
        json.dump({"admin_id": admin_id, "password": password}, f, indent=4)


class Bubble:
    def __init__(self, width, height):
        self.reset(width, height, first_time=True)

    def reset(self, width, height, first_time=False):
        self.x = random.uniform(0, width if width > 0 else 1000)
        self.y = random.uniform(0, height) if first_time else height + random.uniform(10, 50)
        self.radius = random.uniform(12, 35)
        self.speed = random.uniform(0.4, 1.2)
        self.opacity = random.randint(25, 75)
        self.wobble_speed = random.uniform(0.02, 0.05)
        self.wobble = random.uniform(0, 6.28)

    def update(self, width, height):
        self.y -= self.speed
        self.wobble += self.wobble_speed
        self.x += math.sin(self.wobble) * 0.5
        if self.y < -self.radius * 2:
            self.reset(width, height)


class AnimatedBackgroundWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.wave_phase = 0.0
        self.bubbles = []
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate)
        self.timer.start(16)

    def init_bubbles(self):
        w = max(self.width(), 800)
        h = max(self.height(), 600)
        self.bubbles = [Bubble(w, h) for _ in range(25)]

    def resizeEvent(self, event):
        if not self.bubbles:
            self.init_bubbles()
        super().resizeEvent(event)

    def animate(self):
        self.wave_phase += 0.02
        w, h = self.width(), self.height()
        for b in self.bubbles:
            b.update(w, h)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        w = self.width()
        h = self.height()
        painter.fillRect(0, 0, w, h, QColor("#eaf5fc"))
        self.draw_wave(painter, w, h, offset_y=h * 0.45, amplitude=25, frequency=0.008, color=QColor(0, 150, 220, 25), phase_shift=self.wave_phase)
        self.draw_wave(painter, w, h, offset_y=h * 0.55, amplitude=35, frequency=0.005, color=QColor(0, 110, 200, 20), phase_shift=self.wave_phase * 0.7)
        self.draw_wave(painter, w, h, offset_y=h * 0.65, amplitude=20, frequency=0.01, color=QColor(0, 160, 230, 30), phase_shift=self.wave_phase * 1.3)
        for b in self.bubbles:
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(QColor(255, 255, 255, b.opacity)))
            painter.drawEllipse(QPointF(b.x, b.y), b.radius, b.radius)
            painter.setBrush(QBrush(QColor(0, 150, 220, int(b.opacity * 0.4))))
            painter.drawEllipse(QPointF(b.x - b.radius * 0.3, b.y - b.radius * 0.3), b.radius * 0.35, b.radius * 0.35)

    def draw_wave(self, painter, width, height, offset_y, amplitude, frequency, color, phase_shift):
        path = QPainterPath()
        path.moveTo(0, height)
        path.lineTo(0, offset_y)
        x = 0
        while x <= width:
            y = offset_y + math.sin(x * frequency + phase_shift) * amplitude
            path.lineTo(x, y)
            x += 10
        path.lineTo(width, height)
        path.closeSubpath()
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(color))
        painter.drawPath(path)


class AdminPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.selected_pdf_path = None
        self.init_ui()

    def read_data(self):
        try:
            net_data = fetch_network_data(DATA_FILE)
            if net_data:
                return net_data
        except Exception:
            pass
        if not os.path.exists(DATA_FILE):
            return {}
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return {}

    def save_data(self, data):
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=4)
        try:
            push_cloud_data(data)
        except Exception as e:
            print(f"Cloud sync error: {e}")

    def init_ui(self):
        self.setWindowTitle("SOS Hermann Gmeiner School Gandaki - Admin Panel")
        self.resize(1100, 700)
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        self.bg_widget = AnimatedBackgroundWidget(self)
        root_layout.addWidget(self.bg_widget)
        main_layout = QHBoxLayout(self.bg_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Sidebar
        sidebar = QFrame()
        sidebar.setFixedWidth(260)
        sidebar.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.92);
                border-right: 1px solid #cbe3f5;
            }
        """)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(20, 25, 20, 25)
        sidebar_layout.setSpacing(12)

        # Logo & Title
        logo_lbl = QLabel()
        logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), LOGO_FILENAME)
        if not os.path.exists(logo_path):
            logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "486624203_601802256148254_3403736131493055483_n.png")
        if os.path.exists(logo_path):
            pix = QPixmap(logo_path).scaled(70, 70, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            logo_lbl.setPixmap(pix)
            logo_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            logo_lbl.setStyleSheet("border: none; background: transparent;")
            sidebar_layout.addWidget(logo_lbl)

        school_lbl = QLabel("SOS Hermann Gmeiner\nSchool Gandaki")
        school_lbl.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        school_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        school_lbl.setStyleSheet("color: #0066b2; border: none; background: transparent; margin-bottom: 10px;")
        sidebar_layout.addWidget(school_lbl)

        # Sidebar Navigation Buttons
        btn_notices = QPushButton("📢 Notices & PDFs")
        btn_subs = QPushButton("🔄 Substitutions")
        btn_settings = QPushButton("⚙️ Settings")
        self.nav_btns = [btn_notices, btn_subs, btn_settings]
        for idx, btn in enumerate(self.nav_btns):
            btn.setFixedHeight(42)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda _, i=idx: self.switch_page(i))
            sidebar_layout.addWidget(btn)

        sidebar_layout.addStretch()
        main_layout.addWidget(sidebar)

        # Content Area Layout
        content_area = QWidget()
        content_layout = QVBoxLayout(content_area)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # Header Bar
        header_bar = QFrame()
        header_bar.setFixedHeight(50)
        header_bar.setStyleSheet("background: transparent; border-bottom: 1px solid #cbe3f5;")
        header_layout = QHBoxLayout(header_bar)
        header_layout.setContentsMargins(25, 0, 25, 0)
        portal_title = QLabel("Administrative Control Center")
        portal_title.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        portal_title.setStyleSheet("color: #0066b2; border: none; background: transparent;")
        self.time_label = QLabel()
        self.time_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        self.time_label.setStyleSheet("color: #004080; border: none; background: transparent;")
        header_layout.addWidget(portal_title)
        header_layout.addStretch()
        header_layout.addWidget(self.time_label)
        content_layout.addWidget(header_bar)

        # Pages Container
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setStyleSheet("background: transparent;")

        self.notice_page = QWidget()
        self.setup_notice_page()
        self.stacked_widget.addWidget(self.notice_page)

        self.sub_page = QWidget()
        self.setup_sub_page()
        self.stacked_widget.addWidget(self.sub_page)

        self.settings_page = QWidget()
        self.setup_settings_page()
        self.stacked_widget.addWidget(self.settings_page)

        content_layout.addWidget(self.stacked_widget)
        main_layout.addWidget(content_area)

        # Live Clock
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_live_time)
        self.timer.start(1000)
        self.update_live_time()
        self.switch_page(0)

    def update_live_time(self):
        current_str = QDateTime.currentDateTime().toString("ddd MMM d, h:mm A")
        self.time_label.setText(f"🕒 {current_str}")

    def switch_page(self, index):
        self.stacked_widget.setCurrentIndex(index)
        active_style = """
            QPushButton {
                background-color: #0077c8;
                color: #ffffff;
                border-radius: 8px;
                text-align: left;
                padding-left: 15px;
                font-weight: bold;
                border: none;
                font-size: 13px;
            }
        """
        inactive_style = """
            QPushButton {
                background-color: transparent;
                color: #2c3e50;
                border-radius: 8px;
                text-align: left;
                padding-left: 15px;
                font-weight: bold;
                border: none;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #e1f0fa;
                color: #0066b2;
            }
        """
        for i, btn in enumerate(self.nav_btns):
            btn.setStyleSheet(active_style if i == index else inactive_style)

    def setup_notice_page(self):
        layout = QVBoxLayout(self.notice_page)
        layout.setContentsMargins(35, 25, 35, 25)
        layout.setSpacing(15)

        head_lbl = QLabel("Publish Notice & Attach PDF")
        head_lbl.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        head_lbl.setStyleSheet("color: #004080; background: transparent;")
        layout.addWidget(head_lbl)

        form_card = QFrame()
        form_card.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.95);
                border-radius: 12px;
                border: 1px solid #cbe3f5;
                padding: 15px;
            }
        """)
        form_layout = QVBoxLayout(form_card)

        target_layout = QHBoxLayout()
        target_lbl = QLabel("Target Group:")
        target_lbl.setStyleSheet("color: #2c3e50; font-weight: bold; border: none; background: transparent;")
        
        self.combo_target = QComboBox()
        self.combo_target.addItems([
            "Class 6-12", "Class 6-10", "Class 11-12", 
            "Class 6", "Class 7", "Class 8", "Class 9", "Class 10", "Class 11", "Class 12",
            "✏️ Custom Selection / Range..."
        ])

        section_lbl = QLabel("Section:")
        section_lbl.setStyleSheet("color: #2c3e50; font-weight: bold; border: none; background: transparent;")
        self.combo_section = QComboBox()

        combo_style = """
            QComboBox {
                background-color: #ffffff;
                color: #1a2a3a;
                padding: 6px 10px;
                border-radius: 6px;
                border: 1px solid #b2d4ee;
            }
            QComboBox:focus { border: 1px solid #0077c8; }
            QComboBox QAbstractItemView {
                background-color: #ffffff;
                color: #1a2a3a;
                selection-background-color: #0077c8;
                selection-color: #ffffff;
                border: 1px solid #b2d4ee;
                outline: none;
            }
        """
        self.combo_target.setStyleSheet(combo_style)
        self.combo_section.setStyleSheet(combo_style)
        self.combo_target.currentTextChanged.connect(self.handle_target_change)
        self.update_section_options(self.combo_target.currentText())

        target_layout.addWidget(target_lbl)
        target_layout.addWidget(self.combo_target)
        target_layout.addSpacing(20)
        target_layout.addWidget(section_lbl)
        target_layout.addWidget(self.combo_section)
        target_layout.addStretch()
        form_layout.addLayout(target_layout)

        input_style = """
            QLineEdit, QTextEdit {
                background-color: #ffffff;
                color: #1a2a3a;
                padding: 8px;
                border-radius: 6px;
                border: 1px solid #b2d4ee;
            }
            QLineEdit:focus, QTextEdit:focus {
                border: 1px solid #0077c8;
                background-color: #ffffff;
            }
        """
        self.input_notice_title = QLineEdit()
        self.input_notice_title.setPlaceholderText("Notice Title")
        self.input_notice_title.setStyleSheet(input_style)
        form_layout.addWidget(self.input_notice_title)

        self.input_notice_body = QTextEdit()
        self.input_notice_body.setPlaceholderText("Write the notice content here...")
        self.input_notice_body.setStyleSheet(input_style)
        self.input_notice_body.setFixedHeight(90)
        form_layout.addWidget(self.input_notice_body)

        pdf_layout = QHBoxLayout()
        btn_upload = QPushButton("📄 Select PDF Document")
        btn_upload.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_upload.setStyleSheet("""
            QPushButton {
                background-color: #e1f0fa;
                color: #0066b2;
                padding: 6px 14px;
                border-radius: 6px;
                border: 1px solid #b2d4ee;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0077c8;
                color: #ffffff;
            }
        """)
        btn_upload.clicked.connect(self.upload_pdf)
        self.file_label = QLabel("No PDF selected")
        self.file_label.setStyleSheet("color: #7f8c8d; font-style: italic; border: none; background: transparent;")
        pdf_layout.addWidget(btn_upload)
        pdf_layout.addWidget(self.file_label)
        pdf_layout.addStretch()
        form_layout.addLayout(pdf_layout)

        action_layout = QHBoxLayout()
        btn_post = QPushButton("📢 Publish Notice")
        btn_post.setFixedHeight(38)
        btn_post.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_post.setStyleSheet("""
            QPushButton {
                background-color: #0077c8;
                color: #ffffff;
                border-radius: 6px;
                font-weight: bold;
                border: none;
                font-size: 13px;
            }
            QPushButton:hover { background-color: #005fa3; }
        """)
        btn_post.clicked.connect(self.post_notice)

        btn_history = QPushButton("ⓘ Notice History")
        btn_history.setFixedHeight(38)
        btn_history.setFixedWidth(140)
        btn_history.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_history.setStyleSheet("""
            QPushButton {
                background-color: #e1f0fa;
                color: #0066b2;
                border-radius: 6px;
                font-weight: bold;
                border: 1px solid #b2d4ee;
                font-size: 13px;
            }
            QPushButton:hover { background-color: #cbe3f5; }
        """)
        btn_history.clicked.connect(self.open_notice_history)

        action_layout.addWidget(btn_post, 4)
        action_layout.addWidget(btn_history, 1)
        form_layout.addLayout(action_layout)
        layout.addWidget(form_card)

        list_lbl = QLabel("Active Notices (Auto-expires after 12h)")
        list_lbl.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        list_lbl.setStyleSheet("color: #004080; background: transparent; margin-top: 5px;")
        layout.addWidget(list_lbl)

        self.table_notices = QTableWidget(0, 5)
        self.table_notices.setHorizontalHeaderLabels(["Target", "Title", "PDF Attachment", "Date / Time", "Action"])
        self.table_notices.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_notices.setStyleSheet("""
            QTableWidget {
                background-color: rgba(255, 255, 255, 0.95);
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
            }
        """)
        layout.addWidget(self.table_notices)
        self.load_notices()

    def handle_target_change(self, target_text):
        if target_text == "✏️ Custom Selection / Range...":
            custom_text, ok = QInputDialog.getText(
                self, 
                "Custom Class Target", 
                "Enter target class or range (e.g. 'Class 6, 8, 10' or 'Class 7-9'):"
            )
            if ok and custom_text.strip():
                formatted_custom = custom_text.strip()
                if not formatted_custom.lower().startswith("class"):
                    formatted_custom = f"Class {formatted_custom}"
                
                # Check if it already exists in the dropdown
                idx = self.combo_target.findText(formatted_custom)
                if idx == -1:
                    # Insert right above the custom trigger option
                    insert_index = self.combo_target.count() - 1
                    self.combo_target.insertItem(insert_index, formatted_custom)
                    self.combo_target.setCurrentIndex(insert_index)
                else:
                    self.combo_target.setCurrentIndex(idx)
            else:
                self.combo_target.setCurrentIndex(0)
        else:
            self.update_section_options(target_text)

    def update_section_options(self, target_text):
        self.combo_section.clear()
        if target_text in ["Class 11-12", "Class 11", "Class 12"]:
            sections = ["All Sections", "Section A", "Section B", "Section C", "Section D"]
        elif target_text in ["Class 6-10", "Class 6", "Class 7", "Class 8", "Class 9", "Class 10"]:
            sections = ["All Sections", "Section A", "Section B"]
        else:
            sections = ["All Sections", "Section A", "Section B", "Section C", "Section D"]
        self.combo_section.addItems(sections)

    def upload_pdf(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Select PDF Document", "", "PDF Files (*.pdf)")
        if file_name:
            abs_path = os.path.abspath(file_name)
            short_name = os.path.basename(abs_path)
            self.file_label.setText(f"PDF: {short_name}")
            self.selected_pdf_path = abs_path

    def post_notice(self):
        title = self.input_notice_title.text().strip()
        body = self.input_notice_body.toPlainText().strip()
        target = self.combo_target.currentText()
        section = self.combo_section.currentText()

        if target == "✏️ Custom Selection / Range...":
            QMessageBox.warning(self, "Warning", "Please specify a valid class target.")
            return

        if not title:
            QMessageBox.warning(self, "Warning", "Please enter a notice title.")
            return

        notice_obj = {
            "title": title,
            "content": body,
            "target": target,
            "section": section,
            "pdf": self.selected_pdf_path,
            "timestamp": datetime.datetime.now().isoformat()
        }

        data = self.read_data()
        if "notices" not in data:
            data["notices"] = []
        data["notices"].append(notice_obj)
        self.save_data(data)

        self.input_notice_title.clear()
        self.input_notice_body.clear()
        self.file_label.setText("No PDF selected")
        self.selected_pdf_path = None
        QMessageBox.information(self, "Success", "Notice published successfully!")
        self.load_notices()

    def open_notice_history(self):
        history_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "notice.py")
        if os.path.exists(history_path):
            subprocess.Popen([sys.executable, history_path], cwd=os.path.dirname(history_path))
            self.close()
        else:
            QMessageBox.warning(self, "File Missing", "Could not find notice.py in the current directory.")

    def load_notices(self):
        data = self.read_data()
        notices = [n for n in data.get("notices", []) if is_recent(n.get("timestamp"))]
        data["notices"] = notices
        self.save_data(data)

        self.table_notices.setRowCount(len(notices))
        for row, n in enumerate(notices):
            target_str = f"{n.get('target', '')} ({n.get('section', '')})"
            pdf_str = os.path.basename(n.get("pdf")) if n.get("pdf") else "None"
            dt_obj = parse_iso_timestamp(n.get("timestamp"))
            time_display = dt_obj.strftime("%b %d, %I:%M %p") if dt_obj else "Recently"

            self.table_notices.setItem(row, 0, QTableWidgetItem(target_str))
            self.table_notices.setItem(row, 1, QTableWidgetItem(n.get("title", "")))
            self.table_notices.setItem(row, 2, QTableWidgetItem(pdf_str))
            self.table_notices.setItem(row, 3, QTableWidgetItem(time_display))

            btn_del = QPushButton("Delete")
            btn_del.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_del.setStyleSheet("background-color: #e74c3c; color: white; border: none; border-radius: 4px; padding: 4px 10px; font-weight: bold;")
            btn_del.clicked.connect(lambda _, r=row: self.delete_notice(r))
            self.table_notices.setCellWidget(row, 4, btn_del)

    def delete_notice(self, row_idx):
        data = self.read_data()
        if "notices" in data and row_idx < len(data["notices"]):
            data["notices"].pop(row_idx)
            self.save_data(data)
            self.load_notices()

    def setup_sub_page(self):
        layout = QVBoxLayout(self.sub_page)
        layout.setContentsMargins(35, 25, 35, 25)
        layout.setSpacing(15)

        head_lbl = QLabel("Manage Daily Substitutions")
        head_lbl.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        head_lbl.setStyleSheet("color: #004080; background: transparent;")
        layout.addWidget(head_lbl)

        form_card = QFrame()
        form_card.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.95);
                border-radius: 12px;
                border: 1px solid #cbe3f5;
                padding: 15px;
            }
        """)
        form_layout = QHBoxLayout(form_card)

        input_style = """
            QLineEdit {
                background-color: #ffffff;
                color: #1a2a3a;
                padding: 8px;
                border-radius: 6px;
                border: 1px solid #b2d4ee;
            }
            QLineEdit:focus {
                border: 1px solid #0077c8;
                background-color: #ffffff;
            }
        """
        self.sub_class = QLineEdit()
        self.sub_class.setPlaceholderText("Class (e.g. 6)")
        self.sub_class.textChanged.connect(self.update_period_placeholder)

        self.sub_sec = QLineEdit()
        self.sub_sec.setPlaceholderText("Sec (e.g. A)")

        self.sub_period = QLineEdit()
        self.sub_period.setPlaceholderText("Period (1-8)")

        self.sub_absent = QLineEdit()
        self.sub_absent.setPlaceholderText("Absent Teacher")

        self.sub_substitute = QLineEdit()
        self.sub_substitute.setPlaceholderText("Substitute Teacher")

        inputs = [self.sub_class, self.sub_sec, self.sub_period, self.sub_absent, self.sub_substitute]
        for inp in inputs:
            inp.setStyleSheet(input_style)
            form_layout.addWidget(inp)

        btn_add_sub = QPushButton("Add")
        btn_add_sub.setFixedHeight(35)
        btn_add_sub.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_add_sub.setStyleSheet("""
            QPushButton {
                background-color: #0077c8;
                color: #ffffff;
                padding: 6px 18px;
                border-radius: 6px;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover { background-color: #005fa3; }
        """)
        btn_add_sub.clicked.connect(self.add_substitution)
        form_layout.addWidget(btn_add_sub)
        layout.addWidget(form_card)

        self.table_subs = QTableWidget(0, 7)
        self.table_subs.setHorizontalHeaderLabels(["Class", "Sec", "Period", "Absent Teacher", "Substitute", "Date / Time", "Action"])
        self.table_subs.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_subs.setStyleSheet("""
            QTableWidget {
                background-color: rgba(255, 255, 255, 0.95);
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
            }
        """)
        layout.addWidget(self.table_subs)
        self.load_substitutions()

    def update_period_placeholder(self, text):
        val = text.strip()
        if val in ["11", "12"]:
            self.sub_period.setPlaceholderText("Period (1-9)")
        else:
            self.sub_period.setPlaceholderText("Period (1-8)")

    def add_substitution(self):
        c = self.sub_class.text().strip()
        s = self.sub_sec.text().strip()
        p = self.sub_period.text().strip()
        abs_t = self.sub_absent.text().strip()
        sub_t = self.sub_substitute.text().strip()

        if not (c and s and p and sub_t):
            QMessageBox.warning(self, "Warning", "Please fill in required substitution fields.")
            return

        sub_obj = {
            "class": c,
            "section": s,
            "period": p,
            "absent": abs_t,
            "substitute": sub_t,
            "timestamp": datetime.datetime.now().isoformat()
        }

        data = self.read_data()
        if "substitutions" not in data:
            data["substitutions"] = []
        data["substitutions"].append(sub_obj)
        self.save_data(data)

        for inp in [self.sub_class, self.sub_sec, self.sub_period, self.sub_absent, self.sub_substitute]:
            inp.clear()
        self.load_substitutions()

    def load_substitutions(self):
        data = self.read_data()
        subs = [s for s in data.get("substitutions", []) if is_recent(s.get("timestamp"))]
        data["substitutions"] = subs
        self.save_data(data)

        self.table_subs.setRowCount(len(subs))
        for row, s in enumerate(subs):
            dt_obj = parse_iso_timestamp(s.get("timestamp"))
            time_display = dt_obj.strftime("%b %d, %I:%M %p") if dt_obj else "Recently"

            self.table_subs.setItem(row, 0, QTableWidgetItem(str(s.get("class", ""))))
            self.table_subs.setItem(row, 1, QTableWidgetItem(str(s.get("section", ""))))
            self.table_subs.setItem(row, 2, QTableWidgetItem(str(s.get("period", ""))))
            self.table_subs.setItem(row, 3, QTableWidgetItem(s.get("absent", "")))
            self.table_subs.setItem(row, 4, QTableWidgetItem(s.get("substitute", "")))
            self.table_subs.setItem(row, 5, QTableWidgetItem(time_display))

            btn_del = QPushButton("Delete")
            btn_del.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_del.setStyleSheet("background-color: #e74c3c; color: white; border: none; border-radius: 4px; padding: 4px 10px; font-weight: bold;")
            btn_del.clicked.connect(lambda _, r=row: self.delete_substitution(r))
            self.table_subs.setCellWidget(row, 6, btn_del)

    def delete_substitution(self, row_idx):
        data = self.read_data()
        if "substitutions" in data and row_idx < len(data["substitutions"]):
            data["substitutions"].pop(row_idx)
            self.save_data(data)
            self.load_substitutions()

    def setup_settings_page(self):
        layout = QVBoxLayout(self.settings_page)
        layout.setContentsMargins(35, 20, 35, 25)
        layout.setSpacing(15)

        head_lbl = QLabel("System Settings & Configuration")
        head_lbl.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        head_lbl.setStyleSheet("color: #004080; background: transparent;")
        layout.addWidget(head_lbl)

        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(20)

        card_style = """
            QFrame {
                background-color: rgba(255, 255, 255, 0.95);
                border-radius: 12px;
                border: 1px solid #cbe3f5;
            }
        """
        input_style = """
            QLineEdit {
                background-color: #ffffff;
                color: #1a2a3a;
                padding: 10px;
                border-radius: 6px;
                border: 1px solid #b2d4ee;
                font-size: 13px;
            }
            QLineEdit:focus { border: 2px solid #0077c8; }
        """

        # Credentials Card
        creds_card = QFrame()
        creds_card.setStyleSheet(card_style)
        creds_layout = QVBoxLayout(creds_card)
        creds_layout.setContentsMargins(22, 20, 22, 20)
        creds_layout.setSpacing(12)

        c_title = QLabel("🔐 Admin Authentication Credentials")
        c_title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        c_title.setStyleSheet("color: #004080; border: none; background: transparent;")
        creds_layout.addWidget(c_title)

        c_sub = QLabel("Update login credentials saved to local configuration.")
        c_sub.setFont(QFont("Segoe UI", 9))
        c_sub.setStyleSheet("color: #64748b; border: none; background: transparent;")
        creds_layout.addWidget(c_sub)

        creds = load_credentials()
        self.input_new_id = QLineEdit()
        self.input_new_id.setPlaceholderText("New Admin ID")
        self.input_new_id.setText(creds.get("admin_id", ""))
        self.input_new_id.setStyleSheet(input_style)
        creds_layout.addWidget(self.input_new_id)

        self.input_new_pass = QLineEdit()
        self.input_new_pass.setPlaceholderText("New Password")
        self.input_new_pass.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_new_pass.setText(creds.get("password", ""))
        self.input_new_pass.setStyleSheet(input_style)
        creds_layout.addWidget(self.input_new_pass)

        btn_save_creds = QPushButton("💾 Update Credentials")
        btn_save_creds.setFixedHeight(40)
        btn_save_creds.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_save_creds.setStyleSheet("""
            QPushButton {
                background-color: #0077c8;
                color: #ffffff;
                border-radius: 6px;
                font-weight: bold;
                border: none;
                font-size: 13px;
            }
            QPushButton:hover { background-color: #005fa3; }
        """)
        btn_save_creds.clicked.connect(self.update_credentials)
        creds_layout.addWidget(btn_save_creds)
        creds_layout.addStretch()
        cards_layout.addWidget(creds_card, 1)

        # Actions Card
        actions_card = QFrame()
        actions_card.setStyleSheet(card_style)
        actions_layout = QVBoxLayout(actions_card)
        actions_layout.setContentsMargins(22, 20, 22, 20)
        actions_layout.setSpacing(12)

        a_title = QLabel("🛠️ System Operations & Maintenance")
        a_title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        a_title.setStyleSheet("color: #004080; border: none; background: transparent;")
        actions_layout.addWidget(a_title)

        a_sub = QLabel("Quick system controls, help user manual, and session exit.")
        a_sub.setFont(QFont("Segoe UI", 9))
        a_sub.setStyleSheet("color: #64748b; border: none; background: transparent;")
        actions_layout.addWidget(a_sub)

        btn_help = QPushButton("📖 Launch User Manual / Help Guide")
        btn_help.setFixedHeight(40)
        btn_help.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_help.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: #ffffff;
                border-radius: 6px;
                font-weight: bold;
                border: none;
                font-size: 13px;
            }
            QPushButton:hover { background-color: #d68910; }
        """)
        btn_help.clicked.connect(self.open_help_page)
        actions_layout.addWidget(btn_help)

        btn_exit = QPushButton("🚪 Logout & Return to Portal")
        btn_exit.setFixedHeight(40)
        btn_exit.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_exit.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: #ffffff;
                border-radius: 6px;
                font-weight: bold;
                border: none;
                font-size: 13px;
            }
            QPushButton:hover { background-color: #c0392b; }
        """)
        btn_exit.clicked.connect(self.exit_to_adminpage)
        actions_layout.addWidget(btn_exit)

        info_box = QFrame()
        info_box.setStyleSheet("background-color: #e1f0fa; border-radius: 8px; border: 1px solid #b2d4ee; padding: 10px;")
        ib_layout = QVBoxLayout(info_box)
        ib_layout.setContentsMargins(10, 8, 10, 8)

        status_lbl = QLabel("🟢 System Status: Active & Synced\n🔑 Developer Master Fallback: Active")
        status_lbl.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        status_lbl.setStyleSheet("color: #004080; border: none; background: transparent;")
        ib_layout.addWidget(status_lbl)

        actions_layout.addWidget(info_box)
        actions_layout.addStretch()
        cards_layout.addWidget(actions_card, 1)

        layout.addLayout(cards_layout)
        layout.addStretch()

    def update_credentials(self):
        new_id = self.input_new_id.text().strip()
        new_pass = self.input_new_pass.text().strip()
        if not new_id or not new_pass:
            QMessageBox.warning(self, "Warning", "Admin ID and Password cannot be empty.")
            return

        save_credentials(new_id, new_pass)
        QMessageBox.information(
            self,
            "Success",
            "Admin credentials updated successfully!\n\nNote: System will read new credentials on next login. Master developer ID/Password remains available as a fallback."
        )

    def open_help_page(self):
        help_page_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "help.py")
        if os.path.exists(help_page_path):
            subprocess.Popen([sys.executable, help_page_path], cwd=os.path.dirname(help_page_path))
        else:
            QMessageBox.warning(self, "Help File Missing", "Could not find help.py in the current directory.")

    def exit_to_adminpage(self):
        admin_page_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "adminpage.py")
        if os.path.exists(admin_page_path):
            subprocess.Popen([sys.executable, admin_page_path, "--exited"], cwd=os.path.dirname(admin_page_path))
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AdminPanel()
    window.show()
    sys.exit(app.exec())
