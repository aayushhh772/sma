from pathlib import Path
from datetime import datetime
import subprocess
import sys

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle, Line
from kivy.metrics import dp, sp
from kivy.properties import ListProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget


# ============================================================
# WINDOW
# ============================================================

Window.size = (1440, 900)
Window.minimum_width = 1100
Window.minimum_height = 700
Window.clearcolor = (0.035, 0.075, 0.105, 1)


# ============================================================
# COLORS
# ============================================================

BG = (0.035, 0.075, 0.105, 1)
SIDEBAR = (0.025, 0.055, 0.080, 1)

CARD = (0.075, 0.125, 0.170, 1)
INPUT_BG = (0.050, 0.090, 0.125, 1)
INPUT_BORDER = (0.180, 0.280, 0.360, 1)

TEXT = (0.93, 0.95, 0.98, 1)
MUTED = (0.55, 0.65, 0.73, 1)

BLUE = (0.12, 0.22, 0.31, 1)
BLUE_LIGHT = (0.18, 0.31, 0.42, 1)

MAROON = (0.27, 0.095, 0.105, 1)


# ============================================================
# CLASS / SECTION DATA
# ============================================================

CLASS_SECTIONS = {
    "6": ["A", "B"],
    "7": ["A", "B"],
    "8": ["A", "B"],
    "9": ["A", "B"],
    "10": ["A", "B"],
    "11": ["A", "B", "C", "D"],
    "12": ["A", "B", "C", "D"],
}

PERIODS_8 = [
    "1st",
    "2nd",
    "3rd",
    "4th",
    "5th",
    "6th",
    "7th",
    "8th",
]

PERIODS_9 = PERIODS_8 + ["9th"]


# ============================================================
# FIND SOS LOGO
# ============================================================

def find_logo():

    possible_files = [
        "sos_image.png",
        "sos_image.jpg",
        "sos_image.jpeg",
        "assets/sos_image.png",
        "assets/sos_image.jpg",
        "assets/sos_image.jpeg",
    ]

    for filename in possible_files:

        path = Path(filename)

        if path.exists():
            return str(path)

    return None


# ============================================================
# LABEL
# ============================================================

class AppLabel(Label):

    def __init__(
        self,
        text="",
        font_size=12,
        color=TEXT,
        bold=False,
        **kwargs
    ):

        halign = kwargs.pop("halign", "left")
        valign = kwargs.pop("valign", "middle")

        super().__init__(
            text=text,
            font_size=sp(font_size),
            color=color,
            bold=bold,
            halign=halign,
            valign=valign,
            **kwargs
        )

        self.bind(
            size=self._update_text_size
        )

    def _update_text_size(self, *_):

        self.text_size = self.size


# ============================================================
# BUTTON
# ============================================================

class AppButton(Button):

    bg_color = ListProperty(BLUE)

    def __init__(
        self,
        text="",
        font_size=12,
        bg_color=BLUE,
        **kwargs
    ):

        super().__init__(
            text=text,
            font_size=sp(font_size),
            color=TEXT,
            background_normal="",
            background_down="",
            background_color=(0, 0, 0, 0),
            **kwargs
        )

        self.bg_color = bg_color

        with self.canvas.before:

            self._color = Color(*self.bg_color)

            self._rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(9)]
            )

        self.bind(
            pos=self._update_background,
            size=self._update_background
        )

    def _update_background(self, *_):

        self._rect.pos = self.pos
        self._rect.size = self.size


# ============================================================
# INPUT
# ============================================================

class AppInput(TextInput):

    def __init__(
        self,
        hint_text="",
        font_size=12,
        **kwargs
    ):

        super().__init__(
            hint_text=hint_text,
            font_size=sp(font_size),
            foreground_color=TEXT,
            hint_text_color=MUTED,
            background_normal="",
            background_active="",
            background_color=(0, 0, 0, 0),
            padding=[
                dp(14),
                dp(10)
            ],
            multiline=False,
            **kwargs
        )

        with self.canvas.before:

            Color(*INPUT_BG)

            self._rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(8)]
            )

            Color(*INPUT_BORDER)

            self._border = Line(
                rounded_rectangle=(
                    self.x,
                    self.y,
                    self.width,
                    self.height,
                    dp(8)
                ),
                width=1
            )

        self.bind(
            pos=self._update_background,
            size=self._update_background
        )

    def _update_background(self, *_):

        self._rect.pos = self.pos
        self._rect.size = self.size

        self._border.rounded_rectangle = (
            self.x,
            self.y,
            self.width,
            self.height,
            dp(8)
        )


