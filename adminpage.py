import sys
import os
import subprocess

from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QStackedWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QLineEdit,
    QFrame,
    QMessageBox,
)
from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QFont, QPixmap, QPainter, QLinearGradient, QColor, QPainterPath


def get_logo_widget(height=85):
    logo_label = QLabel()
    logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    logo_label.setStyleSheet("background: transparent; border: none;")
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    logo_names = [
        "768999728_1727839055119237_5359534815132452996_n.jpg",
        "input_file_0.png",
        "486624203_601802256148254_3403736131493055483_n.png",
        "logo.png"
    ]
    
    logo_path = None
    for name in logo_names:
        path = os.path.join(base_dir, name)
        if os.path.exists(path):
            logo_path = path
            break
            
    if logo_path:
        pixmap = QPixmap(logo_path)
        scaled_pixmap = pixmap.scaledToHeight(height, Qt.TransformationMode.SmoothTransformation)
        logo_label.setPixmap(scaled_pixmap)
        
    return logo_label


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


class LoginSelectionPage(WaveBackgroundWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(15, 10, 15, 15)
        layout.setSpacing(6)

        self.logo = get_logo_widget(height=85)
        layout.addWidget(self.logo)

        school_title = QLabel("SOS Hermann Gmeiner Secondary School Gandaki")
        school_title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        school_title.setStyleSheet("color: #0369A1; border: none; background: transparent;")
        school_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(school_title)

        subtitle = QLabel("Classroom Management Portal")
        subtitle.setFont(QFont("Segoe UI", 10))
        subtitle.setStyleSheet("color: #64748B; border: none; background: transparent;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)

        card_layout = QHBoxLayout()
        card_layout.setSpacing(14)
        card_layout.setContentsMargins(0, 6, 0, 0)

        self.class_btn = QPushButton("Class Display\n\nDirect Access")
        self.class_btn.setFixedSize(190, 115)
        self.class_btn.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self.class_btn.setStyleSheet(self.get_card_style())
        self.class_btn.clicked.connect(self.controller.open_class_select)

        self.admin_btn = QPushButton("Admin Portal\n\nLogin Required")
        self.admin_btn.setFixedSize(190, 115)
        self.admin_btn.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self.admin_btn.setStyleSheet(self.get_card_style())
        self.admin_btn.clicked.connect(self.controller.show_admin_login)

        card_layout.addWidget(self.class_btn)
        card_layout.addWidget(self.admin_btn)

        layout.addLayout(card_layout)
        self.setLayout(layout)

    def get_card_style(self):
        return """
            QPushButton {
                background-color: rgba(255, 255, 255, 0.92);
                color: #0F172A;
                border: 1px solid #BAE6FD;
                border-radius: 10px;
                padding: 12px;
                text-align: center;
            }
            QPushButton:hover {
                border-color: #0284C7;
                background-color: #FFFFFF;
                color: #0284C7;
            }
            QPushButton:pressed {
                background-color: #E0F2FE;
            }
        """


class AdminLoginPage(WaveBackgroundWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.setContentsMargins(15, 10, 15, 15)

        card = QFrame()
        card.setFixedSize(340, 340)
        card.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.92);
                border-radius: 12px;
                border: 1px solid #BAE6FD;
            }
        """)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 14, 20, 14)
        card_layout.setSpacing(8)

        logo = get_logo_widget(height=70)
        card_layout.addWidget(logo)

        title = QLabel("Admin Sign In")
        title.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        title.setStyleSheet("color: #0F172A; border: none; background: transparent;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(title)

        self.id_input = QLineEdit()
        self.id_input.setPlaceholderText("Admin ID")
        self.id_input.setStyleSheet(self.get_input_style())

        self.pass_input = QLineEdit()
        self.pass_input.setPlaceholderText("Password")
        self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.pass_input.setStyleSheet(self.get_input_style())

        card_layout.addWidget(self.id_input)
        card_layout.addWidget(self.pass_input)

        login_btn = QPushButton("Sign In")
        login_btn.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        login_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0284C7, stop:1 #0369A1);
                color: #FFFFFF;
                border-radius: 6px;
                padding: 9px;
                border: none;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0369A1, stop:1 #0284C7);
            }
            QPushButton:pressed {
                background-color: #075985;
            }
        """)
        login_btn.clicked.connect(self.verify_login)
        card_layout.addWidget(login_btn)

        cancel_btn = QPushButton("Back to Selection")
        cancel_btn.setFont(QFont("Segoe UI", 9))
        cancel_btn.setStyleSheet("""
            QPushButton {
                color: #0369A1;
                border: none;
                background: transparent;
                font-weight: bold;
            }
            QPushButton:hover {
                color: #0284C7;
            }
        """)
        cancel_btn.clicked.connect(self.controller.show_selection)
        card_layout.addWidget(cancel_btn)

        main_layout.addWidget(card)
        self.setLayout(main_layout)

    def get_input_style(self):
        return """
            QLineEdit {
                background-color: #FFFFFF;
                color: #0F172A;
                border: 1px solid #BAE6FD;
                border-radius: 6px;
                padding: 7px 10px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border-color: #0284C7;
            }
        """

    def verify_login(self):
        username = self.id_input.text().strip()
        password = self.pass_input.text().strip()

        if username and password:
            self.id_input.clear()
            self.pass_input.clear()
            self.controller.open_admin_panel()
        else:
            QMessageBox.warning(
                self,
                "Login Error",
                "Please enter both Admin ID and Password."
            )


class MainApp(QStackedWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("SOS Hermann Gmeiner Secondary School Gandaki")
        self.resize(780, 500)

        self.selection_page = LoginSelectionPage(self)
        self.admin_login_page = AdminLoginPage(self)

        self.addWidget(self.selection_page)
        self.addWidget(self.admin_login_page)

        self.setCurrentIndex(0)

    def open_class_select(self):
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            classselect_path = os.path.join(base_dir, "classselect.py")

            if not os.path.exists(classselect_path):
                QMessageBox.critical(
                    self,
                    "File Not Found",
                    "classselect.py was not found.\n\nMake sure classselect.py is in the same folder as this file."
                )
                return

            subprocess.Popen([sys.executable, classselect_path], cwd=base_dir)
            self.close()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not open classselect.py:\n\n{e}")

    def open_admin_panel(self):
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            admin_panel_path = os.path.join(base_dir, "admin_panel.py")

            if not os.path.exists(admin_panel_path):
                QMessageBox.critical(
                    self,
                    "File Not Found",
                    "admin_panel.py was not found.\n\nMake sure admin_panel.py is in the same folder as this file."
                )
                return

            subprocess.Popen([sys.executable, admin_panel_path], cwd=base_dir)
            self.close()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not open admin_panel.py:\n\n{e}")

    def show_selection(self):
        self.setCurrentIndex(0)

    def show_admin_login(self):
        self.setCurrentIndex(1)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec())
