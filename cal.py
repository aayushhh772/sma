import sys
import datetime
import math

from PyQt6.QtCore import Qt, QTimer, QRectF
from PyQt6.QtGui import QFont, QColor, QPainter, QLinearGradient
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QGridLayout,
    QScrollArea,
    QSizePolicy
)


BS_MONTHS = [
    "वैशाख",
    "जेठ",
    "असार",
    "साउन",
    "भदौ",
    "असोज",
    "कार्तिक",
    "मंसिर",
    "पुष",
    "माघ",
    "फागुन",
    "चैत"
]

BS_MONTHS_EN = [
    "Baishakh",
    "Jestha",
    "Asar",
    "Shrawan",
    "Bhadra",
    "Asoj",
    "Kartik",
    "Mangsir",
    "Poush",
    "Magh",
    "Falgun",
    "Chaitra"
]

BS_MONTH_DAYS = [
    31,
    32,
    32,
    31,
    31,
    30,
    30,
    30,
    29,
    29,
    30,
    30
]


MONTH_START_AD = {
    1: datetime.date(2026, 4, 14),
    2: datetime.date(2026, 5, 15),
    3: datetime.date(2026, 6, 15),
    4: datetime.date(2026, 7, 17),
    5: datetime.date(2026, 8, 17),
    6: datetime.date(2026, 9, 17),
    7: datetime.date(2026, 10, 17),
    8: datetime.date(2026, 11, 16),
    9: datetime.date(2026, 12, 16),
    10: datetime.date(2027, 1, 15),
    11: datetime.date(2027, 2, 13),
    12: datetime.date(2027, 3, 15)
}


MONTH_END_AD = {
    1: datetime.date(2026, 5, 14),
    2: datetime.date(2026, 6, 14),
    3: datetime.date(2026, 7, 16),
    4: datetime.date(2026, 8, 16),
    5: datetime.date(2026, 9, 16),
    6: datetime.date(2026, 10, 16),
    7: datetime.date(2026, 11, 15),
    8: datetime.date(2026, 12, 15),
    9: datetime.date(2027, 1, 14),
    10: datetime.date(2027, 2, 12),
    11: datetime.date(2027, 3, 14),
    12: datetime.date(2027, 4, 13)
}


MONTH_GREGORIAN_RANGES = {
    1: "April / May 2026",
    2: "May / June 2026",
    3: "June / July 2026",
    4: "July / August 2026",
    5: "August / September 2026",
    6: "September / October 2026",
    7: "October / November 2026",
    8: "November / December 2026",
    9: "December 2026 / January 2027",
    10: "January / February 2027",
    11: "February / March 2027",
    12: "March / April 2027"
}


HOLIDAYS = {
    1: {
        1: "नयाँ वर्ष २०८३",
        18: "अन्तर्राष्ट्रिय मजदुर दिवस / बुद्ध जयन्ती"
    },

    2: {
        15: "गणतन्त्र दिवस"
    },

    3: {
        28: "भानु जयन्ती",
        30: "गर्मी बिदा",
        31: "गर्मी बिदा",
        32: "गर्मी बिदा"
    },

    4: {
        1: "गर्मी बिदा"
    },

    5: {
        12: "जनैपूर्णिमा",
        18: "श्रीकृष्ण जन्माष्टमी",
        28: "हरितालिका तीज"
    },

    6: {
        25: "घटस्थापना",
        26: "दशैँ बिदा",
        27: "दशैँ बिदा",
        28: "दशैँ बिदा",
        29: "दशैँ बिदा",
        30: "दशैँ बिदा"
    },

    7: {
        1: "दशैँ बिदा",
        2: "दशैँ बिदा",
        3: "दशैँ बिदा",
        4: "दशैँ बिदा",
        5: "दशैँ बिदा",
        6: "दशैँ बिदा",
        7: "दशैँ बिदा",
        8: "कोजाग्रत पूर्णिमा",
        9: "तिहार बिदा",
        10: "तिहार बिदा",
        11: "तिहार बिदा",
        12: "तिहार बिदा",
        13: "तिहार बिदा",
        14: "तिहार बिदा",
        15: "तिहार बिदा",
        16: "तिहार बिदा",
        17: "तिहार बिदा",
        18: "तिहार बिदा",
        19: "तिहार बिदा",
        20: "तिहार बिदा",
        21: "तिहार बिदा",
        22: "तिहार बिदा",
        23: "तिहार बिदा",
        24: "तिहार बिदा",
        25: "तिहार बिदा",
        26: "तिहार बिदा",
        27: "छठ पर्व"
    },

    8: {},

    9: {
        9: "उधौली पर्व",
        10: "क्रिसमस डे",
        15: "तमु ल्होसार",
        27: "पृथ्वी जयन्ती",
        28: "जाडो बिदा",
        29: "जाडो बिदा",
        30: "जाडो बिदा"
    },

    10: {
        4: "जाडो बिदा",
        5: "जाडो बिदा",
        16: "सहिद दिवस",
        22: "गण्डकी प्रदेश स्थापना दिवस",
        24: "सोनाम ल्होसार"
    },

    11: {
        7: "प्रजातन्त्र दिवस",
        24: "अन्तर्राष्ट्रिय महिला दिवस",
        25: "महाशिवरात्रि"
    },

    12: {
        7: "फागु पूर्णिमा / होली",
        24: "वार्षिक बिदा",
        25: "वार्षिक बिदा",
        26: "वार्षिक बिदा",
        27: "वार्षिक बिदा",
        28: "वार्षिक बिदा",
        29: "वार्षिक बिदा",
        30: "वार्षिक बिदा"
    }
}


