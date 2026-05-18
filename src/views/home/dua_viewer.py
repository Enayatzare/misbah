import flet as ft
from src.theme import AppTheme
import asyncio


class DuaViewerPage:
    def __init__(self, page: ft.Page, on_back, dua: dict):
        self.page = page
        self.on_back = on_back
        self.dua = dua

    def build(self):
        title = self.dua.get("title", "دعا")
        subtitle = self.dua.get("subtitle", "")
        file_url = self.dua.get("file_url", "")
        full_url = f"http://enayatzare98.ir/{file_url}" if file_url else ""

        header = ft.Container(
            content=ft.Row(
                [
                    ft.IconButton(
                        icon=ft.icons.Icons.ARROW_BACK,
                        icon_color="#FFFFFF",
                        on_click=lambda e: self.on_back(),
                    ),
                    ft.Text(title, size=18, font_family="Vazir",
                            weight=ft.FontWeight.BOLD, color="#FFFFFF"),
                    ft.Container(expand=True),
                    ft.IconButton(
                        icon=ft.icons.Icons.DOWNLOAD,
                        icon_color="#FFFFFF",
                        on_click=lambda e: self._download_pdf(full_url),
                    ),
                ],
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.Padding(15, 35, 15, 15),
            bgcolor="#0D1B0F",
            border_radius=ft.BorderRadius(0, 0, 20, 20),
        )

        # ستون اطلاعات
        info_items = [
            ft.Icon(ft.icons.Icons.PICTURE_AS_PDF,
                    size=60, color=AppTheme.ERROR),
            ft.Container(height=10),
            ft.Text("برای مشاهده دعا کلیک کنید", size=16, font_family="Vazir",
                    weight=ft.FontWeight.BOLD, color=AppTheme.TEXT_PRIMARY),
            ft.Container(height=4),
            ft.Text(title, size=14, font_family="Vazir",
                    color=AppTheme.TEXT_HINT),
        ]
        if subtitle:
            info_items.append(
                ft.Text(subtitle, size=12, font_family="Vazir", color=AppTheme.TEXT_HINT))

        open_button = ft.Container(
            content=ft.Column(
                info_items,
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            on_click=lambda e: self._open_pdf(full_url),
            padding=30,
            bgcolor="#FFFFFF",
            border_radius=16,
            border=ft.Border.all(2, AppTheme.SECONDARY),
            shadow=ft.BoxShadow(
                spread_radius=0, blur_radius=15, color="#00000015"),
        )

        return ft.Container(
            content=ft.Column(
                [
                    header,
                    ft.Container(
                        content=open_button,
                        alignment=ft.Alignment(0, 0),
                        expand=True,
                        padding=30,
                    ),
                ],
                spacing=0,
            ),
            expand=True,
            gradient=ft.LinearGradient(
                begin=ft.Alignment(0, -1),
                end=ft.Alignment(0, 1),
                colors=["#0D1B0F", "#1A2F1E", "#0D1B0F"],
            ),
        )

    def _open_pdf(self, url: str):
        if url:
            asyncio.create_task(self.page.launch_url(url))

    def _download_pdf(self, url: str):
        if url:
            asyncio.create_task(self.page.launch_url(url))
