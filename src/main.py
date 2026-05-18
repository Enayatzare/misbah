import flet as ft
import asyncio
import os
from src.theme import AppTheme
from src.config import APP_NAME, APP_VERSION
from src.utils.formatters import persian_numbers


def main(page: ft.Page):
    APP_DISPLAY_NAME = "مصباح"
    APP_SUBTITLE = "سامانه‌ی اطلاع‌رسانی مسجد حضرت ابراهیم (ع)"

    page.title = APP_DISPLAY_NAME
    page.padding = 0
    page.rtl = True
    page.bgcolor = "#0D1B0F"

    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    logo_path = os.path.join(project_root, "assets",
                             "images", "logo_transparent.png")

    logo = ft.Container(
        content=ft.Image(src=logo_path, width=120, height=120),
        width=150,
        height=150,
        border=ft.Border.all(2.5, AppTheme.SECONDARY),
        border_radius=ft.BorderRadius.all(100),
        padding=12,
        shadow=ft.BoxShadow(spread_radius=0, blur_radius=25,
                            color=AppTheme.SECONDARY),
        opacity=0.0,
        animate_opacity=ft.Animation(1200, ft.AnimationCurve.EASE_OUT),
    )

    app_name = ft.Text(
        APP_DISPLAY_NAME,
        size=60,
        font_family="IranNastaliq",
        weight=ft.FontWeight.BOLD,
        color=AppTheme.SECONDARY,
        text_align=ft.TextAlign.CENTER,
        offset=ft.Offset(0, 0.3),
        animate_offset=ft.Animation(1000, ft.AnimationCurve.DECELERATE),
        opacity=0.0,
        animate_opacity=ft.Animation(1200, ft.AnimationCurve.EASE_OUT),
    )

    subtitle = ft.Text(
        APP_SUBTITLE,
        size=25,
        font_family="IranNastaliq",
        color="#AAAAAA",
        text_align=ft.TextAlign.CENTER,
        opacity=0.0,
        animate_opacity=ft.Animation(1200, ft.AnimationCurve.EASE_OUT),
    )

    gold_line = ft.Container(
        height=1.5, width=80, bgcolor=AppTheme.SECONDARY, border_radius=1,
        opacity=0.0, animate_opacity=ft.Animation(1000, ft.AnimationCurve.EASE_OUT),
    )

    dedication = ft.Text(
        "تقدیم به ساحت مقدس مهدی زهرا (عج)\nکه چشم‌ها برای زیارت صبحش بیدارند . . .",
        size=18, font_family="IranNastaliq", color=AppTheme.SECONDARY, text_align=ft.TextAlign.CENTER,
        opacity=0.0, animate_opacity=ft.Animation(1500, ft.AnimationCurve.EASE_OUT),
    )

    dots = ft.Row(
        [
            ft.Container(width=6, height=6, border_radius=5, bgcolor=AppTheme.SECONDARY,
                         opacity=0.0, animate_opacity=ft.Animation(1000, ft.AnimationCurve.EASE_IN)),
            ft.Container(width=6, height=6, border_radius=5, bgcolor=AppTheme.SECONDARY,
                         opacity=0.0, animate_opacity=ft.Animation(1000, ft.AnimationCurve.EASE_IN)),
            ft.Container(width=6, height=6, border_radius=5, bgcolor=AppTheme.SECONDARY,
                         opacity=0.0, animate_opacity=ft.Animation(1000, ft.AnimationCurve.EASE_IN)),
        ],
        alignment=ft.MainAxisAlignment.CENTER, spacing=12,
    )

    dhikr = ft.Text(
        "اللهم عجل لولیک الفرج", size=12, font_family="IranNastaliq", color="#888888", text_align=ft.TextAlign.CENTER,
        opacity=0.0, animate_opacity=ft.Animation(1200, ft.AnimationCurve.EASE_OUT),
    )

    # نسخه با اعداد فارسی
    app_version = ft.Text(
        f"نسخه {persian_numbers(APP_VERSION)}",
        size=10, font_family="Vazir", color="#555555", text_align=ft.TextAlign.CENTER,
        opacity=0.0, animate_opacity=ft.Animation(1500, ft.AnimationCurve.EASE_OUT),
    )

    splash_column = ft.Column(
        [
            ft.Container(height=30), logo, ft.Container(height=25),
            app_name, ft.Container(
                height=8), subtitle, ft.Container(height=18),
            gold_line, ft.Container(
                height=35), dedication, ft.Container(height=45),
            dots, ft.Container(height=30), dhikr, ft.Container(
                height=35), app_version,
        ],
        alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0,
    )

    splash_container = ft.Container(
        content=splash_column, alignment=ft.Alignment(0, 0), expand=True)

    bg_gradient = ft.Container(
        gradient=ft.LinearGradient(begin=ft.Alignment(
            0, -1), end=ft.Alignment(0, 1), colors=["#0D1B0F", "#1A2F1E", "#0D1B0F"]),
        expand=True,
    )

    splash_screen = ft.Stack([bg_gradient, splash_container], expand=True)
    page.add(splash_screen)

    async def animate_splash():
        await asyncio.sleep(0.3)
        logo.opacity = 1.0
        page.update()
        await asyncio.sleep(0.5)
        app_name.opacity = 1.0
        app_name.offset = ft.Offset(0, 0)
        page.update()
        await asyncio.sleep(0.4)
        subtitle.opacity = 1.0
        page.update()
        await asyncio.sleep(0.3)
        gold_line.opacity = 1.0
        page.update()
        await asyncio.sleep(0.5)
        dedication.opacity = 1.0
        page.update()
        for dot in dots.controls:
            await asyncio.sleep(0.4)
            dot.opacity = 1.0
            page.update()
        await asyncio.sleep(0.5)
        dhikr.opacity = 1.0
        page.update()
        await asyncio.sleep(0.8)
        app_version.opacity = 1.0
        page.update()
        await asyncio.sleep(4)
        page.clean()
        page.bgcolor = AppTheme.BACKGROUND
        show_main_page(page)

    page.run_task(animate_splash)


def show_main_page(page: ft.Page):
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

    from src.views.auth.login_page import LoginPage

    def on_login_success(user):
        from src.views.home.dashboard import Dashboard
        page.clean()
        page.bgcolor = AppTheme.BACKGROUND
        dashboard = Dashboard(page, user)
        page.add(dashboard.build())
        page.update()

    login_page = LoginPage(page, on_login_success)
    page.clean()
    page.add(login_page.build())
    page.update()


# ft.run(main)
