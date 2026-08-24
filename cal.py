import sys, datetime, math
from PyQt6.QtCore import Qt, QTimer, QRectF
from PyQt6.QtGui import QFont, QColor, QPainter, QLinearGradient
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QGridLayout, QScrollArea, QSizePolicy
)

BS_MONTHS = ["बैशाख", "जेठ", "असार", "साउन", "भदौ", "असोज", "कार्तिक", "मंसिर", "पुष", "माघ", "फागुन", "चैत"]
BS_MONTHS_EN = ["Baisakh", "Jestha", "Asar", "Shrawan", "Bhadra", "Ashwin", "Kartik", "Mangsir", "Poush", "Magh", "Falgun", "Chaitra"]

# Corrected 2083 month lengths
# Jestha = 31
# Asar = 32
# Asoj = 31
# Kartik = 30
# Mangsir = 29
# Poush = 30
# Magh = 29
# Falgun = 30
# Chaitra = 30
BS_MONTH_DAYS = [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30]

# Corrected Gregorian boundaries
MONTH_START_AD = {
    1: datetime.date(2026, 4, 14),
    2: datetime.date(2026, 5, 15),
    3: datetime.date(2026, 6, 15),
    4: datetime.date(2026, 7, 17),
    5: datetime.date(2026, 8, 17),
    6: datetime.date(2026, 9, 17),
    7: datetime.date(2026, 10, 18),
    8: datetime.date(2026, 11, 17),
    9: datetime.date(2026, 12, 16),
    10: datetime.date(2027, 1, 15),
    11: datetime.date(2027, 2, 13),
    12: datetime.date(2027, 3, 15),
}

MONTH_END_AD = {
    1: datetime.date(2026, 5, 14),
    2: datetime.date(2026, 6, 14),
    3: datetime.date(2026, 7, 16),
    4: datetime.date(2026, 8, 16),
    5: datetime.date(2026, 9, 16),
    6: datetime.date(2026, 10, 17),
    7: datetime.date(2026, 11, 16),
    8: datetime.date(2026, 12, 15),
    9: datetime.date(2027, 1, 14),
    10: datetime.date(2027, 2, 12),
    11: datetime.date(2027, 3, 14),
    12: datetime.date(2027, 4, 13),
}

MONTH_GREGORIAN_RANGES = {
    1: "APR/MAY 2026",
    2: "MAY/JUN 2026",
    3: "JUN/JUL 2026",
    4: "JUL/AUG 2026",
    5: "AUG/SEP 2026",
    6: "SEP/OCT 2026",
    7: "OCT/NOV 2026",
    8: "NOV/DEC 2026",
    9: "DEC/JAN 2026/27",
    10: "JAN/FEB 2027",
    11: "FEB/MAR 2027",
    12: "MAR/APR 2027",
}

# ---------------------------------------------------------------------------
# HOLIDAYS
# ---------------------------------------------------------------------------
HOLIDAYS = {
    1: {
        1: "नयाँ वर्ष २०८३",
        18: "अन्तर्राष्ट्रिय मजदुर दिवस/बुद्ध जयन्ती",
    },
    2: {
        15: "गणतन्त्र दिवस",
    },
    3: {
        29: "भानु जयन्ती",
        30: "गर्मी बिदा",
        31: "गर्मी बिदा",
        32: "गर्मी बिदा",
    },
    4: {
        1: "गर्मी बिदा",
    },
    5: {
        12: "जनैपूर्णिमा",
        19: "श्रीकृष्ण जन्माष्टमी",
        29: "हरितालिका तीज",
    },
    6: {
        25: "घटस्थापना",
        29: "दशैं बिदा",
        30: "दशैं बिदा",
        31: "दशैं बिदा",
    },
    7: {
        1: "दशैं बिदा",
        2: "दशैं बिदा",
        3: "दशैं बिदा",
        4: "दशैं बिदा",
        5: "दशैं बिदा",
        6: "दशैं बिदा",
        7: "दशैं बिदा",
        8: "कोजाग्रत पूर्णिमा",
        9: "वार्षिक बिदा",
        10: "वार्षिक बिदा",
        11: "वार्षिक बिदा",
        12: "वार्षिक बिदा",
        13: "वार्षिक बिदा",
        14: "वार्षिक बिदा",
        15: "वार्षिक बिदा",
        16: "वार्षिक बिदा",
        17: "वार्षिक बिदा",
        18: "वार्षिक बिदा",
        19: "वार्षिक बिदा",
        20: "वार्षिक बिदा",
        21: "तिहार बिदा",
        22: "तिहार बिदा",
        23: "तिहार बिदा",
        24: "तिहार बिदा",
        25: "तिहार बिदा",
        26: "तिहार बिदा",
        27: "स्थानीय बिदा",
        29: "छठ पर्व",
    },
    8: {},
    9: {
        9: "उधौली पर्व",
        10: "क्रिसमस दिवस",
        15: "तमु ल्होसार",
        27: "पृथ्वी जयन्ती",
        28: "जाडो बिदा",
        29: "जाडो बिदा",
        30: "जाडो बिदा",
    },
    10: {
        1: "माघे सङ्क्रान्ति",
        4: "जाडो बिदा",
        5: "जाडो बिदा",
        16: "शहिद दिवस",
        22: "गण्डकी प्रदेश स्थापना दिवस",
        24: "सोनाम ल्होसार",
    },
    11: {
        7: "प्रजातन्त्र दिवस",
        22: "महाशिवरात्रि",
        24: "अन्तर्राष्ट्रिय महिला दिवस",
        25: "ग्याल्पो ल्होसार",
    },
    12: {
        7: "होली",
        24: "वार्षिक बिदा",
        25: "वार्षिक बिदा",
        26: "वार्षिक बिदा",
        27: "वार्षिक बिदा",
        28: "वार्षिक बिदा",
        29: "वार्षिक बिदा",
        30: "वार्षिक बिदा",
    },
}

