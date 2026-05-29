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

# سرستون‌ها: از راست به چپ = شنبه تا جمعه
WEEKDAYS = ["ش", "ی", "د", "س", "چ", "پ", "ج"]
MONTH_NAMES = [
    "فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد",
    "شهریور", "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند"
]


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

        self.page.on_pop = lambda e: self.go_back(e)

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

        # عنوان ماه و سال
        self.month_title = ft.Text(
            f"{MONTH_NAMES[self.shamsi_month - 1]} {persian_numbers(str(self.shamsi_year))}",
            size=20,
            font_family="Vazir",
            weight=ft.FontWeight.BOLD,
            color=AppTheme.SECONDARY,
            text_align=ft.TextAlign.CENTER,
        )

        # سرستون روزهای هفته
        weekday_header = ft.Row(
            [
                ft.Container(
                    content=ft.Text(day, size=12, font_family="Vazir",
                                    weight=ft.FontWeight.BOLD,
                                    color="#D4AF37" if day == "ج" else AppTheme.TEXT_HINT),
                    width=42, height=35,
                    alignment=ft.Alignment(0, 0),
                ) for day in WEEKDAYS
            ],
            alignment=ft.MainAxisAlignment.SPACE_AROUND,
        )

        # جدول روزهای ماه
        self.calendar_grid = ft.GridView(
            expand=False,
            runs_count=7,
            spacing=3,
            run_spacing=4,
            max_extent=46,
            height=320,
        )

        # نوار ابزار تقویم: سال، ماه، دکمه امروز
        calendar_toolbar = ft.Column([
            # ردیف اول: تغییر سال + عنوان ماه
            ft.Row([
                ft.IconButton(
                    icon=ft.icons.Icons.KEYBOARD_DOUBLE_ARROW_RIGHT,
                    icon_size=18,
                    icon_color=AppTheme.SECONDARY,
                    tooltip="سال قبل",
                    on_click=lambda e: self._change_year(-1),
                ),
                ft.IconButton(
                    icon=ft.icons.Icons.CHEVRON_LEFT,
                    icon_color=AppTheme.SECONDARY,
                    tooltip="ماه قبل",
                    on_click=lambda e: self._change_month(-1),
                ),
                self.month_title,
                ft.IconButton(
                    icon=ft.icons.Icons.CHEVRON_RIGHT,
                    icon_color=AppTheme.SECONDARY,
                    tooltip="ماه بعد",
                    on_click=lambda e: self._change_month(1),
                ),
                ft.IconButton(
                    icon=ft.icons.Icons.KEYBOARD_DOUBLE_ARROW_LEFT,
                    icon_size=18,
                    icon_color=AppTheme.SECONDARY,
                    tooltip="سال بعد",
                    on_click=lambda e: self._change_year(1),
                ),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Container(height=5),
            # ردیف دوم: دکمه امروز
            ft.Row([
                ft.Container(expand=True),
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.icons.Icons.TODAY, size=14, color=AppTheme.PRIMARY),
                        ft.Text("امروز", size=12, font_family="Vazir", color=AppTheme.PRIMARY),
                    ], spacing=4),
                    padding=ft.Padding(8, 4, 8, 4),
                    bgcolor="#E8F5E9",
                    border_radius=12,
                    on_click=lambda e: self._go_to_today(),
                ),
            ]),
        ])

        calendar_container = ft.Container(
            content=ft.Column([
                calendar_toolbar,
                ft.Container(height=10),
                weekday_header,
                self.calendar_grid,
            ]),
            padding=15,
            bgcolor="#FFFFFF",
            border_radius=16,
            border=ft.Border.all(1, "#E0E0E0"),
            shadow=ft.BoxShadow(spread_radius=0, blur_radius=8, color="#00000010"),
            margin=ft.Margin(0, 10, 0, 10),
        )

        self.prayer_card = ft.Container(
            content=ft.Column([], spacing=8),
            padding=20,
            bgcolor="#FFFFFF",
            border_radius=16,
            border=ft.Border.all(1, "#E0E0E0"),
            shadow=ft.BoxShadow(spread_radius=0, blur_radius=8, color="#00000010"),
        )

        self.prayer_content = ft.Column(
            [
                ft.Container(height=10),
                ft.Row([
                    ft.Icon(ft.icons.Icons.NIGHTLIGHT_ROUND, size=26, color=AppTheme.SECONDARY),
                    ft.Text("اوقات شرعی", size=32, font_family="IranNastaliq",
                            color=AppTheme.SECONDARY, text_align=ft.TextAlign.CENTER),
                ], alignment=ft.MainAxisAlignment.CENTER, spacing=8),
                ft.Container(height=10),
                ft.Container(height=1.5, width=60, bgcolor=AppTheme.SECONDARY, border_radius=1),
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
                    border=ft.Border.all(1, AppTheme.SECONDARY), margin=ft.Margin(10, 0, 10, 0),
                ),
                ft.Container(height=10),
                calendar_container,
                ft.Container(height=10),
                self.prayer_card,
                ft.Container(height=30),
            ],
            alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
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

        self._build_calendar()
        self.load_times()
        return ft.Column([header, page_content], expand=True, spacing=0)

    def _change_year(self, delta: int):
        """تغییر سال"""
        self.shamsi_year += delta
        max_day = self._get_max_day()
        if self.shamsi_day > max_day:
            self.shamsi_day = max_day

        self.month_title.value = f"{MONTH_NAMES[self.shamsi_month - 1]} {persian_numbers(str(self.shamsi_year))}"
        self._build_calendar()
        self._on_day_selected(self.shamsi_day)

    def _change_month(self, delta: int):
        """تغییر ماه با دکمه‌های قبلی/بعدی"""
        self.shamsi_month += delta
        if self.shamsi_month > 12:
            self.shamsi_month = 1
            self.shamsi_year += 1
        elif self.shamsi_month < 1:
            self.shamsi_month = 12
            self.shamsi_year -= 1

        max_day = self._get_max_day()
        if self.shamsi_day > max_day:
            self.shamsi_day = max_day

        self.month_title.value = f"{MONTH_NAMES[self.shamsi_month - 1]} {persian_numbers(str(self.shamsi_year))}"
        self._build_calendar()
        self._on_day_selected(self.shamsi_day)

    def _go_to_today(self):
        """برگشت به تاریخ امروز"""
        today_jd = jdatetime.date.fromgregorian(date=date.today())
        self.shamsi_year = today_jd.year
        self.shamsi_month = today_jd.month
        self.shamsi_day = today_jd.day

        self.month_title.value = f"{MONTH_NAMES[self.shamsi_month - 1]} {persian_numbers(str(self.shamsi_year))}"
        self._build_calendar()
        self._on_day_selected(self.shamsi_day)

    def _get_max_day(self):
        """تعداد روزهای ماه جاری"""
        if self.shamsi_month <= 6:
            return 31
        elif self.shamsi_month <= 11:
            return 30
        else:
            try:
                jdatetime.date(self.shamsi_year, 12, 30)
                return 30
            except:
                return 29

    def _build_calendar(self):
        """ساخت جدول روزهای ماه با تم مذهبی"""
        self.calendar_grid.controls.clear()
        today_jd = jdatetime.date.fromgregorian(date=date.today())

        first_day_jd = jdatetime.date(self.shamsi_year, self.shamsi_month, 1)
        first_weekday = first_day_jd.weekday()  # 0=شنبه, 6=جمعه

        # خانه‌های خالی قبل از اولین روز
        for _ in range(first_weekday):
            self.calendar_grid.controls.append(ft.Container())

        max_day = self._get_max_day()
        for d in range(1, max_day + 1):
            is_today = (self.shamsi_year == today_jd.year and
                        self.shamsi_month == today_jd.month and
                        d == today_jd.day)
            is_selected = (d == self.shamsi_day)

            # محاسبه روز هفته برای تشخیص جمعه
            day_jd = jdatetime.date(self.shamsi_year, self.shamsi_month, d)
            is_friday = (day_jd.weekday() == 6)

            # تعیین رنگ با تم مذهبی
            if is_today and is_selected:
                bg = AppTheme.SECONDARY       # طلایی
                text_color = "#0D1B0F"        # سبز تیره
                weight = ft.FontWeight.BOLD
            elif is_today:
                bg = "#FFF8E1"                # طلایی کمرنگ
                text_color = AppTheme.SECONDARY  # طلایی
                weight = ft.FontWeight.BOLD
            elif is_selected:
                bg = "#1A2F1E"                # سبز تیره
                text_color = AppTheme.SECONDARY  # طلایی
                weight = ft.FontWeight.BOLD
            elif is_friday:
                bg = "#FFFFFF"                # سفید
                text_color = "#D4AF37"        # طلایی (روز عید)
                weight = ft.FontWeight.BOLD
            else:
                bg = "#FFFFFF"                # سفید
                text_color = "#1A2F1E"        # سبز تیره
                weight = ft.FontWeight.NORMAL

            self.calendar_grid.controls.append(
                ft.Container(
                    content=ft.Text(
                        persian_numbers(str(d)),
                        size=14,
                        font_family="Vazir",
                        weight=weight,
                        color=text_color,
                    ),
                    width=42,
                    height=42,
                    bgcolor=bg,
                    border_radius=21,
                    alignment=ft.Alignment(0, 0),
                    on_click=lambda e, day=d: self._on_day_selected(day),
                )
            )

        self.page.update()

    def _on_day_selected(self, day: int):
        """وقتی کاربر روی یک روز کلیک می‌کند"""
        self.shamsi_day = day
        try:
            jd = jdatetime.date(self.shamsi_year, self.shamsi_month, day)
            self.selected_date = jd.togregorian()
            self._build_calendar()
            self.load_times()
        except Exception as e:
            print("Date conversion error:", e)

    def load_times(self):
        calc = PrayerTimesCalculator(
            latitude=LATITUDE, longitude=LONGITUDE,
            date=str(self.selected_date), calculation_method="Tehran",
        )
        pt = calc.fetch_prayer_times()

        prayer_rows = []
        for key, name in PRAYER_NAMES.items():
            time_str = iso_to_time(pt.get(key, "--:--"))
            prayer_rows.append(self._build_prayer_row(name, time_str, key.lower()))

        self.prayer_card.content.controls = prayer_rows
        self.page.update()

    def _build_prayer_row(self, name: str, time: str, key: str):
        colors = {
            "fajr": "#1565C0", "sunrise": "#FF8F00", "dhuhr": "#FFB300",
            "asr": "#F4511E", "maghrib": "#6A1B9A", "isha": "#1B5E20"
        }
        icons = {
            "fajr": ft.icons.Icons.DARK_MODE, "sunrise": ft.icons.Icons.WB_TWILIGHT,
            "dhuhr": ft.icons.Icons.WB_SUNNY, "asr": ft.icons.Icons.FILTER_VINTAGE,
            "maghrib": ft.icons.Icons.NIGHTLIGHT, "isha": ft.icons.Icons.DARK_MODE_OUTLINED
        }
        color = colors.get(key, AppTheme.PRIMARY)
        icon = icons.get(key, ft.icons.Icons.ACCESS_TIME)

        return ft.Container(
            content=ft.Row([
                ft.Icon(icon, size=22, color=color),
                ft.Text(name, size=15, font_family="Vazir",
                        weight=ft.FontWeight.BOLD, color=AppTheme.TEXT_PRIMARY),
                ft.Container(expand=True),
                ft.Text(persian_numbers(time), size=16, font_family="Vazir",
                        weight=ft.FontWeight.BOLD, color=color),
            ], alignment=ft.MainAxisAlignment.START,
               vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.Padding(15, 12, 15, 12),
            bgcolor="#FAFAFA",
            border_radius=12,
            border=ft.Border.all(1, "#E0E0E0"),
        )

    def go_back(self, e):
        self.on_back()