import datetime


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


HOLIDAYS = {
    1: {
        1: "नयाँवर्ष २०८३",
        18: "अन्तर्राष्ट्रिय मजदुर दिवस / बुद्ध जयन्ती"
    },

    2: {
        15: "गणतन्त्र दिवस"
    },

    3: {
        28: "भानुजयन्ती",
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
        26: "दशैँबिदा",
        27: "दशैँबिदा",
        28: "दशैँबिदा",
        29: "दशैँबिदा",
        30: "दशैँबिदा"
    },

    7: {
        1: "दशैँबिदा",
        2: "दशैँबिदा",
        3: "दशैँबिदा",
        4: "दशैँबिदा",
        5: "दशैँबिदा",
        6: "दशैँबिदा",
        7: "दशैँबिदा",
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
        7: "फागुपूर्णिमा / होली",
        24: "वार्षिक बिदा",
        25: "वार्षिक बिदा",
        26: "वार्षिक बिदा",
        27: "वार्षिक बिदा",
        28: "वार्षिक बिदा",
        29: "वार्षिक बिदा",
        30: "वार्षिक बिदा"
    }
}


def gregorian_date(
    month,
    day
):

    return (
        MONTH_START_AD[month]
        + datetime.timedelta(
            days=day - 1
        )
    )


def get_calendar_holiday_dates():

    holiday_dates = set()

    for month, holidays in HOLIDAYS.items():

        for day in holidays:

            holiday_dates.add(
                gregorian_date(
                    month,
                    day
                )
            )

    return holiday_dates


def is_calendar_holiday(
    check_date=None
):

    if check_date is None:

        check_date = datetime.date.today()

    if isinstance(
        check_date,
        datetime.datetime
    ):

        check_date = check_date.date()

    holiday_dates = (
        get_calendar_holiday_dates()
    )

    return check_date in holiday_dates


def is_weekend(
    check_date=None
):

    if check_date is None:

        check_date = datetime.date.today()

    if isinstance(
        check_date,
        datetime.datetime
    ):

        check_date = check_date.date()

    # Your calendar displays Saturday and Sunday
    # in red, so both are treated as non-working days.

    return check_date.weekday() in (
        5,
        6
    )


def is_school_holiday(
    check_date=None
):

    if check_date is None:

        check_date = datetime.date.today()

    if isinstance(
        check_date,
        datetime.datetime
    ):

        check_date = check_date.date()

    return (
        is_calendar_holiday(check_date)
        or
        is_weekend(check_date)
    )


def get_holiday_name(
    check_date=None
):

    if check_date is None:

        check_date = datetime.date.today()

    if isinstance(
        check_date,
        datetime.datetime
    ):

        check_date = check_date.date()

    for month, holidays in HOLIDAYS.items():

        for day, name in holidays.items():

            if gregorian_date(
                month,
                day
            ) == check_date:

                return name

    if is_weekend(check_date):

        return "Weekend"

    return None