HOLIDAY_PANEL_OVERRIDES = {
    3: [(30, 32, "गर्मी बिदा")],
    11: [
        (7, 7, "प्रजातन्त्र दिवस"),
        (24, 24, "अन्तर्राष्ट्रिय महिला दिवस"),
        (25, 25, "ग्याल्पो ल्होसार"),
    ],
}

# ---------------------------------------------------------------------------
# EVENTS
# ---------------------------------------------------------------------------
ACTIVITIES = {
    1: {
        15: "School Opening Day for Teachers (PDP)",
        21: "School Opening Day for Students",
        31: "Creative Writing in English (III-X)",
    },
    2: {
        22: "Speech Competition in English (VI-VII)",
        24: "Parents’ Meeting for Grade VI and X",
        26: "First Unit Test (Nur-X)",
        27: "First Unit Test (Nur-X)",
        28: "First Unit Test (Nur-X)",
        29: "First Unit Test (Nur-X)",
    },
    3: {
        1: "School Opening Day for Grdae XII",
        2: "English Handwriting Competition (III-VIII)",
        4: "School Opening Day for Grade XI",
        5: "Creative Writing in Nepali (III-X)",
        11: "English Handwriting Competition (Nursery-KG)",
        18: "Speech Competition in English (VIII-X)",
        19: "Nepali Handwriting Competition (I-II)",
        23: "Nepali Handwriting Competition (III-VIII)",
        26: "Speech Competition in Nepali (VIII-X)",
    },
    4: {
        4: "School Re-opens",
        5: "Nepali Handwriting Competition (Nursery-KG)",
        8: "Scrabble Competition (VI-X)",
        11: "First Term Exam (Nursery-X)",
        12: "First Term Exam (Nursery-X)",
        13: "First Term Exam (Nursery-X)",
        14: "First Term Exam (Nursery-X)",
        15: "First Term Exam (Nursery-X)",
        16: "First Term Exam (Nursery-X)",
        17: "First Term Exam (Nursery-X)",
        18: "First Term Exam (Nursery-X)",
        19: "First Term Exam (Nursery-X)",
        20: "First Term Exam (Nursery-X)",
        22: "Creative Writing in English (XI-XII)",
        29: "Creative Writing in Nepali (XI-XII)",
    },
    5: {
        1: "Spelling Contest (III-V) / Mid-Term Exam (Grade XI & XII)",
        2: "Rhymes Competition (Nursery-KG) / Mid-Term Exam (Grade XI & XII)",
        3: "Mid-Term Exam (Grade XI & XII)",
        4: "Mid-Term Exam (Grade XI & XII)",
        5: "First Term Result Day (Nursery-X) / Mid-Term Exam (Grade XI & XII)",
        8: "Spelling Contest (VI-VII) / Mid-Term Exam (Grade XI & XII)",
        15: "Speech Competition in Nepali (XI-XII)",
        22: "Maths Race (KG) / Handball Competition Girls (VI-VII)",
        24: "Drawing Competition (I-II)",
        26: "Junior Talent Show",
        31: "Uni Hockey Boys/Girls (VI-VII)",
    },
    6: {
        1: "Speech Competition in English (XI-XII)",
        3: "Cricket Tournament Boys (XI-XII)",
        5: "Second Unit Test Upto Grade X",
        6: "Second Unit Test Upto Grade X",
        7: "Second Unit Test Upto Grade X",
        8: "Second Unit Test Upto Grade X",
        10: "Volleyball Competition Boys/Girls (VIII-X)",
        11: "Cricket Tournament Boys (VIII-X), Badminton Competition Girls (XI-XII)",
        12: "Maths, Science and IT Quiz (III-V)- Maths Department / First Term Exam XI-XII",
        13: "First Term Exam XI-XII",
        14: "Maths Race (Nursery)",
        15: "First Term Exam XI-XII",
        16: "First Term Exam XI-XII",
        17: "First Term Exam XI-XII",
        18: "First Term Exam XI-XII",
        19: "First Term Exam XI-XII",
        20: "First Term Exam XI-XII",
        21: "First Term Exam XI-XII",
        22: "Quiz Contest (KG)",
        23: "Story Telling Competition in English and Nepali (I-II)",
        27: "First Term Result Day (XI & XII)",
        28: "Senior Talent Show",
    },
    7: {
        4: "Maths, Science and IT Quiz (VIII-X)- Science Department",
        5: "Volleyball Competition Boys/Girls (XI-XII)",
        12: "Basketball Competition Boys/Girls (XI-XII)",
        14: "Second Term Exam (Nur-X)",
        15: "Debate Competition in Nepali (XI-XII) / Second Term Exam (Nur-X)",
        16: "Second Term Exam (Nur-X)",
        17: "Second Term Exam (Nur-X)",
        18: "Second Term Exam (Nur-X)",
        19: "Second Term Exam (Nur-X)",
        20: "Second Term Exam (Nur-X)",
        21: "Second Term Exam (Nur-X)",
        22: "Second Term Exam (Nur-X)",
        23: "Second Term Exam (Nur-X)",
        24: "English Spelling Contest (Nursery-KG)",
        26: "Basketball Competition Boys/Girls (VIII-X)",
        29: "Maths Race (I-II) / Second Term Result Day (Nursery-X)",
    },

    # Kartik has no event days.
    8: {
        # Mangsir events
        4: "Maths, Science and IT Quiz (VIII-X)- Science Department",
        5: "Volleyball Competition Boys/Girls (XI-XII)",
        12: "Basketball Competition Boys/Girls (XI-XII)",
        14: "Second Term Exam (Nur-X)",
        15: "Debate Competition in Nepali (XI-XII) / Second Term Exam (Nur-X)",
        16: "Second Term Exam (Nur-X)",
        17: "Second Term Exam (Nur-X)",
        18: "Second Term Exam (Nur-X)",
        21: "Second Term Exam (Nur-X)",
        22: "Second Term Exam (Nur-X)",
        23: "Second Term Exam (Nur-X)",
        24: "English Spelling Contest (Nursery-KG)",
        26: "Basketball Competition Boys/Girls (VIII-X)",
        29: "Maths Race (I-II) / Second Term Result Day (Nursery-X)",
    },

    9: {
        1: "Maths, Science and IT Quiz (III-V)- Computer Department",
        4: "Science Exhibition",
        5: "Football Competition Boys (XI-XII)",
        8: "Nepali Shruti Lekhan Competition (Nursery-KG)",
        14: "Memory Game (KG)",
        17: "Steam General Quiz (XI-XII)",
        23: "Annual Sports Meet",
        24: "Annual Sports Meet",
        25: "Annual Sports Meet",
    },

    10: {
        6: "School Reopens; Second Term Exam (Grade XI-XII)",
        7: "Second Term Exam (Grade XI-XII)",
        8: "Webpage Designing Competition (IX-X); Second Term Exam (Grade XI-XII)",
        9: "Second Term Exam (Grade XI-XII)",
        10: "Second Term Exam (Grade XI-XII)",
        11: "Second Term Exam (Grade XI-XII)",
        12: "Memory Game (I-II); Second Term Exam (Grade XI-XII)",
        13: "Webpage Designing Competition (VI-VIII); Second Term Exam (Grade XI-XII)",
        14: "Second Term Exam (Grade XI-XII)",
        15: "Eco RU Fest (VI-X); Second Term Exam (Grade XI-XII)",
        21: "Creative Writing in Nepali (I-II)",
        25: "Webpage Designing Competition (XI-XII)",
        26: "Second Term Result Day (XI-XII)",
        29: "Creative Writing in English (I-II)",
    },

    # Corrected Falgun:
    # ONLY one event day, on Falgun 6.
    11: {
        6: "Webpage Designing Competition (XI-XII)",
    },

    # Corrected Chaitra:
    # Previous Falgun events moved here exactly.
    12: {
        1: "Pre-Board Exam (Grade XI-XII)",
        2: "Pre-Board Exam (Grade XI-XII)",
        3: "Pre-Board Exam (Grade XI-XII)",
        4: "Pre-Board Exam (Grade XI-XII)",
        5: "Pre-Board Exam (Grade XI-XII)",
        6: "Pre-Board Exam (Grade XI-XII)",
        7: "Pre-Board Exam (Grade XI-XII)",
        8: "Annual Exam (Nur-VII, IX) / Pre-Board Exam (Grade XI-XII)",
        9: "Annual Exam (Nur-VII, IX) / Pre-Board Exam (Grade XI-XII)",
        10: "Annual Exam (Nur-VII, IX) / Pre-Board Exam (Grade XI-XII)",
        11: "Annual Exam (Nur-VII, IX)",
        12: "Annual Exam (Nur-VII, IX)",
        13: "Annual Exam (Nur-VII, IX)",
        14: "Annual Exam (Nur-VII, IX)",
        15: "Annual Exam (Nur-VII, IX)",
        16: "Annual Exam (Nur-VII, IX)",
        17: "Annual Exam (Nur-VII, IX)",
        23: "Annual Result Day (Nur-VII, IX)",
    },
}

