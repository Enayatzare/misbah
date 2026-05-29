import flet as ft
from src.theme import AppTheme
from src.services.api_client import api
from src.utils.formatters import persian_numbers
from datetime import datetime
import jdatetime


class AnnouncementsPage:
    def __init__(self, page: ft.Page, on_back):
        self.page = page
        self.on_back = on_back

        

    def build(self):
        header = ft.Container(
            content=ft.Row(
                [
                    ft.IconButton(icon=ft.icons.Icons.ARROW_BACK,
                                  icon_color="#FFFFFF", on_click=self.go_back),
                    ft.Text("اطلاعیه‌ها", size=18, font_family="Vazir",
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

        self.load_announcements()

        def handle_back(e: ft.KeyboardEvent):
            if e.key in ["Escape", "Back", "GoBack", "ArrowLeft"]:
                self.go_back(e)
        
        self.page.on_keyboard_event = handle_back
        return ft.Column([header, page_content], expand=True, spacing=0)

    def load_announcements(self):
        result = api.get("announcements/get_all.php")

        if isinstance(result, list) and len(result) > 0:
            items = [
                ft.Container(height=10),
                ft.Row(
                    [
                        ft.Icon(ft.icons.Icons.CAMPAIGN, size=28,
                                color=AppTheme.SECONDARY),
                        ft.Text("اطلاعیه‌ها و اخبار", size=32, font_family="IranNastaliq",
                                color=AppTheme.SECONDARY, text_align=ft.TextAlign.CENTER),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=10,
                ),
                ft.Container(height=5),
                ft.Container(height=1.5, width=60,
                             bgcolor=AppTheme.SECONDARY, border_radius=1),
                ft.Container(height=5),
                ft.Text("آخرین اطلاعیه‌های مسجد", size=14, font_family="Vazir",
                        color="#FFFFFF80", text_align=ft.TextAlign.CENTER),


                ft.Container(height=25),
            ]

            for ann in result:
                items.append(self._build_announcement_card(ann))

            items.append(ft.Container(height=20))
            self.content_column.controls = items
            self.content_column.alignment = ft.MainAxisAlignment.START
        else:
            self.content_column.controls = [
                ft.Container(height=60),
                ft.Icon(ft.icons.Icons.CAMPAIGN_OUTLINED,
                        size=50, color="#FFFFFF40"),
                ft.Container(height=10),
                ft.Text("اطلاعیه‌ای ثبت نشده است", size=15,
                        font_family="Vazir", color="#FFFFFFAA"),
            ]
            self.content_column.alignment = ft.MainAxisAlignment.CENTER

        self.page.update()

    def _build_announcement_card(self, ann: dict):
        title = ann.get("title", "بدون عنوان")
        content = ann.get("content", "")
        ann_type = ann.get("type", "general")
        publish_date = ann.get("publish_date", "")
        created_by = ann.get("created_by", "")

        type_colors = {
            "urgent": "#E53935",
            "event": "#1565C0",
            "financial": "#EF6C00",
            "religious": "#7B1FA2",
            "general": AppTheme.PRIMARY,
        }

        type_icons = {
            "urgent": ft.icons.Icons.WARNING,
            "event": ft.icons.Icons.EVENT,
            "financial": ft.icons.Icons.PAYMENTS,
            "religious": ft.icons.Icons.MOSQUE,
            "general": ft.icons.Icons.CAMPAIGN,
        }

        type_labels = {
            "urgent": "فوری",
            "event": "مناسبت",
            "financial": "مالی",
            "religious": "مذهبی",
            "general": "عمومی",
        }

        color = type_colors.get(ann_type, AppTheme.PRIMARY)
        icon = type_icons.get(ann_type, ft.icons.Icons.CAMPAIGN)
        label = type_labels.get(ann_type, "عمومی")

        shamsi_date = ""
        if publish_date:
            try:
                dt = datetime.fromisoformat(
                    publish_date.replace("Z", "+00:00"))
                jd = jdatetime.date.fromgregorian(date=dt.date())
                months = ["فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد",
                          "شهریور", "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند"]
                shamsi_date = f"{persian_numbers(jd.day)} {months[jd.month - 1]} {persian_numbers(jd.year)}"
            except:
                shamsi_date = str(publish_date)[:10]

        short_content = content[:80] + "..." if len(content) > 80 else content

        # ستون محتوا
        content_col = ft.Column([], expand=True)

        # ردیف عنوان
        title_row = ft.Row(
            [
                ft.Container(
                    content=ft.Icon(icon, size=22, color="#FFFFFF"),
                    width=44, height=44,
                    bgcolor=color, border_radius=22,
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Container(width=12),
                ft.Text(title, size=16, font_family="Vazir",
                        weight=ft.FontWeight.BOLD, color=AppTheme.TEXT_PRIMARY),
            ],
        )
        content_col.controls.append(title_row)

        # خلاصه محتوا
        content_col.controls.append(ft.Container(height=4))
        content_col.controls.append(ft.Text(
            short_content, size=12, font_family="Vazir", color=AppTheme.TEXT_SECONDARY))

        # دیوایدر
        content_col.controls.append(ft.Container(height=12))
        content_col.controls.append(ft.Divider(height=1, color="#F0F0F0"))
        content_col.controls.append(ft.Container(height=8))

        # برچسب و تاریخ
        tag_row = ft.Row(
            [
                ft.Container(
                    content=ft.Text(
                        label, size=10, font_family="Vazir", color="#FFFFFF"),
                    bgcolor=color, border_radius=8,
                    padding=ft.Padding(8, 3, 8, 3),
                ),
                ft.Container(expand=True),
                ft.Icon(ft.icons.Icons.SCHEDULE, size=16,
                        color=AppTheme.TEXT_HINT),
                ft.Container(width=4),
                ft.Text(shamsi_date, size=11, font_family="Vazir",
                        color=AppTheme.TEXT_HINT),
            ],
        )
        content_col.controls.append(tag_row)

        # نام ثبت‌کننده
        if created_by:
            content_col.controls.append(ft.Container(height=8))
            content_col.controls.append(ft.Divider(height=1, color="#F0F0F0"))
            content_col.controls.append(ft.Container(height=4))
            content_col.controls.append(
                ft.Text(f"ثبت توسط: {created_by}", size=11,
                        font_family="Vazir", color=AppTheme.TEXT_HINT)
            )

        return ft.Container(
            content=content_col,
            padding=16,
            bgcolor="#FFFFFF",
            border_radius=14,
            border=ft.Border(left=ft.BorderSide(4, AppTheme.SECONDARY)),
            margin=ft.Margin(0, 0, 0, 16),
            shadow=ft.BoxShadow(
                spread_radius=0, blur_radius=8, color="#00000010"),
            on_click=lambda e, a=ann: self._show_detail(
                a, shamsi_date, label, color),
        )

    def _show_detail(self, ann: dict, shamsi_date: str, label: str, color: str):
        ann_id = ann.get("id", 0)
        detail = api.get(f"announcements/get_detail.php?id={ann_id}")

        title = detail.get("title", ann.get("title", ""))
        content = detail.get("content", ann.get("content", ""))

        def close_dlg(e):
            dlg.open = False
            self.page.update()

        dlg = ft.AlertDialog(
            title=ft.Text(title, font_family="Vazir", weight=ft.FontWeight.BOLD,
                          text_align=ft.TextAlign.CENTER, color=color),
            content=ft.Column(
                [
                    ft.Text(f"{label}  |  {shamsi_date}", size=12, font_family="Vazir",
                            color=AppTheme.TEXT_HINT, text_align=ft.TextAlign.CENTER),
                    ft.Divider(height=20, color="#E0E0E0"),
                    ft.Text(content, size=14, font_family="Vazir",
                            color=AppTheme.TEXT_PRIMARY),
                ],
                spacing=10,
                width=300,
                height=300,
                scroll=ft.ScrollMode.AUTO,
            ),
            actions=[ft.TextButton("بستن", on_click=close_dlg)],
        )
        self.page.show_dialog(dlg)

    def go_back(self, e):
        self.on_back()
