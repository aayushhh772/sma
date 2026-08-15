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

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


# ============================================================
# LOGIN SELECTION PAGE
# ============================================================

class LoginSelectionPage(QWidget):
    """Initial selection page: Class vs Admin"""

    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.init_ui()

    def init_ui(self):

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title = QLabel("Classroom Portal")
        title.setFont(
            QFont(
                "Segoe UI",
                24,
                QFont.Weight.Bold
            )
        )

        title.setStyleSheet(
            "color: #ffffff; margin-bottom: 30px;"
        )

        title.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        layout.addWidget(title)

        # ------------------------------------------------------
        # OPTIONS
        # ------------------------------------------------------

        card_layout = QHBoxLayout()
        card_layout.setSpacing(20)

        # ------------------------------------------------------
        # CLASS DISPLAY
        # ------------------------------------------------------

        self.class_btn = QPushButton(
            "🏫\n\nClass Display\n(Direct Access)"
        )

        self.class_btn.setFixedSize(200, 180)

        self.class_btn.setFont(
            QFont("Segoe UI", 12)
        )

        self.class_btn.setStyleSheet(
            self.get_card_style()
        )

        self.class_btn.clicked.connect(
            self.controller.open_class_select
        )

        # ------------------------------------------------------
        # ADMIN
        # ------------------------------------------------------

        self.admin_btn = QPushButton(
            "🔒\n\nAdmin Portal\n(Login Required)"
        )

        self.admin_btn.setFixedSize(200, 180)

        self.admin_btn.setFont(
            QFont("Segoe UI", 12)
        )

        self.admin_btn.setStyleSheet(
            self.get_card_style()
        )

        self.admin_btn.clicked.connect(
            self.controller.show_admin_login
        )

        card_layout.addWidget(
            self.class_btn
        )

        card_layout.addWidget(
            self.admin_btn
        )

        layout.addLayout(card_layout)

        self.setLayout(layout)

    def get_card_style(self):

        return """
            QPushButton {
                background-color: #213042;
                color: #ffffff;
                border: 2px solid #32475e;
                border-radius: 12px;
            }

            QPushButton:hover {
                border-color: #007acc;
                background-color: #2a3d54;
            }
        """


# ============================================================
# ADMIN LOGIN PAGE
# ============================================================