# ---------------------------------------------------------------------------
# MONTHLY STATISTICS
# ---------------------------------------------------------------------------
MONTH_STATISTICS = {
    1: {"working": "12", "teaching": "9", "annual_holidays": "13", "holidays": "2"},
    2: {"working": "20", "teaching": "20", "holidays": "1"},
    3: {"working": "20", "teaching": "20", "annual_holiday": "3", "public_holiday": "1"},
    4: {"working": "20", "teaching": "12", "exam_days": "8", "annual_holidays": "1"},
    5: {"working": "20", "teaching": "20", "holidays": "3"},
    6: {"working": "20", "teaching": "19", "holidays": "1"},
    7: {"working": "1", "teaching": "1", "annual_holiday": "10", "tihar_holidays": "8", "dashain_holidays": "8"},
    8: {"working": "21", "teaching": "13", "exam_days": "8"},
    9: {"working": "16", "teaching": "13", "annual_holidays": "3", "holidays": "4"},
    10: {"working": "17", "teaching": "17", "annual_holiday": "2", "holidays": "3"},
    11: {"working": "17", "teaching": "17", "holidays": "3"},
    12: {"working": "17", "teaching": "5", "annual_holidays": "7", "holidays": "1"},
}

MONTH_SUMMARIES = {
    1: ("12", "9", "2"),
    2: ("20", "20", "1"),
    3: ("20", "20", "1"),
    4: ("20", "12", "1"),
    5: ("20", "20", "3"),
    6: ("20", "19", "1"),
    7: ("1", "1", "10"),
    8: ("21", "13", "—"),
    9: ("16", "13", "4"),
    10: ("17", "17", "3"),
    11: ("17", "17", "3"),
    12: ("17", "5", "1"),
}

