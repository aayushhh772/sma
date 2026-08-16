import sys
import os
import random
import math
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
from PyQt6.QtCore import Qt, QPointF, QTimer
from PyQt6.QtGui import QFont, QPixmap, QPainter, QLinearGradient, QRadialGradient, QColor, QPainterPath


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


class FlowParticle:
    """Soft glowing particle with pulsing radius and gentle horizontal drift."""
    def __init__(self, bounds_width, bounds_height):
        self.reset(bounds_width, bounds_height, random_y=True)

    def reset(self, bounds_width, bounds_height, random_y=False):
        self.base_radius = random.uniform(8, 28)
        self.radius = self.base_radius
        self.x = random.uniform(self.base_radius, max(bounds_width - self.base_radius, self.base_radius + 1))
        self.y = random.uniform(0, bounds_height) if random_y else bounds_height + self.base_radius + random.uniform(0, 40)
        self.speed = random.uniform(0.3, 0.9)
        self.sway_speed = random.uniform(0.015, 0.04)
        self.pulse_speed = random.uniform(0.02, 0.06)
        self.pulse_amplitude = random.uniform(1.5, 4.0)
        self.alpha = random.randint(25, 75)
        self.phase = random.uniform(0, 2 * math.pi)

    def update(self, bounds_width, bounds_height):
        self.y -= self.speed
        self.phase += self.sway_speed
        self.x += math.sin(self.phase) * 0.8
        self.radius = self.base_radius + math.sin(self.phase * 2) * self.pulse_amplitude
        
        if self.y < -self.base_radius * 2:
            self.reset(bounds_width, bounds_height, random_y=False)


class ClassSelection(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("SOS Hermann Gmeiner School Gandaki")
        self.setFixedSize(650, 520)

        # Wave and Particle Animation parameters
        self.flow_time = 0.0
        self.particles = []
        self.init_particles(28)

        # 60 FPS Animation Timer (~16ms)
        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self.update_animation)
        self.animation_timer.start(16)

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

    def init_particles(self, count):
        w = max(self.width(), 650)
        h = max(self.height(), 520)
        self.particles = [FlowParticle(w, h) for _ in range(count)]

    def update_animation(self):
        self.flow_time += 0.025
        if self.flow_time > 2 * math.pi * 100:
            self.flow_time = 0.0
            
        w = self.width()
        h = self.height()
        for p in self.particles:
            p.update(w, h)
            
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()

        # 1. Soft Background Gradient
        gradient = QLinearGradient(0, 0, 0, h)
        gradient.setColorAt(0.0, QColor("#E0F2FE"))
        gradient.setColorAt(0.35, QColor("#F0F9FF"))
        gradient.setColorAt(0.70, QColor("#F8FAFC"))
        gradient.setColorAt(1.0, QColor("#E0F2FE"))
        painter.fillRect(self.rect(), gradient)

        # 2. Dynamic Top Overlapping Waves (Triple Sine Layering)
        wave_top_1 = QPainterPath()
        wave_top_1.moveTo(0, 0)
        
        # Build smooth multi-segment wave curve across the screen width
        steps = 30
        for i in range(steps + 1):
            x = (w / steps) * i
            y = 100 + math.sin(self.flow_time + (x / w) * 2 * math.pi) * 25 + math.cos(self.flow_time * 0.5) * 10
            wave_top_1.lineTo(x, y)
            
        wave_top_1.lineTo(w, 0)
        wave_top_1.closeSubpath()

        top_grad_1 = QLinearGradient(0, 0, w, 150)
        top_grad_1.setColorAt(0.0, QColor(2, 132, 199, 45))
        top_grad_1.setColorAt(1.0, QColor(56, 189, 248, 15))
        painter.fillPath(wave_top_1, top_grad_1)

        wave_top_2 = QPainterPath()
        wave_top_2.moveTo(0, 0)
        for i in range(steps + 1):
            x = (w / steps) * i
            y = 80 + math.cos(self.flow_time * 1.2 + (x / w) * 1.5 * math.pi) * 20
            wave_top_2.lineTo(x, y)
            
        wave_top_2.lineTo(w, 0)
        wave_top_2.closeSubpath()

        top_grad_2 = QLinearGradient(0, 0, w, 130)
        top_grad_2.setColorAt(0.0, QColor(56, 189, 248, 30))
        top_grad_2.setColorAt(1.0, QColor(186, 230, 253, 40))
        painter.fillPath(wave_top_2, top_grad_2)

        # 3. Dynamic Bottom Cresting Waves
        wave_bot_1 = QPainterPath()
        wave_bot_1.moveTo(0, h)
        for i in range(steps + 1):
            x = (w / steps) * i
            y = h - 100 + math.sin(self.flow_time * 0.9 + (x / w) * 2 * math.pi) * 20
            wave_bot_1.lineTo(x, y)
            
        wave_bot_1.lineTo(w, h)
        wave_bot_1.closeSubpath()

        bot_grad_1 = QLinearGradient(0, h - 140, w, h)
        bot_grad_1.setColorAt(0.0, QColor(2, 132, 199, 35))
        bot_grad_1.setColorAt(1.0, QColor(186, 230, 253, 65))
        painter.fillPath(wave_bot_1, bot_grad_1)

        # 4. Floating Soft-Orb Particles
        painter.setPen(Qt.PenStyle.NoPen)
        for p in self.particles:
            rad_grad = QRadialGradient(p.x, p.y, p.radius)
            # Glowing core to transparent edge
            rad_grad.setColorAt(0.0, QColor(224, 242, 254, p.alpha))
            rad_grad.setColorAt(0.4, QColor(56, 189, 248, int(p.alpha * 0.7)))
            rad_grad.setColorAt(0.85, QColor(2, 132, 199, int(p.alpha * 0.2)))
            rad_grad.setColorAt(1.0, QColor(2, 132, 199, 0))
            
            painter.setBrush(rad_grad)
            painter.drawEllipse(
                QPointF(p.x, p.y), 
                p.radius, 
                p.radius
            )

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
