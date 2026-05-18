import flet as ft
from src.theme import AppTheme
from src.services.api_client import api
import os


class RegisterPage:
    def __init__(self, page: ft.Page, on_register_success):
        self.page = page
        self.on_register_success = on_register_success

        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(
            os.path.dirname(os.path.dirname(current_dir)))
        logo_path = os.path.join(
            project_root, "assets", "images", "logo_transparent.png")

        self.logo_image = ft.Image(src=logo_path, width=85, height=85)

        self.name_field = ft.TextField(
            label="نام کامل",
            prefix_icon=ft.icons.Icons.PERSON_OUTLINED,
            border_color="#E0D5C0", focused_border_color=AppTheme.SECONDARY,
            bgcolor="#FFFFFF", border_radius=10, border_width=1, filled=True,
            text_size=15, label_style=ft.TextStyle(font_family="Vazir", color=AppTheme.TEXT_HINT),
            color=AppTheme.TEXT_PRIMARY, cursor_color=AppTheme.SECONDARY,
        )
        self.phone_field = ft.TextField(
            label="شماره تماس", hint_text="۰۹۱۲۳۴۵۶۷۸۹",
            prefix_icon=ft.icons.Icons.PHONE_OUTLINED,
            keyboard_type=ft.KeyboardType.PHONE, max_length=11,
            border_color="#E0D5C0", focused_border_color=AppTheme.SECONDARY,
            bgcolor="#FFFFFF", border_radius=10, border_width=1, filled=True,
            text_size=15, label_style=ft.TextStyle(font_family="Vazir", color=AppTheme.TEXT_HINT),
            hint_style=ft.TextStyle(font_family="Vazir", color="#D0D0D0"),
            color=AppTheme.TEXT_PRIMARY, cursor_color=AppTheme.SECONDARY,
        )
        self.password_field = ft.TextField(
            label="رمز عبور",
            prefix_icon=ft.icons.Icons.LOCK_OUTLINED,
            password=True, can_reveal_password=True,
            border_color="#E0D5C0", focused_border_color=AppTheme.SECONDARY,
            bgcolor="#FFFFFF", border_radius=10, border_width=1, filled=True,
            text_size=15, label_style=ft.TextStyle(font_family="Vazir", color=AppTheme.TEXT_HINT),
            color=AppTheme.TEXT_PRIMARY, cursor_color=AppTheme.SECONDARY,
        )
        self.password_confirm = ft.TextField(
            label="تکرار رمز عبور",
            prefix_icon=ft.icons.Icons.LOCK_RESET,
            password=True, can_reveal_password=True,
            border_color="#E0D5C0", focused_border_color=AppTheme.SECONDARY,
            bgcolor="#FFFFFF", border_radius=10, border_width=1, filled=True,
            text_size=15, label_style=ft.TextStyle(font_family="Vazir", color=AppTheme.TEXT_HINT),
            color=AppTheme.TEXT_PRIMARY, cursor_color=AppTheme.SECONDARY,
        )
        self.error_text = ft.Text(
            "", color=AppTheme.ERROR, size=12, font_family="Vazir", text_align=ft.TextAlign.CENTER)
        self.loading = ft.ProgressBar(
            visible=False, color=AppTheme.PRIMARY, bgcolor="#E0E0E0", height=2)

    def build(self):
        background = ft.Container(
            gradient=ft.LinearGradient(
                begin=ft.Alignment(0, -1), end=ft.Alignment(0, 1),
                colors=["#0D1B0F", "#1A2F1E", "#0D1B0F"],
            ),
            expand=True,
        )

        top_line = ft.Container(height=2, bgcolor=AppTheme.SECONDARY,
                                border_radius=1, margin=ft.Margin(40, 0, 40, 0))
        bottom_line = ft.Container(
            height=2, bgcolor=AppTheme.SECONDARY, border_radius=1, margin=ft.Margin(40, 0, 40, 0))

        dhikr = ft.Text("اللهم عجل لولیک الفرج", size=16, font_family="IranNastaliq",
                        color=AppTheme.TEXT_HINT, text_align=ft.TextAlign.CENTER)

        card = ft.Container(
            content=ft.Column(
                [
                    top_line, ft.Container(height=15),
                    ft.Container(
                        content=self.logo_image, width=105, height=105,
                        border=ft.Border.all(2.5, AppTheme.SECONDARY), border_radius=ft.BorderRadius.all(60),
                        padding=8, bgcolor="#1A2F1E",
                        shadow=ft.BoxShadow(
                            spread_radius=0, blur_radius=20, color=AppTheme.SECONDARY),
                    ),
                    ft.Container(height=15),
                    ft.Text("مصباح", size=60, font_family="IranNastaliq",
                            color=AppTheme.PRIMARY, text_align=ft.TextAlign.CENTER),
                    ft.Container(height=6),
                    ft.Text("سامانه‌ی اطلاع‌رسانی مسجد حضرت ابراهیم (ع)", size=25,
                            font_family="IranNastaliq", color=AppTheme.TEXT_HINT, text_align=ft.TextAlign.CENTER),
                    ft.Container(height=20),
                    self.name_field, ft.Container(height=10),
                    self.phone_field, ft.Container(height=10),
                    self.password_field, ft.Container(height=10),
                    self.password_confirm,
                    ft.Container(height=6), self.error_text,
                    ft.Container(height=6), self.loading,
                    ft.Container(height=16),
                    ft.Button("ثبت‌نام", width=280, height=48,
                              style=ft.ButtonStyle(bgcolor=AppTheme.PRIMARY, color="#FFFFFF", shape=ft.RoundedRectangleBorder(radius=24),
                                                   text_style=ft.TextStyle(size=15, font_family="Vazir", weight=ft.FontWeight.BOLD)),
                              on_click=self.handle_register),
                    ft.Container(height=14),
                    ft.Row([ft.Text("حساب دارید؟", size=12, font_family="Vazir", color=AppTheme.TEXT_HINT),
                            ft.TextButton("ورود", on_click=self.go_to_login,
                                          style=ft.ButtonStyle(color=AppTheme.PRIMARY, text_style=ft.TextStyle(size=12, font_family="Vazir", weight=ft.FontWeight.BOLD)))],
                           alignment=ft.MainAxisAlignment.CENTER, spacing=2),
                    ft.Container(height=15), bottom_line,
                    ft.Container(height=15), dhikr, ft.Container(height=8),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0,
            ),
            padding=ft.Padding(30, 5, 30, 10), bgcolor="#FFFFFFF2", border_radius=20,
            shadow=ft.BoxShadow(spread_radius=0, blur_radius=25, color="#00000030"), width=350,
        )

        return ft.Stack(
            [background, ft.Container(
                content=card, alignment=ft.Alignment(0, 0.1), expand=True)],
            expand=True,
        )

    def handle_register(self, e):
        name = self.name_field.value.strip() if self.name_field.value else ""
        phone = self.phone_field.value.strip() if self.phone_field.value else ""
        password = self.password_field.value if self.password_field.value else ""
        confirm = self.password_confirm.value if self.password_confirm.value else ""
        self.error_text.value = ""
        if not name or not phone or not password:
            self.error_text.value = "لطفاً همه فیلدها را پر کنید"
            self.page.update()
            return
        if not phone.startswith("09") or len(phone) != 11:
            self.error_text.value = "شماره تماس نامعتبر است"
            self.page.update()
            return
        if len(password) < 6:
            self.error_text.value = "رمز عبور باید حداقل ۶ کاراکتر باشد"
            self.page.update()
            return
        if password != confirm:
            self.error_text.value = "رمز عبور و تکرار آن مطابقت ندارند"
            self.page.update()
            return
        self.loading.visible = True
        self.page.update()
        result = api.post(
            "auth/register.php", {"full_name": name, "phone": phone, "password": password})
        self.loading.visible = False
        if "token" in result:
            api.set_token(result["token"])
            self.on_register_success(result["user"])
        else:
            self.error_text.value = result.get("error", "خطا در ثبت‌نام")
        self.page.update()

    def go_to_login(self, e):
        import sys
        import os
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from src.views.auth.login_page import LoginPage
        login_page = LoginPage(self.page, self.on_register_success)
        self.page.clean()
        self.page.add(login_page.build())
        self.page.update()