ACTIVITIES = {
    1: {
        15: "School Opening Day for Teachers (PDP)",
        21: "School Opening Day for Students",
        31: "Creative Writing in English (III–X)"
    },

    2: {
        22: "Speech Competition in English (VI–VII)",
        24: "Parents' Meeting for Grade VI and X",
        26: "First Unit Test (Nur–X)",
        27: "First Unit Test (Nur–X)",
        28: "First Unit Test (Nur–X)",
        29: "First Unit Test (Nur–X)"
    },

    3: {
        1: "School Opening Day for Grade XII",
        2: "English Handwriting Competition (III–VIII)",
        4: "School Opening Day for Grade XI",
        5: "Creative Writing in Nepali (III–X)",
        11: "English Handwriting Competition (Nursery–KG)",
        18: "Speech Competition in English (VIII–X)",
        19: "Nepali Handwriting Competition (I–II)",
        23: "Nepali Handwriting Competition (III–VIII)",
        26: "Speech Competition in Nepali (VIII–X)"
    },

    4: {
        4: "School Re-opens",
        5: "Nepali Handwriting Competition (Nursery–KG)",
        8: "Scrabble Competition (VI–X)",
        11: "First Term Exam (Nursery–X)",
        12: "First Term Exam (Nursery–X)",
        13: "First Term Exam (Nursery–X)",
        14: "First Term Exam (Nursery–X)",
        15: "First Term Exam (Nursery–X)",
        16: "First Term Exam (Nursery–X)",
        17: "First Term Exam (Nursery–X)",
        18: "First Term Exam (Nursery–X)",
        19: "First Term Exam (Nursery–X)",
        20: "First Term Exam (Nursery–X)",
        22: "Creative Writing in English (XI–XII)",
        29: "Creative Writing in Nepali (XI–XII)"
    },

    5: {
        1: "Spelling Contest (III–V)",
        2: "Rhymes Competition (Nursery–KG)",
        5: "First Term Result Day (Nursery–X)",
        8: "Spelling Contest (VI–VII)",
        15: "Speech Competition in Nepali (XI–XII)",
        22: "Maths Race (KG) / Handball Competition Girls (V–VII)",
        24: "Drawing Competition (I–II)",
        26: "Junior Talent Show",
        31: "Uni Hockey Boys/Girls (VI–VII)"
    },

    6: {
        1: "Speech Competition in English (XI–XII)",
        3: "Cricket Tournament Boys (XI–XII)",
        5: "Second Unit Test Upto Grade X",
        6: "Second Unit Test Upto Grade X",
        7: "Second Unit Test Upto Grade X",
        8: "Second Unit Test Upto Grade X",
        10: "Volleyball Competition Boys/Girls (VIII–X)",
        11: "Cricket Tournament Boys (VIII–X) / Badminton Competition Girls (XI–XII)",
        12: "Maths, Science and IT Quiz (III–V) - Maths Dept",
        14: "Maths Race (Nursery)",
        12: "Maths, Science and IT Quiz (III–V) - Maths Dept",
        22: "Quiz Contest (KG)",
        23: "Story Telling Competition in English and Nepali (I–II)",
        27: "First Term Result Day (XI & XII)",
        28: "Senior Talent Show",
        5: "Second Unit Test Upto Grade X",
        6: "Second Unit Test Upto Grade X",
        7: "Second Unit Test Upto Grade X",
        8: "Second Unit Test Upto Grade X",
        10: "Volleyball Competition Boys/Girls (VIII–X)",
        11: "Cricket Tournament Boys (VIII–X) / Badminton Competition Girls (XI–XII)",
        12: "Maths, Science and IT Quiz (III–V) - Maths Dept",
        14: "Maths Race (Nursery)",
        22: "Quiz Contest (KG)",
        23: "Story Telling Competition in English and Nepali (I–II)",
        27: "First Term Result Day (XI & XII)",
        28: "Senior Talent Show"
    },

    7: {
        30: "School Reopens"
    },

    8: {
        4: "Maths, Science and IT Quiz (VIII–X)",
        5: "Volleyball Competition Boys/Girls (XI–XII)",
        12: "Basketball Competition Boys/Girls (XI–XII)",
        14: "Second Term Exam (Nur–X)",
        15: "Second Term Exam (Nur–X)",
        16: "Second Term Exam (Nur–X)",
        17: "Second Term Exam (Nur–X)",
        18: "Second Term Exam (Nur–X)",
        19: "Second Term Exam (Nur–X)",
        20: "Second Term Exam (Nur–X)",
        21: "Second Term Exam (Nur–X)",
        24: "English Spelling Contest (Nursery–KG)",
        26: "Basketball Competition Boys/Girls (VIII–X)",
        29: "Second Term Result Day (Nursery–X)"
    },

    9: {
        1: "Maths, Science and IT Quiz (III–V) - Computer Dept",
        4: "Science Exhibition",
        5: "Football Competition Boys (XI–XII)",
        8: "Nepali Shruti Lekhan Competition (Nursery–KG)",
        14: "Memory Game (KG)",
        17: "Steam General Quiz (XI–XII)",
        23: "Annual Sports Meet",
        24: "Annual Sports Meet",
        25: "Annual Sports Meet"
    },

    10: {
        6: "School Reopens",
        7: "Second Term Exam (Grade XI–XII)",
        8: "Webpage Designing Competition (IX–X)",
        9: "Second Term Exam (Grade XI–XII)",
        10: "Second Term Exam (Grade XI–XII)",
        11: "Second Term Exam (Grade XI–XII)",
        12: "Memory Game (I–II)",
        13: "Webpage Designing Competition (VI–VIII)",
        15: "Eco RU Fest (VI–X)",
        21: "Creative Writing in Nepali (I–II)",
        25: "Webpage Designing Competition (XI–XII)",
        26: "Second Term Result Day (XI–XII)",
        29: "Creative Writing in English (I–II)"
    },

    11: {
        6: "Webpage Designing Competition (XI–XII)"
    },

    12: {
        1: "Pre-Board Exam (Grade XI–XII)",
        2: "Pre-Board Exam (Grade XI–XII)",
        3: "Pre-Board Exam (Grade XI–XII)",
        4: "Pre-Board Exam (Grade XI–XII)",
        5: "Pre-Board Exam (Grade XI–XII)",
        6: "Pre-Board Exam (Grade XI–XII)",
        7: "Pre-Board Exam (Grade XI–XII)",
        8: "Annual Exam (Nur–VII, IX)",
        9: "Annual Exam (Nur–VII, IX)",
        10: "Annual Exam (Nur–VII, IX)",
        11: "Annual Exam (Nur–VII, IX)",
        12: "Annual Exam (Nur–VII, IX)",
        13: "Annual Exam (Nur–VII, IX)",
        14: "Annual Exam (Nur–VII, IX)",
        15: "Annual Exam (Nur–VII, IX)",
        16: "Annual Exam (Nur–VII, IX)",
        17: "Annual Exam (Nur–VII, IX)",
        23: "Annual Result Day (Nur–VII, IX)"
    }
}


