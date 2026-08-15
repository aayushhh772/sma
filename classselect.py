import sys
import subprocess
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QComboBox,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class ClassSelection(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Class Selection")
        self.setFixedSize(650, 500)

        # Dark bluish background
        self.setStyleSheet("""
            QWidget {
                background-color: #182B3A;
                color: white;
                font-family: Arial;
            }

            QLabel {
                color: white;
            }

            QComboBox {
                background-color: #243D50;
                color: white;
                border: 1px solid #3E5D72;
                border-radius: 10px;
                padding: 12px;
                font-size: 16px;
            }

            QComboBox:hover {
                border: 1px solid #63839A;
            }

            QComboBox QAbstractItemView {
                background-color: #243D50;
                color: white;
                selection-background-color: #35566D;
                selection-color: white;
            }

            QPushButton {
                background-color: #3A6078;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 13px;
                font-size: 16px;
                font-weight: bold;
            }

            QPushButton:hover {
                background-color: #4B718A;
            }

            QPushButton:pressed {
                background-color: #2E5066;
            }
        """)

        self.create_ui()

    def create_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(40, 30, 40, 30)
        main_layout.setSpacing(20)

        # Header
        header = QLabel("Class Selection")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)

        header_font = QFont()
        header_font.setPointSize(28)
        header_font.setBold(True)
        header.setFont(header_font)

        main_layout.addWidget(header)

        # Subtitle
        subtitle = QLabel("Select your class and section")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("""
            color: #AFC1CF;
            font-size: 15px;
        """)

        main_layout.addWidget(subtitle)

        # Card
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #1F3546;
                border-radius: 15px;
            }
        """)

        card_layout = QVBoxLayout()
        card_layout.setContentsMargins(30, 30, 30, 30)
        card_layout.setSpacing(15)

        # Class label
        class_label = QLabel("Class")
        class_label.setStyleSheet("""
            font-size: 15px;
            font-weight: bold;
            color: #C8D6DF;
        """)

        card_layout.addWidget(class_label)

        # Class dropdown
        self.class_dropdown = QComboBox()

        for i in range(6, 13):
            self.class_dropdown.addItem(f"Class {i}", i)

        self.class_dropdown.currentIndexChanged.connect(
            self.update_sections
        )

        card_layout.addWidget(self.class_dropdown)

        # Section label
        section_label = QLabel("Section")
        section_label.setStyleSheet("""
            font-size: 15px;
            font-weight: bold;
            color: #C8D6DF;
        """)

        card_layout.addWidget(section_label)

        # Section dropdown
        self.section_dropdown = QComboBox()

        card_layout.addWidget(self.section_dropdown)

        # Continue button
        self.continue_button = QPushButton("Continue")
        self.continue_button.clicked.connect(self.continue_selection)

        card_layout.addSpacing(10)
        card_layout.addWidget(self.continue_button)

        # Result label
        self.result_label = QLabel("")
        self.result_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.result_label.setStyleSheet("""
            color: #B7CBD8;
            font-size: 15px;
            font-weight: bold;
        """)

        card_layout.addWidget(self.result_label)

        card.setLayout(card_layout)

        main_layout.addWidget(card)
        main_layout.addStretch()

        self.setLayout(main_layout)

        # Initialize sections
        self.update_sections()

    def update_sections(self):
        selected_class = self.class_dropdown.currentData()
        self.section_dropdown.clear()

        # Classes 6 to 10 have sections A and B
        # Classes 11 and 12 have sections A, B, C, and D
        if selected_class <= 10:
            sections = ["A", "B"]
        else:
            sections = ["A", "B", "C", "D"]

        self.section_dropdown.addItems(sections)

    def continue_selection(self):
        selected_class = self.class_dropdown.currentData()
        selected_section = self.section_dropdown.currentText()

        full_class_name = f"Class {selected_class} {selected_section}"

        # Launch test.py using the active Python executable
        subprocess.Popen([sys.executable, "test.py", full_class_name])
        
        # Close the current ClassSelection window
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = ClassSelection()
    window.show()

    sys.exit(app.exec())
