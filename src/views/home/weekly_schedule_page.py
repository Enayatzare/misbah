import flet as ft
from src.theme import AppTheme
from src.services.api_client import api
from src.utils.formatters import persian_numbers


DAYS_OF_WEEK = {
    "saturday": "شنبه",
    "sunday": "یکشنبه",
    "monday": "دوشنبه",
    "tuesday": "سه‌شنبه",
    "wednesday": "چهارشنبه",
    "thursday": "پنجشنبه",
    "friday": "جمعه",
}


class WeeklySchedulePage:
    def __init__(self, page: ft.Page, on_back):
        self.page = page
        self.on_back = on_back

        self.page.on_pop = lambda e: self.go_back(e)

    def build(self):
        header = ft.Container(
            content=ft.Row(
                [
                    ft.IconButton(icon=ft.icons.Icons.ARROW_BACK,
                                  icon_color="#FFFFFF", on_click=self.go_back),
                    ft.Text("برنامه هفتگی", size=18, font_family="Vazir",
                            weight=ft.FontWeight.BOLD, color="#FFFFFF"),
                ],
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.Padding(15, 35, 15, 15),
            bgcolor="#0D1B0F",
        )

        self.content_column = ft.Column(
            [ft.Container(height=50), ft.ProgressBar(
                width=80, color=AppTheme.SECONDARY)],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

        scrollable = ft.ListView(
            controls=[self.content_column], expand=True, padding=20)

        page_content = ft.Container(
            content=scrollable,
            expand=True,
            gradient=ft.LinearGradient(
                begin=ft.Alignment(0, -1), end=ft.Alignment(0, 1),
                colors=["#0D1B0F", "#1A2F1E", "#0D1B0F"],
            ),
        )

        self.load_schedule()
        return ft.Column([header, page_content], expand=True, spacing=0)

    def load_schedule(self):
        result = api.get("events/get_weekly_schedule.php")

        if isinstance(result, list) and len(result) > 0:
            days = {}
            for item in result:
                day = item.get("day", "saturday")
                if day not in days:
                    days[day] = []
                days[day].append(item)

            items = [
                ft.Container(height=10),
                ft.Row(
                    [
                        ft.Icon(ft.icons.Icons.CALENDAR_MONTH,
                                size=28, color=AppTheme.SECONDARY),
                        ft.Text("برنامه هفتگی", size=32, font_family="IranNastaliq",
                                color=AppTheme.SECONDARY, text_align=ft.TextAlign.CENTER),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=10,
                ),
                ft.Container(height=1.5, width=60,
                             bgcolor=AppTheme.SECONDARY, border_radius=1),
                ft.Container(height=5),
                ft.Text("برنامه ثابت هفتگی مسجد", size=14, font_family="Vazir",
                        color="#FFFFFF80", text_align=ft.TextAlign.CENTER),
                ft.Container(height=25),
            ]

            day_order = ["saturday", "sunday", "monday",
                         "tuesday", "wednesday", "thursday", "friday"]

            for day in day_order:
                day_name = DAYS_OF_WEEK.get(day, day)
                is_friday = day == "friday"

                if is_friday:
                    day_container = ft.Container(
                        content=ft.Row(
                            [
                                ft.Container(
                                    width=4, height=24, bgcolor=AppTheme.SECONDARY, border_radius=2),
                                ft.Container(width=10),
                                ft.Icon(ft.icons.Icons.STAR, size=20,
                                        color=AppTheme.SECONDARY),
                                ft.Container(width=8),
                                ft.Text(day_name, size=16, font_family="Vazir",
                                        weight=ft.FontWeight.BOLD, color=AppTheme.SECONDARY),
                            ],
                        ),
                        padding=ft.Padding(10, 8, 10, 8),
                        bgcolor="#FFF8E1",
                        border_radius=10,
                        margin=ft.Margin(0, 12, 0, 6),
                    )
                else:
                    day_container = ft.Container(
                        content=ft.Row(
                            [
                                ft.Container(
                                    width=4, height=24, bgcolor=AppTheme.SECONDARY, border_radius=2),
                                ft.Container(width=10),
                                ft.Icon(ft.icons.Icons.TODAY, size=20,
                                        color=AppTheme.SECONDARY),
                                ft.Container(width=8),
                                ft.Text(day_name, size=16, font_family="Vazir",
                                        weight=ft.FontWeight.BOLD, color=AppTheme.SECONDARY),
                            ],
                        ),
                        margin=ft.Margin(0, 12, 0, 6),
                    )

                items.append(day_container)
                if day != "friday":
                    items.append(
                        ft.Container(
                            height=1,
                            bgcolor=AppTheme.SECONDARY,
                            opacity=0.3,
                            margin=ft.Margin(20, 0, 20, 0),
                        )
                    )
                if day in days:
                    for program in days[day]:
                        items.append(self._build_program_card(program))
                else:
                    items.append(
                        ft.Container(
                            content=ft.Text(
                                "برنامه‌ای ثبت نشده", size=12, font_family="Vazir", color="#FFFFFF40"),
                            padding=ft.Padding(16, 8, 16, 8),
                            margin=ft.Margin(0, 0, 0, 8),
                        )
                    )

            items.append(ft.Container(height=20))
            self.content_column.controls = items
            self.content_column.alignment = ft.MainAxisAlignment.START
        else:
            self.content_column.controls = [
                ft.Container(height=60),
                ft.Icon(ft.icons.Icons.EVENT_BUSY, size=50, color="#FFFFFF40"),
                ft.Container(height=10),
                ft.Text("برنامه هفتگی ثبت نشده است", size=15,
                        font_family="Vazir", color="#FFFFFFAA"),
            ]
            self.content_column.alignment = ft.MainAxisAlignment.CENTER

        self.page.update()

    def _build_program_card(self, program: dict):
        title = program.get("title", "بدون عنوان")
        time_start = program.get("time_start", "")
        time_end = program.get("time_end", "")
        description = program.get("description", "")
        lecturer = program.get("lecturer", "")

        time_str = ""
        if time_end:
            time_str = persian_numbers(time_end[:5])
        if time_start:
            time_str += f" - {persian_numbers(time_start[:5])}"

        content_col = ft.Column([], expand=True)

        # عنوان برنامه
        title_row = ft.Row(
            [
                ft.Text(title, size=15, font_family="Vazir",
                        weight=ft.FontWeight.BOLD, color=AppTheme.TEXT_PRIMARY,
                        overflow=ft.TextOverflow.VISIBLE,
                        no_wrap=False),
                ft.Container(expand=True),
            ]
        )
        if time_str:
            title_row.controls.append(
                ft.Container(
                    content=ft.Text(time_str, size=12, font_family="Vazir",
                                    weight=ft.FontWeight.BOLD, color=AppTheme.SECONDARY),
                    bgcolor="#FFF8E1",
                    border_radius=8,
                    padding=ft.Padding(10, 4, 10, 4),
                )
            )
        content_col.controls.append(title_row)

        # سخنران
        if lecturer:
            content_col.controls.append(ft.Container(height=4))
            content_col.controls.append(ft.Text(
                f"🎙 {lecturer}", size=12, font_family="Vazir",
                color=AppTheme.TEXT_HINT,
                overflow=ft.TextOverflow.VISIBLE,
                no_wrap=False,
            ))

        # توضیحات
        if description:
            content_col.controls.append(ft.Container(height=4))
            content_col.controls.append(ft.Text(
                description,
                size=12,
                font_family="Vazir",
                color=AppTheme.TEXT_SECONDARY,
                overflow=ft.TextOverflow.VISIBLE,
                no_wrap=False,
            ))

        # کل محتوای کارت داخل یک Row با اسکرول افقی
        card_content = ft.Row(
            [
                ft.Container(width=12),
                content_col,
            ],
            vertical_alignment=ft.CrossAxisAlignment.START,
            scroll=ft.ScrollMode.AUTO,
        )

        return ft.Container(
            content=card_content,
            padding=ft.Padding(12, 10, 12, 10),
            bgcolor="#FFFFFF",
            border_radius=10,
            border=ft.Border(left=ft.BorderSide(4, AppTheme.SECONDARY)),
            margin=ft.Margin(0, 0, 0, 8),
            shadow=ft.BoxShadow(
                spread_radius=0, blur_radius=4, color="#00000008"),
        )

    def go_back(self, e):
        self.on_back()