# ============================================================
# TEACHER NAME INPUT
# ============================================================

class TeacherNameInput(AppInput):

    def insert_text(self, substring, from_undo=False):

        filtered = ""

        for character in substring:

            if (
                ("A" <= character <= "Z")
                or ("a" <= character <= "z")
                or character == " "
            ):

                filtered += character

        super().insert_text(
            filtered,
            from_undo=from_undo
        )


# ============================================================
# SPINNER
# ============================================================

class AppSpinner(Spinner):

    def __init__(
        self,
        text="Select",
        values=(),
        font_size=12,
        **kwargs
    ):

        super().__init__(
            text=text,
            values=values,
            font_size=sp(font_size),
            color=TEXT,
            background_normal="",
            background_down="",
            background_color=(0, 0, 0, 0),
            **kwargs
        )

        with self.canvas.before:

            Color(*INPUT_BG)

            self._rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(8)]
            )

            Color(*INPUT_BORDER)

            self._border = Line(
                rounded_rectangle=(
                    self.x,
                    self.y,
                    self.width,
                    self.height,
                    dp(8)
                ),
                width=1
            )

        self.bind(
            pos=self._update_background,
            size=self._update_background
        )

    def _update_background(self, *_):

        self._rect.pos = self.pos
        self._rect.size = self.size

        self._border.rounded_rectangle = (
            self.x,
            self.y,
            self.width,
            self.height,
            dp(8)
        )


# ============================================================
# CARD
# ============================================================

class Card(BoxLayout):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        with self.canvas.before:

            Color(*CARD)

            self._rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(13)]
            )

        self.bind(
            pos=self._update_background,
            size=self._update_background
        )

    def _update_background(self, *_):

        self._rect.pos = self.pos
        self._rect.size = self.size


# ============================================================
# NAVIGATION BUTTON
# ============================================================

class NavigationButton(Button):

    def __init__(
        self,
        text="",
        selected=False,
        **kwargs
    ):

        super().__init__(
            text=text,
            font_size=sp(11),
            color=TEXT,
            background_normal="",
            background_down="",
            background_color=(0, 0, 0, 0),
            **kwargs
        )

        button_color = BLUE if selected else SIDEBAR

        with self.canvas.before:

            Color(*button_color)

            self._rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(9)]
            )

        self.bind(
            pos=self._update_background,
            size=self._update_background
        )

    def _update_background(self, *_):

        self._rect.pos = self.pos
        self._rect.size = self.size


# ============================================================
# ADMIN PANEL
# ============================================================

