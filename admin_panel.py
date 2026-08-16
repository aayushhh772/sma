import sys
import os
import subprocess
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QGridLayout, QFileDialog, QFrame, 
    QLineEdit, QComboBox, QListWidget, QTextEdit, QScrollArea
)
from PyQt6.QtCore import Qt, QTimer, QTime, QDate, QPointF
from PyQt6.QtGui import QFont, QPainter, QLinearGradient, QColor, QPainterPath


class WaveBackgroundWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0.0, QColor("#E0F2FE"))
        gradient.setColorAt(0.35, QColor("#F0F9FF"))
        gradient.setColorAt(0.70, QColor("#F8FAFC"))
        gradient.setColorAt(1.0, QColor("#E0F2FE"))
        painter.fillRect(self.rect(), gradient)

        wave_path1 = QPainterPath()
        wave_path1.moveTo(0, 0)
        wave_path1.lineTo(0, 140)
        wave_path1.cubicTo(
            QPointF(self.width() * 0.3, 200),
            QPointF(self.width() * 0.7, 80),
            QPointF(self.width(), 160)
        )
        wave_path1.lineTo(self.width(), 0)
        wave_path1.closeSubpath()

        wave_grad1 = QLinearGradient(0, 0, self.width(), 200)
        wave_grad1.setColorAt(0.0, QColor(2, 132, 199, 40))
        wave_grad1.setColorAt(1.0, QColor(56, 189, 248, 20))
        painter.fillPath(wave_path1, wave_grad1)

        wave_path2 = QPainterPath()
        wave_path2.moveTo(0, self.height())
        wave_path2.lineTo(0, self.height() - 110)
        wave_path2.cubicTo(
            QPointF(self.width() * 0.35, self.height() - 160),
            QPointF(self.width() * 0.65, self.height() - 40),
            QPointF(self.width(), self.height() - 110)
        )
        wave_path2.lineTo(self.width(), self.height())
        wave_path2.closeSubpath()

        wave_grad2 = QLinearGradient(0, self.height() - 160, self.width(), self.height())
        wave_grad2.setColorAt(0.0, QColor(2, 132, 199, 25))
        wave_grad2.setColorAt(1.0, QColor(186, 230, 253, 60))
        painter.fillPath(wave_path2, wave_grad2)

        painter.end()


