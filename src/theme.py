import flet as ft


class AppTheme:
    PRIMARY = "#1B5E20"
    PRIMARY_LIGHT = "#2E7D32"
    SECONDARY = "#D4AF37"
    SECONDARY_LIGHT = "#FFD700"
    BACKGROUND = "#FFF8E7"
    SURFACE = "#FFFFFF"
    CARD_BG = "#FFFFFF"
    TEXT_PRIMARY = "#3E2723"
    TEXT_SECONDARY = "#5D4037"
    TEXT_HINT = "#8D6E63"
    SUCCESS = "#2E7D32"
    ERROR = "#C62828"
    WARNING = "#F57F17"
    INFO = "#1565C0"

    @staticmethod
    def get_theme():
        # دیکشنری فونت‌ها - فقط نام فونت و مسیر نسبی
        # مسیر به پوشه‌ای که فایل woff در آن قرار دارد
        fonts_dict = {
            "Vazir": "/fonts/Vazir.woff",  # یا Vazirmatn.woff
            "IranNastaliq": "/fonts/IranNastaliq.woff",  # اختیاری
        }

        return ft.Theme(
            use_material3=True,
            font_family="Vazir",  # فونت پیش‌فرض کل برنامه
            fonts=fonts_dict,  # ⚠️ این خط اضافه شده است
            scaffold_bgcolor=AppTheme.BACKGROUND,
            color_scheme=ft.ColorScheme(
                primary=AppTheme.PRIMARY,
                on_primary="#FFFFFF",
                primary_container=AppTheme.PRIMARY_LIGHT,
                on_primary_container="#FFFFFF",
                secondary=AppTheme.SECONDARY,
                on_secondary="#000000",
                secondary_container=AppTheme.SECONDARY_LIGHT,
                on_secondary_container="#000000",
                surface=AppTheme.SURFACE,
                on_surface=AppTheme.TEXT_PRIMARY,
                surface_container=AppTheme.CARD_BG,
                on_surface_variant=AppTheme.TEXT_SECONDARY,
                error=AppTheme.ERROR,
                on_error="#FFFFFF",
                error_container="#FFCDD2",
                on_error_container="#B71C1C",
                outline=AppTheme.SECONDARY,
                outline_variant=AppTheme.TEXT_HINT,
            ),
            text_theme=ft.TextTheme(
                body_large=ft.TextStyle(
                    font_family="Vazir", color=AppTheme.TEXT_PRIMARY),
                body_medium=ft.TextStyle(
                    font_family="Vazir", color=AppTheme.TEXT_SECONDARY),
                body_small=ft.TextStyle(
                    font_family="Vazir", color=AppTheme.TEXT_HINT),
                title_large=ft.TextStyle(
                    font_family="Vazir", color=AppTheme.TEXT_PRIMARY, weight="bold"),
                title_medium=ft.TextStyle(
                    font_family="Vazir", color=AppTheme.TEXT_PRIMARY),
                label_large=ft.TextStyle(
                    font_family="Vazir", color=AppTheme.TEXT_PRIMARY, weight="bold"),
            ),
            visual_density=ft.ThemeVisualDensity.COMFORTABLE,
        )