MONTH_SUMMARIES = {
    1: ("12", "9", "13"),
    2: ("20", "20", "1"),
    3: ("20", "20", "3"),
    4: ("20", "12", "1"),
    5: ("20", "20", "3"),
    6: ("20", "19", "1"),
    7: ("1", "1", "10"),
    8: ("21", "13", "0"),
    9: ("16", "13", "4"),
    10: ("17", "17", "3"),
    11: ("17", "17", "3"),
    12: ("17", "5", "8")
}


DAY_NAMES = [
    "सोमबार",
    "मंगलबार",
    "बुधबार",
    "बिहीबार",
    "शुक्रबार",
    "शनिबार",
    "आइतबार"
]


NEPALI_DIGITS = str.maketrans(
    "0123456789",
    "०१२३४५६७८९"
)


def nepali_number(number):
    return str(number).translate(NEPALI_DIGITS)


def gregorian_date(month, day):
    return MONTH_START_AD[month] + datetime.timedelta(days=day - 1)


def current_bs_month():
    today = datetime.date.today()

    for month in range(1, 13):
        if MONTH_START_AD[month] <= today <= MONTH_END_AD[month]:
            return month

    if today < MONTH_START_AD[1]:
        return 1

    return 12


def group_consecutive_events(events):
    if not events:
        return []

    days = sorted(events.keys())
    groups = []

    start = days[0]
    previous = days[0]
    current_name = events[start]

    for day in days[1:]:
        if day == previous + 1 and events[day] == current_name:
            previous = day
        else:
            groups.append((start, previous, current_name))
            start = day
            previous = day
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

        painter.setRenderHint(
            QPainter.RenderHint.Antialiasing
        )

        gradient = QLinearGradient(
            0,
            0,
            self.width(),
            self.height()
        )

        gradient.setColorAt(
            0,
            QColor("#E0F2FE")
        )

        gradient.setColorAt(
            0.5,
            QColor("#F8FDFF")
        )

        gradient.setColorAt(
            1,
            QColor("#E0F2FE")
        )

        painter.fillRect(
            self.rect(),
            gradient
        )

        painter.setPen(Qt.PenStyle.NoPen)

        for index, (x, y, size) in enumerate(self.bubbles):
            dx = math.sin(
                self.phase * 0.008 + index
            ) * 22

            dy = math.cos(
                self.phase * 0.006 + index
            ) * 18

            painter.setBrush(
                QColor(125, 211, 252, 32)
            )

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

        self.holiday = (
            HOLIDAYS
            .get(month, {})
            .get(day)
        )

        self.activity = (
            ACTIVITIES
            .get(month, {})
            .get(day)
        )

        self.today = (
            self.ad_date == datetime.date.today()
        )

        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )

        if compact:
            self.setMinimumHeight(60)
        else:
            self.setMinimumHeight(0)

        layout = QVBoxLayout(self)

        if compact:
            layout.setContentsMargins(6, 3, 6, 3)
        else:
            layout.setContentsMargins(8, 5, 7, 5)

        layout.setSpacing(0)

        top = QHBoxLayout()

        self.number = QLabel(
            nepali_number(day)
        )

        number_size = 20 if compact else 24

        self.number.setFont(
            QFont(
                "Noto Sans Devanagari",
                number_size,
                QFont.Weight.Black
            )
        )

        top.addWidget(self.number)
        top.addStretch()

        if self.today:
            badge = QLabel("TODAY")

            badge.setFont(
                QFont(
                    "Segoe UI",
                    6 if compact else 7,
                    QFont.Weight.Bold
                )
            )

            badge.setStyleSheet(
                """
                QLabel {
                    color: white;
                    background: transparent;
                    border: none;
                    padding: 1px 3px;
                }
                """
            )

            top.addWidget(badge)

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

        layout.addWidget(self.gregorian)

        self.update_style()

    def update_style(self):
        bg = "#FFFFFF"
        border = "#D8F0FC"

        number = "#0284C7"
        greg = "#64748B"

        weekday = self.ad_date.weekday()

        is_saturday = weekday == 5
        is_sunday = weekday == 6

        if self.holiday:
            number = "#C1121F"
            greg = "#C1121F"

        elif self.activity:
            number = "#15803D"
            greg = "#15803D"

        elif is_saturday or is_sunday:
            number = "#C1121F"
            greg = "#C1121F"

        if self.today:
            bg = "#0284C7"
            border = "#0369A1"
            number = "#FFFFFF"
            greg = "#FFFFFF"

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
                color: {number};
                background: transparent;
                border: none;
            }}
            """
        )

        self.gregorian.setStyleSheet(
            f"""
            QLabel {{
                color: {greg};
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

        if start == end:
            date_text = nepali_number(start)
        else:
            date_text = (
                f"{nepali_number(start)}"
                f"–"
                f"{nepali_number(end)}"
            )

        date_label = QLabel(date_text)

        date_label.setFixedSize(52, 36)

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
            QLabel {{
                color: {accent};
                background: #FFFFFF;
                border: none;
                border-radius: 8px;
                padding: 0px;
                font-size: 13px;
                font-weight: 900;
            }}
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
            QLabel {{
                color: {accent};
                border: none;
                background: transparent;
                padding: 1px;
            }}
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
            QLabel {{
                color: {accent};
                background: transparent;
                border: none;
            }}
            """
        )

        layout.addWidget(label)


class EventPanel(QFrame):
    def __init__(
        self,
        title,
        events,
        accent,
        symbol
    ):
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

        header.addWidget(icon)

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
            QLabel {{
                color: {accent};
                border: none;
            }}
            """
        )

        header.addWidget(label)
        header.addStretch()

        count = QLabel(str(len(events)))

        count.setFixedSize(28, 24)

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
            QLabel {{
                color: {accent};
                background: #F0F9FF;
                border: none;
                border-radius: 7px;
            }}
            """
        )

        header.addWidget(count)

        layout.addLayout(header)

        line = QFrame()

        line.setFixedHeight(1)

        line.setStyleSheet(
            """
            background: #E0F2FE;
            border: none;
            """
        )

        layout.addWidget(line)

        scroll = QScrollArea()

        scroll.setWidgetResizable(True)

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
            """
            QWidget {
                background: transparent;
            }
            """
        )

        container_layout = QVBoxLayout(container)

        container_layout.setContentsMargins(
            0, 0, 3, 0
        )

        container_layout.setSpacing(6)

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
            if accent == "#C1121F":
                empty_text = "No holidays scheduled this month."
            else:
                empty_text = "No events scheduled this month."

            container_layout.addWidget(
                EmptyEventRow(
                    empty_text,
                    accent
                )
            )

        container_layout.addStretch()

        scroll.setWidget(container)

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
            """
            color: #0369A1;
            border: none;
            """
        )

        layout.addWidget(title)

        working, teaching, holidays = (
            MONTH_SUMMARIES[month]
        )

        values = [
            ("Working Days", working),
            ("Teaching Days", teaching),
            ("Holidays", holidays)
        ]

        for name, value in values:
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
                """
                color: #0284C7;
                border: none;
                """
            )

            row.addWidget(name_label)
            row.addStretch()
            row.addWidget(value_label)

            layout.addLayout(row)


class CalendarWindow(QWidget):
    def __init__(self, previous_window=None):
        super().__init__()

        self.previous_window = previous_window

        self.month = current_bs_month()

        self.setWindowTitle(
            "SMA Academic Calendar"
        )

        self.setMinimumSize(
            1200,
            720
        )

        self.resize(
            1400,
            820
        )

        self.background = BubbleBackground(self)

        self.background.lower()

        self.build_ui()

        self.show_month(self.month)

    def resizeEvent(self, event):
        self.background.resize(
            self.size()
        )

        super().resizeEvent(event)

    def build_ui(self):
        main = QVBoxLayout(self)

        main.setContentsMargins(
            22, 18, 22, 15
        )

        main.setSpacing(10)

        header = QFrame()

        header.setFixedHeight(76)

        header.setStyleSheet(
            """
            QFrame {
                background: rgba(255,255,255,240);
                border: 1px solid #BAE6FD;
                border-radius: 18px;
            }
            """
        )

        header_layout = QHBoxLayout(header)

        header_layout.setContentsMargins(
            18, 10, 18, 10
        )

        title_box = QVBoxLayout()

        title = QLabel(
            "Academic Calendar"
        )

        title.setFont(
            QFont(
                "Segoe UI",
                22,
                QFont.Weight.Bold
            )
        )

        title.setStyleSheet(
            """
            color: #0369A1;
            border: none;
            """
        )

        subtitle = QLabel(
            "SMA  •  B.S. २०८३  •  Academic Year 2026–2027"
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

        title_box.addWidget(title)
        title_box.addWidget(subtitle)

        header_layout.addLayout(title_box)
        header_layout.addStretch()

        nepali_year = QLabel(
            "ने.सं. ११४६ / ११४७"
        )

        nepali_year.setFont(
            QFont(
                "Noto Sans Devanagari",
                9,
                QFont.Weight.Bold
            )
        )

        nepali_year.setStyleSheet(
            """
            QLabel {
                color: #0369A1;
                background: #E0F2FE;
                padding: 8px 12px;
                border-radius: 8px;
                border: none;
            }
            """
        )

        header_layout.addWidget(nepali_year)

        back_button = QPushButton(
            "←  Back to Dashboard"
        )

        back_button.setFixedHeight(36)

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

        header_layout.addWidget(back_button)

        main.addWidget(header)

        navigation = QFrame()

        navigation.setFixedHeight(60)

        navigation.setStyleSheet(
            """
            QFrame {
                background: rgba(255,255,255,230);
                border: 1px solid #D7EFFB;
                border-radius: 15px;
            }
            """
        )

        nav = QHBoxLayout(navigation)

        nav.setContentsMargins(
            10, 7, 10, 7
        )

        self.prev = QPushButton("‹")
        self.next = QPushButton("›")

        self.prev.setFixedSize(38, 38)
        self.next.setFixedSize(38, 38)

        for button in [self.prev, self.next]:
            button.setFont(
                QFont(
                    "Segoe UI",
                    20,
                    QFont.Weight.Bold
                )
            )

            button.setStyleSheet(
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

        nav.addWidget(self.prev)

        center = QVBoxLayout()

        self.month_title = QLabel()

        self.month_title.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.month_title.setFont(
            QFont(
                "Noto Sans Devanagari",
                16,
                QFont.Weight.Bold
            )
        )

        self.month_title.setStyleSheet(
            """
            color: #0369A1;
            border: none;
            """
        )

        self.month_subtitle = QLabel()

        self.month_subtitle.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.month_subtitle.setFont(
            QFont(
                "Segoe UI",
                7
            )
        )

        self.month_subtitle.setStyleSheet(
            """
            color: #64748B;
            border: none;
            """
        )

        center.addWidget(
            self.month_title
        )

        center.addWidget(
            self.month_subtitle
        )

        nav.addLayout(center, 1)

        today_button = QPushButton(
            "Today"
        )

        today_button.setFixedHeight(34)

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

        nav.addWidget(today_button)
        nav.addWidget(self.next)

        main.addWidget(navigation)

        content = QHBoxLayout()

        content.setSpacing(12)

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

        calendar_layout = QVBoxLayout(calendar)

        calendar_layout.setContentsMargins(
            10, 10, 10, 10
        )

        self.grid = QGridLayout()

        self.grid.setSpacing(5)

        calendar_layout.addLayout(
            self.grid
        )

        content.addWidget(
            calendar,
            4
        )

        sidebar = QFrame()

        sidebar.setFixedWidth(350)

        sidebar.setStyleSheet(
            """
            QFrame {
                background: rgba(255,255,255,230);
                border: 1px solid #BAE6FD;
                border-radius: 18px;
            }
            """
        )

        sidebar_layout = QVBoxLayout(sidebar)

        sidebar_layout.setContentsMargins(
            9, 9, 9, 9
        )

        sidebar_layout.setSpacing(8)

        self.holiday_panel = QWidget()

        self.holiday_layout = QVBoxLayout(
            self.holiday_panel
        )

        self.holiday_layout.setContentsMargins(
            0, 0, 0, 0
        )

        self.event_panel = QWidget()

        self.event_layout = QVBoxLayout(
            self.event_panel
        )

        self.event_layout.setContentsMargins(
            0, 0, 0, 0
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

        content.addWidget(sidebar)

        main.addLayout(
            content,
            1
        )

        footer = QHBoxLayout()

        legend = QLabel(
            "■ Holidays    "
            "■ Events    "
            "■ Today"
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
            QLabel {
                color: #64748B;
                border: none;
            }
            """
        )

        footer.addWidget(legend)
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
            """
            QLabel {
                color: #0284C7;
                border: none;
            }
            """
        )

        footer.addWidget(current)

        main.addLayout(footer)

    def clear(self, layout):
        while layout.count():
            item = layout.takeAt(0)

            widget = item.widget()

            if widget:
                widget.deleteLater()

    def show_month(self, month):
        self.month = month

        self.month_title.setText(
            f"{BS_MONTHS[month - 1]} "
            f"{nepali_number(2083)}"
        )

        self.month_subtitle.setText(
            f"{BS_MONTHS_EN[month - 1]} 2083"
            f"   •   "
            f"{MONTH_GREGORIAN_RANGES[month]}"
        )

        self.clear(self.grid)

        for column, name in enumerate(DAY_NAMES):
            label = QLabel(name)

            label.setAlignment(
                Qt.AlignmentFlag.AlignCenter
            )

            label.setFixedHeight(29)

            label.setFont(
                QFont(
                    "Noto Sans Devanagari",
                    8,
                    QFont.Weight.Bold
                )
            )

            if column in (5, 6):
                label.setStyleSheet(
                    """
                    QLabel {
                        color: #C1121F;
                        background: #FFFFFF;
                        border-radius: 7px;
                    }
                    """
                )
            else:
                label.setStyleSheet(
                    """
                    QLabel {
                        color: #0369A1;
                        background: #FFFFFF;
                        border-radius: 7px;
                    }
                    """
                )

            self.grid.addWidget(
                label,
                0,
                column
            )

        start = MONTH_START_AD[month]

        offset = start.weekday()

        total = BS_MONTH_DAYS[month - 1]

        rows_needed = math.ceil(
            (offset + total) / 7
        )

        compact = rows_needed >= 6

        for day in range(1, total + 1):
            position = offset + day - 1

            row = (position // 7) + 1
            column = position % 7

            cell = DateCell(
                month,
                day,
                compact
            )

            self.grid.addWidget(
                cell,
                row,
                column
            )

        for column in range(7):
            self.grid.setColumnStretch(
                column,
                1
            )

        row_height = 64 if rows_needed >= 6 else 86

        for row in range(1, 7):
            self.grid.setRowStretch(
                row,
                1
            )

            self.grid.setRowMinimumHeight(
                row,
                row_height
            )

        self.update_panels(month)

        self.prev.setEnabled(month > 1)
        self.next.setEnabled(month < 12)

    def update_panels(self, month):
        self.clear(self.holiday_layout)
        self.clear(self.event_layout)

        holiday_groups = group_consecutive_events(
            HOLIDAYS.get(month, {})
        )

        event_groups = group_consecutive_events(
            ACTIVITIES.get(month, {})
        )

        holiday_widget = EventPanel(
            "LEAVE / HOLIDAYS",
            holiday_groups,
            "#C1121F",
            "●"
        )

        event_widget = EventPanel(
            "EVENT DAYS",
            event_groups,
            "#15803D",
            "●"
        )

        self.holiday_layout.addWidget(
            holiday_widget
        )

        self.event_layout.addWidget(
            event_widget
        )

        old_summary = self.summary_panel

        sidebar_layout = (
            old_summary
            .parentWidget()
            .layout()
        )

        if sidebar_layout:
            index = sidebar_layout.indexOf(
                old_summary
            )

            sidebar_layout.removeWidget(
                old_summary
            )

            old_summary.deleteLater()

            self.summary_panel = SummaryPanel(
                month
            )

            sidebar_layout.insertWidget(
                index,
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
        if self.previous_window is not None:
            self.previous_window.show()
            self.previous_window.raise_()
            self.previous_window.activateWindow()

        self.close()

    def closeEvent(self, event):
        if self.previous_window is not None:
            self.previous_window.show()
            self.previous_window.raise_()
            self.previous_window.activateWindow()

        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    app.setApplicationName(
        "SMA Academic Calendar"
    )

    app.setFont(
        QFont(
            "Segoe UI",
            9
        )
    )

    window = CalendarWindow()

    window.show()

    sys.exit(
        app.exec()
    )