class AdminPanel(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SOS HGS Gandaki - Admin Panel")
        self.setMinimumSize(1000, 680)
        self.resize(1200, 800)

        # State Variables
        self.selected_pdf_path = None

        self.init_ui()

    def init_ui(self):
        central_widget = WaveBackgroundWidget()
        self.setCentralWidget(central_widget)

        root_layout = QHBoxLayout(central_widget)
        root_layout.setContentsMargins(12, 12, 12, 12)
        root_layout.setSpacing(12)

        # ---------------- SIDEBAR ----------------
        sidebar = QFrame()
        sidebar.setFixedWidth(110)
        sidebar.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.90);
                border: 1px solid #BAE6FD;
                border-radius: 12px;
            }
        """)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(10, 16, 10, 16)
        sidebar_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

        dash_btn = QPushButton("DASHBOARD")
        dash_btn.setFixedSize(85, 75)
        dash_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        dash_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0284C7, stop:1 #0369A1);
                color: #FFFFFF;
                font-size: 10px;
                font-weight: bold;
                border-radius: 10px;
                border: none;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0369A1, stop:1 #0284C7);
            }
        """)
        sidebar_layout.addWidget(dash_btn)

        sidebar_layout.addStretch()

        support_btn = QPushButton("SUPPORT\n& HELP")
        support_btn.setFixedSize(85, 60)
        support_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        support_btn.setStyleSheet("""
            QPushButton {
                background-color: #E0F2FE;
                color: #0284C7;
                font-size: 10px;
                font-weight: bold;
                border-radius: 10px;
                border: 1px solid #BAE6FD;
            }
            QPushButton:hover {
                background-color: #BAE6FD;
                color: #0369A1;
            }
            QPushButton:pressed {
                background-color: #7DD3FC;
            }
        """)
        support_btn.clicked.connect(self.launch_help_page)
        sidebar_layout.addWidget(support_btn)

        logout_btn = QPushButton("LOG OUT")
        logout_btn.setFixedSize(85, 60)
        logout_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        logout_btn.setStyleSheet("""
            QPushButton {
                background-color: #FEF2F2;
                color: #E11D48;
                font-size: 10px;
                font-weight: bold;
                border-radius: 10px;
                border: 1px solid #FECDD3;
            }
            QPushButton:hover {
                background-color: #FFE4E6;
                color: #BE123C;
            }
            QPushButton:pressed {
                background-color: #FCA5A5;
            }
        """)
        logout_btn.clicked.connect(self.launch_admin_page)
        sidebar_layout.addWidget(logout_btn)

        root_layout.addWidget(sidebar)

        # ---------------- CONTENT AREA ----------------
        content_area = QWidget()
        content_area.setStyleSheet("background: transparent;")
        content_layout = QVBoxLayout(content_area)
        content_layout.setContentsMargins(10, 8, 10, 8)
        content_layout.setSpacing(12)

        # ---------------- HEADER ----------------
        header_layout = QHBoxLayout()

        title_widget = QWidget()
        title_widget.setStyleSheet("background: transparent;")
        title_layout = QVBoxLayout(title_widget)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(2)

        main_title = QLabel("SOS HGS GANDAKI")
        main_title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        main_title.setStyleSheet("color: #0369A1; background: transparent;")

        sub_title = QLabel("ADMIN PORTAL")
        sub_title.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        sub_title.setStyleSheet("color: #64748B; letter-spacing: 1px; background: transparent;")

        title_layout.addWidget(main_title)
        title_layout.addWidget(sub_title)
        header_layout.addWidget(title_widget)

        header_layout.addStretch()

        self.clock_label = QLabel()
        self.clock_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        self.clock_label.setStyleSheet("color: #0F172A; background: transparent;")
        self.clock_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        header_layout.addWidget(self.clock_label)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_clock)
        self.timer.start(1000)
        self.update_clock()

        content_layout.addLayout(header_layout)

        # ---------------- MAIN GRID ----------------
        grid_layout = QGridLayout()
        grid_layout.setSpacing(12)

        # ---------------- 1. SUBSTITUTION CARD ----------------
        sub_card = QFrame()
        sub_card.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.92);
                border: 1px solid #BAE6FD;
                border-radius: 12px;
            }
        """)
        sub_layout = QVBoxLayout(sub_card)
        sub_layout.setContentsMargins(18, 14, 18, 14)
        sub_layout.setSpacing(10)

        sub_title_lbl = QLabel("LIVE SUBSTITUTION ENTRY")
        sub_title_lbl.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        sub_title_lbl.setStyleSheet("color: #0369A1; border: none; background: transparent;")
        sub_layout.addWidget(sub_title_lbl)

        row1_layout = QHBoxLayout()
        row1_layout.setSpacing(12)

        class_container, self.class_combo = self.create_combobox_field("Class", [str(i) for i in range(6, 13)])
        section_container, self.section_combo = self.create_combobox_field("Section", [])
        period_container, self.period_combo = self.create_combobox_field("Period", [])

        row1_layout.addWidget(class_container)
        row1_layout.addWidget(section_container)
        row1_layout.addWidget(period_container)

        sub_layout.addLayout(row1_layout)

        self.class_combo.currentIndexChanged.connect(self.update_dependent_dropdowns)
        self.update_dependent_dropdowns()

        row2_layout = QHBoxLayout()
        row2_layout.setSpacing(12)

        self.absent_teacher_input = self.create_input_field(row2_layout, "Absent Teacher", "Enter absent teacher name")
        self.sub_teacher_input = self.create_input_field(row2_layout, "Substitute Teacher", "Enter substitute teacher name")

        sub_layout.addLayout(row2_layout)

        post_sub_btn = QPushButton("POST LIVE SUBSTITUTION")
        post_sub_btn.setFixedHeight(38)
        post_sub_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        post_sub_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0284C7, stop:1 #0369A1);
                color: #FFFFFF;
                font-size: 11px;
                font-weight: bold;
                border-radius: 6px;
                border: none;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0369A1, stop:1 #0284C7);
            }
        """)
        sub_layout.addWidget(post_sub_btn)

        grid_layout.addWidget(sub_card, 0, 0, 1, 2)

        # ---------------- 2. NOTICES CARD WITH SCROLL AREA ----------------
        notices_card = QFrame()
        notices_card.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.92);
                border: 1px solid #BAE6FD;
                border-radius: 12px;
            }
        """)
        outer_notices_layout = QVBoxLayout(notices_card)
        outer_notices_layout.setContentsMargins(14, 12, 14, 12)
        outer_notices_layout.setSpacing(6)

        notices_title = QLabel("NOTICES ENTRY")
        notices_title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        notices_title.setStyleSheet("color: #0369A1; border: none; background: transparent;")
        outer_notices_layout.addWidget(notices_title)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }
            QScrollBar:vertical {
                border: none;
                background: #F1F5F9;
                width: 6px;
                border-radius: 3px;
            }
            QScrollBar::handle:vertical {
                background: #BAE6FD;
                border-radius: 3px;
            }
            QScrollBar::handle:vertical:hover {
                background: #0284C7;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)

        scroll_content = QWidget()
        scroll_content.setStyleSheet("background: transparent;")
        notices_layout = QVBoxLayout(scroll_content)
        notices_layout.setContentsMargins(4, 4, 10, 4)
        notices_layout.setSpacing(10)

        self.notice_title_input = QLineEdit()
        self.notice_title_input.setPlaceholderText("Enter Notice Title")
        self.notice_title_input.setFixedHeight(34)
        self.notice_title_input.setStyleSheet("""
            QLineEdit {
                background-color: #FFFFFF;
                color: #0F172A;
                border: 1px solid #BAE6FD;
                border-radius: 6px;
                padding: 4px 10px;
                font-size: 11px;
            }
            QLineEdit:focus {
                border-color: #0284C7;
            }
        """)
        notices_layout.addWidget(self.notice_title_input)

        self.notice_content_input = QTextEdit()
        self.notice_content_input.setPlaceholderText("Write the details/content of the notice here...")
        self.notice_content_input.setMinimumHeight(70)
        self.notice_content_input.setStyleSheet("""
            QTextEdit {
                background-color: #FFFFFF;
                color: #0F172A;
                border: 1px solid #BAE6FD;
                border-radius: 6px;
                padding: 6px 10px;
                font-size: 11px;
            }
            QTextEdit:focus {
                border-color: #0284C7;
            }
        """)
        notices_layout.addWidget(self.notice_content_input)

        target_label = QLabel("Target Audience / Class Range:")
        target_label.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        target_label.setStyleSheet("color: #0369A1; border: none; background: transparent;")
        notices_layout.addWidget(target_label)

        range_layout = QHBoxLayout()
        range_layout.setSpacing(8)

        target_preset_container, self.target_preset_combo = self.create_combobox_field(
            "Preset Target", 
            ["All Classes (6-12)", "Junior High (6-10)", "Senior High (11-12)", "Custom Grade Range"]
        )
        range_layout.addWidget(target_preset_container)

        self.custom_range_widget = QWidget()
        self.custom_range_widget.setStyleSheet("border: none; background: transparent;")
        custom_layout = QHBoxLayout(self.custom_range_widget)
        custom_layout.setContentsMargins(0, 0, 0, 0)
        custom_layout.setSpacing(6)

        start_cnt, self.start_grade_combo = self.create_combobox_field("From", [str(i) for i in range(6, 13)])
        end_cnt, self.end_grade_combo = self.create_combobox_field("To", [str(i) for i in range(6, 13)])
        self.end_grade_combo.setCurrentText("12")

        custom_layout.addWidget(start_cnt)
        custom_layout.addWidget(end_cnt)

        range_layout.addWidget(self.custom_range_widget)

        section_cnt, self.notice_section_combo = self.create_combobox_field(
            "Section", 
            ["All Sections", "Section A", "Section B", "Section C", "Section D"]
        )
        range_layout.addWidget(section_cnt)

        notices_layout.addLayout(range_layout)

        self.target_preset_combo.currentIndexChanged.connect(self.on_preset_changed)
        self.start_grade_combo.currentIndexChanged.connect(self.update_notice_sections)
        self.end_grade_combo.currentIndexChanged.connect(self.update_notice_sections)
        self.custom_range_widget.setVisible(False)

        pdf_container = QWidget()
        pdf_container.setStyleSheet("border: none; background: transparent;")
        pdf_layout = QHBoxLayout(pdf_container)
        pdf_layout.setContentsMargins(0, 0, 0, 0)
        pdf_layout.setSpacing(8)

        self.file_label = QLabel("No PDF Selected")
        self.file_label.setFont(QFont("Segoe UI", 9))
        self.file_label.setStyleSheet("color: #64748B; border: none; background: transparent;")
        pdf_layout.addWidget(self.file_label)

        upload_pdf_btn = QPushButton("BROWSE PDF")
        upload_pdf_btn.setFixedHeight(32)
        upload_pdf_btn.setFixedWidth(110)
        upload_pdf_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        upload_pdf_btn.setStyleSheet("""
            QPushButton {
                background-color: #E0F2FE;
                color: #0369A1;
                font-size: 10px;
                font-weight: bold;
                border-radius: 6px;
                border: 1px solid #BAE6FD;
            }
            QPushButton:hover {
                background-color: #BAE6FD;
                color: #0284C7;
            }
        """)
        upload_pdf_btn.clicked.connect(self.upload_pdf)
        pdf_layout.addWidget(upload_pdf_btn)
        notices_layout.addWidget(pdf_container)

        post_notice_btn = QPushButton("POST NOTICE")
        post_notice_btn.setFixedHeight(36)
        post_notice_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        post_notice_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0284C7, stop:1 #0369A1);
                color: #FFFFFF;
                font-size: 11px;
                font-weight: bold;
                border-radius: 6px;
                border: none;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0369A1, stop:1 #0284C7);
            }
        """)
        post_notice_btn.clicked.connect(self.post_notice)
        notices_layout.addWidget(post_notice_btn)

        scroll_area.setWidget(scroll_content)
        outer_notices_layout.addWidget(scroll_area)

        grid_layout.addWidget(notices_card, 1, 0)

        # ---------------- 3. RECENT NOTICES CARD ----------------
        recent_card = QFrame()
        recent_card.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.92);
                border: 1px solid #BAE6FD;
                border-radius: 12px;
            }
        """)
        recent_layout = QVBoxLayout(recent_card)
        recent_layout.setContentsMargins(18, 14, 18, 14)
        recent_layout.setSpacing(10)

        rec_top_layout = QHBoxLayout()
        rec_top_layout.setContentsMargins(0, 0, 0, 0)
        rec_title = QLabel("RECENT NOTICES")
        rec_title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        rec_title.setStyleSheet("color: #0369A1; border: none; background: transparent;")
        rec_top_layout.addWidget(rec_title)

        rec_search = QLineEdit()
        rec_search.setPlaceholderText("Search notices...")
        rec_search.setFixedSize(140, 30)
        rec_search.setStyleSheet("""
            QLineEdit {
                background-color: #FFFFFF;
                color: #0F172A;
                border: 1px solid #BAE6FD;
                border-radius: 6px;
                padding: 3px 8px;
                font-size: 10px;
            }
            QLineEdit:focus {
                border-color: #0284C7;
            }
        """)
        rec_search.textChanged.connect(self.filter_recent_notices)
        rec_top_layout.addWidget(rec_search)
        recent_layout.addLayout(rec_top_layout)

        self.recent_notices_list = QListWidget()
        self.recent_notices_list.setStyleSheet("""
            QListWidget {
                background-color: #FFFFFF;
                color: #0F172A;
                border: 1px solid #BAE6FD;
                border-radius: 6px;
                padding: 4px;
                font-size: 11px;
            }
            QListWidget::item {
                padding: 6px;
                border-bottom: 1px solid #F1F5F9;
            }
        """)
        recent_layout.addWidget(self.recent_notices_list)

        grid_layout.addWidget(recent_card, 1, 1)

        grid_layout.setRowStretch(0, 0)
        grid_layout.setRowStretch(1, 1)
        grid_layout.setColumnStretch(0, 1)
        grid_layout.setColumnStretch(1, 1)

        content_layout.addLayout(grid_layout)

        footer_label = QLabel("SOS HGS Gandaki • School Management System")
        footer_label.setFont(QFont("Segoe UI", 9))
        footer_label.setStyleSheet("color: #64748B; background: transparent;")
        content_layout.addWidget(footer_label)

        root_layout.addWidget(content_area)

    def create_combobox_field(self, label_text, items):
        container = QWidget()
        container.setStyleSheet("border: none; background: transparent;")
        vbox = QVBoxLayout(container)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(4)

        lbl = QLabel(label_text)
        lbl.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        lbl.setStyleSheet("color: #0369A1; border: none; background: transparent;")
        vbox.addWidget(lbl)

        combo = QComboBox()
        combo.setFixedHeight(34)
        if items:
            combo.addItems(items)

        combo.setStyleSheet("""
            QComboBox {
                background-color: #FFFFFF;
                color: #0F172A;
                border: 1px solid #BAE6FD;
                border-radius: 6px;
                padding-left: 8px;
                font-size: 10px;
            }
            QComboBox::drop-down {
                border: none;
                width: 18px;
            }
            QComboBox:focus {
                border-color: #0284C7;
            }
            QComboBox QAbstractItemView {
                background-color: #FFFFFF;
                color: #0F172A;
                selection-background-color: #E0F2FE;
                selection-color: #0369A1;
                border: 1px solid #BAE6FD;
                outline: none;
                padding: 4px;
            }
        """)
        vbox.addWidget(combo)
        return container, combo

    def on_preset_changed(self):
        selected = self.target_preset_combo.currentText()
        if selected == "Custom Grade Range":
            self.custom_range_widget.setVisible(True)
        else:
            self.custom_range_widget.setVisible(False)
        self.update_notice_sections()

    def update_notice_sections(self):
        preset = self.target_preset_combo.currentText()

        if preset == "Junior High (6-10)":
            has_senior = False
        elif preset == "Senior High (11-12)":
            has_senior = True
        elif preset == "All Classes (6-12)":
            has_senior = True
        else:
            try:
                start = int(self.start_grade_combo.currentText() or 6)
                end = int(self.end_grade_combo.currentText() or 12)
                has_senior = (start >= 11 or end >= 11)
            except ValueError:
                has_senior = True

        current_sec = self.notice_section_combo.currentText()
        self.notice_section_combo.clear()

        if has_senior:
            self.notice_section_combo.addItems(["All Sections", "Section A", "Section B", "Section C", "Section D"])
        else:
            self.notice_section_combo.addItems(["All Sections", "Section A", "Section B"])

        if self.notice_section_combo.findText(current_sec) != -1:
            self.notice_section_combo.setCurrentText(current_sec)

    def update_dependent_dropdowns(self):
        try:
            selected_class = int(self.class_combo.currentText())
        except ValueError:
            selected_class = 6

        self.section_combo.clear()
        if selected_class <= 10:
            self.section_combo.addItems(["A", "B"])
        else:
            self.section_combo.addItems(["A", "B", "C", "D"])

        self.period_combo.clear()
        if selected_class <= 10:
            self.period_combo.addItems([str(i) for i in range(1, 9)])
        else:
            self.period_combo.addItems([str(i) for i in range(1, 10)])

    def create_input_field(self, layout, label_text, placeholder):
        container = QWidget()
        container.setStyleSheet("border: none; background: transparent;")
        vbox = QVBoxLayout(container)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(4)

        lbl = QLabel(label_text)
        lbl.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        lbl.setStyleSheet("color: #0369A1; border: none; background: transparent;")
        vbox.addWidget(lbl)

        field = QLineEdit()
        field.setPlaceholderText(placeholder)
        field.setFixedHeight(36)
        field.setStyleSheet("""
            QLineEdit {
                background-color: #FFFFFF;
                color: #0F172A;
                border: 1px solid #BAE6FD;
                border-radius: 6px;
                padding: 4px 10px;
                font-size: 11px;
            }
            QLineEdit:focus {
                border-color: #0284C7;
            }
        """)
        vbox.addWidget(field)
        layout.addWidget(container)
        return field

    def filter_recent_notices(self, text):
        query = text.strip().lower()
        for i in range(self.recent_notices_list.count()):
            item = self.recent_notices_list.item(i)
            item.setHidden(query not in item.text().lower())

    def update_clock(self):
        current_time = QTime.currentTime().toString("hh:mm:ss AP")
        current_date = QDate.currentDate().toString("dddd, d MMMM yyyy")
        self.clock_label.setText(f"{current_time}\n{current_date}")

    def upload_pdf(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Select PDF Document", "", "PDF Files (*.pdf)"
        )
        if file_name:
            short_name = os.path.basename(file_name)
            self.file_label.setText(f"PDF: {short_name}")
            self.selected_pdf_path = short_name

    def post_notice(self):
        title_text = self.notice_title_input.text().strip()
        if not title_text:
            return

        preset = self.target_preset_combo.currentText()
        section = self.notice_section_combo.currentText()

        if preset == "Custom Grade Range":
            start_g = self.start_grade_combo.currentText()
            end_g = self.end_grade_combo.currentText()
            target_tag = f"Class {start_g}-{end_g}" if start_g != end_g else f"Class {start_g}"
        elif preset == "Junior High (6-10)":
            target_tag = "Class 6-10"
        elif preset == "Senior High (11-12)":
            target_tag = "Class 11-12"
        else:
            target_tag = "Class 6-12"

        if section != "All Sections":
            target_tag += f" ({section})"

        notice_display = f"• [{target_tag}] {title_text}"
        if self.selected_pdf_path:
            notice_display += f" [PDF: {self.selected_pdf_path}]"

        self.recent_notices_list.insertItem(0, notice_display)

        if self.recent_notices_list.count() > 10:
            self.recent_notices_list.takeItem(10)

        self.notice_title_input.clear()
        self.notice_content_input.clear()
        self.file_label.setText("No PDF Selected")
        self.selected_pdf_path = None

    def launch_help_page(self):
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            help_path = os.path.join(base_dir, "help.py")
            if not os.path.exists(help_path):
                print(f"❌ ERROR: File not found at {help_path}")
                return
            subprocess.Popen([sys.executable, help_path], cwd=base_dir)
            self.close()
        except Exception as e:
            print(f"❌ Error launching help.py: {e}")

    def launch_admin_page(self):
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            adminpage_path = os.path.join(base_dir, "adminpage.py")
            subprocess.Popen([sys.executable, adminpage_path], cwd=base_dir)
            QApplication.quit()
        except Exception as e:
            print(f"Error launching adminpage.py: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)

    app.setStyle("Fusion")
    font = QFont("Segoe UI", 10)
    font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
    app.setFont(font)

    app.setStyleSheet("""
        QComboBox QAbstractItemView {
            background-color: #FFFFFF;
            color: #0F172A;
            selection-background-color: #E0F2FE;
            selection-color: #0369A1;
            border: 1px solid #BAE6FD;
            outline: none;
            padding: 4px;
        }
    """)

    window = AdminPanel()
    window.show()
    sys.exit(app.exec())
