from src.main import main
import flet as ft
import os

if __name__ == "__main__":
    # تابع wrapper برای تنظیم فونت قبل از اجرای برنامه
    def run_with_fonts(page: ft.Page):
        # تنظیم فونت‌های سفارشی با مسیر نسبی (برای APK)
        page.fonts = {
            "Vazir": "fonts/Vazir.woff",
            "IranNastaliq": "fonts/IranNastaliq.woff",
        }
        # فراخوانی تابع اصلی برنامه
        main(page)

    ft.app(target=run_with_fonts)
