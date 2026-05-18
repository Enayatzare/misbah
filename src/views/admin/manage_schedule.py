# ==========================================
# فایل: src/views/admin/manage_schedule.py
# (نسخه اصلاح شده - نمایش صحیح ساعت شروع و پایان)
# ==========================================
import flet as ft
from src.theme import AppTheme
from src.services.api_client import api
from src.utils.formatters import persian_numbers


DAYS_OF_WEEK = [
    ("saturday", "شنبه"), ("sunday", "یکشنبه"), ("monday", "دوشنبه"),
    ("tuesday", "سه‌شنبه"), ("wednesday", "چهارشنبه"), ("thursday", "پنجشنبه"),
    ("friday", "جمعه")
]


class ManageSchedule:
    def __init__(self, page: ft.Page, on_back):
        self.page = page
        self.on_back = on_back
        self.all_items = []

    def build(self):
        header = ft.Container(
            content=ft.Row(
                [
                    ft.IconButton(icon=ft.icons.Icons.ARROW_BACK,
                                  icon_color="#FFFFFF", on_click=self.go_back),
                    ft.Text("مدیریت برنامه هفتگی", size=18, font_family="Vazir",
                            weight=ft.FontWeight.BOLD, color="#FFFFFF"),
                    ft.Container(expand=True),
                    ft.IconButton(icon=ft.icons.Icons.LOGOUT,
                                  icon_color="#FF5252", on_click=self._logout),
                ],
                alignment=ft.MainAxisAlignment.START,
            ),
            padding=ft.Padding(15, 35, 15, 15), bgcolor="#0D1B0F",
        )

        self.search_field = ft.TextField(
            hint_text="🔍 جستجو...", border_radius=10, bgcolor="#FFFFFF", text_size=14, on_change=self._on_search)
        self.content_column = ft.Column([ft.Container(height=50), ft.ProgressBar(
            width=80, color=AppTheme.SECONDARY)], alignment=ft.MainAxisAlignment.CENTER)
        scrollable = ft.ListView(
            controls=[self.content_column], expand=True, padding=20)
        page_content = ft.Container(content=scrollable, expand=True, gradient=ft.LinearGradient(
            begin=ft.Alignment(0, -1), end=ft.Alignment(0, 1), colors=["#0D1B0F", "#1A2F1E", "#0D1B0F"]))
        self.load_schedule()
        return ft.Column([header, page_content], expand=True, spacing=0)

    def load_schedule(self):
        result = api.get("events/get_weekly_schedule.php")
        self.all_items = result if isinstance(result, list) else []
        self._display(self.all_items)

    def _display(self, items):
        total = len(items)
        total_str = persian_numbers(str(total))
        content = [
            ft.Container(height=10),
            ft.Row([ft.Icon(ft.icons.Icons.CALENDAR_MONTH, size=24, color=AppTheme.SECONDARY),
                    ft.Text(f"مدیریت برنامه هفتگی ({total_str} مورد)", size=26, font_family="IranNastaliq", color=AppTheme.SECONDARY)],
                   alignment=ft.MainAxisAlignment.CENTER, spacing=10),
            ft.Container(height=15),
            ft.Button("➕ افزودن برنامه جدید", width=250, style=ft.ButtonStyle(bgcolor=AppTheme.PRIMARY, color="#FFFFFF", shape=ft.RoundedRectangleBorder(radius=12)),
                      on_click=self._show_create_form),
            ft.Container(height=10), self.search_field, ft.Container(
                height=15),
        ]
        if items:
            for item in items:
                content.append(self._build_card(item))
        else:
            content.append(ft.Text("برنامه‌ای یافت نشد", size=14,
                           font_family="Vazir", color="#FFFFFF60"))
        content.append(ft.Container(height=30))
        self.content_column.controls = content
        self.content_column.alignment = ft.MainAxisAlignment.START
        self.page.update()

    def _on_search(self, e):
        query = self.search_field.value.strip() if self.search_field.value else ""
        filtered = [s for s in self.all_items if query in s.get(
            "title", "")] if query else self.all_items
        self._display(filtered)

    def _build_card(self, item: dict):
        day = item.get("day", "saturday")
        title = item.get("title", "")
        time_start = item.get("time_start", "")[:5]
        time_end = item.get("time_end", "")[:5]
        day_name = dict(DAYS_OF_WEEK).get(day, day)
        return ft.Container(
            content=ft.Column([
                ft.Row([ft.Text(day_name, size=14, font_family="Vazir", weight=ft.FontWeight.BOLD, color=AppTheme.SECONDARY),
                        ft.Container(expand=True),
                        ft.Text(f"{persian_numbers(time_end)} - {persian_numbers(time_start)}" if time_start else "", size=12, font_family="Vazir", color=AppTheme.TEXT_HINT)]),
                ft.Text(title, size=15, font_family="Vazir",
                        weight=ft.FontWeight.BOLD, color=AppTheme.TEXT_PRIMARY),
                ft.Container(height=6),
                ft.Row([ft.Container(expand=True),
                        ft.IconButton(icon=ft.icons.Icons.EDIT, icon_size=18, icon_color=AppTheme.PRIMARY,
                                      on_click=lambda e, s=item: self._show_edit_form(s)),
                        ft.IconButton(icon=ft.icons.Icons.DELETE, icon_size=18, icon_color=AppTheme.ERROR, on_click=lambda e, s=item: self._delete_item(s))]),
            ]),
            padding=14, bgcolor="#FFFFFF", border_radius=12, border=ft.Border(left=ft.BorderSide(4, AppTheme.SECONDARY)), margin=ft.Margin(0, 0, 0, 10),
        )

    def _show_create_form(self, e):
        title_field = ft.TextField(
            label="عنوان برنامه", border_radius=10, bgcolor="#FFFFFF")
        day_dd = ft.Dropdown(label="روز", value="saturday", options=[ft.dropdown.Option(
            d[0], d[1]) for d in DAYS_OF_WEEK], border_radius=10, bgcolor="#FFFFFF")
        time_start_field = ft.TextField(
            label="ساعت شروع", border_radius=10, bgcolor="#FFFFFF")
        time_end_field = ft.TextField(
            label="ساعت پایان", border_radius=10, bgcolor="#FFFFFF")
        lecturer_field = ft.TextField(
            label="سخنران/ مداح", border_radius=10, bgcolor="#FFFFFF")
        desc_field = ft.TextField(
            label="توضیحات", border_radius=10, bgcolor="#FFFFFF", max_lines=2, multiline=True)
        msg = ft.Text("", color=AppTheme.ERROR, size=12)

        def save(e):
            if not title_field.value:
                msg.value = "عنوان الزامی است"
                self.page.update()
                return
            data = {"title": title_field.value, "day": day_dd.value, "time_start": time_start_field.value or "", "time_end": time_end_field.value or "",
                    "lecturer": lecturer_field.value or "", "description": desc_field.value or ""}
            result = api.post("admin/events/create.php", data)
            if result.get("message"):
                dlg.open = False
                self.page.update()
                self._show_success("برنامه ایجاد شد")
                self._reload()
            else:
                msg.value = result.get("error", "خطا")
                self.page.update()

        def close(e): dlg.open = False; self.page.update()
        dlg = ft.AlertDialog(title=ft.Text("افزودن برنامه", font_family="Vazir", weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                             content=ft.Column([title_field, ft.Container(height=8), day_dd, ft.Container(height=8), time_start_field, ft.Container(height=8),
                                                time_end_field, ft.Container(height=8), lecturer_field, ft.Container(height=8), desc_field, ft.Container(height=8), msg], width=300),
                             actions=[ft.TextButton("انصراف", on_click=close), ft.Button("ذخیره", on_click=save, style=ft.ButtonStyle(bgcolor=AppTheme.PRIMARY, color="#FFFFFF"))])
        self.page.show_dialog(dlg)

    def _show_edit_form(self, item: dict):
        title_field = ft.TextField(label="عنوان", value=item.get(
            "title", ""), border_radius=10, bgcolor="#FFFFFF")
        day_dd = ft.Dropdown(label="روز", value=item.get("day", "saturday"), options=[
                             ft.dropdown.Option(d[0], d[1]) for d in DAYS_OF_WEEK], border_radius=10, bgcolor="#FFFFFF")
        time_start_field = ft.TextField(label="ساعت شروع", value=item.get(
            "time_start", "")[:5], border_radius=10, bgcolor="#FFFFFF")
        time_end_field = ft.TextField(label="ساعت پایان", value=item.get(
            "time_end", "")[:5], border_radius=10, bgcolor="#FFFFFF")
        lecturer_field = ft.TextField(label="سخنران", value=item.get(
            "lecturer", ""), border_radius=10, bgcolor="#FFFFFF")
        desc_field = ft.TextField(label="توضیحات", value=item.get(
            "description", ""), border_radius=10, bgcolor="#FFFFFF", max_lines=2, multiline=True)
        msg = ft.Text("", color=AppTheme.ERROR, size=12)

        def save(e):
            data = {"id": item.get("id"), "title": title_field.value, "day": day_dd.value, "time_start": time_start_field.value or "",
                    "time_end": time_end_field.value or "", "lecturer": lecturer_field.value or "", "description": desc_field.value or ""}
            result = api.post("admin/events/update.php", data)
            if result.get("message"):
                dlg.open = False
                self.page.update()
                self._show_success("برنامه ویرایش شد")
                self._reload()
            else:
                msg.value = result.get("error", "خطا")
                self.page.update()

        def close(e): dlg.open = False; self.page.update()
        dlg = ft.AlertDialog(title=ft.Text("ویرایش", font_family="Vazir", weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                             content=ft.Column([title_field, ft.Container(height=8), day_dd, ft.Container(height=8), time_start_field, ft.Container(height=8),
                                                time_end_field, ft.Container(height=8), lecturer_field, ft.Container(height=8), desc_field, ft.Container(height=8), msg], width=300),
                             actions=[ft.TextButton("انصراف", on_click=close), ft.Button("ذخیره", on_click=save, style=ft.ButtonStyle(bgcolor=AppTheme.PRIMARY, color="#FFFFFF"))])
        self.page.show_dialog(dlg)

    def _delete_item(self, item: dict):
        def confirm(e): api.post("admin/events/delete.php", {"id": item.get(
            "id")}); dlg.open = False; self.page.update(); self._show_success("برنامه حذف شد"); self._reload()

        def close(e): dlg.open = False; self.page.update()
        dlg = ft.AlertDialog(title=ft.Text("حذف", font_family="Vazir", weight=ft.FontWeight.BOLD), content=ft.Text(f"آیا از حذف «{item.get('title', '')}» اطمینان دارید؟", font_family="Vazir"),
                             actions=[ft.TextButton("انصراف", on_click=close), ft.Button("حذف", on_click=confirm, style=ft.ButtonStyle(bgcolor=AppTheme.ERROR, color="#FFFFFF"))])
        self.page.show_dialog(dlg)

    def _show_success(self, msg: str):
        snack = ft.SnackBar(
            ft.Text(f"✅ {msg}", font_family="Vazir"), bgcolor=AppTheme.PRIMARY)
        self.page.overlay.append(snack)
        snack.open = True
        self.page.update()
        import time
        time.sleep(1.5)

    def _reload(self): self.page.clean(); self.page.add(
        self.build()); self.page.update()

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

    def go_back(self, e): self.on_back()
