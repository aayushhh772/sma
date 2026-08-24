import sys
import os
import json
import math
import random
import pygame
import subprocess
from PyQt6.QtWidgets import (
    QApplication, QWidget, QStackedWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QFrame, QMessageBox, QPushButton
)
from PyQt6.QtCore import Qt, QTimer, QElapsedTimer, pyqtProperty, QDateTime
from PyQt6.QtGui import QFont, QPainter, QLinearGradient, QRadialGradient, QColor, QPainterPath, QPixmap

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KEYBOARD_SOUND = os.path.join(BASE_DIR, "keyboard.mp3")
UI_SOUND = os.path.join(BASE_DIR, "ui.wav")
UI1_SOUND = os.path.join(BASE_DIR, "ui1.wav")
LOGO_FILE = os.path.join(BASE_DIR, "logo.jpg")
CREDENTIALS_FILE = os.path.join(BASE_DIR, "admin_credentials.json")

pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=512)
try:
    pygame.mixer.init()
    AUDIO_READY = True
except Exception:
    AUDIO_READY = False

keyboard_sound = None
ui_sound = None
ui1_sound = None

if AUDIO_READY:
    try:
        if os.path.exists(KEYBOARD_SOUND):
            keyboard_sound = pygame.mixer.Sound(KEYBOARD_SOUND)
    except Exception:
        pass
    try:
        if os.path.exists(UI_SOUND):
            ui_sound = pygame.mixer.Sound(UI_SOUND)
    except Exception:
        pass
    try:
        if os.path.exists(UI1_SOUND):
            ui1_sound = pygame.mixer.Sound(UI1_SOUND)
    except Exception:
        pass

def play_click_sound():
    if not AUDIO_READY or ui1_sound is None:
        return
    try:
        channel = pygame.mixer.find_channel(True)
        if channel:
            channel.set_volume(0.30)
            channel.play(ui1_sound)
    except Exception:
        pass

class Bubble:
    def __init__(self, width, height):
        self.reset(width, height, True)

    def reset(self, width, height, random_position=False):
        self.radius = random.uniform(5, 24)
        self.x = random.uniform(0, max(width, 1))
        if random_position:
            self.y = random.uniform(0, max(height, 1))
        else:
            self.y = height + self.radius + 20
        self.speed = random.uniform(0.18, 0.55)
        self.phase = random.uniform(0, math.pi * 2)
        self.wobble = random.uniform(0.15, 0.55)
        self.alpha = random.randint(22, 65)

    def update(self, width, height):
        self.y -= self.speed
        self.phase += 0.018
        self.x += math.sin(self.phase) * self.wobble
        if self.y < -self.radius * 2:
            self.reset(width, height, False)

