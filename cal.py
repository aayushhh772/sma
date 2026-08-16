import sys
import os
import calendar
import random
import math
import subprocess
from datetime import datetime

from PyQt6.QtCore import Qt, QPointF, QTimer
from PyQt6.QtGui import QFont, QPixmap, QPainter, QLinearGradient, QRadialGradient, QColor, QPainterPath
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
    QGridLayout, QLabel, QPushButton, QFrame
)


def get_logo_widget(height=90):
    logo_label = QLabel()
    logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    logo_names = [
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


class CalendarCell(QLabel):
    def __init__(self, text="", bg_color="rgba(255, 255, 255, 0.92)", text_color="#0F172A", border_color="#BAE6FD", font_size=15):
        super().__init__(text)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet(f"""
            QLabel {{
                background-color: {bg_color};
                color: {text_color};
                border: 1px solid {border_color};
                border-radius: 6px;
                font-weight: bold;
                font-size: {font_size}px;
            }}
        """)


class CalendarWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.year = datetime.now().year
        self.month = datetime.now().month
        
        self.setWindowTitle("SOS Hermann Gmeiner Secondary School Gandaki")
        self.resize(780, 620)

        # Wave and Particle Animation parameters
        self.flow_time = 0.0
        self.particles = []
        self.init_particles(32)

        # 60 FPS Animation Timer (~16ms)
        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self.update_animation)
        self.animation_timer.start(16)

        self.setStyleSheet("""
            QLabel {
                color: #0F172A;
                background: transparent;
            }
        """)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(15, 10, 15, 12)
        self.main_layout.setSpacing(6)

        top_bar = QHBoxLayout()
        top_bar.setContentsMargins(0, 0, 0, 0)
        
        self.logo = get_logo_widget(height=90)
        top_bar.addWidget(self.logo, alignment=Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addLayout(top_bar)

        self.card_frame = QFrame()
        self.card_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.90);
                border: 1px solid #BAE6FD;
                border-radius: 12px;
            }
        """)
        
        self.card_layout = QVBoxLayout(self.card_frame)
        self.card_layout.setContentsMargins(12, 10, 12, 10)
        self.card_layout.setSpacing(6)

        self.main_layout.addWidget(self.card_frame, stretch=1)
        
        self.show_calendar()

    def init_particles(self, count):
        w = max(self.width(), 780)
        h = max(self.height(), 620)
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
        
        steps = 30
        for i in range(steps + 1):
            x = (w / steps) * i
            y = 120 + math.sin(self.flow_time + (x / w) * 2 * math.pi) * 30 + math.cos(self.flow_time * 0.5) * 12
            wave_top_1.lineTo(x, y)
            
        wave_top_1.lineTo(w, 0)
        wave_top_1.closeSubpath()

        top_grad_1 = QLinearGradient(0, 0, w, 180)
        top_grad_1.setColorAt(0.0, QColor(2, 132, 199, 45))
        top_grad_1.setColorAt(1.0, QColor(56, 189, 248, 15))
        painter.fillPath(wave_top_1, top_grad_1)

        wave_top_2 = QPainterPath()
        wave_top_2.moveTo(0, 0)
        for i in range(steps + 1):
            x = (w / steps) * i
            y = 95 + math.cos(self.flow_time * 1.2 + (x / w) * 1.5 * math.pi) * 22
            wave_top_2.lineTo(x, y)
            
        wave_top_2.lineTo(w, 0)
        wave_top_2.closeSubpath()

        top_grad_2 = QLinearGradient(0, 0, w, 140)
        top_grad_2.setColorAt(0.0, QColor(56, 189, 248, 30))
        top_grad_2.setColorAt(1.0, QColor(186, 230, 253, 40))
        painter.fillPath(wave_top_2, top_grad_2)

        # 3. Dynamic Bottom Cresting Waves
        wave_bot_1 = QPainterPath()
        wave_bot_1.moveTo(0, h)
        for i in range(steps + 1):
            x = (w / steps) * i
            y = h - 110 + math.sin(self.flow_time * 0.9 + (x / w) * 2 * math.pi) * 25
            wave_bot_1.lineTo(x, y)
            
        wave_bot_1.lineTo(w, h)
        wave_bot_1.closeSubpath()

        bot_grad_1 = QLinearGradient(0, h - 150, w, h)
        bot_grad_1.setColorAt(0.0, QColor(2, 132, 199, 35))
        bot_grad_1.setColorAt(1.0, QColor(186, 230, 253, 65))
        painter.fillPath(wave_bot_1, bot_grad_1)

        # 4. Floating Soft-Orb Particles
        painter.setPen(Qt.PenStyle.NoPen)
        for p in self.particles:
            rad_grad = QRadialGradient(p.x, p.y, p.radius)
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

    def go_to_test(self):
        subprocess.Popen([sys.executable, 'test.py'])
        QApplication.quit()

    def show_calendar(self):
        while self.card_layout.count():
            child = self.card_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        title_container = QWidget()
        title_container.setStyleSheet("background: transparent; border: none;")
        title_layout = QHBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 0)

        title_text = f"{calendar.month_name[self.month]} {self.year}"
        title_label = QLabel(title_text)
        title_label.setFixedHeight(48)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0284C7, stop:1 #0369A1);
                color: #FFFFFF;
                border: none;
                border-radius: 8px;
                font-size: 20px;
                font-weight: bold;
            }
        """)

        back_button = QPushButton("<--", title_label)
        back_button.setGeometry(10, 7, 65, 34)
        back_button.setCursor(Qt.CursorShape.PointingHandCursor)
        back_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.2);
                color: #FFFFFF;
                border: 1px solid rgba(255, 255, 255, 0.4);
                font-size: 14px;
                font-weight: bold;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.35);
            }
            QPushButton:pressed {
                background-color: rgba(0, 0, 0, 0.15);
            }
        """)
        back_button.clicked.connect(self.go_to_test)

        title_layout.addWidget(title_label)
        self.card_layout.addWidget(title_container)

        grid_layout = QGridLayout()
        grid_layout.setSpacing(4)

        weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        for col, day in enumerate(weekdays):
            header_cell = CalendarCell(
                text=day,
                bg_color="#E0F2FE",
                text_color="#0369A1",
                border_color="#BAE6FD",
                font_size=13
            )
            grid_layout.addWidget(header_cell, 0, col)

        month_matrix = calendar.monthcalendar(self.year, self.month)
        while len(month_matrix) < 6:
            month_matrix.append([0] * 7)

        today = datetime.now()
        current_year, current_month, current_day = today.year, today.month, today.day

        for row_idx, week in enumerate(month_matrix, start=1):
            grid_layout.setRowStretch(row_idx, 1)
            for col_idx, day in enumerate(week):
                if day == 0:
                    cell = CalendarCell(
                        text="",
                        bg_color="rgba(241, 245, 249, 0.5)",
                        text_color="#94A3B8",
                        border_color="#E2E8F0"
                    )
                elif self.year == current_year and self.month == current_month and day == current_day:
                    cell = CalendarCell(
                        text=str(day),
                        bg_color="#0284C7",
                        text_color="#FFFFFF",
                        border_color="#0369A1",
                        font_size=17
                    )
                elif col_idx >= 5:
                    cell = CalendarCell(
                        text=str(day),
                        bg_color="#FEF2F2",
                        text_color="#E11D48",
                        border_color="#FECDD3",
                        font_size=17
                    )
                else:
                    cell = CalendarCell(
                        text=str(day),
                        bg_color="#FFFFFF",
                        text_color="#0F172A",
                        border_color="#BAE6FD",
                        font_size=17
                    )

                grid_layout.addWidget(cell, row_idx, col_idx)

        for c in range(7):
            grid_layout.setColumnStretch(c, 1)

        self.card_layout.addLayout(grid_layout, stretch=1)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CalendarWidget()
    window.show()
    sys.exit(app.exec())
