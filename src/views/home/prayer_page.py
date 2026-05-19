import flet as ft
from src.theme import AppTheme
from datetime import date, timedelta, datetime
from prayer_times_calculator_offline import PrayerTimesCalculator
import jdatetime
from src.utils.formatters import persian_numbers


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


def iso_to_time(iso_str: str) -> str:
    if not iso_str or iso_str == "--:--":
        return "--:--"
    try:
        dt = datetime.fromisoformat(iso_str)
        local_dt = dt + timedelta(hours=TIMEZONE_OFFSET)
        return local_dt.strftime("%H:%M")
    except:
        return iso_str[:5] if len(iso_str) >= 5 else "--:--"


class PrayerPage:
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
                    ft.IconButton(icon=ft.icons.Icons.ARROW_BACK,
                                  icon_color="#FFFFFF", on_click=self.go_back),
                    ft.Text("اوقات شرعی", size=18, font_family="Vazir",
                            weight=ft.FontWeight.BOLD, color="#FFFFFF"),
                ],
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.Padding(15, 35, 15, 15),
            bgcolor="#0D1B0F",
            border_radius=ft.BorderRadius(0, 0, 20, 20),
        )

        self.title_text = ft.Row(
            [
                ft.Icon(ft.icons.Icons.NIGHTLIGHT_ROUND,
                        size=26, color=AppTheme.SECONDARY),
                ft.Text("اوقات شرعی امروز", size=32, font_family="IranNastaliq",
                        color=AppTheme.SECONDARY, text_align=ft.TextAlign.CENTER),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=8,
        )

        self.date_items = ft.Column(
            [], spacing=8, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

        days = get_days_in_month(self.shamsi_year, self.shamsi_month)

        # ========== PopupMenuButton روز (بدون آیکون، با ▼) ==========
        self.day_menu = ft.PopupMenuButton(
            content=ft.Row([
                ft.Text(persian_numbers(str(self.shamsi_day)),
                        size=14, font_family="Vazir"),
                ft.Text("▼", size=10, color=AppTheme.TEXT_HINT)
            ], spacing=4, alignment=ft.MainAxisAlignment.CENTER),
            items=[
                ft.PopupMenuItem(
                    content=ft.Text(persian_numbers(str(d)),
                                    font_family="Vazir", size=14),
                    on_click=lambda e, d=d: self._on_date_changed(day=d)
                ) for d in days
            ],
            bgcolor="#FFFFFF",
            shape=ft.RoundedRectangleBorder(radius=10),
            elevation=2,
        )

        # ========== PopupMenuButton ماه (بدون آیکون، با ▼) ==========
        self.month_menu = ft.PopupMenuButton(
            content=ft.Row([
                ft.Text(SHAMSI_MONTHS[self.shamsi_month - 1]
                        [1], size=14, font_family="Vazir"),
                ft.Text("▼", size=10, color=AppTheme.TEXT_HINT)
            ], spacing=4, alignment=ft.MainAxisAlignment.CENTER),
            items=[
                ft.PopupMenuItem(
                    content=ft.Text(m[1], font_family="Vazir", size=14),
                    on_click=lambda e, m=int(
                        m[0]): self._on_date_changed(month=m)
                ) for m in SHAMSI_MONTHS
            ],
            bgcolor="#FFFFFF",
            shape=ft.RoundedRectangleBorder(radius=10),
            elevation=2,
        )

        # ========== PopupMenuButton سال (بدون آیکون، با ▼) ==========
        self.year_menu = ft.PopupMenuButton(
            content=ft.Row([
                ft.Text(persian_numbers(str(self.shamsi_year)),
                        size=14, font_family="Vazir"),
                ft.Text("▼", size=10, color=AppTheme.TEXT_HINT)
            ], spacing=4, alignment=ft.MainAxisAlignment.CENTER),
            items=[
                ft.PopupMenuItem(
                    content=ft.Text(persian_numbers(str(y)),
                                    font_family="Vazir", size=14),
                    on_click=lambda e, y=y: self._on_date_changed(year=y)
                ) for y in SHAMSI_YEARS
            ],
            bgcolor="#FFFFFF",
            shape=ft.RoundedRectangleBorder(radius=10),
            elevation=2,
        )

        date_selector = ft.Container(
            content=ft.Column(
                [
                    ft.Text("انتخاب تاریخ", size=13, font_family="Vazir",
                            weight=ft.FontWeight.BOLD, color=AppTheme.TEXT_HINT),
                    ft.Container(height=8),
                    ft.Row([self.day_menu, self.month_menu, self.year_menu],
                           alignment=ft.MainAxisAlignment.CENTER, spacing=8),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=15, bgcolor="#FFFFFF", border_radius=16,
            border=ft.Border.all(1, "#E0E0E0"), margin=ft.Margin(0, 0, 0, 10),
            shadow=ft.BoxShadow(
                spread_radius=0, blur_radius=8, color="#00000010"),
        )

        self.prayer_card = ft.Container(
            content=ft.Column([], spacing=8), padding=20, bgcolor="#FFFFFF",
            border_radius=16, border=ft.Border.all(1, "#E0E0E0"),
            shadow=ft.BoxShadow(
                spread_radius=0, blur_radius=8, color="#00000010"),
        )

        self.prayer_content = ft.Column(
            [
                ft.Container(height=20), self.title_text,
                ft.Container(height=10), ft.Container(
                    height=1.5, width=60, bgcolor=AppTheme.SECONDARY, border_radius=1),
                ft.Container(height=15),
                ft.Container(
                    content=ft.Column([
                        ft.Text("أَقِمِ الصَّلَاةَ لِدُلُوكِ الشَّمْسِ", size=17, font_family="Vazir",
                                color=AppTheme.TEXT_PRIMARY, text_align=ft.TextAlign.CENTER),
                        ft.Container(height=6),
                        ft.Text("نماز را در وقت خود به پا دارید (اسراء - ۷۸)", size=12,
                                font_family="Vazir", color=AppTheme.TEXT_HINT, text_align=ft.TextAlign.CENTER),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=ft.Padding(20, 16, 20, 16), bgcolor="#F8F4E8", border_radius=12,
                    border=ft.Border.all(1, AppTheme.SECONDARY), margin=ft.Margin(20, 0, 20, 0),
                ),
                ft.Container(height=15),
                ft.Container(content=self.date_items, padding=10,
                             bgcolor="#FAFAFA", border_radius=12),
                ft.Container(height=10),
                date_selector,
                ft.Container(height=15), self.prayer_card, ft.Container(
                    height=30),
            ],
            alignment=ft.MainAxisAlignment.START, horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

        scrollable = ft.ListView(
            controls=[self.prayer_content], expand=True, padding=20)
        page_content = ft.Container(
            content=scrollable,
            expand=True,
            gradient=ft.LinearGradient(
                begin=ft.Alignment(0, -1), end=ft.Alignment(0, 1),
                colors=["#0D1B0F", "#1A2F1E", "#0D1B0F"],
            ),
        )
        self.load_times()
        return ft.Column([header, page_content], expand=True, spacing=0)

    def _on_date_changed(self, day: int = None, month: int = None, year: int = None):
        """مدیریت تغییر تاریخ از طریق PopupMenuButton"""

        if day is not None:
            self.shamsi_day = day
            # به‌روزرسانی متن دکمه روز
            self.day_menu.content.controls[0].value = persian_numbers(str(day))

        if month is not None:
            self.shamsi_month = month
            # به‌روزرسانی متن دکمه ماه
            self.month_menu.content.controls[0].value = SHAMSI_MONTHS[month - 1][1]
            # به‌روزرسانی لیست روزها هنگام تغییر ماه
            days = get_days_in_month(self.shamsi_year, self.shamsi_month)
            if self.shamsi_day > max(days):
                self.shamsi_day = max(days)
                self.day_menu.content.controls[0].value = persian_numbers(
                    str(self.shamsi_day))

        if year is not None:
            self.shamsi_year = year
            # به‌روزرسانی متن دکمه سال
            self.year_menu.content.controls[0].value = persian_numbers(
                str(year))
            # بررسی تطابق روز با ماه جدید
            days = get_days_in_month(self.shamsi_year, self.shamsi_month)
            if self.shamsi_day > max(days):
                self.shamsi_day = max(days)
                self.day_menu.content.controls[0].value = persian_numbers(
                    str(self.shamsi_day))

        try:
            jd = jdatetime.date(
                self.shamsi_year, self.shamsi_month, self.shamsi_day)
            self.selected_date = jd.togregorian()
            self.load_times()
            self.page.update()
        except Exception as e:
            print("Date conversion error:", e)

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
                    ft.Text(persian_numbers(shamsi), size=15, font_family="Vazir", weight=ft.FontWeight.BOLD, color="#1565C0")], spacing=8)
        )

        if gregorian:
            day = persian_numbers(gregorian.get("day", ""))
            month = gregorian.get("month", {}).get("en", "")
            year = persian_numbers(gregorian.get("year", ""))
            date_items_list.append(
                ft.Row([ft.Icon(ft.icons.Icons.TODAY, size=18, color="#00897B"),
                        ft.Text(f"{day} {month} {year}", size=14, font_family="Vazir", color="#00897B")], spacing=8)
            )

        if hijri:
            day = persian_numbers(hijri.get("day", ""))
            month = hijri.get("month", {}).get("ar", "")
            year = persian_numbers(hijri.get("year", ""))
            date_items_list.append(
                ft.Row([ft.Icon(ft.icons.Icons.NIGHTLIGHT, size=18, color="#8E24AA"),
                        ft.Text(f"{day} {month} {year}", size=15, font_family="Vazir", color="#8E24AA")], spacing=8)
            )

        self.date_items.controls = date_items_list

        prayer_rows = []
        for key, name in PRAYER_NAMES.items():
            time_str = iso_to_time(pt.get(key, "--:--"))
            prayer_rows.append(self._build_prayer_row(
                name, time_str, key.lower()))

        self.prayer_card.content.controls = prayer_rows

        if self.selected_date == date.today():
            self.title_text.controls[1].value = "اوقات شرعی امروز"
        else:
            self.title_text.controls[
                1].value = f"اوقات شرعی {persian_numbers(self._format_shamsi(self.selected_date))}"
        self.page.update()

    def _build_prayer_row(self, name: str, time: str, key: str):
        colors = {"fajr": "#1565C0", "sunrise": "#FF8F00", "dhuhr": "#FFB300",
                  "asr": "#F4511E", "maghrib": "#6A1B9A", "isha": "#1B5E20"}
        icons = {"fajr": ft.icons.Icons.DARK_MODE, "sunrise": ft.icons.Icons.WB_TWILIGHT, "dhuhr": ft.icons.Icons.WB_SUNNY,
                 "asr": ft.icons.Icons.FILTER_VINTAGE, "maghrib": ft.icons.Icons.NIGHTLIGHT, "isha": ft.icons.Icons.DARK_MODE_OUTLINED}
        color = colors.get(key, AppTheme.PRIMARY)
        icon = icons.get(key, ft.icons.Icons.ACCESS_TIME)

        return ft.Container(
            content=ft.Row([ft.Icon(icon, size=22, color=color),
                            ft.Text(name, size=15, font_family="Vazir",
                                    weight=ft.FontWeight.BOLD, color=AppTheme.TEXT_PRIMARY),
                            ft.Container(expand=True),
                            ft.Text(persian_numbers(time), size=16, font_family="Vazir", weight=ft.FontWeight.BOLD, color=color)],
                           alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.Padding(15, 12, 15, 12), bgcolor="#FAFAFA", border_radius=12, border=ft.Border.all(1, "#E0E0E0"),
        )

    def _format_shamsi(self, d: date) -> str:
        try:
            jd = jdatetime.date.fromgregorian(date=d)
            months = ["فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد",
                      "شهریور", "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند"]
            return f"{jd.day} {months[jd.month - 1]} {jd.year}"
        except:
            return str(d)

    def go_back(self, e):
        self.on_back()