class AnimatedBackground(QWidget):
    def __init__(self, intensity=1.0):
        super().__init__()
        self.intensity = intensity
        self.phase = 0.0
        bubble_count = int(55 * intensity)
        self.bubbles = [Bubble(1400, 900) for _ in range(bubble_count)]
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate)
        self.timer.start(16)

    def animate(self):
        self.phase += 0.010
        for bubble in self.bubbles:
            bubble.update(self.width(), self.height())
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        width = self.width()
        height = self.height()
        background = QLinearGradient(0, 0, 0, height)
        background.setColorAt(0.0, QColor(168, 221, 245))
        background.setColorAt(0.20, QColor(203, 237, 250))
        background.setColorAt(0.48, QColor(235, 248, 253))
        background.setColorAt(0.78, QColor(242, 250, 253))
        background.setColorAt(1.0, QColor(184, 229, 248))
        painter.fillRect(self.rect(), background)

        glow = QRadialGradient(width * 0.5, height * 0.45, width * 0.70)
        glow.setColorAt(0.0, QColor(255, 255, 255, int(145 * self.intensity)))
        glow.setColorAt(0.45, QColor(255, 255, 255, int(60 * self.intensity)))
        glow.setColorAt(1.0, QColor(255, 255, 255, 0))
        painter.fillRect(self.rect(), glow)

        top_wave = QPainterPath()
        top_wave.moveTo(0, 0)
        top_wave.lineTo(0, 175)
        top_wave.cubicTo(
            width * 0.18, 215 + math.sin(self.phase) * 10,
            width * 0.43, 125 + math.cos(self.phase) * 12,
            width * 0.68, 155 + math.sin(self.phase + 1) * 10
        )
        top_wave.cubicTo(
            width * 0.83, 175 + math.cos(self.phase) * 10,
            width * 0.92, 145 + math.sin(self.phase + 8),
            width, 180
        )
        top_wave.lineTo(width, 0)
        top_wave.closeSubpath()

        top_gradient = QLinearGradient(0, 0, width, 200)
        top_gradient.setColorAt(0.0, QColor(14, 165, 233, int(65 * self.intensity)))
        top_gradient.setColorAt(0.5, QColor(56, 189, 248, int(42 * self.intensity)))
        top_gradient.setColorAt(1.0, QColor(125, 211, 252, int(18 * self.intensity)))
        painter.fillPath(top_wave, top_gradient)

        center_glow = QRadialGradient(width * 0.5, height * 0.56, min(width, height) * 0.45)
        center_glow.setColorAt(0.0, QColor(186, 230, 253, int(42 * self.intensity)))
        center_glow.setColorAt(0.45, QColor(186, 230, 253, int(22 * self.intensity)))
        center_glow.setColorAt(1.0, QColor(186, 230, 253, 0))
        painter.fillRect(self.rect(), center_glow)

        bottom_wave = QPainterPath()
        bottom_wave.moveTo(0, height)
        bottom_wave.lineTo(0, height - 105)
        bottom_wave.cubicTo(
            width * 0.20, height - 145,
            width * 0.43, height - 65,
            width * 0.67, height - 100
        )
        bottom_wave.cubicTo(
            width * 0.83, height - 125,
            width * 0.93, height - 80,
            width, height - 110
        )
        bottom_wave.lineTo(width, height)
        bottom_wave.closeSubpath()

        bottom_gradient = QLinearGradient(0, height - 160, width, height)
        bottom_gradient.setColorAt(0.0, QColor(56, 189, 248, int(18 * self.intensity)))
        bottom_gradient.setColorAt(1.0, QColor(14, 165, 233, int(55 * self.intensity)))
        painter.fillPath(bottom_wave, bottom_gradient)

        painter.setPen(Qt.PenStyle.NoPen)
        for bubble in self.bubbles:
            gradient = QRadialGradient(bubble.x, bubble.y, bubble.radius)
            alpha = int(bubble.alpha * self.intensity)
            gradient.setColorAt(0.0, QColor(255, 255, 255, int(alpha * 0.9)))
            gradient.setColorAt(0.35, QColor(125, 211, 252, int(alpha * 0.75)))
            gradient.setColorAt(0.75, QColor(56, 189, 248, int(alpha * 0.30)))
            gradient.setColorAt(1.0, QColor(56, 189, 248, 0))
            painter.setBrush(gradient)
            painter.drawEllipse(
                int(bubble.x - bubble.radius),
                int(bubble.y - bubble.radius),
                int(bubble.radius * 2),
                int(bubble.radius * 2)
            )
        painter.end()

