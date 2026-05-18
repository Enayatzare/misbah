# ==========================================
# 📁 فایل: src/views/admin/manage_announcements.py
# ==========================================
import flet as ft
from src.theme import AppTheme
from src.services.api_client import api
from src.utils.formatters import persian_numbers


class ManageAnnouncements:
    def __init__(self, page: ft.Page, on_back):
        self.page = page
        self.on_back = on_back
        self.all_announcements = []

    def build(self):
        header = ft.Container(
            content=ft.Row(
                [
                    ft.IconButton(icon=ft.icons.Icons.ARROW_BACK,
                                  icon_color="#FFFFFF", on_click=self.go_back),
                    ft.Text("مدیریت اطلاعیه‌ها", size=18, font_family="Vazir",
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
            hint_text="🔍 جستجو در اطلاعیه‌ها...",
            border_radius=10, bgcolor="#FFFFFF", text_size=14,
            on_change=self._on_search,
        )

        self.content_column = ft.Column(
            [ft.Container(height=50), ft.ProgressBar(
                width=80, color=AppTheme.SECONDARY)],
            alignment=ft.MainAxisAlignment.CENTER,
        )

        scrollable = ft.ListView(
            controls=[self.content_column], expand=True, padding=20)

        page_content = ft.Container(
            content=scrollable, expand=True,
            gradient=ft.LinearGradient(
                begin=ft.Alignment(0, -1), end=ft.Alignment(0, 1),
                colors=["#0D1B0F", "#1A2F1E", "#0D1B0F"],
            ),
        )

        self.load_announcements()
        return ft.Column([header, page_content], expand=True, spacing=0)

    def load_announcements(self):
        result = api.get("admin/announcements/list.php")
        if isinstance(result, dict) and result.get("announcements"):
            self.all_announcements = result["announcements"]
        elif isinstance(result, list):
            self.all_announcements = result
        else:
            self.all_announcements = []
        self._display(self.all_announcements)

    def _display(self, announcements):
        total = len(announcements)
        total_str = persian_numbers(str(total))

        content = [
            ft.Container(height=10),
            ft.Row(
                [ft.Icon(ft.icons.Icons.CAMPAIGN, size=24, color=AppTheme.SECONDARY),
                 ft.Text(f"مدیریت اطلاعیه‌ها ({total_str} مورد)", size=28, font_family="IranNastaliq", color=AppTheme.SECONDARY)],
                alignment=ft.MainAxisAlignment.CENTER, spacing=10,
            ),
            ft.Container(height=15),
            ft.Button("➕ ایجاد اطلاعیه جدید", width=250,
                      style=ft.ButtonStyle(
                          bgcolor=AppTheme.PRIMARY, color="#FFFFFF", shape=ft.RoundedRectangleBorder(radius=12)),
                      on_click=self._show_create_form),
            ft.Container(height=10),
            self.search_field,
            ft.Container(height=15),
        ]

        if announcements:
            for ann in announcements:
                content.append(self._build_admin_card(ann))
        else:
            content.append(ft.Text("اطلاعیه‌ای یافت نشد", size=14,
                           font_family="Vazir", color="#FFFFFF60"))

        content.append(ft.Container(height=30))
        self.content_column.controls = content
        self.content_column.alignment = ft.MainAxisAlignment.START
        self.page.update()

    def _on_search(self, e):
        query = self.search_field.value.strip() if self.search_field.value else ""
        if query:
            filtered = [
                a for a in self.all_announcements if query in a.get("title", "")]
        else:
            filtered = self.all_announcements
        self._display(filtered)

    def _build_admin_card(self, ann: dict):
        title = ann.get("title", "بدون عنوان")
        ann_type = ann.get("type", "general")
        is_published = ann.get("is_published", 1)

        type_labels = {"urgent": "فوری", "event": "مناسبت",
                       "financial": "مالی", "religious": "مذهبی", "general": "عمومی"}
        label = type_labels.get(ann_type, "عمومی")
        status_text = "✅ منتشر شده" if is_published else "⏳ پیش‌نویس"
        status_color = AppTheme.PRIMARY if is_published else AppTheme.WARNING

        return ft.Container(
            content=ft.Column([
                ft.Row([ft.Text(title, size=15, font_family="Vazir", weight=ft.FontWeight.BOLD, color=AppTheme.TEXT_PRIMARY),
                        ft.Container(expand=True), ft.Text(status_text, size=11, font_family="Vazir", color=status_color)]),
                ft.Container(height=6),
                ft.Row([ft.Container(content=ft.Text(label, size=10, font_family="Vazir", color="#FFFFFF"), bgcolor=AppTheme.PRIMARY, border_radius=8, padding=ft.Padding(8, 3, 8, 3)),
                        ft.Container(expand=True),
                        ft.IconButton(icon=ft.icons.Icons.EDIT, icon_size=18, icon_color=AppTheme.PRIMARY,
                                      on_click=lambda e, a=ann: self._show_edit_form(a)),
                        ft.IconButton(icon=ft.icons.Icons.DELETE, icon_size=18, icon_color=AppTheme.ERROR, on_click=lambda e, a=ann: self._delete_announcement(a))]),
            ]),
            padding=14, bgcolor="#FFFFFF", border_radius=12, border=ft.Border(left=ft.BorderSide(4, AppTheme.SECONDARY)), margin=ft.Margin(0, 0, 0, 10),
        )

    def _show_create_form(self, e):
        title_field = ft.TextField(
            label="عنوان", border_radius=10, bgcolor="#FFFFFF")
        content_field = ft.TextField(
            label="متن اطلاعیه", border_radius=10, bgcolor="#FFFFFF", max_lines=3, multiline=True)
        type_dd = ft.Dropdown(label="نوع", value="general", options=[ft.dropdown.Option("general", "عمومی"), ft.dropdown.Option("urgent", "فوری"), ft.dropdown.Option(
            "event", "مناسبت"), ft.dropdown.Option("religious", "مذهبی"), ft.dropdown.Option("financial", "مالی")], border_radius=10, bgcolor="#FFFFFF")
        msg = ft.Text("", color=AppTheme.ERROR, size=12)

        def save(e):
            if not title_field.value or not content_field.value:
                msg.value = "عنوان و متن الزامی است"
                self.page.update()
                return
            result = api.post("admin/announcements/create.php", {
                              "title": title_field.value, "content": content_field.value, "type": type_dd.value})
            if result.get("message"):
                dlg.open = False
                self.page.update()
                self._show_success("اطلاعیه ایجاد شد")
                self._reload()
            else:
                msg.value = result.get("error", "خطا")
                self.page.update()

        def close(e): dlg.open = False; self.page.update()

        dlg = ft.AlertDialog(
            title=ft.Text("ایجاد اطلاعیه", font_family="Vazir",
                          weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
            content=ft.Column([title_field, ft.Container(height=10), content_field, ft.Container(
                height=10), type_dd, ft.Container(height=8), msg], width=300),
            actions=[ft.TextButton("انصراف", on_click=close), ft.Button(
                "ذخیره", on_click=save, style=ft.ButtonStyle(bgcolor=AppTheme.PRIMARY, color="#FFFFFF"))],
        )
        self.page.show_dialog(dlg)

    def _show_edit_form(self, ann: dict):
        title_field = ft.TextField(label="عنوان", value=ann.get(
            "title", ""), border_radius=10, bgcolor="#FFFFFF")
        content_field = ft.TextField(label="متن اطلاعیه", value=ann.get(
            "content", ""), border_radius=10, bgcolor="#FFFFFF", max_lines=3, multiline=True)
        type_dd = ft.Dropdown(label="نوع", value=ann.get("type", "general"), options=[ft.dropdown.Option("general", "عمومی"), ft.dropdown.Option("urgent", "فوری"), ft.dropdown.Option(
            "event", "مناسبت"), ft.dropdown.Option("religious", "مذهبی"), ft.dropdown.Option("financial", "مالی")], border_radius=10, bgcolor="#FFFFFF")
        msg = ft.Text("", color=AppTheme.ERROR, size=12)

        def save(e):
            if not title_field.value or not content_field.value:
                msg.value = "عنوان و متن الزامی است"
                self.page.update()
                return
            result = api.post("admin/announcements/update.php", {"id": ann.get(
                "id"), "title": title_field.value, "content": content_field.value, "type": type_dd.value})
            if result.get("message"):
                dlg.open = False
                self.page.update()
                self._show_success("اطلاعیه ویرایش شد")
                self._reload()
            else:
                msg.value = result.get("error", "خطا")
                self.page.update()

        def close(e): dlg.open = False; self.page.update()

        dlg = ft.AlertDialog(
            title=ft.Text("ویرایش اطلاعیه", font_family="Vazir",
                          weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
            content=ft.Column([title_field, ft.Container(height=10), content_field, ft.Container(
                height=10), type_dd, ft.Container(height=8), msg], width=300),
            actions=[ft.TextButton("انصراف", on_click=close), ft.Button(
                "ذخیره", on_click=save, style=ft.ButtonStyle(bgcolor=AppTheme.PRIMARY, color="#FFFFFF"))],
        )
        self.page.show_dialog(dlg)

    def _delete_announcement(self, ann: dict):
        def confirm(e): api.post("admin/announcements/delete.php", {"id": ann.get(
            "id")}); dlg.open = False; self.page.update(); self._show_success("اطلاعیه حذف شد"); self._reload()

        def close(e): dlg.open = False; self.page.update()
        dlg = ft.AlertDialog(title=ft.Text("حذف", font_family="Vazir", weight=ft.FontWeight.BOLD), content=ft.Text(f"آیا از حذف «{ann.get('title', '')}» اطمینان دارید؟", font_family="Vazir"), actions=[
                             ft.TextButton("انصراف", on_click=close), ft.Button("حذف", on_click=confirm, style=ft.ButtonStyle(bgcolor=AppTheme.ERROR, color="#FFFFFF"))])
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
