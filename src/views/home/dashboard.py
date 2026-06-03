import flet as ft
from src.theme import AppTheme
from src.services.api_client import api
from src.utils.formatters import persian_numbers
import os
import sys
import requests
import asyncio


sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class Dashboard:
    def __init__(self, page: ft.Page, user: dict):
        self.page = page
        self.user = user
        self.logo_path = "assets/images/logo_transparent.png"

        # تنظیم رویداد back برای دیالوگ خروج
        self.page.on_pop = self.on_back_pressed

    def on_back_pressed(self, e):
        """نمایش دیالوگ خروج از برنامه"""
        def on_confirm(e):
            self.page.window.close()

        def on_cancel(e):
            dlg.open = False
            self.page.update()

        dlg = ft.AlertDialog(
            bgcolor="#0D1B0F",
            title=ft.Text("خروج از برنامه", font_family="Vazir",
                          weight=ft.FontWeight.BOLD, color=AppTheme.SECONDARY,
                          text_align=ft.TextAlign.CENTER),
            content=ft.Text("آیا می‌خواهید از برنامه خارج شوید؟",
                            font_family="Vazir", color="#FFFFFF",
                            text_align=ft.TextAlign.CENTER),
            actions=[
                ft.TextButton("خیر", on_click=on_cancel,
                              style=ft.ButtonStyle(color="#FFFFFF60")),
                ft.Button("بله", on_click=on_confirm,
                          style=ft.ButtonStyle(bgcolor=AppTheme.ERROR, color="#FFFFFF")),
            ],
            actions_alignment=ft.MainAxisAlignment.CENTER,
        )
        self.page.show_dialog(dlg)
        return True  # جلوگیری از خروج خودکار

    def build(self):
        user_initial = self.user.get("full_name", "?")[0]
        user_name = self.user.get("full_name", "کاربر")

        popup_menu = ft.PopupMenuButton(
            icon=ft.icons.Icons.MENU,
            icon_color="#FFFFFF",
            bgcolor="#0D1B0F",
            items=[
                ft.PopupMenuItem(
                    content=ft.Column([
                        ft.Container(height=10),
                        ft.Row([ft.Container(content=ft.Text(user_initial, size=22, color="#FFFFFF", font_family="Vazir", weight=ft.FontWeight.BOLD), width=50,
                               height=50, bgcolor=AppTheme.PRIMARY, border_radius=25, alignment=ft.Alignment(0, 0))], alignment=ft.MainAxisAlignment.CENTER),
                        ft.Container(height=8),
                        ft.Text(user_name, size=14, font_family="Vazir", weight=ft.FontWeight.BOLD,
                                color="#FFFFFF", text_align=ft.TextAlign.CENTER),
                        ft.Container(height=4),
                        ft.Text(self.user.get("phone", ""), size=11, font_family="Vazir",
                                color="#FFFFFF80", text_align=ft.TextAlign.CENTER),
                        ft.Container(height=10),
                        ft.Divider(height=1, color="#FFFFFF20"),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    on_click=None,
                ),
                ft.PopupMenuItem(
                    content=ft.Row([ft.Icon(ft.icons.Icons.PERSON, size=20, color="#FFFFFF"), ft.Text(
                        "پروفایل کاربری", font_family="Vazir", color="#FFFFFF")]),
                    on_click=self._show_profile_page,
                ),
                ft.PopupMenuItem(
                    content=ft.Row([ft.Icon(ft.icons.Icons.HISTORY, size=20, color="#FFFFFF"), ft.Text(
                        "تاریخچه مشارکت‌ها", font_family="Vazir", color="#FFFFFF")]),
                    on_click=self._show_donation_history,
                ),
                ft.PopupMenuItem(
                    content=ft.Row([ft.Icon(ft.icons.Icons.NOTIFICATIONS, size=20, color="#FFFFFF"), ft.Text(
                        "اعلان‌ها", font_family="Vazir", color="#FFFFFF")]),
                    on_click=self._show_notifications_dialog,
                ),
                ft.PopupMenuItem(
                    content=ft.Row([ft.Icon(ft.icons.Icons.HELP, size=20, color="#FFFFFF"), ft.Text(
                        "راهنما", font_family="Vazir", color="#FFFFFF")]),
                    on_click=self._show_help,
                ),
                ft.PopupMenuItem(
                    content=ft.Row([ft.Icon(ft.icons.Icons.INFO, size=20, color="#FFFFFF"), ft.Text(
                        "درباره ما", font_family="Vazir", color="#FFFFFF")]),
                    on_click=self._show_about,
                ),
                ft.PopupMenuItem(),
                ft.PopupMenuItem(
                    content=ft.Row([ft.Icon(ft.icons.Icons.LOGOUT, size=20, color="#FFFFFF"), ft.Text(
                        "خروج از حساب", font_family="Vazir", color="#FFFFFF")]),
                    on_click=self._logout,
                ),
            ],
        )

        header = ft.Container(
            content=ft.Column([
                ft.Row([
                    popup_menu,
                    ft.Image(src=self.logo_path, width=35, height=35),
                    ft.Text("مصباح", size=35, font_family="IranNastaliq",
                            color=AppTheme.SECONDARY),
                    ft.Container(expand=True),

                    ft.Container(width=8),
                    ft.Container(content=ft.Icon(ft.icons.Icons.NOTIFICATIONS_OUTLINED,
                                 size=22, color="#FFFFFF"), on_click=self.show_notifications),
                ], alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                ft.Container(height=6),
                ft.Text(f"{user_name} خوش آمدید 👋", size=14,
                        font_family="Vazir", color="#FFFFFFCC"),
            ]),
            padding=ft.Padding(20, 35, 20, 15), bgcolor="#0D1B0F", border_radius=ft.BorderRadius(0, 0, 25, 25),
        )

        # کارت مخصوص ذکر شمار (با ایموجی)
        tasbih_card = ft.Container(
            content=ft.Column([
                ft.Text("📿", size=36, text_align=ft.TextAlign.CENTER),
                ft.Container(height=8),
                ft.Text("ذکر شمار", size=13, font_family="Vazir", weight=ft.FontWeight.BOLD,
                        color=AppTheme.TEXT_PRIMARY, text_align=ft.TextAlign.CENTER)
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor="#C8E6C9",  # سبز کمرنگ
            border_radius=16,
            border=ft.Border.all(2.5, "#D4AF37"),
            padding=15,
            shadow=ft.BoxShadow(spread_radius=0, blur_radius=10, color="#00000010"),
            on_click=self.show_tasbih,
        )

        cards = ft.GridView(
            expand=True, runs_count=2, spacing=12, run_spacing=12, padding=20,
            controls=[
                self._build_card("اوقات شرعی", ft.icons.Icons.NIGHTLIGHT_ROUND,
                                 "#D4AF37", "#FFECB3", self.show_prayer_times),
                self._build_card(
                    "قرآن و ادعیه", ft.icons.Icons.MENU_BOOK, "#1B5E20", "#C8E6C9", self.show_duas),
                self._build_card("اطلاعیه‌ها", ft.icons.Icons.CAMPAIGN,
                                 "#E53935", "#FFCDD2", self.show_announcements),
                self._build_card("برنامه هفتگی", ft.icons.Icons.CALENDAR_MONTH,
                                 "#1565C0", "#BBDEFB", self.show_schedule),
                self._build_card("مشارکت‌های مردمی", ft.icons.Icons.HANDSHAKE,
                                 "#EF6C00", "#FFE0B2", self.show_donations),
                self._build_card("آگهی ترحیم", ft.icons.Icons.FLAG,
                                 "#616161", "#E0E0E0", self.show_deceased),
                tasbih_card,  # کارت ذکر شمار
            ],
        )
        if self.user.get("role") in ["admin", "super_admin"]:
            cards.controls.append(self._build_card(
                "پنل مدیریت", ft.icons.Icons.DASHBOARD_CUSTOMIZE, "#6A1B9A", "#E1BEE7", self.show_admin_panel))

        main_content = ft.Column(
            [
                header,
                ft.Container(
                    content=ft.Text("دسترسی سریع", size=16, font_family="Vazir",
                                    weight=ft.FontWeight.BOLD, color=AppTheme.TEXT_PRIMARY),
                    padding=ft.Padding(20, 20, 0, 0)
                ),
                cards,
                ft.Container(height=80),
            ],
            spacing=0,
        )

        scrollable_content = ft.ListView(
            controls=[main_content],
            expand=True,
            padding=0,
        )

        result = ft.Container(
            content=scrollable_content,
            bgcolor=AppTheme.BACKGROUND,
            expand=True,
        )

        self._check_for_update()

        return result

    def _build_card(self, title: str, icon, color: str, bg_color: str, on_click):
        return ft.Container(
            content=ft.Column([ft.Icon(icon, size=36, color=color), ft.Container(height=8), ft.Text(title, size=13, font_family="Vazir", weight=ft.FontWeight.BOLD,
                              color=AppTheme.TEXT_PRIMARY, text_align=ft.TextAlign.CENTER)], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor=bg_color, border_radius=16, border=ft.Border.all(2.5, color), padding=15, shadow=ft.BoxShadow(spread_radius=0, blur_radius=10, color="#00000010"), on_click=on_click,
        )

    def _check_for_update(self):
        try:
            response = requests.get(
                "http://enayatzare98.ir/version.json", timeout=5)
            if response.status_code == 200:
                update_info = response.json()
                latest_version = update_info.get("version", "1.0.0")
                current_version = "1.0.0"
                if latest_version > current_version:
                    self._show_update_dialog(update_info)
        except:
            pass

    def _show_update_dialog(self, update_info):
        changes = update_info.get("changes", [])
        changes_text = "\n".join([f"✨ {c}" for c in changes])

        def download(e):
            dlg.open = False
            self.page.update()
            asyncio.create_task(self.page.launch_url(update_info["apk_url"]))

        def later(e):
            dlg.open = False
            self.page.update()

        dlg = ft.AlertDialog(
            bgcolor="#0D1B0F",
            title=ft.Text(""),
            content=ft.Column([
                ft.Container(height=5),
                ft.Icon(ft.icons.Icons.SYSTEM_UPDATE,
                        size=50, color=AppTheme.SECONDARY),
                ft.Container(height=10),
                ft.Text("🆕 نسخه جدید در دسترس است!", size=18, font_family="Vazir",
                        weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER, color=AppTheme.SECONDARY),
                ft.Container(height=4),
                ft.Row([ft.Container(height=1.5, width=40, bgcolor=AppTheme.SECONDARY,
                       border_radius=1)], alignment=ft.MainAxisAlignment.CENTER),
                ft.Container(height=10),
                ft.Text(f"نسخه {update_info['version']}", size=16, font_family="Vazir",
                        color="#FFFFFF", text_align=ft.TextAlign.CENTER),
                ft.Container(height=10),
                ft.Divider(height=1, color="#FFFFFF20"),
                ft.Container(height=10),
                ft.Text("تغییرات:", size=13, font_family="Vazir",
                        weight=ft.FontWeight.BOLD, color="#FFFFFF80"),
                ft.Container(height=6),
                ft.Text(changes_text, size=12, font_family="Vazir",
                        color="#FFFFFF", text_align=ft.TextAlign.RIGHT),
                ft.Container(height=10),
                ft.Divider(height=1, color="#FFFFFF20"),
                ft.Container(height=8),
                ft.Text(f"📅 تاریخ انتشار: {update_info['release_date']}",
                        size=11, font_family="Vazir", color="#FFFFFF60"),
                ft.Container(height=5),
            ], width=290, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            actions=[
                ft.TextButton("بعداً", on_click=later,
                              style=ft.ButtonStyle(color="#FFFFFF60")),
                ft.Button("📥 دانلود نسخه جدید", on_click=download,
                          style=ft.ButtonStyle(bgcolor=AppTheme.PRIMARY, color="#FFFFFF", shape=ft.RoundedRectangleBorder(radius=8))),
            ],
        )
        self.page.show_dialog(dlg)

    def show_prayer_times(self, e):
        from src.views.home.prayer_page import PrayerPage
        def on_back(): self.page.clean(); self.page.add(self.build()); self.page.update()
        self.page.clean()
        self.page.add(PrayerPage(self.page, on_back).build())
        self.page.update()

    def show_duas(self, e):
        from src.views.home.duas_page import DuasPage
        def on_back(): self.page.clean(); self.page.add(self.build()); self.page.update()
        self.page.clean()
        self.page.add(DuasPage(self.page, on_back).build())
        self.page.update()

    def show_announcements(self, e):
        from src.views.home.announcements_page import AnnouncementsPage
        def on_back(): self.page.clean(); self.page.add(self.build()); self.page.update()
        self.page.clean()
        self.page.add(AnnouncementsPage(self.page, on_back).build())
        self.page.update()

    def show_schedule(self, e):
        from src.views.home.weekly_schedule_page import WeeklySchedulePage
        def on_back(): self.page.clean(); self.page.add(self.build()); self.page.update()
        self.page.clean()
        self.page.add(WeeklySchedulePage(self.page, on_back).build())
        self.page.update()

    def show_donations(self, e):
        from src.views.home.donations_page import DonationsPage
        def on_back(): self.page.clean(); self.page.add(self.build()); self.page.update()
        self.page.clean()
        self.page.add(DonationsPage(self.page, on_back, self.user).build())
        self.page.update()

    def show_deceased(self, e):
        from src.views.home.deceased_page import DeceasedPage
        def on_back(): self.page.clean(); self.page.add(self.build()); self.page.update()
        self.page.clean()
        self.page.add(DeceasedPage(self.page, on_back).build())
        self.page.update()

    def show_tasbih(self, e):
        from src.views.home.tasbih_page import TasbihPage
        def on_back(): 
            self.page.clean()
            self.page.add(self.build())
            self.page.update()
        self.page.clean()
        self.page.add(TasbihPage(self.page, on_back).build())
        self.page.update()
        

    def show_admin_panel(self, e):
        from src.views.admin.admin_panel import AdminPanel
        def on_back(): self.page.clean(); self.page.add(self.build()); self.page.update()
        self.page.clean()
        self.page.add(AdminPanel(self.page, on_back, self.user).build())
        self.page.update()

    def show_notifications(self, e): self._show_coming_soon("اعلان‌ها")

    def _show_snack(self, message: str):
        self.page.snack_bar = ft.SnackBar(ft.Text(message))
        self.page.snack_bar.open = True
        self.page.update()

    def _show_coming_soon(self, section: str):
        def close(e): dlg.open = False; self.page.update()
        dlg = ft.AlertDialog(bgcolor="#0D1B0F", title=ft.Text(f"📢 {section}", font_family="Vazir", weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER, color=AppTheme.SECONDARY), content=ft.Text(
            "این بخش به‌زودی اضافه خواهد شد", size=13, font_family="Vazir", color="#FFFFFF", text_align=ft.TextAlign.CENTER), actions=[ft.TextButton("باشه", on_click=close, style=ft.ButtonStyle(color=AppTheme.SECONDARY))])
        self.page.show_dialog(dlg)

    def _logout(self, e):
        api.clear_token()
        self.page.clean()
        from src.views.auth.login_page import LoginPage
        def on_login_success(user): self.page.clean(); self.page.add(
            Dashboard(self.page, user).build()); self.page.update()
        login_page = LoginPage(self.page, on_login_success)
        self.page.add(login_page.build())
        self.page.update()

    def _show_profile_page(self, e):
        def close(e): dlg.open = False; self.page.update()
        dlg = ft.AlertDialog(bgcolor="#0D1B0F", content=ft.Column([
            ft.Container(height=5),
            ft.Text("پروفایل کاربری", size=20, font_family="Vazir", weight=ft.FontWeight.BOLD,
                    text_align=ft.TextAlign.CENTER, color=AppTheme.SECONDARY),
            ft.Container(height=6), ft.Row([ft.Container(
                height=1.5, width=40, bgcolor=AppTheme.SECONDARY, border_radius=1)], alignment=ft.MainAxisAlignment.CENTER),
            ft.Container(height=15), ft.Row([ft.Icon(
                ft.icons.Icons.PERSON, size=50, color=AppTheme.PRIMARY)], alignment=ft.MainAxisAlignment.CENTER),
            ft.Container(height=10),
            ft.Text(self.user.get("full_name", ""), size=18, font_family="Vazir",
                    weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER, color="#FFFFFF"),
            ft.Text(self.user.get("phone", ""), size=14, font_family="Vazir",
                    text_align=ft.TextAlign.CENTER, color="#FFFFFF80"),
            ft.Text("مدیر سیستم" if self.user.get("role") == "super_admin" else "مدیر" if self.user.get("role") == "admin" else "کاربر", size=12, font_family="Vazir",
                    text_align=ft.TextAlign.CENTER, color="#FFFFFF60"),
            ft.Container(height=15),
            ft.Text("جهت ویرایش اطلاعات، با مدیر سیستم تماس بگیرید", size=11,
                    font_family="Vazir", color="#FFFFFF40", text_align=ft.TextAlign.CENTER),
            ft.Container(height=10),
        ], width=260, horizontal_alignment=ft.CrossAxisAlignment.CENTER), actions=[ft.TextButton("بستن", on_click=close, style=ft.ButtonStyle(color=AppTheme.SECONDARY))])
        self.page.show_dialog(dlg)

    def _show_donation_history(self, e):
        result = api.get("financial/get_user_history.php")
        user_full_name = self.user.get("full_name", "کاربر")

        if result.get("transactions"):
            items = [
                ft.Text(f"تاریخچه مشارکت‌های {user_full_name}", size=16, font_family="Vazir",
                        weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER, color=AppTheme.SECONDARY),
                ft.Container(height=6),
                ft.Row([ft.Container(height=1.5, width=40, bgcolor=AppTheme.SECONDARY, border_radius=1)],
                       alignment=ft.MainAxisAlignment.CENTER),
                ft.Container(height=15)
            ]
            for tx in result["transactions"][:20]:
                amount = tx.get("amount", 0)
                status = tx.get("status", "pending")
                plan_title = tx.get("plan_title", "")

                # تعیین وضعیت نمایشی برای هر چهار حالت
                if status == "completed":
                    status_text = "✅ تأیید شده"
                    status_color = "#81C784"
                elif status == "rejected":
                    status_text = "❌ رد شده"
                    status_color = "#EF5350"
                elif status == "rejected_general":
                    status_text = "🕌 صندوق مسجد"
                    status_color = "#D4AF37"
                else:
                    status_text = "⏳ در انتظار"
                    status_color = "#FFB74D"

                # ساخت محتوای کارت
                card_content = [
                    ft.Row([
                        ft.Text(f"{persian_numbers(f'{int(float(amount)):,}')} تومان",
                                size=14, font_family="Vazir", weight=ft.FontWeight.BOLD, color="#212121"),
                        ft.Container(expand=True),
                        ft.Text(status_text, size=12,
                                font_family="Vazir", color=status_color)
                    ]),
                    ft.Text(f"توسط {user_full_name}",
                            size=11, font_family="Vazir", color=AppTheme.TEXT_HINT),
                ]

                if plan_title:
                    card_content.append(
                        ft.Text(plan_title, size=10, font_family="Vazir",
                                color=AppTheme.TEXT_HINT)
                    )

                items.append(
                    ft.Container(
                        content=ft.Column(card_content),
                        padding=10, bgcolor="#FFFFFF", border_radius=8, margin=ft.Margin(0, 0, 0, 6)
                    )
                )
            total_donated = result.get("total_donated", 0)
            if total_donated:
                items.append(ft.Container(height=10))
                items.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Text("مجموع مشارکت‌ها:", size=12,
                                    font_family="Vazir", color=AppTheme.TEXT_HINT),
                            ft.Container(expand=True),
                            ft.Text(f"{persian_numbers(f'{int(float(total_donated)):,}')} تومان",
                                    size=14, font_family="Vazir", weight=ft.FontWeight.BOLD, color=AppTheme.PRIMARY)
                        ]),
                        padding=10, bgcolor="#E8F5E9", border_radius=8, margin=ft.Margin(0, 5, 0, 0)
                    )
                )
        else:
            items = [ft.Text(f"کاربر {user_full_name} تاکنون کمکی ثبت نکرده است",
                             size=14, font_family="Vazir", color="#FFFFFF60", text_align=ft.TextAlign.CENTER)]

        def close(e):
            dlg.open = False
            self.page.update()

        dlg = ft.AlertDialog(
            bgcolor="#0D1B0F",
            content=ft.Column(items, width=300, height=400,
                              scroll=ft.ScrollMode.AUTO, spacing=0),
            actions=[ft.TextButton(
                "بستن", on_click=close, style=ft.ButtonStyle(color=AppTheme.SECONDARY))]
        )
        self.page.show_dialog(dlg)

    def _show_notifications_dialog(self, e):
        result = api.get("notifications/get_user_notifications.php")
        def close(e): dlg.open = False; self.page.update()
        if result and result.get("notifications"):
            items = [ft.Text("اعلان‌ها", size=16, font_family="Vazir", weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER, color=AppTheme.SECONDARY), ft.Container(
                height=6), ft.Row([ft.Container(height=1.5, width=40, bgcolor=AppTheme.SECONDARY, border_radius=1)], alignment=ft.MainAxisAlignment.CENTER), ft.Container(height=15)]
            for n in result["notifications"][:10]:
                items.append(ft.Container(content=ft.Column([ft.Text(n.get("title", ""), size=13, font_family="Vazir", weight=ft.FontWeight.BOLD, color=AppTheme.TEXT_PRIMARY), ft.Text(
                    n.get("message", ""), size=11, font_family="Vazir", color=AppTheme.TEXT_HINT)]), padding=10, bgcolor="#FFFFFF", border_radius=8, margin=ft.Margin(0, 0, 0, 6)))
        else:
            items = [ft.Text("اعلانی ندارید", size=14, font_family="Vazir",
                             color="#FFFFFF60", text_align=ft.TextAlign.CENTER)]
        dlg = ft.AlertDialog(bgcolor="#0D1B0F", content=ft.Column(items, width=300, height=300, scroll=ft.ScrollMode.AUTO, spacing=0), actions=[
                             ft.TextButton("بستن", on_click=close, style=ft.ButtonStyle(color=AppTheme.SECONDARY))])
        self.page.show_dialog(dlg)

    def _show_help(self, e):
        def close(e): dlg.open = False; self.page.update()
        sections = [
            ("🌙 اوقات شرعی", "اوقات شرعی هر روز به صورت خودکار محاسبه و نمایش داده می‌شود",
             ft.icons.Icons.NIGHTLIGHT_ROUND, "#D4AF37"),
            ("📿 قرآن و ادعیه", "دعاها، زیارات و سوره‌های قرآن را مشاهده کنید",
             ft.icons.Icons.MENU_BOOK, "#1B5E20"),
            ("📢 اطلاعیه‌ها", "آخرین اطلاعیه‌ها و اخبار مسجد را دنبال کنید",
             ft.icons.Icons.CAMPAIGN, "#E53935"),
            ("📅 برنامه هفتگی", "برنامه ثابت هفتگی مسجد را مشاهده کنید",
             ft.icons.Icons.CALENDAR_MONTH, "#1565C0"),
            ("🤝 مشارکت‌های مردمی", "در طرح‌های کمک به مسجد مشارکت کنید",
             ft.icons.Icons.HANDSHAKE, "#EF6C00"),
            ("🏴 آگهی ترحیم", "اعلامیه‌های ترحیم را مشاهده کنید",
             ft.icons.Icons.FLAG, "#616161"),
            ("⚙️ پنل مدیریت", "مخصوص مدیران - مدیریت محتوای اپلیکیشن",
             ft.icons.Icons.DASHBOARD_CUSTOMIZE, "#6A1B9A"),
        ]
        help_items = [ft.Text("راهنما", size=20, font_family="Vazir", weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER, color=AppTheme.SECONDARY), ft.Container(
            height=6), ft.Row([ft.Container(height=1.5, width=40, bgcolor=AppTheme.SECONDARY, border_radius=1)], alignment=ft.MainAxisAlignment.CENTER), ft.Container(height=15)]
        for title, desc, icon, color in sections:
            help_items.append(ft.Container(content=ft.Row([ft.Container(content=ft.Icon(icon, size=24, color="#FFFFFF"), width=42, height=42, bgcolor=color, border_radius=21, alignment=ft.Alignment(0, 0)), ft.Container(width=12), ft.Column([ft.Text(
                title, size=14, font_family="Vazir", weight=ft.FontWeight.BOLD, color=AppTheme.TEXT_PRIMARY), ft.Text(desc, size=11, font_family="Vazir", color=AppTheme.TEXT_HINT)], expand=True)]), padding=12, bgcolor="#FFFFFF", border_radius=12, margin=ft.Margin(0, 0, 0, 8)))
        dlg = ft.AlertDialog(bgcolor="#0D1B0F", content=ft.Column(help_items, width=320, height=400, scroll=ft.ScrollMode.AUTO, spacing=0), actions=[
                             ft.TextButton("بستن", on_click=close, style=ft.ButtonStyle(color=AppTheme.SECONDARY))])
        self.page.show_dialog(dlg)

    def _show_about(self, e):
        def close(e): dlg.open = False; self.page.update()
        dlg = ft.AlertDialog(bgcolor="#0D1B0F", content=ft.Column([
            ft.Container(height=10),
            ft.Text("مصباح", size=32, font_family="IranNastaliq",
                    color=AppTheme.SECONDARY, text_align=ft.TextAlign.CENTER),
            ft.Container(height=4), ft.Row([ft.Container(
                height=1.5, width=40, bgcolor=AppTheme.SECONDARY, border_radius=1)], alignment=ft.MainAxisAlignment.CENTER),
            ft.Container(height=15),
            ft.Text("سامانه اطلاع‌رسانی", size=14, font_family="Vazir",
                    color="#FFFFFF", text_align=ft.TextAlign.CENTER),
            ft.Text("مسجد حضرت ابراهیم (ع)", size=16, font_family="Vazir",
                    weight=ft.FontWeight.BOLD, color="#FFFFFF", text_align=ft.TextAlign.CENTER),
            ft.Container(height=15), ft.Divider(
                height=1, color="#FFFFFF20"), ft.Container(height=10),
            ft.Text("نسخه ۱.۰.۰", size=16, font_family="Vazir",
                    color="#FFFFFF40", text_align=ft.TextAlign.CENTER),
            ft.Text("طراح و برنامه‌نویس: امین عنایت زارع", size=16,
                    font_family="Vazir", color="#FFFFFF60", text_align=ft.TextAlign.CENTER),
            ft.Container(height=15), ft.Divider(
                height=1, color="#FFFFFF20"), ft.Container(height=15),
            ft.Text("تقدیم به ساحت مقدس", size=14, font_family="Vazir",
                    color="#FFFFFF", text_align=ft.TextAlign.CENTER),
            ft.Text("حضرت ولی عصر (ارواحنا فداه)", size=16, font_family="Vazir", weight=ft.FontWeight.BOLD,
                    color="#FFFFFF", text_align=ft.TextAlign.CENTER),
            ft.Container(height=10),
        ], width=280, spacing=0, horizontal_alignment=ft.CrossAxisAlignment.CENTER), actions=[ft.TextButton("بستن", on_click=close, style=ft.ButtonStyle(color=AppTheme.SECONDARY))])
        self.page.show_dialog(dlg)