class RoundedLogo(QLabel):
    def __init__(self, width=135, height=135, radius=22, parent=None):
        super().__init__(parent)
        self.logo_width = width
        self.logo_height = height
        self.radius = radius
        self.setFixedSize(width, height)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet("background: transparent; border: none;")
        self.set_logo()

    def set_logo(self):
        if not os.path.exists(LOGO_FILE):
            return
        pixmap = QPixmap(LOGO_FILE)
        if pixmap.isNull():
            return
        scaled = pixmap.scaled(
            self.logo_width, self.logo_height,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        rounded = QPixmap(scaled.size())
        rounded.fill(Qt.GlobalColor.transparent)
        painter = QPainter(rounded)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        path = QPainterPath()
        path.addRoundedRect(0, 0, scaled.width(), scaled.height(), self.radius, self.radius)
        painter.setClipPath(path)
        painter.drawPixmap(0, 0, scaled)
        painter.end()
        self.setPixmap(rounded)

class HoverButton(QWidget):
    def __init__(self, title, subtitle, parent=None):
        super().__init__(parent)
        self.title = title
        self.subtitle = subtitle
        self.hover_progress = 0.0
        self.hovered = False
        self.normal_width = 350
        self.normal_height = 115
        self.hover_width = 380
        self.hover_height = 125
        self.setFixedSize(self.hover_width, self.hover_height)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.animation = QTimer(self)
        self.animation.setInterval(10)
        self.animation.timeout.connect(self.animate_hover)
        self.hover_channel = None
        self.hover_timer = None
        self.hover_elapsed = None

    def get_hover_progress(self):
        return self.hover_progress

    def set_hover_progress(self, value):
        self.hover_progress = value
        self.update()

    hoverProgress = pyqtProperty(float, fget=get_hover_progress, fset=set_hover_progress)

    def animate_hover(self):
        target = 1.0 if self.hovered else 0.0
        difference = target - self.hover_progress
        if abs(difference) < 0.008:
            self.hover_progress = target
            self.animation.stop()
        else:
            self.hover_progress += difference * 0.18
            self.update()

    def enterEvent(self, event):
        self.hovered = True
        self.animation.start()
        self.start_hover_sound()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.hovered = False
        self.animation.start()
        self.stop_hover_sound()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            play_click_sound()
            parent = self.parent()
            while parent is not None:
                if hasattr(parent, "button_clicked"):
                    parent.button_clicked(self.title)
                    break
                parent = parent.parent()
        super().mousePressEvent(event)

    def start_hover_sound(self):
        self.stop_hover_sound()
        if not AUDIO_READY or ui_sound is None:
            return
        try:
            self.hover_channel = pygame.mixer.find_channel(True)
            if self.hover_channel:
                self.hover_channel.set_volume(0.16)
                self.hover_channel.play(ui_sound)
                self.hover_elapsed = QElapsedTimer()
                self.hover_elapsed.start()
                self.hover_timer = QTimer(self)
                self.hover_timer.timeout.connect(self.update_hover_sound)
                self.hover_timer.start(10)
        except Exception:
            pass

    def update_hover_sound(self):
        if self.hover_channel is None or self.hover_elapsed is None:
            return
        elapsed = self.hover_elapsed.elapsed()
        if elapsed < 800:
            self.hover_channel.set_volume(0.16)
        elif elapsed < 1000:
            progress = (elapsed - 800) / 200
            self.hover_channel.set_volume(0.16 * (1.0 - progress))
        else:
            self.stop_hover_sound()

    def stop_hover_sound(self):
        if self.hover_timer:
            self.hover_timer.stop()
            self.hover_timer.deleteLater()
            self.hover_timer = None
        if self.hover_channel:
            self.hover_channel.stop()
            self.hover_channel.set_volume(0.0)
            self.hover_channel = None
            self.hover_elapsed = None

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        progress = self.hover_progress
        current_width = self.normal_width + (self.hover_width - self.normal_width) * progress
        current_height = self.normal_height + (self.hover_height - self.normal_height) * progress
        x = (self.width() - current_width) / 2
        y = (self.height() - current_height) / 2
        if progress > 0.01:
            background = QColor(7, 89, 133, 255)
            border = QColor(7, 89, 133, 255)
            title_color = QColor(255, 255, 255)
            subtitle_color = QColor(220, 239, 248)
        else:
            background = QColor(255, 255, 255, 242)
            border = QColor(186, 230, 253, 255)
            title_color = QColor(3, 105, 161)
            subtitle_color = QColor(100, 116, 139)

        path = QPainterPath()
        path.addRoundedRect(x, y, current_width, current_height, 18, 18)
        painter.fillPath(path, background)
        painter.setPen(border)
        painter.drawPath(path)
        painter.setFont(QFont("Segoe UI", 17, QFont.Weight.DemiBold))
        painter.setPen(title_color)
        painter.drawText(int(x), int(y + 28), int(current_width), 35, Qt.AlignmentFlag.AlignCenter, self.title)
        painter.setFont(QFont("Segoe UI", 11))
        painter.setPen(subtitle_color)
        painter.drawText(int(x), int(y + 68), int(current_width), 25, Qt.AlignmentFlag.AlignCenter, self.subtitle)
        painter.end()

class SelectionPage(AnimatedBackground):
    def __init__(self, controller):
        super().__init__(intensity=1.0)
        self.controller = controller
        self.typing_text = "Admin Management Portal"
        self.typing_timer = None
        self.typing_elapsed = None
        self.keyboard_channel = None
        self.keyboard_timer = None
        self.keyboard_elapsed = None
        self.setup_ui()
        QTimer.singleShot(1000, self.start_typing)

    def setup_ui(self):
        main = QVBoxLayout(self)
        main.setContentsMargins(50, 15, 50, 30)
        main.setSpacing(0)

        header_layout = QHBoxLayout()
        header_layout.addStretch()
        self.time_label = QLabel()
        self.time_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        self.time_label.setStyleSheet("color: #0369A1; background: transparent; border: none;")
        header_layout.addWidget(self.time_label)
        main.addLayout(header_layout)

        self.time_timer = QTimer(self)
        self.time_timer.timeout.connect(self.update_live_time)
        self.time_timer.start(1000)
        self.update_live_time()

        main.addStretch(1)
        logo = RoundedLogo(135, 135, 22)
        main.addWidget(logo, 0, Qt.AlignmentFlag.AlignCenter)
        main.addSpacing(18)

        title = QLabel("SOS Hermann Gmeiner School Gandaki")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Segoe UI", 27, QFont.Weight.Bold))
        title.setStyleSheet("QLabel { color: #0369A1; background: transparent; border: none; }")
        main.addWidget(title)

        self.subtitle = QLabel()
        self.subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.subtitle.setFixedHeight(40)
        self.subtitle.setFont(QFont("Segoe UI", 17))
        self.subtitle.setStyleSheet("QLabel { color: #64748B; background: transparent; border: none; }")
        main.addWidget(self.subtitle)
        main.addSpacing(28)

        button_area = QWidget()
        button_area.setMaximumWidth(420)
        button_layout = QHBoxLayout(button_area)
        button_layout.setContentsMargins(0, 0, 0, 0)

        self.admin_button = HoverButton("Admin Portal", "Login Required")
        button_layout.addWidget(self.admin_button)

        main.addWidget(button_area, 0, Qt.AlignmentFlag.AlignCenter)
        main.addSpacing(45)

        info = QLabel("Select portal to continue")
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info.setFont(QFont("Segoe UI", 10))
        info.setStyleSheet("QLabel { color: #94A3B8; background: transparent; border: none; }")
        main.addWidget(info)
        main.addStretch(1)

    def update_live_time(self):
        current_str = QDateTime.currentDateTime().toString("ddd MMM d, h:mm A")
        self.time_label.setText(f"🕒 {current_str}")

    def button_clicked(self, title):
        if title == "Admin Portal":
            self.controller.open_admin_login()

    def start_typing(self):
        self.typing_elapsed = QElapsedTimer()
        self.typing_elapsed.start()
        self.typing_timer = QTimer(self)
        self.typing_timer.timeout.connect(self.update_typing)
        self.typing_timer.start(16)
        self.start_keyboard_sound()

    def update_typing(self):
        elapsed = min(self.typing_elapsed.elapsed(), 1500)
        count = int(len(self.typing_text) * elapsed / 1500)
        self.subtitle.setText(self.typing_text[:count])
        if elapsed >= 1500:
            self.subtitle.setText(self.typing_text)
            self.typing_timer.stop()

    def start_keyboard_sound(self):
        if not AUDIO_READY or keyboard_sound is None:
            return
        try:
            self.keyboard_channel = pygame.mixer.find_channel(True)
            if self.keyboard_channel:
                self.keyboard_channel.set_volume(0.65)
                self.keyboard_channel.play(keyboard_sound)
                self.keyboard_elapsed = QElapsedTimer()
                self.keyboard_elapsed.start()
                self.keyboard_timer = QTimer(self)
                self.keyboard_timer.timeout.connect(self.update_keyboard_sound)
                self.keyboard_timer.start(10)
        except Exception:
            pass

    def update_keyboard_sound(self):
        if self.keyboard_channel is None:
            return
        elapsed = self.keyboard_elapsed.elapsed()
        if elapsed < 1250:
            self.keyboard_channel.set_volume(0.65)
        elif elapsed < 1500:
            progress = (elapsed - 1250) / 250
            self.keyboard_channel.set_volume(0.65 * (1.0 - progress))
        else:
            self.keyboard_channel.stop()
            self.keyboard_channel.set_volume(0.0)
            if self.keyboard_timer:
                self.keyboard_timer.stop()

class AdminLoginPage(AnimatedBackground):
    def __init__(self, controller):
        super().__init__(intensity=0.55)
        self.controller = controller
        self.setup_ui()

    def setup_ui(self):
        main = QVBoxLayout(self)
        main.setContentsMargins(50, 15, 50, 25)
        main.setSpacing(0)

        header_layout = QHBoxLayout()
        header_layout.addStretch()
        self.time_label = QLabel()
        self.time_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        self.time_label.setStyleSheet("color: #0369A1; background: transparent; border: none;")
        header_layout.addWidget(self.time_label)
        main.addLayout(header_layout)

        self.time_timer = QTimer(self)
        self.time_timer.timeout.connect(self.update_live_time)
        self.time_timer.start(1000)
        self.update_live_time()

        main.addStretch(1)

        title = QLabel("Admin Portal")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Segoe UI", 32, QFont.Weight.Bold))
        title.setStyleSheet("QLabel { color: #0369A1; background: transparent; border: none; }")
        main.addWidget(title)

        subtitle = QLabel("Enter your credentials to continue")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setFont(QFont("Segoe UI", 15))
        subtitle.setStyleSheet("QLabel { color: #64748B; background: transparent; border: none; }")
        main.addWidget(subtitle)
        main.addSpacing(15)

        card = QFrame()
        card.setFixedWidth(700)
        card.setStyleSheet(
            "QFrame { background-color: rgba(255, 255, 255, 242); border: 1px solid #BAE6FD; border-radius: 22px; }"
        )
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(50, 20, 50, 20)
        card_layout.setSpacing(6)

        username_label = QLabel("Admin ID")
        username_label.setFont(QFont("Segoe UI", 11, QFont.Weight.DemiBold))
        username_label.setStyleSheet("QLabel { color: #0F172A; background: transparent; border: none; }")
        card_layout.addWidget(username_label)

        self.username = QLineEdit()
        self.username.setPlaceholderText("Enter your Admin ID")
        self.username.setFixedHeight(45)
        self.username.setStyleSheet(self.input_style())
        self.username.returnPressed.connect(self.login)
        card_layout.addWidget(self.username)
        card_layout.addSpacing(2)

        password_label = QLabel("Password")
        password_label.setFont(QFont("Segoe UI", 11, QFont.Weight.DemiBold))
        password_label.setStyleSheet("QLabel { color: #0F172A; background: transparent; border: none; }")
        card_layout.addWidget(password_label)

        self.password = QLineEdit()
        self.password.setPlaceholderText("Enter your password")
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        self.password.setFixedHeight(45)
        self.password.setStyleSheet(self.input_style())
        self.password.returnPressed.connect(self.login)
        card_layout.addWidget(self.password)
        card_layout.addSpacing(8)

        login = QPushButton("Login")
        login.setCursor(Qt.CursorShape.PointingHandCursor)
        login.setFixedHeight(44)
        login.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        login.setStyleSheet(
            "QPushButton { background-color: #0284C7; color: white; border: none; border-radius: 10px; padding: 8px; }"
            "QPushButton:hover { background-color: #0369A1; }"
            "QPushButton:pressed { background-color: #075985; }"
        )
        login.clicked.connect(self.login)
        card_layout.addWidget(login)

        forgot_pwd = QPushButton("Forgot password?")
        forgot_pwd.setCursor(Qt.CursorShape.PointingHandCursor)
        forgot_pwd.setFixedHeight(28)
        forgot_pwd.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        forgot_pwd.setStyleSheet(
            "QPushButton { background-color: transparent; color: #E11D48; border: none; }"
            "QPushButton:hover { color: #BE123C; text-decoration: underline; }"
        )
        forgot_pwd.clicked.connect(self.forgot_password)
        card_layout.addWidget(forgot_pwd)

        back = QPushButton("Back")
        back.setCursor(Qt.CursorShape.PointingHandCursor)
        back.setFixedHeight(38)
        back.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        back.setStyleSheet(
            "QPushButton { background-color: transparent; color: #0284C7; border: 1px solid #BAE6FD; border-radius: 9px; padding: 4px; }"
            "QPushButton:hover { background-color: #F0F9FF; border: 1px solid #0284C7; color: #0369A1; }"
            "QPushButton:pressed { background-color: #E0F2FE; }"
        )
        back.clicked.connect(self.controller.show_selection)
        card_layout.addWidget(back)

        main.addWidget(card, 0, Qt.AlignmentFlag.AlignCenter)
        main.addSpacing(15)

        school_name = QLabel("SOS Hermann Gmeiner School Gandaki")
        school_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        school_name.setFont(QFont("Segoe UI", 10))
        school_name.setStyleSheet("QLabel { color: #94A3B8; background: transparent; border: none; }")
        main.addWidget(school_name, 0, Qt.AlignmentFlag.AlignCenter)
        main.addStretch(1)

    def update_live_time(self):
        current_str = QDateTime.currentDateTime().toString("ddd MMM d, h:mm A")
        self.time_label.setText(f"🕒 {current_str}")

    def input_style(self):
        return (
            "QLineEdit { background-color: white; color: #0F172A; border: 1px solid #BAE6FD; "
            "border-radius: 10px; padding-left: 16px; padding-right: 16px; font-size: 15px; } "
            "QLineEdit:focus { border: 2px solid #0284C7; background-color: #FFFFFF; }"
        )

    def forgot_password(self):
        play_click_sound()
        QMessageBox.information(self, "Forgot Password", "CONTACT THE DEVELOPERS !!!")

    def validate_credentials(self, entered_id, entered_password):
        if entered_id == "SOSADMIN1" and entered_password == "ADMIN404":
            return True

        if os.path.exists(CREDENTIALS_FILE):
            try:
                with open(CREDENTIALS_FILE, "r") as f:
                    creds = json.load(f)
                    custom_id = creds.get("admin_id")
                    custom_pass = creds.get("password")
                    if entered_id == custom_id and entered_password == custom_pass:
                        return True
            except Exception as e:
                print(f"Error reading credentials file: {e}")

        return False

    def login(self):
        username = self.username.text().strip()
        password = self.password.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "Login Error", "Please enter both Admin ID and Password.")
            return

        if self.validate_credentials(username, password):
            play_click_sound()
            self.username.clear()
            self.password.clear()
            self.controller.open_admin_panel()
        else:
            QMessageBox.critical(self, "Login Error", "Invalid Admin ID or Password.")

class MainApp(QStackedWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SOS Hermann Gmeiner School Gandaki")
        self.setMinimumSize(600, 300)
        self.resize(1200, 750)
        self.selection_page = SelectionPage(self)
        self.admin_login_page = AdminLoginPage(self)
        self.addWidget(self.selection_page)
        self.addWidget(self.admin_login_page)
        self.setCurrentWidget(self.selection_page)

    def show_selection(self):
        self.setCurrentWidget(self.selection_page)

    def open_admin_login(self):
        self.setCurrentWidget(self.admin_login_page)

    def open_admin_panel(self):
        path = os.path.join(BASE_DIR, "admin_panel.py")
        if not os.path.exists(path):
            QMessageBox.critical(self, "File Not Found", "admin_panel.py was not found.")
            return
        try:
            subprocess.Popen([sys.executable, path], cwd=BASE_DIR)
            self.close()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not open admin_panel.py:\n\n{e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainApp()
    window.show()
    sys.exit(app.exec())