MONTH_QUOTES = {
    1: "One child, one teacher, one book, and one pen can change the world. —Malala Yousafzai",
    3: "The future belongs to those who believe in the beauty of their dreams. —Eleanor Roosevelt",
    5: "Education is the ability to listen to almost anything without losing your temper or your self-confidence. —Robert Frost",
    7: "Excellence is never an accident; it is the result of high intention and intelligent effort. —Aristotle",
    9: "Learning without thought is labor lost; thought without learning is perilous. —Confucius",
    11: "Teaching is not transferring knowledge but creating the possibilities for the production of knowledge. —Paulo Freire",
}

DAY_NAMES = [
    "आइतबार",
    "सोमबार",
    "मंगलबार",
    "बुधबार",
    "बिहीबार",
    "शुक्रबार",
    "शनिबार"
]

NEPALI_DIGITS = str.maketrans("0123456789", "०१२३४५६७८९")

# ---------------------------------------------------------------------------
# COLORS
# ---------------------------------------------------------------------------
BLUE = "#0284C7"
BLUE_DARK = "#0369A1"
RED = "#8B0000"
GREEN = "#166534"
WHITE = "#FFFFFF"
CELL_BORDER = "#D8F0FC"


def nepali_number(number):
    return str(number).translate(NEPALI_DIGITS)


def gregorian_date(month, day):
    return MONTH_START_AD[month] + datetime.timedelta(days=day - 1)


def current_bs_month():
    today = datetime.date.today()

    for month in range(1, 13):
        if MONTH_START_AD[month] <= today <= MONTH_END_AD[month]:
            return month

    return 1 if today < MONTH_START_AD[1] else 12


def group_consecutive_events(events):
    if not events:
        return []

    days = sorted(events.keys())
    groups = []

    start = previous = days[0]
    current_name = events[start]

    for day in days[1:]:
        if day == previous + 1 and events[day] == current_name:
            previous = day
        else:
            groups.append((start, previous, current_name))
            start = previous = day
            current_name = events[day]

    groups.append((start, previous, current_name))
    return groups


class BubbleBackground(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.phase = 0

        self.bubbles = [
            (40, 60, 180),
            (390, 90, 150),
            (820, 40, 220),
            (1040, 470, 190),
            (150, 600, 150)
        ]

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate)
        self.timer.start(45)

    def animate(self):
        self.phase += 1
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        gradient = QLinearGradient(
            0,
            0,
            self.width(),
            self.height()
        )

        gradient.setColorAt(0, QColor("#E0F2FE"))
        gradient.setColorAt(0.5, QColor("#F8FDFF"))
        gradient.setColorAt(1, QColor("#E0F2FE"))

        painter.fillRect(self.rect(), gradient)
        painter.setPen(Qt.PenStyle.NoPen)

        for index, (x, y, size) in enumerate(self.bubbles):
            dx = math.sin(self.phase * 0.008 + index) * 22
            dy = math.cos(self.phase * 0.006 + index) * 18

            painter.setBrush(QColor(125, 211, 252, 32))

            painter.drawEllipse(
                QRectF(
                    x + dx,
                    y + dy,
                    size,
                    size
                )
            )


class DateCell(QFrame):
    def __init__(self, month, day, compact=False):
        super().__init__()

        self.month = month
        self.day = day
        self.compact = compact

        self.ad_date = gregorian_date(
            month,
            day
        )

        self.holiday = HOLIDAYS.get(
            month,
            {}
        ).get(day)

        self.activity = ACTIVITIES.get(
            month,
            {}
        ).get(day)

        self.today = (
            self.ad_date == datetime.date.today()
        )

        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )

        self.setMinimumHeight(
            60 if compact else 0
        )

        layout = QVBoxLayout(self)

        if compact:
            layout.setContentsMargins(
                6, 3, 6, 3
            )
        else:
            layout.setContentsMargins(
                8, 5, 7, 5
            )

        layout.setSpacing(0)

        top = QHBoxLayout()

        self.number = QLabel(
            nepali_number(day)
        )

        self.number.setFont(
            QFont(
                "Noto Sans Devanagari",
                20 if compact else 24,
                QFont.Weight.Black
            )
        )

        top.addWidget(
            self.number
        )

        top.addStretch()

        layout.addLayout(top)
        layout.addStretch()

        self.gregorian = QLabel(
            self.ad_date.strftime("%d %b")
        )

        self.gregorian.setFont(
            QFont(
                "Segoe UI",
                7 if compact else 8,
                QFont.Weight.Bold
            )
        )

        layout.addWidget(
            self.gregorian
        )

        self.update_style()

    def update_style(self):
        bg = WHITE
        border = CELL_BORDER

        weekday = self.ad_date.weekday()

        # Holiday = dark red
        # Event = dark green
        # Saturday/Sunday = dark red
        # Normal weekday = blue

        if self.holiday:
            text_color = RED

        elif self.activity:
            text_color = GREEN

        elif weekday in (5, 6):
            text_color = RED

        else:
            text_color = BLUE

        # Today gets the inverted color treatment.
        if self.today:
            bg = text_color
            border = text_color
            number_color = WHITE
            gregorian_color = WHITE
        else:
            number_color = text_color
            gregorian_color = text_color

        self.setStyleSheet(
            f"""
            QFrame {{
                background: {bg};
                border: 1px solid {border};
                border-radius: 10px;
            }}
            """
        )

        self.number.setStyleSheet(
            f"""
            QLabel {{
                color: {number_color};
                background: transparent;
                border: none;
            }}
            """
        )

        self.gregorian.setStyleSheet(
            f"""
            QLabel {{
                color: {gregorian_color};
                background: transparent;
                border: none;
            }}
            """
        )


