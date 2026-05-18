import flet as ft
from src.theme import AppTheme
from datetime import date, timedelta, datetime
from prayer_times_calculator_offline import PrayerTimesCalculator
import jdatetime


LATITUDE = 32.3989
LONGITUDE = 48.4223
TIMEZONE_OFFSET = 3.5

PRAYER_NAMES = {
    "Fajr": "صبح",
    "Sunrise": "طلوع آفتاب",
    "Dhuhr": "ظهر",
    "Asr": "عصر",
    "Maghrib": "مغرب",
    "Isha": "عشاء",
}

SHAMSI_YEARS = list(range(1400, 1430))
SHAMSI_MONTHS = [
    ("1", "فروردین"), ("2", "اردیبهشت"), ("3", "خرداد"),
    ("4", "تیر"), ("5", "مرداد"), ("6", "شهریور"),
    ("7", "مهر"), ("8", "آبان"), ("9", "آذر"),
    ("10", "دی"), ("11", "بهمن"), ("12", "اسفند"),
]


def get_days_in_month(year: int, month: int) -> list:
    if month <= 6:
        return list(range(1, 32))
    elif month <= 11:
        return list(range(1, 31))
    else:
        try:
            is_leap = jdatetime.date(year, 12, 30).day == 30
        except:
            is_leap = False
        return list(range(1, 31 if is_leap else 30))


def to_persian_numbers(text: str) -> str:
    if not text:
        return text
    english = "0123456789"
    persian = "۰۱۲۳۴۵۶۷۸۹"
    result = ""
    for char in str(text):
        if char in english:
            result += persian[english.index(char)]
        else:
            result += char
    return result


def iso_to_time(iso_str: str) -> str:
    if not iso_str or iso_str == "--:--":
        return "--:--"
    try:
        dt = datetime.fromisoformat(iso_str)
        local_dt = dt + timedelta(hours=TIMEZONE_OFFSET)
        return local_dt.strftime("%H:%M")
    except:
        return iso_str[:5] if len(iso_str) >= 5 else "--:--"


