import flet as ft
from src.theme import AppTheme
from src.services.api_client import api
from src.utils.formatters import persian_numbers
import jdatetime
from datetime import datetime


class ManageUsers:
    def __init__(self, page: ft.Page, on_back):
        self.page = page
        self.on_back = on_back
        self.all_users = []
        self.current_page = 1
        self.per_page = 20
        self.current_tab = "all"

        

    def build(self):
        header = ft.Container(
            content=ft.Row(
                [
                    ft.IconButton(icon=ft.icons.Icons.ARROW_BACK,
                                  icon_color="#FFFFFF", on_click=self.go_back),
                    ft.Text("مدیریت کاربران", size=18, font_family="Vazir",
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

        self.search_field = ft.TextField(
            hint_text="🔍 جستجوی کاربر...", border_radius=10, bgcolor="#FFFFFF", text_size=14, on_change=self._on_search)
        self.content_column = ft.Column([ft.Container(height=50), ft.ProgressBar(
            width=80, color=AppTheme.SECONDARY)], alignment=ft.MainAxisAlignment.CENTER)
        scrollable = ft.ListView(
            controls=[self.content_column], expand=True, padding=20)
        page_content = ft.Container(content=scrollable, expand=True, gradient=ft.LinearGradient(
            begin=ft.Alignment(0, -1), end=ft.Alignment(0, 1), colors=["#0D1B0F", "#1A2F1E", "#0D1B0F"]))
        self.load_users()

        self.page.on_pop = lambda e: self.go_back(e)
        return ft.Column([header, page_content], expand=True, spacing=0)

    def load_users(self):
        result = api.get("admin/users/list.php")
        if isinstance(result, dict) and result.get("users"):
            self.all_users = result["users"]
        elif isinstance(result, list):
            self.all_users = result
        else:
            self.all_users = []
        self._display()

    def _get_filtered_users(self):
        if self.current_tab == "admin":
            return [u for u in self.all_users if u.get("role") in ("admin", "super_admin")]
        elif self.current_tab == "user":
            return [u for u in self.all_users if u.get("role") == "user"]
        elif self.current_tab == "inactive":
            return [u for u in self.all_users if not u.get("is_active", 1)]
        return self.all_users

    def _get_page_users(self, users):
        start = (self.current_page - 1) * self.per_page
        end = start + self.per_page
        return users[start:end]

    def _display(self):
        query = self.search_field.value.strip() if self.search_field.value else ""
        filtered = self._get_filtered_users()
        if query:
            filtered = [u for u in filtered if query in str(
                u.get("full_name", "")) or query in str(u.get("phone", ""))]
        total_all = len(self.all_users)
        total_filtered = len(filtered)
        page_users = self._get_page_users(filtered)
        total_pages = max(
            1, (total_filtered + self.per_page - 1) // self.per_page)

        content = [
            ft.Container(height=10),
            ft.Row([ft.Icon(ft.icons.Icons.PEOPLE, size=24, color=AppTheme.SECONDARY), ft.Text(
                f"مدیریت کاربران ({persian_numbers(str(total_all))} نفر)", size=24, font_family="IranNastaliq", color=AppTheme.SECONDARY)], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
            ft.Container(height=10),
            ft.Button("➕ افزودن کاربر جدید", width=250, style=ft.ButtonStyle(bgcolor=AppTheme.PRIMARY, color="#FFFFFF",
                      shape=ft.RoundedRectangleBorder(radius=12)), on_click=lambda e: self._show_user_form()),
            ft.Container(height=10), self.search_field, ft.Container(
                height=10),
        ]

        tabs = [("همه", "all"), ("مدیران", "admin"),
                ("کاربران", "user"), ("غیرفعال", "inactive")]
        tab_row = ft.Row(spacing=6, alignment=ft.MainAxisAlignment.CENTER)
        for label, tab_id in tabs:
            is_active = self.current_tab == tab_id
            tab_row.controls.append(ft.Container(content=ft.Text(label, size=12, font_family="Vazir", weight=ft.FontWeight.BOLD if is_active else None, color="#000000" if is_active else "#000000"), padding=ft.Padding(
                12, 6, 12, 6), bgcolor=AppTheme.SECONDARY if is_active else "#FFFFFF", border_radius=16, on_click=lambda e, t=tab_id: self._switch_tab(t)))
        content.append(tab_row)
        content.append(ft.Container(height=15))

        if page_users:
            for user in page_users:
                content.append(self._build_user_card(user))
        else:
            content.append(ft.Text("کاربری یافت نشد", size=14,
                           font_family="Vazir", color="#FFFFFF60"))

        if total_pages > 1:
            content.append(ft.Container(height=15))
            pag_row = ft.Row(alignment=ft.MainAxisAlignment.CENTER, spacing=10)
            pag_row.controls.append(ft.IconButton(icon=ft.icons.Icons.CHEVRON_RIGHT, icon_color=AppTheme.PRIMARY if self.current_page >
                                    1 else "#FFFFFF30", on_click=self._prev_page if self.current_page > 1 else None))
            pag_row.controls.append(ft.Text(
                f"صفحه {persian_numbers(str(self.current_page))} از {persian_numbers(str(total_pages))}", size=12, font_family="Vazir", color="#FFFFFF80"))
            pag_row.controls.append(ft.IconButton(icon=ft.icons.Icons.CHEVRON_LEFT, icon_color=AppTheme.PRIMARY if self.current_page <
                                    total_pages else "#FFFFFF30", on_click=self._next_page if self.current_page < total_pages else None))
            content.append(pag_row)

        content.append(ft.Container(height=30))
        self.content_column.controls = content
        self.content_column.alignment = ft.MainAxisAlignment.START
        self.page.update()

    def _switch_tab(self, tab_id: str):
        self.current_tab = tab_id
        self.current_page = 1
        self._display()

    def _on_search(self, e): self.current_page = 1; self._display()

    def _prev_page(self, e):
        if self.current_page > 1:
            self.current_page -= 1
            self._display()

    def _next_page(self, e): self.current_page += 1; self._display()

    def _format_date(self, date_str: str) -> str:
        if not date_str:
            return ""
        try:
            dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            jd = jdatetime.date.fromgregorian(date=dt.date())
            months = ["فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد",
                      "شهریور", "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند"]
            return f"{persian_numbers(str(jd.day))} {months[jd.month - 1]} {persian_numbers(str(jd.year))}"
        except:
            return ""

    def _build_user_card(self, user: dict):
        name = user.get("full_name", "")
        phone = user.get("phone", "")
        role = user.get("role", "user")
        is_active = user.get("is_active", 1)
        created_at = user.get("created_at", "")
        role_labels = {"super_admin": "مدیر کل",
                       "admin": "مدیر", "user": "کاربر"}
        role_label = role_labels.get(role, "کاربر")
        role_color = {"super_admin": "#7B1FA2", "admin": "#1565C0",
                      "user": "#1B5E20"}.get(role, AppTheme.PRIMARY)
        status_text = "✅ فعال" if is_active else "⛔ غیرفعال"
        status_color = AppTheme.PRIMARY if is_active else AppTheme.ERROR
        join_date = self._format_date(created_at)

        info_col = ft.Column([ft.Text(name, size=14, font_family="Vazir", weight=ft.FontWeight.BOLD, color=AppTheme.TEXT_PRIMARY), ft.Text(
            phone, size=11, font_family="Vazir", color=AppTheme.TEXT_HINT)], expand=True)
        if join_date:
            info_col.controls.append(ft.Text(
                f"🎂 عضو از {join_date}", size=10, font_family="Vazir", color=AppTheme.TEXT_HINT))

        btn_row = ft.Row([ft.Text(status_text, size=11, font_family="Vazir", color=status_color), ft.Container(expand=True),
                          ft.IconButton(icon=ft.icons.Icons.EDIT, icon_size=16, icon_color=AppTheme.PRIMARY,
                                        on_click=lambda e, u=user: self._show_user_form(u)),
                          ft.IconButton(icon=ft.icons.Icons.DELETE, icon_size=16, icon_color=AppTheme.ERROR, on_click=lambda e, u=user: self._delete_user(u))])
        if is_active:
            btn_row.controls.insert(1, ft.TextButton("⛔ غیرفعال", on_click=lambda e, u=user: self._toggle_user(
                u, 0), style=ft.ButtonStyle(color=AppTheme.ERROR, text_style=ft.TextStyle(size=10, font_family="Vazir"))))
        else:
            btn_row.controls.insert(1, ft.TextButton("✅ فعال", on_click=lambda e, u=user: self._toggle_user(
                u, 1), style=ft.ButtonStyle(color=AppTheme.PRIMARY, text_style=ft.TextStyle(size=10, font_family="Vazir"))))

        return ft.Container(
            content=ft.Column([ft.Row([ft.Container(content=ft.Text(name[0] if name else "?", size=18, color="#FFFFFF", font_family="Vazir"), width=40, height=40, bgcolor=role_color, border_radius=20, alignment=ft.Alignment(0, 0)),
                                       ft.Container(width=10), info_col,
                                       ft.Container(content=ft.Text(role_label, size=10, font_family="Vazir", color="#FFFFFF"), bgcolor=role_color, border_radius=8, padding=ft.Padding(8, 3, 8, 3))]),
                              ft.Container(height=6), btn_row]),
            padding=12, bgcolor="#FFFFFF", border_radius=12, border=ft.Border(left=ft.BorderSide(4, AppTheme.SECONDARY)), margin=ft.Margin(0, 0, 0, 10),
        )

    def _show_user_form(self, user=None):
        is_edit = user is not None
        name_field = ft.TextField(label="نام کامل", value=user.get(
            "full_name", "") if user else "", border_radius=10, bgcolor="#FFFFFF")
        phone_field = ft.TextField(label="شماره تماس", value=user.get(
            "phone", "") if user else "", border_radius=10, bgcolor="#FFFFFF")
        password_field = ft.TextField(
            label="رمز عبور (خالی = بدون تغییر)" if is_edit else "رمز عبور", password=True, border_radius=10, bgcolor="#FFFFFF")
        role_dd = ft.Dropdown(label="نقش", value=user.get("role", "user") if user else "user", options=[
                              ft.dropdown.Option("user", "کاربر"), ft.dropdown.Option("admin", "مدیر")], border_radius=10, bgcolor="#FFFFFF")
        msg = ft.Text("", color=AppTheme.ERROR, size=12)

        def save(e):
            if not name_field.value or not phone_field.value:
                msg.value = "نام و شماره تماس الزامی است"
                self.page.update()
                return
            if not is_edit and not password_field.value:
                msg.value = "رمز عبور الزامی است"
                self.page.update()
                return
            data = {"full_name": name_field.value,
                    "phone": phone_field.value, "role": role_dd.value}
            if password_field.value:
                data["password"] = password_field.value
            if is_edit:
                data["id"] = user.get("id")
                result = api.post("admin/users/update.php", data)
            else:
                result = api.post("admin/users/create.php", data)
            if result.get("message"):
                dlg.open = False
                self.page.update()
                self._show_success(
                    "کاربر ویرایش شد" if is_edit else "کاربر ایجاد شد")
                self._reload()
            else:
                msg.value = result.get("error", "خطا")
                self.page.update()

        def close(e): dlg.open = False; self.page.update()

        dlg = ft.AlertDialog(title=ft.Text("ویرایش کاربر" if is_edit else "افزودن کاربر", font_family="Vazir", weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                             content=ft.Column([name_field, ft.Container(height=8), phone_field, ft.Container(
                                 height=8), password_field, ft.Container(height=8), role_dd, ft.Container(height=8), msg], width=300),
                             actions=[ft.TextButton("انصراف", on_click=close), ft.Button("ذخیره", on_click=save, style=ft.ButtonStyle(bgcolor=AppTheme.PRIMARY, color="#FFFFFF"))])
        self.page.show_dialog(dlg)

    def _delete_user(self, user: dict):
        def confirm(e): api.post("admin/users/delete.php", {"id": user.get(
            "id")}); dlg.open = False; self.page.update(); self._show_success("کاربر حذف شد"); self._reload()

        def close(e): dlg.open = False; self.page.update()
        dlg = ft.AlertDialog(title=ft.Text("حذف کاربر", font_family="Vazir", weight=ft.FontWeight.BOLD), content=ft.Text(f"آیا از حذف «{user.get('full_name', '')}» اطمینان دارید؟", font_family="Vazir"), actions=[
                             ft.TextButton("انصراف", on_click=close), ft.Button("حذف", on_click=confirm, style=ft.ButtonStyle(bgcolor=AppTheme.ERROR, color="#FFFFFF"))])
        self.page.show_dialog(dlg)

    def _toggle_user(self, user: dict, is_active: int): api.post("admin/users/update.php", {"id": user.get(
        "id"), "is_active": is_active}); self._show_success("وضعیت کاربر تغییر کرد"); self._reload()

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
        from src.services.api_client import api
        from src.views.auth.login_page import LoginPage
        api.clear_token()
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
