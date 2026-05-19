import flet as ft
from src.theme import AppTheme
from src.services.api_client import api


class DuasPage:
    def __init__(self, page: ft.Page, on_back):
        self.page = page
        self.on_back = on_back

    def build(self):
        header = ft.Container(
            content=ft.Row(
                [
                    ft.IconButton(icon=ft.icons.Icons.ARROW_BACK,
                                  icon_color="#FFFFFF", on_click=self.go_back),
                    ft.Text("قرآن و ادعیه", size=18, font_family="Vazir",
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

        self.load_duas()
        return ft.Column([header, page_content], expand=True, spacing=0)

    def load_duas(self):
        result = api.get("duas/get_list.php")

        if isinstance(result, list) and len(result) > 0:
            items = [
                ft.Container(height=10),
                ft.Row(
                    [
                        ft.Icon(ft.icons.Icons.MENU_BOOK, size=28,
                                color=AppTheme.SECONDARY),
                        ft.Text("قرآن و ادعیه", size=32, font_family="IranNastaliq",
                                color=AppTheme.SECONDARY, text_align=ft.TextAlign.CENTER),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=10,
                ),
                ft.Container(height=1.5, width=100,
                             bgcolor=AppTheme.SECONDARY, border_radius=1),
                ft.Container(height=15),
            ]
            for dua in result:
                items.append(self._build_dua_card(dua))
            items.append(ft.Container(height=20))
            self.content_column.controls = items
            self.content_column.alignment = ft.MainAxisAlignment.START
        else:
            self.content_column.controls = [
                ft.Container(height=60),
                ft.Text("دعایی ثبت نشده است", size=15,
                        font_family="Vazir", color="#FFFFFFAA"),
            ]
            self.content_column.alignment = ft.MainAxisAlignment.CENTER
        self.page.update()

    def _build_dua_card(self, dua: dict):
        title = dua.get("title", "بدون عنوان")

        is_quran = any(word in title for word in [
                       "سوره", "آیات", "آیت", "قرآن"])

        if is_quran:
            icon = ft.icons.Icons.LOCAL_LIBRARY
            bg_color = "#E8F5E9"
            icon_color = "#2E7D32"
        else:
            icon = ft.icons.Icons.MENU_BOOK
            bg_color = "#E3F2FD"
            icon_color = "#1565C0"

        return ft.Container(
            content=ft.Row(
                [
                    ft.Container(
                        content=ft.Icon(icon, size=20, color=icon_color),
                        width=42, height=42,
                        bgcolor=bg_color, border_radius=21,
                        alignment=ft.Alignment(0, 0),
                    ),
                    ft.Container(width=14),
                    ft.Text(title, size=15, font_family="Vazir",
                            weight=ft.FontWeight.BOLD, color=AppTheme.TEXT_PRIMARY),
                    ft.Container(expand=True),
                    ft.Icon(ft.icons.Icons.CHEVRON_LEFT,
                            size=18, color=AppTheme.TEXT_HINT),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.Padding(16, 14, 16, 14),
            bgcolor="#FFFFFF",
            border_radius=12,
            border=ft.Border.all(1, "#E0E0E0"),
            margin=ft.Margin(0, 0, 0, 8),
            shadow=ft.BoxShadow(
                spread_radius=0, blur_radius=4, color="#00000010"),
            on_click=lambda e, d=dua: self._open_dua(d),
        )

    def _open_dua(self, dua: dict):
        file_url = dua.get("file_url", "")
        if file_url:
            full_url = f"http://enayatzare98.ir/{file_url}"
            import asyncio
            asyncio.create_task(self.page.launch_url(full_url))

    def _close_pdf_dialog(self, dialog):
        dialog.open = False
        self.page.overlay.remove(dialog)
        self.page.update()

    def go_back(self, e):
        self.on_back()
