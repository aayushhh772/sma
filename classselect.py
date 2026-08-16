import sys
import os
import random
import math
import subprocess

from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QComboBox, QPushButton, QVBoxLayout, QFrame, QMessageBox, QListView
)
from PyQt6.QtCore import Qt, QPointF, QTimer, QUrl
from PyQt6.QtGui import QFont, QPainter, QLinearGradient, QRadialGradient, QColor, QPainterPath
from PyQt6.QtMultimedia import QSoundEffect

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ADMIN_PAGE_FILE = os.path.join(BASE_DIR, "adminpage.py")

class FlowParticle:
    def __init__(self, width, height):
        self.reset(width, height, True)

    def reset(self, width, height, random_position=False):
        self.base_radius = random.uniform(8, 26)
        self.radius = self.base_radius
        self.x = random.uniform(self.base_radius, max(width - self.base_radius, self.base_radius + 1))
        if random_position:
            self.y = random.uniform(0, height)
        else:
            self.y = height + self.base_radius + random.uniform(10, 50)
        self.speed = random.uniform(0.25, 0.75)
        self.phase = random.uniform(0, math.pi * 2)
        self.sway = random.uniform(0.3, 0.9)
        self.pulse = random.uniform(0.015, 0.035)
        self.alpha = random.randint(25, 65)

    def update(self, width, height):
        self.y -= self.speed
        self.phase += self.pulse
        self.x += math.sin(self.phase) * self.sway
        self.radius = self.base_radius + math.sin(self.phase * 2) * 2.0
        if self.y < -self.radius * 2:
            self.reset(width, height, False)