class PrayerTimesPage:
    def __init__(self, page: ft.Page, on_back):
        self.page = page
        self.on_back = on_back
        self.selected_date = date.today()

        today_jd = jdatetime.date.fromgregorian(date=self.selected_date)
        self.shamsi_year = today_jd.year
        self.shamsi_month = today_jd.month
        self.shamsi_day = today_jd.day

    def build(self):
        header = ft.Container(
            content=ft.Row(
                [
                    ft.IconButton(icon=ft.icons.Icons.ARROW_BACK, icon_color="#FFFFFF", on_click=self.go_back),
                    ft.Text("اوقات شرعی", size=18, font_family="Vazir", weight=ft.FontWeight.BOLD, color="#FFFFFF"),
                ],
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.Padding(15, 35, 15, 15),
            bgcolor="#0D1B0F",
            border_radius=ft.BorderRadius(0, 0, 20, 20),
        )

        self.title_text = ft.Text(
            "اوقات شرعی امروز", size=20, font_family="Vazir", weight=ft.FontWeight.BOLD, color=AppTheme.PRIMARY, text_align=ft.TextAlign.CENTER,
        )

        self.date_items = ft.Column([], spacing=8, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

        days = get_days_in_month(self.shamsi_year, self.shamsi_month)

        self.day_dd = ft.Dropdown(
            value=self.shamsi_day,
            options=[ft.dropdown.Option(d, to_persian_numbers(str(d))) for d in days],
            width=80, text_size=14, bgcolor="#FFFFFF", border_radius=10,
            on_select=self._on_shamsi_changed,
            text_style=ft.TextStyle(font_family="Vazir"),
        )

        self.month_dd = ft.Dropdown(
            value=str(self.shamsi_month),
            options=[ft.dropdown.Option(m[0], m[1]) for m in SHAMSI_MONTHS],
            width=110, text_size=14, bgcolor="#FFFFFF", border_radius=10,
            on_select=self._on_shamsi_changed,
            text_style=ft.TextStyle(font_family="Vazir"),
        )

        self.year_dd = ft.Dropdown(
            value=str(self.shamsi_year),
            options=[ft.dropdown.Option(str(y), to_persian_numbers(str(y))) for y in SHAMSI_YEARS],
            width=95, text_size=14, bgcolor="#FFFFFF", border_radius=10,
            on_select=self._on_shamsi_changed,
            text_style=ft.TextStyle(font_family="Vazir"),
        )

        date_selector = ft.Container(
            content=ft.Column(
                [
                    ft.Text("انتخاب تاریخ", size=13, font_family="Vazir", weight=ft.FontWeight.BOLD, color=AppTheme.TEXT_HINT),
                    ft.Container(height=8),
                    ft.Row([self.day_dd, self.month_dd, self.year_dd], alignment=ft.MainAxisAlignment.CENTER, spacing=8),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=15, bgcolor="#FFFFFF", border_radius=16,
            shadow=ft.BoxShadow(spread_radius=0, blur_radius=10, color="#00000010"),
            border=ft.Border.all(1, "#E0E0E0"), margin=ft.Margin(0, 0, 0, 10),
        )

        self.prayer_card = ft.Container(
            content=ft.Column([], spacing=8), padding=20, bgcolor="#FFFFFF",
            border_radius=16, shadow=ft.BoxShadow(spread_radius=0, blur_radius=15, color="#00000010"),
            border=ft.Border.all(1, "#E0E0E0"),
        )

        self.prayer_content = ft.Column(
            [
                ft.Container(height=20), self.title_text,
                ft.Container(height=10), ft.Container(height=1.5, width=60, bgcolor=AppTheme.SECONDARY, border_radius=1),
                ft.Container(height=15),
                ft.Container(
                    content=ft.Column([
                        ft.Text("أَقِمِ الصَّلَاةَ لِدُلُوكِ الشَّمْسِ", size=17, font_family="Vazir", color=AppTheme.TEXT_PRIMARY, text_align=ft.TextAlign.CENTER),
                        ft.Container(height=6),
                        ft.Text("نماز را در وقت خود به پا دارید", size=12, font_family="Vazir", color=AppTheme.TEXT_HINT, text_align=ft.TextAlign.CENTER),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=ft.Padding(20, 16, 20, 16), bgcolor="#F8F4E8", border_radius=12,
                    border=ft.Border.all(1, AppTheme.SECONDARY), margin=ft.Margin(20, 0, 20, 0),
                ),
                ft.Container(height=15),
                ft.Container(content=self.date_items, padding=10, bgcolor="#FAFAFA", border_radius=12),
                ft.Container(height=10),
                date_selector,
                ft.Container(height=15), self.prayer_card, ft.Container(height=30),
            ],
            alignment=ft.MainAxisAlignment.START, horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

        scrollable = ft.ListView(controls=[self.prayer_content], expand=True, padding=0)
        page_content = ft.Container(content=scrollable, expand=True, bgcolor="#FFFFFF")
        self.load_times()
        return ft.Column([header, page_content], expand=True, spacing=0)

    def _on_shamsi_changed(self, e):
        self.shamsi_year = int(self.year_dd.value)
        self.shamsi_month = int(self.month_dd.value)
        self.shamsi_day = int(self.day_dd.value)

        days = get_days_in_month(self.shamsi_year, self.shamsi_month)
        self.day_dd.options = [ft.dropdown.Option(d, to_persian_numbers(str(d))) for d in days]
        if self.shamsi_day not in days:
            self.shamsi_day = days[-1]
            self.day_dd.value = self.shamsi_day

        try:
            jd = jdatetime.date(self.shamsi_year, self.shamsi_month, self.shamsi_day)
            self.selected_date = jd.togregorian()
        except:
            return

        self.page.update()
        self.load_times()

    def load_times(self):
        calc = PrayerTimesCalculator(
            latitude=LATITUDE, longitude=LONGITUDE,
            date=str(self.selected_date), calculation_method="Tehran",
        )
        pt = calc.fetch_prayer_times()

        hijri = pt.get("date", {}).get("hijri", {})
        gregorian = pt.get("date", {}).get("gregorian", {})

        date_items_list = []

        shamsi = self._format_shamsi(self.selected_date)
        date_items_list.append(
            ft.Row([ft.Icon(ft.icons.Icons.CALENDAR_MONTH, size=18, color="#1565C0"),
                     ft.Text(to_persian_numbers(shamsi), size=15, font_family="Vazir", weight=ft.FontWeight.BOLD, color="#1565C0")], spacing=8)
        )

        if gregorian:
            day = to_persian_numbers(gregorian.get('day', ''))
            month = gregorian.get('month', {}).get('en', '')
            year = to_persian_numbers(gregorian.get('year', ''))
            date_items_list.append(
                ft.Row([ft.Icon(ft.icons.Icons.TODAY, size=18, color="#00897B"),
                         ft.Text(f"{day} {month} {year}", size=14, font_family="Vazir", color="#00897B")], spacing=8)
            )

        if hijri:
            day = to_persian_numbers(hijri.get('day', ''))
            month = hijri.get('month', {}).get('ar', '')
            year = to_persian_numbers(hijri.get('year', ''))
            date_items_list.append(
                ft.Row([ft.Icon(ft.icons.Icons.NIGHTLIGHT, size=18, color="#8E24AA"),
                         ft.Text(f"{day} {month} {year}", size=15, font_family="Vazir", color="#8E24AA")], spacing=8)
            )

        self.date_items.controls = date_items_list

        prayer_rows = []
        for key, name in PRAYER_NAMES.items():
            time_str = iso_to_time(pt.get(key, "--:--"))
            prayer_rows.append(self._build_prayer_row(name, time_str, key.lower()))

        self.prayer_card.content.controls = prayer_rows

        if self.selected_date == date.today():
            self.title_text.value = "اوقات شرعی امروز"
        else:
            self.title_text.value = f"اوقات شرعی {to_persian_numbers(self._format_shamsi(self.selected_date))}"
        self.page.update()

    def _build_prayer_row(self, name: str, time: str, key: str):
        colors = {"fajr": "#1565C0", "sunrise": "#FF8F00", "dhuhr": "#FFB300", "asr": "#F4511E", "maghrib": "#6A1B9A", "isha": "#1B5E20"}
        icons = {"fajr": ft.icons.Icons.DARK_MODE, "sunrise": ft.icons.Icons.WB_TWILIGHT, "dhuhr": ft.icons.Icons.WB_SUNNY, "asr": ft.icons.Icons.FILTER_VINTAGE, "maghrib": ft.icons.Icons.NIGHTLIGHT, "isha": ft.icons.Icons.DARK_MODE_OUTLINED}
        color = colors.get(key, AppTheme.PRIMARY)
        icon = icons.get(key, ft.icons.Icons.ACCESS_TIME)

        return ft.Container(
            content=ft.Row([ft.Icon(icon, size=22, color=color),
                             ft.Text(name, size=15, font_family="Vazir", weight=ft.FontWeight.BOLD, color=AppTheme.TEXT_PRIMARY),
                             ft.Container(expand=True),
                             ft.Text(to_persian_numbers(time), size=16, font_family="Vazir", weight=ft.FontWeight.BOLD, color=color)],
                            alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.Padding(15, 12, 15, 12), bgcolor="#FAFAFA", border_radius=12, border=ft.Border.all(1, "#E0E0E0"),
        )

    def _format_shamsi(self, d: date) -> str:
        try:
            jd = jdatetime.date.fromgregorian(date=d)
            months = ["فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور", "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند"]
            return f"{jd.day} {months[jd.month - 1]} {jd.year}"
        except:
            return str(d)

    def go_back(self, e):
        self.on_back()