class EventRow(QFrame):
    def __init__(self, start, end, text, accent):
        super().__init__()

        self.setMinimumHeight(46)

        self.setStyleSheet(
            """
            QFrame {
                background: #F8FCFF;
                border: none;
                border-radius: 10px;
            }
            """
        )

        row_layout = QHBoxLayout(self)
        row_layout.setContentsMargins(
            7, 6, 7, 6
        )

        row_layout.setSpacing(9)

        date_text = (
            nepali_number(start)
            if start == end
            else f"{nepali_number(start)}–{nepali_number(end)}"
        )

        date_label = QLabel(
            date_text
        )

        date_label.setFixedSize(
            52,
            36
        )

        date_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        date_label.setFont(
            QFont(
                "Noto Sans Devanagari",
                13,
                QFont.Weight.Black
            )
        )

        date_label.setStyleSheet(
            f"""
            color: {accent};
            background: #FFFFFF;
            border: none;
            border-radius: 8px;
            padding: 0px;
            font-weight: 900;
            """
        )

        text_label = QLabel(text)

        text_label.setWordWrap(True)

        text_label.setFont(
            QFont(
                "Segoe UI",
                8,
                QFont.Weight.Medium
            )
        )

        text_label.setStyleSheet(
            f"""
            color: {accent};
            border: none;
            background: transparent;
            padding: 1px;
            """
        )

        row_layout.addWidget(
            date_label,
            0,
            Qt.AlignmentFlag.AlignTop
        )

        row_layout.addWidget(
            text_label,
            1
        )


class EmptyEventRow(QFrame):
    def __init__(self, text, accent):
        super().__init__()

        self.setMinimumHeight(46)

        self.setStyleSheet(
            """
            QFrame {
                background: #F8FCFF;
                border: none;
                border-radius: 10px;
            }
            """
        )

        layout = QHBoxLayout(self)

        layout.setContentsMargins(
            10, 10, 10, 10
        )

        label = QLabel(text)

        label.setWordWrap(True)

        label.setFont(
            QFont(
                "Segoe UI",
                8,
                QFont.Weight.Medium
            )
        )

        label.setStyleSheet(
            f"""
            color: {accent};
            background: transparent;
            border: none;
            """
        )

        layout.addWidget(label)


class EventPanel(QFrame):
    def __init__(self, title, events, accent, symbol):
        super().__init__()

        self.setStyleSheet(
            """
            QFrame {
                background: rgba(255,255,255,245);
                border: 1px solid #D7EFFB;
                border-radius: 16px;
            }
            """
        )

        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            11, 10, 11, 10
        )

        layout.setSpacing(7)

        header = QHBoxLayout()

        icon = QLabel(symbol)

        icon.setFont(
            QFont(
                "Segoe UI",
                11
            )
        )

        icon.setStyleSheet(
            "border: none;"
        )

        header.addWidget(
            icon
        )

        label = QLabel(title)

        label.setFont(
            QFont(
                "Segoe UI",
                9,
                QFont.Weight.Bold
            )
        )

        label.setStyleSheet(
            f"""
            color: {accent};
            border: none;
            """
        )

        header.addWidget(
            label
        )

        header.addStretch()

        count = QLabel(
            str(len(events))
        )

        count.setFixedSize(
            28,
            24
        )

        count.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        count.setFont(
            QFont(
                "Segoe UI",
                8,
                QFont.Weight.Bold
            )
        )

        count.setStyleSheet(
            f"""
            color: {accent};
            background: #F0F9FF;
            border: none;
            border-radius: 7px;
            """
        )

        header.addWidget(
            count
        )

        layout.addLayout(
            header
        )

        line = QFrame()

        line.setFixedHeight(1)

        line.setStyleSheet(
            "background: #E0F2FE; border: none;"
        )

        layout.addWidget(
            line
        )

        scroll = QScrollArea()

        scroll.setWidgetResizable(
            True
        )

        scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        scroll.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )

        scroll.setFrameShape(
            QFrame.Shape.NoFrame
        )

        scroll.setStyleSheet(
            """
            QScrollArea {
                background: transparent;
                border: none;
            }

            QScrollBar:vertical {
                background: #E0F2FE;
                width: 7px;
                border-radius: 3px;
                margin: 2px;
            }

            QScrollBar::handle:vertical {
                background: #7DD3FC;
                min-height: 35px;
                border-radius: 3px;
            }

            QScrollBar::handle:vertical:hover {
                background: #0284C7;
            }

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
            }

            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {
                background: transparent;
            }
            """
        )

        container = QWidget()

        container.setStyleSheet(
            "background: transparent;"
        )

        container_layout = QVBoxLayout(
            container
        )

        container_layout.setContentsMargins(
            0, 0, 3, 0
        )

        container_layout.setSpacing(
            6
        )

        if events:
            for start, end, text in events:
                container_layout.addWidget(
                    EventRow(
                        start,
                        end,
                        text,
                        accent
                    )
                )
        else:
            empty_text = (
                "No holidays scheduled this month."
                if accent == RED
                else
                "No events scheduled this month."
            )

            container_layout.addWidget(
                EmptyEventRow(
                    empty_text,
                    accent
                )
            )

        container_layout.addStretch()

        scroll.setWidget(
            container
        )

        layout.addWidget(
            scroll,
            1
        )