class AdminLoginPage(QWidget):
    """Admin Authentication View"""

    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.init_ui()

    def init_ui(self):

        main_layout = QVBoxLayout()

        main_layout.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        # ------------------------------------------------------
        # FORM CARD
        # ------------------------------------------------------

        card = QFrame()

        card.setFixedSize(
            340,
            360
        )

        card.setStyleSheet(
            """
            background-color: #1b2836;
            border-radius: 12px;
            border: 1px solid #2c3e50;
            """
        )

        card_layout = QVBoxLayout(card)

        card_layout.setContentsMargins(
            25,
            25,
            25,
            25
        )

        # ------------------------------------------------------
        # TITLE
        # ------------------------------------------------------

        title = QLabel(
            "Admin Sign In"
        )

        title.setFont(
            QFont(
                "Segoe UI",
                16,
                QFont.Weight.Bold
            )
        )

        title.setStyleSheet(
            "color: #ffffff; border: none;"
        )

        title.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        card_layout.addWidget(title)

        # ------------------------------------------------------
        # ADMIN ID
        # ------------------------------------------------------

        self.id_input = QLineEdit()

        self.id_input.setPlaceholderText(
            "Admin ID"
        )

        self.id_input.setStyleSheet(
            self.get_input_style()
        )

        # ------------------------------------------------------
        # PASSWORD
        # ------------------------------------------------------

        self.pass_input = QLineEdit()

        self.pass_input.setPlaceholderText(
            "Password"
        )

        self.pass_input.setEchoMode(
            QLineEdit.EchoMode.Password
        )

        self.pass_input.setStyleSheet(
            self.get_input_style()
        )

        card_layout.addWidget(
            self.id_input
        )

        card_layout.addWidget(
            self.pass_input
        )

        # ------------------------------------------------------
        # LOGIN BUTTON
        # ------------------------------------------------------

        login_btn = QPushButton(
            "Login to Panel"
        )

        login_btn.setFont(
            QFont(
                "Segoe UI",
                10,
                QFont.Weight.Bold
            )
        )

        login_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #007acc;
                color: white;
                border-radius: 6px;
                padding: 10px;
                border: none;
            }

            QPushButton:hover {
                background-color: #0062a3;
            }
            """
        )

        login_btn.clicked.connect(
            self.verify_login
        )

        card_layout.addWidget(
            login_btn
        )

        # ------------------------------------------------------
        # BACK BUTTON
        # ------------------------------------------------------

        cancel_btn = QPushButton(
            "Back to Selection"
        )

        cancel_btn.setStyleSheet(
            """
            color: #8b9dc3;
            border: none;
            margin-top: 5px;
            """
        )

        cancel_btn.clicked.connect(
            self.controller.show_selection
        )

        card_layout.addWidget(
            cancel_btn
        )

        main_layout.addWidget(card)

        self.setLayout(main_layout)

    # ========================================================
    # INPUT STYLE
    # ========================================================

    def get_input_style(self):

        return """
            QLineEdit {
                background-color: #121c26;
                color: white;
                border: 1px solid #32475e;
                border-radius: 6px;
                padding: 10px;
                font-size: 13px;
            }

            QLineEdit:focus {
                border-color: #007acc;
            }
        """

    # ========================================================
    # VERIFY LOGIN
    # ========================================================

    def verify_login(self):

        username = self.id_input.text().strip()
        password = self.pass_input.text().strip()

        if username and password:

            self.id_input.clear()
            self.pass_input.clear()

            # Open the separate admin_panel.py
            self.controller.open_admin_panel()

        else:

            QMessageBox.warning(
                self,
                "Login Error",
                "Please enter both Admin ID and Password."
            )


# ============================================================
# MAIN APP CONTROLLER
# ============================================================

class MainApp(QStackedWidget):
    """Main controller for the application"""

    def __init__(self):

        super().__init__()

        self.setWindowTitle(
            "Classroom Management Portal"
        )

        self.resize(
            950,
            600
        )

        self.setStyleSheet(
            "background-color: #16222f;"
        )

        # ------------------------------------------------------
        # CREATE PAGES
        # ------------------------------------------------------

        self.selection_page = LoginSelectionPage(
            self
        )

        self.admin_login_page = AdminLoginPage(
            self
        )

        # ------------------------------------------------------
        # ADD PAGES
        # ------------------------------------------------------

        self.addWidget(
            self.selection_page
        )

        self.addWidget(
            self.admin_login_page
        )

        # Start at selection
        self.setCurrentIndex(0)

    # ========================================================
    # OPEN CLASSSELECT.PY
    # ========================================================

    def open_class_select(self):

        try:

            base_dir = os.path.dirname(
                os.path.abspath(__file__)
            )

            classselect_path = os.path.join(
                base_dir,
                "classselect.py"
            )

            if not os.path.exists(
                classselect_path
            ):

                QMessageBox.critical(
                    self,
                    "File Not Found",
                    "classselect.py was not found.\n\n"
                    "Make sure classselect.py is in "
                    "the same folder as this file."
                )

                return

            subprocess.Popen(
                [
                    sys.executable,
                    classselect_path
                ],
                cwd=base_dir
            )

            self.close()

        except Exception as e:

            QMessageBox.critical(
                self,
                "Error",
                f"Could not open classselect.py:\n\n{e}"
            )

    # ========================================================
    # OPEN ADMIN_PANEL.PY
    # ========================================================

    def open_admin_panel(self):

        try:

            # Get the folder containing this login program
            base_dir = os.path.dirname(
                os.path.abspath(__file__)
            )

            # Find admin_panel.py
            admin_panel_path = os.path.join(
                base_dir,
                "admin_panel.py"
            )

            # Check if it exists
            if not os.path.exists(
                admin_panel_path
            ):

                QMessageBox.critical(
                    self,
                    "File Not Found",
                    "admin_panel.py was not found.\n\n"
                    "Make sure admin_panel.py is in "
                    "the same folder as this file."
                )

                return

            # Start admin_panel.py
            subprocess.Popen(
                [
                    sys.executable,
                    admin_panel_path
                ],
                cwd=base_dir
            )

            # Close the login program
            self.close()

        except Exception as e:

            QMessageBox.critical(
                self,
                "Error",
                f"Could not open admin_panel.py:\n\n{e}"
            )

    # ========================================================
    # SHOW SELECTION
    # ========================================================

    def show_selection(self):

        self.setCurrentIndex(0)

    # ========================================================
    # SHOW ADMIN LOGIN
    # ========================================================

    def show_admin_login(self):

        self.setCurrentIndex(1)


# ============================================================
# PROGRAM START
# ============================================================

if __name__ == "__main__":

    app = QApplication(sys.argv)

    window = MainApp()

    window.show()

    sys.exit(
        app.exec()
    )