class ClassSelection(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SOS Hermann Gmeiner Secondary School Gandaki")
        self.setMinimumSize(900, 600)
        self.resize(1200, 750)
        self.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent, False)

        self.flow_time = 0.0
        self.particles = []
        self.init_particles(30)

        self.ui1_sound = QSoundEffect(self)
        self.ui2_sound = QSoundEffect(self)
        ui1_path = os.path.join(BASE_DIR, "ui1.wav")
        ui2_path = os.path.join(BASE_DIR, "ui2.wav")

        if os.path.exists(ui1_path):
            self.ui1_sound.setSource(QUrl.fromLocalFile(ui1_path))
            self.ui1_sound.setVolume(0.35)

        if os.path.exists(ui2_path):
            self.ui2_sound.setSource(QUrl.fromLocalFile(ui2_path))
            self.ui2_sound.setVolume(0.30)

        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self.update_animation)
        self.animation_timer.start(16)

        self.setStyleSheet("""
            QWidget { background-color: #E0F2FE; }
            QLabel { background: transparent; border: none; }
            QComboBox {
                background-color: #FFFFFF; color: #0F172A; border: 1px solid #BAE6FD;
                border-radius: 11px; padding: 13px 16px; font-size: 16px; min-height: 28px;
            }
            QComboBox:hover { border-color: #0284C7; }
            QComboBox:focus { border: 1px solid #0284C7; }
            QComboBox::drop-down { background: transparent; border: none; width: 36px; }
            QComboBox::down-arrow { width: 10px; height: 10px; }
            QComboBox QAbstractItemView {
                background-color: #FFFFFF; color: #0F172A; selection-background-color: #0284C7;
                selection-color: #FFFFFF; border: 1px solid #BAE6FD; border-radius: 10px;
                padding: 4px; outline: none; margin: 0px; font-size: 16px;
            }
            QComboBox QAbstractItemView::item {
                background-color: #FFFFFF; color: #0F172A; border: none; border-radius: 7px;
                padding: 10px 11px; min-height: 25px;
            }
            QComboBox QAbstractItemView::item:hover { background-color: #E0F2FE; color: #0369A1; }
            QComboBox QAbstractItemView::item:selected { background-color: #0284C7; color: #FFFFFF; }
            QPushButton#continueButton {
                background-color: #0284C7; color: #FFFFFF; border: none; border-radius: 11px;
                padding: 14px; font-size: 16px; font-weight: bold; min-height: 22px;
            }
            QPushButton#continueButton:hover { background-color: #0369A1; }
            QPushButton#continueButton:pressed { background-color: #075985; }
            QPushButton#backButton {
                background: transparent; color: #0284C7; border: 1px solid #BAE6FD;
                border-radius: 11px; padding: 12px; font-size: 15px; font-weight: bold; min-height: 20px;
            }
            QPushButton#backButton:hover { background-color: #F0FAFE; border-color: #0284C7; color: #075985; }
        """)

        self.create_ui()
        QTimer.singleShot(100, self.play_ui1)

    def init_particles(self, count):
        width = max(self.width(), 900)
        height = max(self.height(), 600)
        self.particles = [FlowParticle(width, height) for _ in range(count)]

    def update_animation(self):
        self.flow_time += 0.012
        width = self.width()
        height = self.height()
        for particle in self.particles:
            particle.update(width, height)
        self.update()

    def play_ui1(self):
        if self.ui1_sound.source().isValid():
            self.ui1_sound.stop()
            self.ui1_sound.play()

    def play_ui2(self):
        if self.ui2_sound.source().isValid():
            self.ui2_sound.stop()
            self.ui2_sound.play()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)

        width = self.width()
        height = self.height()

        background = QLinearGradient(0, 0, 0, height)
        background.setColorAt(0.0, QColor("#BFE7F8"))
        background.setColorAt(0.23, QColor("#D8F0FA"))
        background.setColorAt(0.48, QColor("#EEF9FD"))
        background.setColorAt(0.75, QColor("#F5FBFE"))
        background.setColorAt(1.0, QColor("#C9EBF9"))
        painter.fillRect(self.rect(), background)

        center_glow = QRadialGradient(width * 0.5, height * 0.48, max(width, height) * 0.72)
        center_glow.setColorAt(0.0, QColor(255, 255, 255, 130))
        center_glow.setColorAt(0.42, QColor(255, 255, 255, 55))
        center_glow.setColorAt(1.0, QColor(255, 255, 255, 0))
        painter.fillRect(self.rect(), center_glow)

        top_wave = QPainterPath()
        top_wave.moveTo(0, 0)
        top_wave.lineTo(0, 185)
        points = []
        for i in range(5):
            x = width * i / 4
            y = 185 + math.sin(self.flow_time + i * 1.25) * 22
            points.append(QPointF(x, y))

        for i in range(4):
            p0, p1 = points[i], points[i + 1]
            dx = (p1.x() - p0.x()) / 3
            top_wave.cubicTo(QPointF(p0.x() + dx, p0.y()), QPointF(p1.x() - dx, p1.y()), p1)

        top_wave.lineTo(width, 0)
        top_wave.closeSubpath()

        top_gradient = QLinearGradient(0, 0, width, 210)
        top_gradient.setColorAt(0.0, QColor(14, 165, 233, 60))
        top_gradient.setColorAt(0.55, QColor(56, 189, 248, 32))
        top_gradient.setColorAt(1.0, QColor(125, 211, 252, 10))
        painter.fillPath(top_wave, top_gradient)

        bottom_wave = QPainterPath()
        bottom_wave.moveTo(0, height)
        bottom_wave.lineTo(0, height - 105)
        points = []
        for i in range(5):
            x = width * i / 4
            y = height - 105 + math.sin(self.flow_time * 0.75 + i * 1.2) * 20
            points.append(QPointF(x, y))

        for i in range(4):
            p0, p1 = points[i], points[i + 1]
            dx = (p1.x() - p0.x()) / 3
            bottom_wave.cubicTo(QPointF(p0.x() + dx, p0.y()), QPointF(p1.x() - dx, p1.y()), p1)

        bottom_wave.lineTo(width, height)
        bottom_wave.closeSubpath()

        bottom_gradient = QLinearGradient(0, height - 150, width, height)
        bottom_gradient.setColorAt(0.0, QColor(56, 189, 248, 12))
        bottom_gradient.setColorAt(1.0, QColor(14, 165, 233, 55))
        painter.fillPath(bottom_wave, bottom_gradient)

        painter.setPen(Qt.PenStyle.NoPen)
        for particle in self.particles:
            radius = max(particle.radius, 1)
            particle_gradient = QRadialGradient(particle.x, particle.y, radius)
            particle_gradient.setColorAt(0.0, QColor(255, 255, 255, particle.alpha))
            particle_gradient.setColorAt(0.38, QColor(125, 211, 252, int(particle.alpha * 0.65)))
            particle_gradient.setColorAt(0.75, QColor(56, 189, 248, int(particle.alpha * 0.25)))
            particle_gradient.setColorAt(1.0, QColor(56, 189, 248, 0))
            painter.setBrush(particle_gradient)
            painter.drawEllipse(QPointF(particle.x, particle.y), radius, radius)

        painter.end()

    def create_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 28, 40, 30)
        main_layout.setSpacing(0)
        main_layout.addStretch(1)

        title = QLabel("Class Selection")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Segoe UI", 32, QFont.Weight.Bold))
        title.setStyleSheet("QLabel { color: #0369A1; background: transparent; border: none; }")
        main_layout.addWidget(title)

        subtitle = QLabel("Select your class and section to continue")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setFont(QFont("Segoe UI", 19))
        subtitle.setStyleSheet("QLabel { color: #64748B; background: transparent; border: none; }")
        main_layout.addWidget(subtitle)
        main_layout.addSpacing(30)

        card = QFrame()
        card.setFixedWidth(700)
        card.setMinimumHeight(500)
        card.setStyleSheet(
            "QFrame { background-color: rgba(255, 255, 255, 242); border: 1px solid #BAE6FD; border-radius: 24px; }"
        )

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(48, 38, 48, 20)
        card_layout.setSpacing(13)

        class_label = QLabel("Class")
        class_label.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        class_label.setStyleSheet("QLabel { color: #0F172A; background: transparent; border: none; }")
        card_layout.addWidget(class_label)

        self.class_dropdown = QComboBox()
        self.class_dropdown.setView(QListView())
        for i in range(6, 13):
            self.class_dropdown.addItem(f"Class {i}", i)
        self.class_dropdown.activated.connect(self.play_ui2)
        self.class_dropdown.currentIndexChanged.connect(self.update_sections)
        card_layout.addWidget(self.class_dropdown)
        card_layout.addSpacing(10)

        section_label = QLabel("Section")
        section_label.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        section_label.setStyleSheet("QLabel { color: #0F172A; background: transparent; border: none; }")
        card_layout.addWidget(section_label)

        self.section_dropdown = QComboBox()
        self.section_dropdown.setView(QListView())
        self.section_dropdown.activated.connect(self.play_ui2)
        card_layout.addWidget(self.section_dropdown)
        card_layout.addSpacing(18)

        continue_button = QPushButton("Continue")
        continue_button.setObjectName("continueButton")
        continue_button.setCursor(Qt.CursorShape.PointingHandCursor)
        continue_button.clicked.connect(self.continue_selection)
        card_layout.addWidget(continue_button)

        self.result_label = QLabel("")
        self.result_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.result_label.setStyleSheet(
            "QLabel { color: #0284C7; font-size: 14px; font-weight: bold; background: transparent; border: none; }"
        )
        card_layout.addWidget(self.result_label)

        card_layout.addSpacing(12)

        back_button = QPushButton("Back")
        back_button.setObjectName("backButton")
        back_button.setCursor(Qt.CursorShape.PointingHandCursor)
        back_button.clicked.connect(self.go_back)
        card_layout.addWidget(back_button)

        card_layout.addSpacing(6)

        school_footer = QLabel("SOS Hermann Gmeiner School Gandaki")
        school_footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        school_footer.setFont(QFont("Segoe UI", 11))
        school_footer.setStyleSheet("QLabel { color: #94A3B8; background: transparent; border: none; }")
        card_layout.addWidget(school_footer)

        main_layout.addWidget(card, 0, Qt.AlignmentFlag.AlignHCenter)
        main_layout.addSpacing(22)

        self.update_sections()

    def update_sections(self):
        selected_class = self.class_dropdown.currentData()
        self.section_dropdown.blockSignals(True)
        self.section_dropdown.clear()
        sections = ["A", "B"] if selected_class <= 10 else ["A", "B", "C", "D"]
        self.section_dropdown.addItems(sections)
        self.section_dropdown.blockSignals(False)

    def continue_selection(self):
        selected_class = self.class_dropdown.currentData()
        selected_section = self.section_dropdown.currentText()
        full_class_name = f"Class {selected_class} {selected_section}"
        test_file = os.path.join(BASE_DIR, "test.py")

        if not os.path.exists(test_file):
            QMessageBox.critical(self, "File Not Found", "test.py was not found.")
            return

        self.result_label.setText(full_class_name)
        self.play_ui1()
        QTimer.singleShot(350, lambda: self.open_test_file(test_file, full_class_name))

    def open_test_file(self, test_file, full_class_name):
        try:
            subprocess.Popen([sys.executable, test_file, full_class_name], cwd=BASE_DIR)
            self.close()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not open test.py:\n\n{e}")

    def go_back(self):
        if not os.path.exists(ADMIN_PAGE_FILE):
            QMessageBox.critical(self, "File Not Found", "adminpage.py was not found.")
            return
        try:
            subprocess.Popen([sys.executable, ADMIN_PAGE_FILE], cwd=BASE_DIR)
            self.close()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not return to the Admin Portal:\n\n{e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = ClassSelection()
    window.show()
    sys.exit(app.exec())