class SummaryPanel(QFrame):
    def __init__(self, month):
        super().__init__()

        self.setStyleSheet(
            """
            QFrame {
                background: #F8FCFF;
                border: 1px solid #D7EFFB;
                border-radius: 14px;
            }
            """
        )

        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            12, 10, 12, 10
        )

        title = QLabel(
            "MONTHLY SUMMARY"
        )

        title.setFont(
            QFont(
                "Segoe UI",
                8,
                QFont.Weight.Bold
            )
        )

        title.setStyleSheet(
            f"""
            color: {BLUE_DARK};
            border: none;
            """
        )

        layout.addWidget(
            title
        )

        working, teaching, holidays = MONTH_SUMMARIES[month]

        for name, value in [
            ("Working Days", working),
            ("Teaching Days", teaching),
            ("Holidays", holidays)
        ]:
            row = QHBoxLayout()

            name_label = QLabel(name)

            name_label.setFont(
                QFont(
                    "Segoe UI",
                    7
                )
            )

            name_label.setStyleSheet(
                """
                color: #64748B;
                border: none;
                """
            )

            value_label = QLabel(value)

            value_label.setFont(
                QFont(
                    "Segoe UI",
                    9,
                    QFont.Weight.Bold
                )
            )

            value_label.setStyleSheet(
                f"""
                color: {BLUE};
                border: none;
                """
            )

            row.addWidget(
                name_label
            )

            row.addStretch()

            row.addWidget(
                value_label
            )

            layout.addLayout(
                row
            )


