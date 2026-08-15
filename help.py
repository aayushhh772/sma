import sys, os, subprocess, webbrowser
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QFrame, QMessageBox, QScrollArea)
from PyQt6.QtGui import QFont, QPainter, QPainterPath, QColor, QLinearGradient
from PyQt6.QtCore import Qt

class WaveHeader(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(140)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        bg_gradient = QLinearGradient(0, 0, self.width(), self.height())
        bg_gradient.setColorAt(0.0, QColor("#0a192f"))
        bg_gradient.setColorAt(1.0, QColor("#0e2a47"))
        painter.fillRect(self.rect(), bg_gradient)
        
        path1 = QPainterPath()
        path1.moveTo(0, self.height() * 0.7)
        path1.cubicTo(self.width() * 0.3, self.height() * 0.4, 
                      self.width() * 0.6, self.height() * 0.9, 
                      self.width(), self.height() * 0.5)
        path1.lineTo(self.width(), self.height())
        path1.lineTo(0, self.height())
        path1.closeSubpath()
        
        wave_grad1 = QLinearGradient(0, 0, self.width(), 0)
        wave_grad1.setColorAt(0.0, QColor(0, 119, 182, 120))
        wave_grad1.setColorAt(1.0, QColor(72, 202, 228, 80))
        painter.fillPath(path1, wave_grad1)

        path2 = QPainterPath()
        path2.moveTo(0, self.height() * 0.85)
        path2.cubicTo(self.width() * 0.25, self.height() * 0.65, 
                      self.width() * 0.7, self.height() * 0.95, 
                      self.width(), self.height() * 0.65)
        path2.lineTo(self.width(), self.height())
        path2.lineTo(0, self.height())
        path2.closeSubpath()

        wave_grad2 = QLinearGradient(0, 0, self.width(), 0)
        wave_grad2.setColorAt(0.0, QColor(0, 180, 216, 160))
        wave_grad2.setColorAt(1.0, QColor(144, 224, 239, 120))
        painter.fillPath(path2, wave_grad2)

class HelpWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def open_email(self, email):
        try:
            webbrowser.open(f"mailto:{email}")
        except Exception as e:
            QMessageBox.warning(self, "Unable to Open Email", f"Could not open email application.\n\n{e}")

    def open_adminpage(self):
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            adminpage_path = os.path.join(base_dir, "adminpage.py")
            if not os.path.isfile(adminpage_path):
                QMessageBox.warning(self, "File Not Found", "adminpage.py was not found in project directory.")
                return
            subprocess.Popen([sys.executable, adminpage_path], cwd=base_dir)
            self.close()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not open adminpage.py.\n\n{e}")

    def create_email_card(self, name, email):
        card = QFrame()
        card.setStyleSheet("QFrame { background: #ffffff; border: 1px solid #e0e8f0; border-radius: 10px; }")
        layout = QHBoxLayout(card)
        layout.setContentsMargins(16, 10, 16, 10)

        icon = QLabel("✉")
        icon.setFont(QFont("Segoe UI", 16))
        icon.setStyleSheet("color: #0077b6; border: none;")
        icon.setFixedWidth(30)
        layout.addWidget(icon)

        text_layout = QVBoxLayout()
        name_label = QLabel(name)
        name_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        name_label.setStyleSheet("color: #0f172a; border: none;")
        
        email_label = QLabel(email)
        email_label.setFont(QFont("Segoe UI", 9))
        email_label.setStyleSheet("color: #64748b; border: none;")
        
        text_layout.addWidget(name_label)
        text_layout.addWidget(email_label)
        layout.addLayout(text_layout)
        layout.addStretch()

        contact_btn = QPushButton("Contact")
        contact_btn.setFixedSize(85, 32)
        contact_btn.setStyleSheet("""
            QPushButton { background: #0077b6; color: #ffffff; border: none; border-radius: 6px; font-weight: bold; }
            QPushButton:hover { background: #0096c7; }
            QPushButton:pressed { background: #03045e; }
        """)
        contact_btn.clicked.connect(lambda checked=False, addr=email: self.open_email(addr))
        layout.addWidget(contact_btn)

        return card

    def create_faq(self, question, answer):
        card = QFrame()
        card.setStyleSheet("QFrame { background: #ffffff; border: 1px solid #e0e8f0; border-radius: 8px; }")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(14, 10, 14, 10)

        q_label = QLabel(question)
        q_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        q_label.setStyleSheet("color: #0f172a; border: none;")
        
        a_label = QLabel(answer)
        a_label.setWordWrap(True)
        a_label.setFont(QFont("Segoe UI", 9))
        a_label.setStyleSheet("color: #475569; border: none;")

        layout.addWidget(q_label)
        layout.addWidget(a_label)
        return card

    def init_ui(self):
        self.setWindowTitle("Help & Support")
        self.resize(850, 650)
        self.setStyleSheet("""
            QWidget { background-color: #f8fafc; color: #0f172a; font-family: 'Segoe UI'; }
            QScrollBar:vertical { background: #f1f5f9; width: 8px; border-radius: 4px; }
            QScrollBar::handle:vertical { background: #cbd5e1; border-radius: 4px; }
            QScrollBar::handle:vertical:hover { background: #94a3b8; }
        """)

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("QScrollArea { border: none; }")

        scroll_content = QWidget()
        main_layout = QVBoxLayout(scroll_content)
        main_layout.setContentsMargins(0, 0, 0, 20)
        main_layout.setSpacing(14)

        header = WaveHeader()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(30, 15, 30, 35)

        title_layout = QVBoxLayout()
        title = QLabel("Help & Support")
        title.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        title.setStyleSheet("color: #ffffff; border: none; background: transparent;")

        subtitle = QLabel("Classroom Management System")
        subtitle.setFont(QFont("Segoe UI", 10))
        subtitle.setStyleSheet("color: #90e0ef; border: none; background: transparent;")

        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)
        header_layout.addLayout(title_layout)
        header_layout.addStretch()

        sos_badge = QFrame()
        sos_badge.setFixedSize(65, 65)
        sos_badge.setStyleSheet("""
            QFrame {
                background: #ffffff;
                border-radius: 32px;
                border: 2px solid #90e0ef;
            }
        """)
        sos_layout = QVBoxLayout(sos_badge)
        sos_layout.setContentsMargins(0, 0, 0, 0)
        
        sos_label = QLabel("SOS")
        sos_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sos_label.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        sos_label.setStyleSheet("color: #d97706; border: none; background: transparent;")
        sos_layout.addWidget(sos_label)

        header_layout.addWidget(sos_badge)
        main_layout.addWidget(header)

        content_wrapper = QWidget()
        content_layout = QVBoxLayout(content_wrapper)
        content_layout.setContentsMargins(30, 0, 30, 0)
        content_layout.setSpacing(12)

        supp_title = QLabel("Contact & Support")
        supp_title.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        supp_title.setStyleSheet("color: #0f172a;")
        content_layout.addWidget(supp_title)

        emails = [
            ("Support Team", "irajmadhav061@gmail.com"),
            ("Support Team", "pandeyaayush978@gmail.com"),
            ("Support Team", "hellopratik2021@gmail.com"),
            ("Support Team", "kaflealdrin@gmail.com"),
            
        ]
        for name, email in emails:
            content_layout.addWidget(self.create_email_card(name, email))

        faq_title = QLabel("Quick Help")
        faq_title.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        faq_title.setStyleSheet("color: #0f172a; margin-top: 10px;")
        content_layout.addWidget(faq_title)

        faqs = [
            ("Attendance is not being marked.", "Make sure the barcode/QR scanner is connected and system active."),
            ("The application is not opening.", "Restart application and verify Python files are in the correct path."),
            ("I need further assistance.", "Use the Contact buttons above to reach the support team directly.")
        ]
        for q, a in faqs:
            content_layout.addWidget(self.create_faq(q, a))

        footer = QHBoxLayout()
        footer.addStretch()

        back_btn = QPushButton("← Back to Dashboard")
        back_btn.setFixedSize(170, 38)
        back_btn.setStyleSheet("""
            QPushButton { background: #ffffff; color: #0077b6; border: 1px solid #0077b6; border-radius: 6px; font-weight: bold; }
            QPushButton:hover { background: #e0f2fe; }
            QPushButton:pressed { background: #bae6fd; }
        """)
        back_btn.clicked.connect(self.open_adminpage)
        footer.addWidget(back_btn)

        content_layout.addLayout(footer)
        main_layout.addWidget(content_wrapper)

        scroll_area.setWidget(scroll_content)
        root_layout.addWidget(scroll_area)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HelpWindow()
    window.show()
    sys.exit(app.exec())