class AdminPanel(BoxLayout):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        self.orientation = "horizontal"

        self.class_spinner = None
        self.section_spinner = None
        self.period_spinner = None

        self.absent_teacher = None
        self.substitute_teacher = None

        self.lower_class_spinner = None
        self.upper_class_spinner = None

        self.notice_title = None
        self.notice_content = None

        self.time_label = None

        self.build_sidebar()
        self.build_main_content()

        Clock.schedule_interval(
            self.update_clock,
            1
        )

        self.update_clock()

    # ========================================================
    # SIDEBAR
    # ========================================================

    def build_sidebar(self):

        sidebar = BoxLayout(
            orientation="vertical",
            size_hint_x=None,
            width=dp(105),
            padding=[
                dp(12),
                dp(20),
                dp(12),
                dp(20)
            ],
            spacing=dp(12)
        )

        with sidebar.canvas.before:

            Color(*SIDEBAR)

            sidebar_rect = RoundedRectangle(
                pos=sidebar.pos,
                size=sidebar.size,
                radius=[dp(10)]
            )

        def update_sidebar(*_):

            sidebar_rect.pos = sidebar.pos
            sidebar_rect.size = sidebar.size

        sidebar.bind(
            pos=update_sidebar,
            size=update_sidebar
        )

        sidebar.add_widget(
            Widget(
                size_hint_y=None,
                height=dp(20)
            )
        )

        sidebar.add_widget(
            AppLabel(
                text="●",
                font_size=18,
                color=(1, 0.75, 0.25, 1),
                halign="center",
                size_hint_y=None,
                height=dp(35)
            )
        )

        dashboard = NavigationButton(
            text="⌂\nDASHBOARD",
            selected=True,
            size_hint_y=None,
            height=dp(82)
        )

        dashboard.bind(
            on_release=lambda *_:
            self.show_message(
                "Dashboard",
                "You are already on the Admin Panel."
            )
        )

        sidebar.add_widget(dashboard)

        sidebar.add_widget(
            Widget()
        )

        settings = NavigationButton(
            text="⚙\nSETTINGS",
            size_hint_y=None,
            height=dp(82)
        )

        settings.bind(
            on_release=lambda *_:
            self.show_message(
                "Settings",
                "Settings will be connected later."
            )
        )

        sidebar.add_widget(settings)

        logout = NavigationButton(
            text="↪\nLOG OUT",
            size_hint_y=None,
            height=dp(82)
        )

        with logout.canvas.before:

            Color(*MAROON)

            logout_rect = RoundedRectangle(
                pos=logout.pos,
                size=logout.size,
                radius=[dp(9)]
            )

        def update_logout(*_):

            logout_rect.pos = logout.pos
            logout_rect.size = logout.size

        logout.bind(
            pos=update_logout,
            size=update_logout
        )

        logout.bind(
            on_release=lambda *_:
            self.logout_confirmation()
        )

        sidebar.add_widget(logout)

        self.add_widget(sidebar)

    # ========================================================
    # MAIN CONTENT
    # ========================================================

    def build_main_content(self):

        main = BoxLayout(
            orientation="vertical",
            padding=[
                dp(34),
                dp(25),
                dp(34),
                dp(18)
            ],
            spacing=dp(18)
        )

        self.add_widget(main)

        header = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(82),
            spacing=dp(18)
        )

        logo_path = find_logo()

        if logo_path:

            logo = Image(
                source=logo_path,
                size_hint_x=None,
                width=dp(65),
                keep_ratio=True,
                allow_stretch=True
            )

        else:

            logo = AppLabel(
                text="SOS",
                font_size=17,
                bold=True,
                size_hint_x=None,
                width=dp(65),
                halign="center"
            )

        header.add_widget(logo)

        title_box = BoxLayout(
            orientation="vertical"
        )

        title_box.add_widget(
            AppLabel(
                text="SOS HGS GANDAKI",
                font_size=21,
                bold=True
            )
        )

        title_box.add_widget(
            AppLabel(
                text="ADMIN PANEL",
                font_size=11,
                color=MUTED
            )
        )

        header.add_widget(title_box)

        header.add_widget(
            Widget()
        )

        self.time_label = AppLabel(
            text="",
            font_size=14,
            bold=True,
            size_hint_x=None,
            width=dp(200),
            halign="center"
        )

        header.add_widget(
            self.time_label
        )

        main.add_widget(header)

        scroll = ScrollView(
            do_scroll_x=False,
            bar_width=dp(5)
        )

        content = BoxLayout(
            orientation="vertical",
            spacing=dp(18),
            size_hint_y=None
        )

        content.bind(
            minimum_height=content.setter("height")
        )

        top_row = BoxLayout(
            spacing=dp(18),
            size_hint_y=None,
            height=dp(300)
        )

        top_row.add_widget(
            self.build_substitution()
        )

        top_row.add_widget(
            self.build_upcoming()
        )

        content.add_widget(top_row)

        bottom_row = BoxLayout(
            spacing=dp(18),
            size_hint_y=None,
            height=dp(300)
        )

        bottom_row.add_widget(
            self.build_notice()
        )

        bottom_row.add_widget(
            self.build_recent()
        )

        content.add_widget(bottom_row)

        scroll.add_widget(content)

        main.add_widget(scroll)

        footer = BoxLayout(
            size_hint_y=None,
            height=dp(35)
        )

        footer.add_widget(
            AppLabel(
                text="SOS HGS Gandaki • School Management System",
                font_size=9,
                color=MUTED
            )
        )

        main.add_widget(footer)

    # ========================================================
    # CLOCK
    # ========================================================

    def update_clock(self, *_):

        if self.time_label is None:
            return

        now = datetime.now()

        self.time_label.text = (
            now.strftime("%I:%M %p")
            + "\n"
            + now.strftime("%A, %d %B %Y")
        )

    # ========================================================
    # SUBSTITUTION PANEL
    # ========================================================

    def build_substitution(self):

        card = Card(
            orientation="vertical",
            padding=dp(22),
            spacing=dp(13)
        )

        card.add_widget(
            AppLabel(
                text="LIVE SUBSTITUTION ENTRY",
                font_size=14,
                bold=True,
                size_hint_y=None,
                height=dp(30)
            )
        )

        row1 = BoxLayout(
            spacing=dp(9),
            size_hint_y=None,
            height=dp(48)
        )

        row1.add_widget(
            AppLabel(
                text="Class",
                font_size=11,
                size_hint_x=None,
                width=dp(45)
            )
        )

        self.class_spinner = AppSpinner(
            text="Select Class",
            values=tuple(CLASS_SECTIONS.keys())
        )

        self.class_spinner.bind(
            text=self.class_changed
        )

        row1.add_widget(
            self.class_spinner
        )

        row1.add_widget(
            AppLabel(
                text="Section",
                font_size=11,
                size_hint_x=None,
                width=dp(58)
            )
        )

        self.section_spinner = AppSpinner(
            text="Select Section",
            values=()
        )

        row1.add_widget(
            self.section_spinner
        )

        row1.add_widget(
            AppLabel(
                text="Period",
                font_size=11,
                size_hint_x=None,
                width=dp(48)
            )
        )

        self.period_spinner = AppSpinner(
            text="Select Period",
            values=tuple(PERIODS_8)
        )

        row1.add_widget(
            self.period_spinner
        )

        card.add_widget(row1)

        row2 = BoxLayout(
            spacing=dp(9),
            size_hint_y=None,
            height=dp(48)
        )

        row2.add_widget(
            AppLabel(
                text="Absent Teacher",
                font_size=10,
                size_hint_x=None,
                width=dp(92)
            )
        )

        self.absent_teacher = TeacherNameInput(
            hint_text="Teacher name",
            font_size=11
        )

        row2.add_widget(
            self.absent_teacher
        )

        row2.add_widget(
            AppLabel(
                text="Substitute Teacher",
                font_size=10,
                size_hint_x=None,
                width=dp(110)
            )
        )

        self.substitute_teacher = TeacherNameInput(
            hint_text="Teacher name",
            font_size=11
        )

        row2.add_widget(
            self.substitute_teacher
        )

        card.add_widget(row2)

        post = AppButton(
            text="POST LIVE",
            font_size=12,
            bg_color=BLUE_LIGHT,
            size_hint_y=None,
            height=dp(46)
        )

        post.bind(
            on_release=lambda *_:
            self.submit_substitution()
        )

        card.add_widget(post)

        return card

    # ========================================================
    # CLASS CHANGED
    # ========================================================

    def class_changed(
        self,
        spinner,
        selected_class
    ):

        if selected_class not in CLASS_SECTIONS:
            return

        self.section_spinner.values = tuple(
            CLASS_SECTIONS[selected_class]
        )

        self.section_spinner.text = "Select Section"

        if selected_class in ("11", "12"):

            self.period_spinner.values = tuple(
                PERIODS_9
            )

        else:

            self.period_spinner.values = tuple(
                PERIODS_8
            )

        self.period_spinner.text = "Select Period"

    # ========================================================
    # UPCOMING SUBSTITUTIONS
    # ========================================================

    def build_upcoming(self):

        card = Card(
            orientation="vertical",
            padding=dp(22),
            spacing=dp(10)
        )

        header = BoxLayout(
            size_hint_y=None,
            height=dp(45)
        )

        header.add_widget(
            AppLabel(
                text="UPCOMING LIVE SUBSTITUTIONS",
                font_size=14,
                bold=True
            )
        )

        search = AppInput(
            hint_text="Search",
            font_size=11,
            size_hint_x=None,
            width=dp(170),
            height=dp(40)
        )

        header.add_widget(search)

        card.add_widget(header)

        scroll = ScrollView(
            do_scroll_x=False,
            bar_width=dp(4)
        )

        list_box = GridLayout(
            cols=1,
            size_hint_y=None,
            spacing=dp(4)
        )

        list_box.bind(
            minimum_height=list_box.setter("height")
        )

        for _ in range(5):

            list_box.add_widget(
                AppLabel(
                    text="",
                    font_size=11,
                    size_hint_y=None,
                    height=dp(32),
                    color=MUTED
                )
            )

        scroll.add_widget(list_box)

        card.add_widget(scroll)

        return card

    # ========================================================
    # NOTICE ENTRY
    # ========================================================

    def build_notice(self):

        card = Card(
            orientation="vertical",
            padding=dp(22),
            spacing=dp(10)
        )

        card.add_widget(
            AppLabel(
                text="NOTICES ENTRY",
                font_size=14,
                bold=True,
                size_hint_y=None,
                height=dp(30)
            )
        )

        self.notice_title = AppInput(
            hint_text="Title",
            font_size=11,
            size_hint_y=None,
            height=dp(45)
        )

        card.add_widget(
            self.notice_title
        )

        self.notice_content = AppInput(
            hint_text="Content",
            font_size=11,
            size_hint_y=None,
            height=dp(45)
        )

        card.add_widget(
            self.notice_content
        )

        class_range = BoxLayout(
            spacing=dp(8),
            size_hint_y=None,
            height=dp(46)
        )

        class_range.add_widget(
            AppLabel(
                text="Class",
                font_size=11,
                size_hint_x=None,
                width=dp(48)
            )
        )

        values = self.class_range_values()

        self.lower_class_spinner = AppSpinner(
            text="Lower",
            values=tuple(values),
            font_size=10
        )

        self.upper_class_spinner = AppSpinner(
            text="Upper",
            values=tuple(values),
            font_size=10
        )

        class_range.add_widget(
            self.lower_class_spinner
        )

        class_range.add_widget(
            AppLabel(
                text="to",
                font_size=11,
                size_hint_x=None,
                width=dp(22),
                halign="center"
            )
        )

        class_range.add_widget(
            self.upper_class_spinner
        )

        card.add_widget(class_range)

        post = AppButton(
            text="POST NOTICE",
            font_size=12,
            bg_color=BLUE_LIGHT,
            size_hint_y=None,
            height=dp(46)
        )

        post.bind(
            on_release=lambda *_:
            self.submit_notice()
        )

        card.add_widget(post)

        return card

    # ========================================================
    # CLASS RANGE
    # ========================================================

    def class_range_values(self):

        values = []

        for class_number, sections in CLASS_SECTIONS.items():

            for section in sections:

                values.append(
                    f"{class_number} {section}"
                )

        return values

    # ========================================================
    # RECENT NOTICES
    # ========================================================

    def build_recent(self):

        card = Card(
            orientation="vertical",
            padding=dp(22),
            spacing=dp(10)
        )

        header = BoxLayout(
            size_hint_y=None,
            height=dp(45)
        )

        header.add_widget(
            AppLabel(
                text="RECENT NOTICES",
                font_size=14,
                bold=True
            )
        )

        search = AppInput(
            hint_text="Search",
            font_size=11,
            size_hint_x=None,
            width=dp(170),
            height=dp(40)
        )

        header.add_widget(search)

        card.add_widget(header)

        scroll = ScrollView(
            do_scroll_x=False,
            bar_width=dp(4)
        )

        list_box = GridLayout(
            cols=1,
            size_hint_y=None
        )

        list_box.bind(
            minimum_height=list_box.setter("height")
        )

        for _ in range(5):

            list_box.add_widget(
                AppLabel(
                    text="",
                    font_size=11,
                    size_hint_y=None,
                    height=dp(32),
                    color=MUTED
                )
            )

        scroll.add_widget(list_box)

        card.add_widget(scroll)

        return card

    # ========================================================
    # SUBSTITUTION VALIDATION
    # ========================================================

    def submit_substitution(self):

        selected_class = self.class_spinner.text
        selected_section = self.section_spinner.text
        selected_period = self.period_spinner.text

        absent = self.absent_teacher.text.strip()
        substitute = self.substitute_teacher.text.strip()

        if selected_class == "Select Class":

            self.show_message(
                "Validation",
                "Please select a class."
            )
            return

        if selected_section == "Select Section":

            self.show_message(
                "Validation",
                "Please select a section."
            )
            return

        if selected_period == "Select Period":

            self.show_message(
                "Validation",
                "Please select a period."
            )
            return

        if not absent:

            self.show_message(
                "Validation",
                "Please enter the absent teacher."
            )
            return

        if not substitute:

            self.show_message(
                "Validation",
                "Please enter the substitute teacher."
            )
            return

        self.show_message(
            "Success",
            "Substitution information is ready to be connected to the backend."
        )

    # ========================================================
    # NOTICE VALIDATION
    # ========================================================

    def submit_notice(self):

        title = self.notice_title.text.strip()
        content = self.notice_content.text.strip()

        lower = self.lower_class_spinner.text
        upper = self.upper_class_spinner.text

        if not title:

            self.show_message(
                "Validation",
                "Please enter a notice title."
            )
            return

        if not content:

            self.show_message(
                "Validation",
                "Please enter notice content."
            )
            return

        if lower == "Lower":

            self.show_message(
                "Validation",
                "Please select the lower class."
            )
            return

        if upper == "Upper":

            self.show_message(
                "Validation",
                "Please select the upper class."
            )
            return

        lower_number = int(
            lower.split()[0]
        )

        upper_number = int(
            upper.split()[0]
        )

        if lower_number > upper_number:

            self.show_message(
                "Validation",
                "The lower class cannot be higher than the upper class."
            )
            return

        self.show_message(
            "Success",
            "Notice information is ready to be connected to the backend."
        )

    # ========================================================
    # LOGOUT CONFIRMATION
    # ========================================================

    def logout_confirmation(self):

        layout = BoxLayout(
            orientation="vertical",
            padding=dp(22),
            spacing=dp(20)
        )

        layout.add_widget(
            AppLabel(
                text="Are you sure you want to log out?",
                font_size=13,
                halign="center"
            )
        )

        buttons = BoxLayout(
            spacing=dp(14),
            size_hint_y=None,
            height=dp(50)
        )

        yes_button = AppButton(
            text="Yes, Log out",
            font_size=11,
            bg_color=MAROON
        )

        no_button = AppButton(
            text="No, Keep me Logged in",
            font_size=11,
            bg_color=BLUE
        )

        buttons.add_widget(
            yes_button
        )

        buttons.add_widget(
            no_button
        )

        layout.add_widget(
            buttons
        )

        popup = Popup(
            title="Log Out",
            content=layout,
            size_hint=(None, None),
            size=(dp(470), dp(235)),
            auto_dismiss=False,
            separator_color=BLUE_LIGHT
        )

        yes_button.bind(
            on_release=lambda *_:
            self.perform_logout(popup)
        )

        no_button.bind(
            on_release=popup.dismiss
        )

        popup.open()

    # ========================================================
    # LOGOUT ACTION
    # ========================================================

    def perform_logout(self, popup):

        # Close confirmation popup
        popup.dismiss()

        # Find adminpage.py in the same folder as admin_panel.py
        adminpage_path = Path(__file__).resolve().parent / "adminpage.py"
        
        if not adminpage_path.exists():

            self.show_message(
                "Error",
                "adminpage.py was not found.\n\n"
                "Make sure adminpage.py is in the same folder "
                "as admin_panel.py."
            )
            return
        try:
            # Open adminpage.py first
            subprocess.Popen(
                [
                    sys.executable,
                    str(adminpage_path)
                ],
                cwd=str(adminpage_path.parent)
            )
            # Then close admin_panel.py
            Clock.schedule_once(
                lambda *_: App.get_running_app().stop(),
                0.2
            )
        except Exception as error:

            self.show_message(
                "Logout Error",
                f"Could not open adminpage.py.\n\n{error}"
            )
    def show_message(self, title, message):
        layout = BoxLayout(
            orientation="vertical",
            padding=dp(20),
            spacing=dp(18)
        )
        layout.add_widget(
            AppLabel(
                text=message,
                font_size=12,
                halign="center"
            )
        )
        close_button = AppButton(
            text="OK",
            font_size=12,
            bg_color=BLUE,
            size_hint_y=None,
            height=dp(46)
        )
        layout.add_widget(
            close_button
        )
        popup = Popup(
            title=title,
            content=layout,
            size_hint=(None, None),
            size=(dp(460), dp(225)),
            auto_dismiss=False,
            separator_color=BLUE_LIGHT
        )
        close_button.bind(
            on_release=popup.dismiss
        )
        popup.open()
class AdminPanelApp(App):
    title = "SOS HGS Gandaki - Admin Panel"
    def build(self):
        Window.clearcolor = BG
        return AdminPanel()
if __name__ == "__main__":
    AdminPanelApp().run()
