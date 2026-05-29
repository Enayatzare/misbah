import flet as ft
from src.theme import AppTheme
from src.services.api_client import api


class DeceasedPage:
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
                    ft.Text("آگهی ترحیم", size=18, font_family="Vazir",
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

        self.load_deceased()
        return ft.Column([header, page_content], expand=True, spacing=0)

    def load_deceased(self):
        result = api.get("social/get_deceased.php")

        if isinstance(result, list) and len(result) > 0:
            items = [
                ft.Container(height=10),
                ft.Row(
                    [
                        ft.Icon(ft.icons.Icons.FLAG, size=28,
                                color=AppTheme.SECONDARY),
                        ft.Text("آگهی ترحیم", size=32, font_family="IranNastaliq",
                                color=AppTheme.SECONDARY, text_align=ft.TextAlign.CENTER),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=10,
                ),
                ft.Container(height=5),
                ft.Text("إِنَّا لِلَّهِ وَإِنَّا إِلَيْهِ رَاجِعُونَ", size=16,
                        font_family="Vazir", color="#FFFFFF80", text_align=ft.TextAlign.CENTER),
                ft.Container(height=5),
                ft.Container(height=1.5, width=60,
                             bgcolor=AppTheme.SECONDARY, border_radius=1),
                ft.Container(height=20),
            ]

            for dec in result:
                items.append(self._build_deceased_card(dec))

            items.append(ft.Container(height=20))
            self.content_column.controls = items
            self.content_column.alignment = ft.MainAxisAlignment.START
        else:
            self.content_column.controls = [
                ft.Container(height=60),
                ft.Icon(ft.icons.Icons.FLAG_OUTLINED,
                        size=50, color="#FFFFFF40"),
                ft.Container(height=10),
                ft.Text("آگهی ترحیمی ثبت نشده است", size=15,
                        font_family="Vazir", color="#FFFFFFAA"),
            ]
            self.content_column.alignment = ft.MainAxisAlignment.CENTER

        self.page.update()

    def _build_deceased_card(self, dec: dict):
        name = dec.get("name", "مرحوم")
        funeral_date = dec.get("funeral_date", "")
        funeral_location = dec.get("funeral_location", "")
        memorial_date = dec.get("memorial_date", "")
        memorial_location = dec.get("memorial_location", "")
        description = dec.get("description", "")
        created_by = dec.get("created_by_name", "")

        content_items = [
            ft.Container(height=6, bgcolor="#212121",
                         border_radius=ft.BorderRadius(8, 8, 0, 0)),
            ft.Container(height=16),
            ft.Text(name, size=22, font_family="Vazir", weight=ft.FontWeight.BOLD,
                    color=AppTheme.TEXT_PRIMARY, text_align=ft.TextAlign.CENTER),
            ft.Container(height=4),
            ft.Text("مرحوم مغفور", size=14, font_family="Vazir",
                    color=AppTheme.TEXT_HINT, text_align=ft.TextAlign.CENTER),
            ft.Divider(height=20, color="#E0E0E0"),
        ]

        # مراسم تشییع
        if funeral_date or funeral_location:
            content_items.append(
                ft.Row([ft.Icon(ft.icons.Icons.EVENT, size=18, color=AppTheme.PRIMARY), ft.Container(width=8),
                        ft.Text("مراسم تشییع", size=14, font_family="Vazir", weight=ft.FontWeight.BOLD, color=AppTheme.PRIMARY)])
            )
            content_items.append(ft.Container(height=4))
            if funeral_date:
                content_items.append(ft.Text(
                    f"📅 {funeral_date}", size=14, font_family="Vazir", color=AppTheme.TEXT_SECONDARY))
            if funeral_location:
                content_items.append(ft.Text(
                    f"📍 {funeral_location}", size=14, font_family="Vazir", color=AppTheme.TEXT_SECONDARY))
            content_items.append(ft.Container(height=10))

        # مراسم یادبود (ختم)
        if memorial_date or memorial_location:
            content_items.append(
                ft.Row([ft.Icon(ft.icons.Icons.EVENT, size=18, color="#7B1FA2"), ft.Container(width=8),
                        ft.Text("مراسم یادبود (ختم)", size=14, font_family="Vazir", weight=ft.FontWeight.BOLD, color="#7B1FA2")])
            )
            content_items.append(ft.Container(height=4))
            if memorial_date:
                content_items.append(ft.Text(
                    f"📅 {memorial_date}", size=14, font_family="Vazir", color=AppTheme.TEXT_SECONDARY))
            if memorial_location:
                content_items.append(ft.Text(
                    f"📍 {memorial_location}", size=14, font_family="Vazir", color=AppTheme.TEXT_SECONDARY))
            content_items.append(ft.Container(height=10))

        # توضیحات
        if description:
            content_items.append(ft.Text(
                description, size=14, font_family="Vazir", color=AppTheme.TEXT_SECONDARY))

        # نام ثبت‌کننده
        if created_by:
            content_items.append(ft.Container(height=12))
            content_items.append(ft.Divider(height=1, color="#F0F0F0"))
            content_items.append(ft.Container(height=8))
            content_items.append(
                ft.Text(f"ثبت توسط: {created_by}", size=11,
                        font_family="Vazir", color=AppTheme.TEXT_HINT)
            )

        return ft.Container(
            content=ft.Column(content_items),
            padding=ft.Padding(20, 0, 20, 20),
            bgcolor="#FFFFFF",
            border_radius=14,
            border=ft.Border(left=ft.BorderSide(4, "#616161")),
            margin=ft.Margin(0, 0, 0, 16),
            shadow=ft.BoxShadow(
                spread_radius=0, blur_radius=8, color="#00000010"),
        )

    def go_back(self, e):
        self.on_back()
