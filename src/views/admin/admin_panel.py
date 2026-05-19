import flet as ft
from src.theme import AppTheme
from src.services.api_client import api
from src.utils.formatters import persian_numbers


class AdminPanel:
    def __init__(self, page: ft.Page, on_back, user: dict):
        self.page = page
        self.on_back = on_back
        self.user = user

    def build(self):
        header = ft.Container(
            content=ft.Row(
                [
                    ft.IconButton(icon=ft.icons.Icons.ARROW_BACK,
                                  icon_color="#FFFFFF", on_click=self.go_back),
                    ft.Text("پنل مدیریت", size=18, font_family="Vazir",
                            weight=ft.FontWeight.BOLD, color="#FFFFFF"),
                    ft.Container(expand=True),
                    ft.IconButton(icon=ft.icons.Icons.LOGOUT,
                                  icon_color="#FF5252", on_click=self._logout),
                ],
                alignment=ft.MainAxisAlignment.START,
            ),
            padding=ft.Padding(15, 35, 15, 15),
            bgcolor="#0D1B0F",
        )

        self.stats_row = ft.Row(
            spacing=10, alignment=ft.MainAxisAlignment.CENTER, wrap=True)

        menu_items = ft.GridView(
            expand=True,
            runs_count=2,
            spacing=12,
            run_spacing=12,
            padding=20,
            controls=[
                self._build_menu_card(
                    "اطلاعیه‌ها", ft.icons.Icons.CAMPAIGN, "#E53935", self.manage_announcements),
                self._build_menu_card(
                    "قرآن و ادعیه", ft.icons.Icons.MENU_BOOK, "#1B5E20", self.manage_duas),
                self._build_menu_card(
                    "برنامه هفتگی", ft.icons.Icons.CALENDAR_MONTH, "#1565C0", self.manage_schedule),
                self._build_menu_card(
                    "مشارکت‌های مردمی", ft.icons.Icons.HANDSHAKE, "#EF6C00", self.manage_donations),
                self._build_menu_card(
                    "آگهی ترحیم", ft.icons.Icons.FLAG, "#616161", self.manage_deceased),
                self._build_menu_card(
                    "کاربران", ft.icons.Icons.PEOPLE, "#7B1FA2", self.manage_users),
            ],
        )

        page_content = ft.Container(
            content=ft.ListView(
                controls=[
                    ft.Container(height=15),
                    ft.Row(
                        [ft.Icon(ft.icons.Icons.ADMIN_PANEL_SETTINGS, size=28, color=AppTheme.SECONDARY),
                         ft.Text("پنل مدیریت", size=36, font_family="IranNastaliq", color=AppTheme.SECONDARY)],
                        alignment=ft.MainAxisAlignment.CENTER, spacing=10,
                    ),
                    ft.Container(height=8),
                    ft.Row([ft.Container(height=1.5, width=60, bgcolor=AppTheme.SECONDARY,
                           border_radius=1)], alignment=ft.MainAxisAlignment.CENTER),
                    ft.Container(height=20),
                    ft.Text("📊 آمار کلی", size=16, font_family="Vazir", weight=ft.FontWeight.BOLD,
                            color="#FFFFFF", text_align=ft.TextAlign.CENTER),
                    ft.Container(height=10),
                    self.stats_row,
                    ft.Container(height=25),
                    ft.Text("⚙️ بخش‌های مدیریت", size=16, font_family="Vazir",
                            weight=ft.FontWeight.BOLD, color="#FFFFFF", text_align=ft.TextAlign.CENTER),
                    ft.Container(height=5),
                    menu_items,
                ],
                padding=ft.Padding(0, 0, 0, 20),
            ),
            expand=True,
            gradient=ft.LinearGradient(
                begin=ft.Alignment(0, -1), end=ft.Alignment(0, 1),
                colors=["#0D1B0F", "#1A2F1E", "#0D1B0F"],
            ),
        )

        self.load_stats()
        return ft.Column([header, page_content], expand=True, spacing=0)

    def load_stats(self):
        stats = api.get("admin/dashboard/get_stats.php")

        # همچنین تعداد آگهی‌های ترحیم را به طور جداگانه دریافت می‌کنیم
        deceased_result = api.get("social/get_deceased.php")
        total_deceased = len(deceased_result) if isinstance(
            deceased_result, list) else 0

        if stats and "error" not in stats:
            self.stats_row.controls = [
                self._build_stat_card("اطلاعیه‌ها", ft.icons.Icons.CAMPAIGN, "#E53935", persian_numbers(
                    str(stats.get("total_announcements", 0)))),
                self._build_stat_card("قرآن و ادعیه", ft.icons.Icons.MENU_BOOK, "#1B5E20", persian_numbers(
                    str(stats.get("total_duas", 0)))),
                self._build_stat_card("برنامه‌ها", ft.icons.Icons.CALENDAR_MONTH, "#1565C0", persian_numbers(
                    str(stats.get("total_events", 0)))),
                self._build_stat_card("در انتظار", ft.icons.Icons.HANDSHAKE, "#EF6C00", persian_numbers(
                    str(stats.get("pending_donations", 0)))),
                # ✅ کارت جدید برای آگهی ترحیم
                self._build_stat_card("آگهی ترحیم", ft.icons.Icons.FLAG, "#616161", persian_numbers(
                    str(total_deceased))),
            ]
            self.page.update()

    def _build_stat_card(self, title: str, icon, color: str, value: str):
        return ft.Container(
            content=ft.Row(
                [
                    ft.Icon(icon, size=18, color=color),
                    ft.Container(width=6),
                    ft.Text(value, size=18, font_family="Vazir",
                            weight=ft.FontWeight.BOLD, color=color),
                    ft.Container(width=4),
                    ft.Text(title, size=10, font_family="Vazir",
                            color=AppTheme.TEXT_HINT),
                ],
            ),
            padding=ft.Padding(8, 6, 8, 6),
            bgcolor="#FFFFFF",
            border_radius=10,
            width=170,
        )

    def _build_menu_card(self, title: str, icon, color: str, on_click):
        return ft.Container(
            content=ft.Column(
                [
                    ft.Container(
                        content=ft.Icon(icon, size=30, color="#FFFFFF"),
                        width=55, height=55,
                        bgcolor=color, border_radius=28,
                        alignment=ft.Alignment(0, 0),
                    ),
                    ft.Container(height=10),
                    ft.Text(title, size=13, font_family="Vazir", weight=ft.FontWeight.BOLD,
                            color=AppTheme.TEXT_PRIMARY, text_align=ft.TextAlign.CENTER),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            bgcolor="#FFFFFF",
            border_radius=14,
            border=ft.Border(left=ft.BorderSide(4, AppTheme.SECONDARY)),
            padding=15,
            shadow=ft.BoxShadow(
                spread_radius=0, blur_radius=8, color="#00000010"),
            on_click=on_click,
        )

    def manage_announcements(self, e):
        from src.views.admin.manage_announcements import ManageAnnouncements
        def on_back(): self.page.clean(); self.page.add(self.build()); self.page.update()
        page = ManageAnnouncements(self.page, on_back)
        self.page.clean()
        self.page.add(page.build())
        self.page.update()

    def manage_duas(self, e):
        from src.views.admin.manage_duas import ManageDuas
        def on_back(): self.page.clean(); self.page.add(self.build()); self.page.update()
        page = ManageDuas(self.page, on_back)
        self.page.clean()
        self.page.add(page.build())
        self.page.update()

    def manage_schedule(self, e):
        from src.views.admin.manage_schedule import ManageSchedule
        def on_back(): self.page.clean(); self.page.add(self.build()); self.page.update()
        page = ManageSchedule(self.page, on_back)
        self.page.clean()
        self.page.add(page.build())
        self.page.update()

    def manage_donations(self, e):
        from src.views.admin.manage_donations import ManageDonations
        def on_back(): self.page.clean(); self.page.add(self.build()); self.page.update()
        page = ManageDonations(self.page, on_back)
        self.page.clean()
        self.page.add(page.build())
        self.page.update()

    def manage_deceased(self, e):
        from src.views.admin.manage_deceased import ManageDeceased
        def on_back(): self.page.clean(); self.page.add(self.build()); self.page.update()
        page = ManageDeceased(self.page, on_back)
        self.page.clean()
        self.page.add(page.build())
        self.page.update()

    def manage_users(self, e):
        from src.views.admin.manage_users import ManageUsers
        def on_back(): self.page.clean(); self.page.add(self.build()); self.page.update()
        page = ManageUsers(self.page, on_back)
        self.page.clean()
        self.page.add(page.build())
        self.page.update()

    def _show_snack(self, msg: str):
        self.page.snack_bar = ft.SnackBar(ft.Text(msg))
        self.page.snack_bar.open = True
        self.page.update()

    def _logout(self, e):
        from src.services.api_client import api as api_mod
        from src.views.auth.login_page import LoginPage
        api_mod.clear_token()
        self.page.clean()

        def on_login_success(user):
            from src.views.home.dashboard import Dashboard
            self.page.clean()
            self.page.add(Dashboard(self.page, user).build())
            self.page.update()
        login_page = LoginPage(self.page, on_login_success)
        self.page.add(login_page.build())
        self.page.update()

    def go_back(self, e):
        self.on_back()
