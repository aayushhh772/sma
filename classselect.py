import sys
import os
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
from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QFont, QPixmap, QPainter, QLinearGradient, QColor, QPainterPath


def get_logo_widget(height=60):
    logo_label = QLabel()
    logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    logo_names = [
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


class ClassSelection(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("SOS Hermann Gmeiner School Gandaki")
        self.setFixedSize(650, 520)

        self.setStyleSheet("""
            QLabel {
                color: #0F172A;
                background: transparent;
            }

            QComboBox {
                background-color: #FFFFFF;
                color: #0F172A;
                border: 1px solid #BAE6FD;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 14px;
            }

            QComboBox:hover {
                border-color: #0284C7;
            }

            QComboBox::drop-down {
                border: none;
                padding-right: 10px;
            }

            QComboBox QAbstractItemView {
                background-color: #FFFFFF;
                color: #0F172A;
                selection-background-color: #0284C7;
                selection-color: #FFFFFF;
                border: 1px solid #BAE6FD;
            }

            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0284C7, stop:1 #0284C7);
                color: #FFFFFF;
                border: none;
                border-radius: 6px;
                padding: 11px;
                font-size: 14px;
                font-weight: bold;
            }

            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0369A1, stop:1 #0284C7);
            }

            QPushButton:pressed {
                background: #075985;
            }
        """)

        self.create_ui()

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
            QPointF(self.width() * 0.35, self.height() - 170),
            QPointF(self.width() * 0.65, self.height() - 50),
            QPointF(self.width(), self.height() - 120)
        )
        wave_path2.lineTo(self.width(), self.height())
        wave_path2.closeSubpath()

        wave_grad2 = QLinearGradient(0, self.height() - 170, self.width(), self.height())
        wave_grad2.setColorAt(0.0, QColor(2, 132, 199, 25))
        wave_grad2.setColorAt(1.0, QColor(186, 230, 253, 60))
        painter.fillPath(wave_path2, wave_grad2)

        painter.end()

    def create_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(40, 20, 40, 30)
        main_layout.setSpacing(10)

        self.logo = get_logo_widget(height=60)
        main_layout.addWidget(self.logo)

        header = QLabel("Class Selection")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)

        header_font = QFont()
        header_font.setPointSize(20)
        header_font.setBold(True)
        header.setFont(header_font)

        main_layout.addWidget(header)

        subtitle = QLabel("Select your class and section to continue")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("""
            color: #0369A1;
            font-size: 13px;
            font-weight: 500;
        """)

        main_layout.addWidget(subtitle)

        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.92);
                border-radius: 12px;
                border: 1px solid #BAE6FD;
            }
        """)

        card_layout = QVBoxLayout()
        card_layout.setContentsMargins(30, 22, 30, 22)
        card_layout.setSpacing(10)

        class_label = QLabel("Class")
        class_label.setStyleSheet("""
            font-size: 13px;
            font-weight: bold;
            color: #0F172A;
            border: none;
        """)

        card_layout.addWidget(class_label)

        self.class_dropdown = QComboBox()

        for i in range(6, 13):
            self.class_dropdown.addItem(f"Class {i}", i)

        self.class_dropdown.currentIndexChanged.connect(
            self.update_sections
        )

        card_layout.addWidget(self.class_dropdown)

        section_label = QLabel("Section")
        section_label.setStyleSheet("""
            font-size: 13px;
            font-weight: bold;
            color: #0F172A;
            border: none;
        """)

        card_layout.addWidget(section_label)

        self.section_dropdown = QComboBox()

        card_layout.addWidget(self.section_dropdown)

        self.continue_button = QPushButton("Continue")
        self.continue_button.clicked.connect(self.continue_selection)

        card_layout.addSpacing(6)
        card_layout.addWidget(self.continue_button)

        self.result_label = QLabel("")
        self.result_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.result_label.setStyleSheet("""
            color: #0284C7;
            font-size: 13px;
            font-weight: bold;
            border: none;
        """)

        card_layout.addWidget(self.result_label)

        card.setLayout(card_layout)

        main_layout.addWidget(card)
        main_layout.addStretch()

        self.setLayout(main_layout)

        self.update_sections()

    def update_sections(self):
        selected_class = self.class_dropdown.currentData()
        self.section_dropdown.clear()

        if selected_class <= 10:
            sections = ["A", "B"]
        else:
            sections = ["A", "B", "C", "D"]

        self.section_dropdown.addItems(sections)

    def continue_selection(self):
        selected_class = self.class_dropdown.currentData()
        selected_section = self.section_dropdown.currentText()

        full_class_name = f"Class {selected_class} {selected_section}"

        subprocess.Popen([sys.executable, "test.py", full_class_name])
        
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = ClassSelection()
    window.show()

    sys.exit(app.exec())