class CalendarWindow(QWidget):
    def __init__(self, previous_window=None):
        super().__init__()

        self.previous_window = previous_window
        self.month = current_bs_month()

        self.setWindowTitle(
            "SOS HGS School Gandaki - School Operation Calendar"
        )

        self.setMinimumSize(
            1200,
            720
        )

        self.resize(
            1400,
            820
        )

        self.background = BubbleBackground(
            self
        )

        self.background.lower()

        self.build_ui()
        self.show_month(
            self.month
        )

    def resizeEvent(self, event):
        self.background.resize(
            self.size()
        )

        super().resizeEvent(
            event
        )

    def build_ui(self):
        main = QVBoxLayout(self)

        main.setContentsMargins(
            22, 18, 22, 15
        )

        main.setSpacing(
            10
        )

        # ---------------------------------------------------------------
        # HEADER
        # ---------------------------------------------------------------
        header = QFrame()

        header.setFixedHeight(
            76
        )

        header.setStyleSheet(
            """
            QFrame {
                background: rgba(255,255,255,240);
                border: 1px solid #BAE6FD;
                border-radius: 18px;
            }
            """
        )

        header_layout = QHBoxLayout(
            header
        )

        header_layout.setContentsMargins(
            18, 10, 18, 10
        )

        title_box = QVBoxLayout()

        title = QLabel(
            "SCHOOL OPERATION CALENDAR"
        )

        title.setFont(
            QFont(
                "Segoe UI",
                22,
                QFont.Weight.Bold
            )
        )

        title.setStyleSheet(
            f"""
            color: {BLUE_DARK};
            border: none;
            """
        )

        subtitle = QLabel(
            "SOS HGS School Gandaki  •  Academic Year 2083 (2026-27)"
        )

        subtitle.setFont(
            QFont(
                "Segoe UI",
                8,
                QFont.Weight.Medium
            )
        )

        subtitle.setStyleSheet(
            """
            color: #64748B;
            border: none;
            """
        )

        title_box.addWidget(
            title
        )

        title_box.addWidget(
            subtitle
        )

        header_layout.addLayout(
            title_box
        )

        header_layout.addStretch()

        nepali_year = QLabel(
            "ने. सं. २०८३"
        )

        nepali_year.setFont(
            QFont(
                "Noto Sans Devanagari",
                9,
                QFont.Weight.Bold
            )
        )

        nepali_year.setStyleSheet(
            f"""
            color: {BLUE_DARK};
            background: #E0F2FE;
            padding: 8px 12px;
            border-radius: 8px;
            border: none;
            """
        )

        header_layout.addWidget(
            nepali_year
        )

        back_button = QPushButton(
            "←  Back to Dashboard"
        )

        back_button.setFixedHeight(
            36
        )

        back_button.setFont(
            QFont(
                "Segoe UI",
                8,
                QFont.Weight.Bold
            )
        )

        back_button.setStyleSheet(
            """
            QPushButton {
                color: #0284C7;
                background: #F0F9FF;
                border: 1px solid #BAE6FD;
                border-radius: 9px;
                padding: 0 12px;
            }

            QPushButton:hover {
                background: #E0F2FE;
                border-color: #7DD3FC;
            }
            """
        )

        back_button.clicked.connect(
            self.go_back
        )

        header_layout.addWidget(
            back_button
        )

        main.addWidget(
            header
        )

        # ---------------------------------------------------------------
        # NAVIGATION
        # ---------------------------------------------------------------
        navigation = QFrame()

        navigation.setFixedHeight(
            82
        )

        navigation.setStyleSheet(
            """
            QFrame {
                background: rgba(255,255,255,230);
                border: 1px solid #D7EFFB;
                border-radius: 15px;
            }
            """
        )

        nav = QHBoxLayout(
            navigation
        )

        nav.setContentsMargins(
            10, 4, 10, 4
        )

        self.prev = QPushButton("‹")
        self.next = QPushButton("›")

        for btn in [
            self.prev,
            self.next
        ]:
            btn.setFixedSize(
                42,
                42
            )

            btn.setFont(
                QFont(
                    "Segoe UI",
                    20,
                    QFont.Weight.Bold
                )
            )

            btn.setStyleSheet(
                """
                QPushButton {
                    color: #0284C7;
                    background: #E0F2FE;
                    border: none;
                    border-radius: 9px;
                }

                QPushButton:hover {
                    background: #BAE6FD;
                }
                """
            )

        self.prev.clicked.connect(
            self.previous_month
        )

        self.next.clicked.connect(
            self.next_month
        )

        nav.addWidget(
            self.prev
        )

        center = QVBoxLayout()

        center.setContentsMargins(
            0, 0, 0, 0
        )

        center.setSpacing(
            2
        )

        self.month_title = QLabel()

        self.month_title.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.month_title.setFont(
            QFont(
                "Noto Sans Devanagari",
                15,
                QFont.Weight.Bold
            )
        )

        self.month_title.setStyleSheet(
            f"""
            color: {BLUE_DARK};
            border: none;
            padding: 0px;
            """
        )

        self.month_subtitle = QLabel()

        self.month_subtitle.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.month_subtitle.setFont(
            QFont(
                "Segoe UI",
                8
            )
        )

        self.month_subtitle.setStyleSheet(
            """
            color: #64748B;
            border: none;
            padding: 0px;
            """
        )

        center.addWidget(
            self.month_title
        )

        center.addWidget(
            self.month_subtitle
        )

        nav.addLayout(
            center,
            1
        )

        today_button = QPushButton(
            "Today"
        )

        today_button.setFixedHeight(
            34
        )

        today_button.setFont(
            QFont(
                "Segoe UI",
                8,
                QFont.Weight.Bold
            )
        )

        today_button.setStyleSheet(
            """
            QPushButton {
                color: white;
                background: #0284C7;
                border: none;
                border-radius: 8px;
                padding: 0 14px;
            }

            QPushButton:hover {
                background: #0369A1;
            }
            """
        )

        today_button.clicked.connect(
            self.go_today
        )

        nav.addWidget(
            today_button
        )

        nav.addWidget(
            self.next
        )

        main.addWidget(
            navigation
        )

        # ---------------------------------------------------------------
        # CONTENT
        # ---------------------------------------------------------------
        content = QHBoxLayout()

        content.setSpacing(
            12
        )

        calendar = QFrame()

        calendar.setStyleSheet(
            """
            QFrame {
                background: #DFF3FC;
                border: 1px solid #BAE6FD;
                border-radius: 18px;
            }
            """
        )

        calendar_layout = QVBoxLayout(
            calendar
        )

        calendar_layout.setContentsMargins(
            10,
            10,
            10,
            10
        )

        self.grid = QGridLayout()

        self.grid.setSpacing(
            5
        )

        calendar_layout.addLayout(
            self.grid
        )

        content.addWidget(
            calendar,
            4
        )

        # ---------------------------------------------------------------
        # SIDEBAR
        # ---------------------------------------------------------------
        sidebar = QFrame()

        sidebar.setFixedWidth(
            350
        )

        sidebar.setStyleSheet(
            """
            QFrame {
                background: rgba(255,255,255,230);
                border: 1px solid #BAE6FD;
                border-radius: 18px;
            }
            """
        )

        sidebar_layout = QVBoxLayout(
            sidebar
        )

        sidebar_layout.setContentsMargins(
            9,
            9,
            9,
            9
        )

        sidebar_layout.setSpacing(
            8
        )

        self.holiday_panel = QWidget()
        self.event_panel = QWidget()

        self.holiday_layout = QVBoxLayout(
            self.holiday_panel
        )

        self.event_layout = QVBoxLayout(
            self.event_panel
        )

        self.holiday_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        self.event_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        sidebar_layout.addWidget(
            self.holiday_panel,
            1
        )

        sidebar_layout.addWidget(
            self.event_panel,
            1
        )

        self.summary_panel = SummaryPanel(
            self.month
        )

        sidebar_layout.addWidget(
            self.summary_panel
        )

        content.addWidget(
            sidebar
        )

        main.addLayout(
            content,
            1
        )

        # ---------------------------------------------------------------
        # FOOTER
        # ---------------------------------------------------------------
        footer = QHBoxLayout()

        legend = QLabel(
            "■ Holidays    ■ Events    ■ Today"
        )

        legend.setFont(
            QFont(
                "Segoe UI",
                7,
                QFont.Weight.Bold
            )
        )

        legend.setStyleSheet(
            """
            color: #64748B;
            border: none;
            """
        )

        footer.addWidget(
            legend
        )

        footer.addStretch()

        current = QLabel(
            datetime.date.today().strftime(
                "%d %B %Y"
            )
        )

        current.setFont(
            QFont(
                "Segoe UI",
                7,
                QFont.Weight.Bold
            )
        )

        current.setStyleSheet(
            f"""
            color: {BLUE};
            border: none;
            """
        )

        footer.addWidget(
            current
        )

        main.addLayout(
            footer
        )

    def clear(self, layout):
        while layout.count():
            item = layout.takeAt(0)

            if item.widget():
                item.widget().deleteLater()

    def show_month(self, month):
        self.month = month

        self.month_title.setText(
            f"{BS_MONTHS[month - 1]} "
            f"{nepali_number(2083)}"
        )

        self.month_subtitle.setText(
            f"{BS_MONTHS_EN[month - 1]} 2083   •   "
            f"{MONTH_GREGORIAN_RANGES[month]}"
        )

        self.clear(
            self.grid
        )

        # ---------------------------------------------------------------
        # DAY NAMES
        # Sunday and Saturday = dark red
        # Other weekdays = blue
        # ---------------------------------------------------------------
        for col, name in enumerate(
            DAY_NAMES
        ):
            label = QLabel(name)

            label.setAlignment(
                Qt.AlignmentFlag.AlignCenter
            )

            label.setFixedHeight(
                29
            )

            label.setFont(
                QFont(
                    "Noto Sans Devanagari",
                    8,
                    QFont.Weight.Bold
                )
            )

            if col in (0, 6):
                day_color = RED
            else:
                day_color = BLUE

            label.setStyleSheet(
                f"""
                QLabel {{
                    color: {day_color};
                    background: #FFFFFF;
                    border-radius: 7px;
                }}
                """
            )

            self.grid.addWidget(
                label,
                0,
                col
            )

        # ---------------------------------------------------------------
        # MONTH GRID
        # ---------------------------------------------------------------
        start = MONTH_START_AD[month]

        # Python weekday:
        # Monday = 0 ... Sunday = 6
        # Calendar begins Sunday.
        offset = (
            start.weekday() + 1
        ) % 7

        total = BS_MONTH_DAYS[
            month - 1
        ]

        rows_needed = math.ceil(
            (offset + total) / 7
        )

        compact = (
            rows_needed >= 6
        )

        for day in range(
            1,
            total + 1
        ):
            pos = (
                offset +
                day -
                1
            )

            self.grid.addWidget(
                DateCell(
                    month,
                    day,
                    compact
                ),
                (pos // 7) + 1,
                pos % 7
            )

        for col in range(7):
            self.grid.setColumnStretch(
                col,
                1
            )

        row_height = (
            64
            if rows_needed >= 6
            else 86
        )

        for r in range(1, 7):
            self.grid.setRowStretch(
                r,
                1
            )

            self.grid.setRowMinimumHeight(
                r,
                row_height
            )

        self.update_panels(
            month
        )

        self.prev.setEnabled(
            month > 1
        )

        self.next.setEnabled(
            month < 12
        )

    def update_panels(self, month):
        self.clear(
            self.holiday_layout
        )

        self.clear(
            self.event_layout
        )

        holiday_events = (
            HOLIDAY_PANEL_OVERRIDES.get(
                month
            )
        )

        if holiday_events is None:
            holiday_events = (
                group_consecutive_events(
                    HOLIDAYS.get(
                        month,
                        {}
                    )
                )
            )

        self.holiday_layout.addWidget(
            EventPanel(
                "LEAVE / HOLIDAYS",
                holiday_events,
                RED,
                "●"
            )
        )

        event_events = (
            group_consecutive_events(
                ACTIVITIES.get(
                    month,
                    {}
                )
            )
        )

        self.event_layout.addWidget(
            EventPanel(
                "EVENT DAYS",
                event_events,
                GREEN,
                "●"
            )
        )

        sidebar_layout = (
            self.summary_panel
            .parentWidget()
            .layout()
        )

        if sidebar_layout:
            idx = sidebar_layout.indexOf(
                self.summary_panel
            )

            sidebar_layout.removeWidget(
                self.summary_panel
            )

            self.summary_panel.deleteLater()

            self.summary_panel = SummaryPanel(
                month
            )

            sidebar_layout.insertWidget(
                idx,
                self.summary_panel
            )

    def previous_month(self):
        if self.month > 1:
            self.show_month(
                self.month - 1
            )

    def next_month(self):
        if self.month < 12:
            self.show_month(
                self.month + 1
            )

    def go_today(self):
        self.show_month(
            current_bs_month()
        )

    def go_back(self):
        if self.previous_window:
            self.previous_window.show()
            self.previous_window.raise_()
            self.previous_window.activateWindow()

        self.close()

    def closeEvent(self, event):
        if self.previous_window:
            self.previous_window.show()
            self.previous_window.raise_()
            self.previous_window.activateWindow()

        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    app.setApplicationName(
        "SOS HGS School Gandaki - School Operation Calendar"
    )

    app.setFont(
        QFont(
            "Segoe UI",
            9
        )
    )

    window = CalendarWindow()
    window.show()

    sys.exit(app.exec())
