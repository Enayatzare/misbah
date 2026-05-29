# ==========================================
# 📁 فایل: src/views/admin/manage_duas.py
# (نسخه نهایی - فقط ویرایش و حذف، بدون دکمه افزودن)
# ==========================================
import flet as ft
from src.theme import AppTheme
from src.services.api_client import api
from src.utils.formatters import persian_numbers


class ManageDuas:
    def __init__(self, page: ft.Page, on_back):
        self.page = page
        self.on_back = on_back
        self.all_duas = []

        self.page.on_pop = lambda e: self.go_back(e)

    def _is_quran(self, title: str) -> bool:
        quran_words = ["سوره", "آیات", "آیت", "قرآن", "الرحمن", "انفال",
                       "دخان", "فتح", "حشر", "واقعه", "یس", "یاسین", "ذاریات"]
        return any(word in title for word in quran_words)

    def build(self):
        header = ft.Container(
            content=ft.Row(
                [
                    ft.IconButton(icon=ft.icons.Icons.ARROW_BACK,
                                  icon_color="#FFFFFF", on_click=self.go_back),
                    ft.Text("مدیریت قرآن و ادعیه", size=18, font_family="Vazir",
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
            hint_text="🔍 جستجو...", border_radius=10, bgcolor="#FFFFFF", text_size=14, on_change=self._on_search)
        self.content_column = ft.Column([ft.Container(height=50), ft.ProgressBar(
            width=80, color=AppTheme.SECONDARY)], alignment=ft.MainAxisAlignment.CENTER)
        scrollable = ft.ListView(
            controls=[self.content_column], expand=True, padding=20)
        page_content = ft.Container(content=scrollable, expand=True, gradient=ft.LinearGradient(
            begin=ft.Alignment(0, -1), end=ft.Alignment(0, 1), colors=["#0D1B0F", "#1A2F1E", "#0D1B0F"]))
        self.load_duas()
        return ft.Column([header, page_content], expand=True, spacing=0)

    def load_duas(self):
        result = api.get("duas/get_list.php")
        self.all_duas = result if isinstance(result, list) else []
        self._display(self.all_duas)

    def _display(self, duas):
        total = len(duas)
        total_str = persian_numbers(str(total))
        content = [
            ft.Container(height=10),
            ft.Row([ft.Icon(ft.icons.Icons.MENU_BOOK, size=24, color=AppTheme.SECONDARY),
                    ft.Text(f"مدیریت قرآن و ادعیه ({total_str} مورد)", size=28, font_family="IranNastaliq", color=AppTheme.SECONDARY)],
                   alignment=ft.MainAxisAlignment.CENTER, spacing=10),
            ft.Container(height=5),
            ft.Row([ft.Container(height=1.5, width=60, bgcolor=AppTheme.SECONDARY,
                   border_radius=1)], alignment=ft.MainAxisAlignment.CENTER),
            ft.Container(height=15),
            self.search_field,
            ft.Container(height=15),
        ]
        if duas:
            for dua in duas:
                content.append(self._build_dua_card(dua))
        else:
            content.append(ft.Text("موردی یافت نشد", size=14,
                           font_family="Vazir", color="#FFFFFF60"))
        content.append(ft.Container(height=30))
        self.content_column.controls = content
        self.content_column.alignment = ft.MainAxisAlignment.START
        self.page.update()

    def _on_search(self, e):
        query = self.search_field.value.strip() if self.search_field.value else ""
        filtered = [d for d in self.all_duas if query in d.get(
            "title", "")] if query else self.all_duas
        self._display(filtered)

    def _build_dua_card(self, dua: dict):
        title = dua.get("title", "")
        category = dua.get("category", "")
        file_url = dua.get("file_url", "")
        is_quran = self._is_quran(title)
        type_label = "📖 سوره" if is_quran else "📿 دعا"
        return ft.Container(
            content=ft.Column([
                ft.Row([ft.Text(title, size=14, font_family="Vazir", weight=ft.FontWeight.BOLD, color=AppTheme.TEXT_PRIMARY), ft.Container(expand=True),
                        ft.IconButton(icon=ft.icons.Icons.EDIT, icon_size=16, icon_color=AppTheme.PRIMARY,
                                      on_click=lambda e, d=dua: self._show_edit_form(d)),
                        ft.IconButton(icon=ft.icons.Icons.DELETE, icon_size=16, icon_color=AppTheme.ERROR, on_click=lambda e, d=dua: self._delete_dua(d))]),
                ft.Container(height=4),
                ft.Row([ft.Text(f"{type_label} | {category}", size=11, font_family="Vazir", color=AppTheme.TEXT_HINT), ft.Container(expand=True),
                        ft.Text("📎 دارد" if file_url else "❌ فایل ندارد", size=11, font_family="Vazir", color=AppTheme.PRIMARY if file_url else AppTheme.ERROR)]),
            ]),
            padding=12, bgcolor="#FFFFFF", border_radius=12, border=ft.Border(left=ft.BorderSide(4, AppTheme.SECONDARY)), margin=ft.Margin(0, 0, 0, 8),
        )

    def _show_edit_form(self, dua: dict):
        title_field = ft.TextField(label="عنوان", value=dua.get(
            "title", ""), border_radius=10, bgcolor="#FFFFFF")
        cat_dd = ft.Dropdown(label="دسته‌بندی", value=dua.get("category", "عمومی"), options=[ft.dropdown.Option(
            "دعای هفتگی", "دعای هفتگی"), ft.dropdown.Option("منفرقه", "منفرقه"), ft.dropdown.Option("عمومی", "عمومی")], border_radius=10, bgcolor="#FFFFFF")
        file_field = ft.TextField(label="نام فایل PDF", value=dua.get(
            "file_url", ""), border_radius=10, bgcolor="#FFFFFF")
        msg = ft.Text("", color=AppTheme.ERROR, size=12)

        def save(e):
            result = api.post("admin/duas/update.php", {"id": dua.get("id"), "title": title_field.value,
                              "category": cat_dd.value, "file_url": file_field.value if file_field.value else None})
            if result.get("message"):
                dlg.open = False
                self.page.update()
                item_type = "سوره" if self._is_quran(
                    title_field.value) else "دعا"
                self._show_success(f"{item_type} ویرایش شد")
                self._reload()
            else:
                msg.value = result.get("error", "خطا")
                self.page.update()

        def close(e): dlg.open = False; self.page.update()

        dlg = ft.AlertDialog(title=ft.Text("ویرایش", font_family="Vazir", weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                             content=ft.Column([title_field, ft.Container(height=10), cat_dd, ft.Container(
                                 height=10), file_field, ft.Container(height=8), msg], width=300),
                             actions=[ft.TextButton("انصراف", on_click=close), ft.Button("ذخیره", on_click=save, style=ft.ButtonStyle(bgcolor=AppTheme.PRIMARY, color="#FFFFFF"))])
        self.page.show_dialog(dlg)

    def _delete_dua(self, dua: dict):
        def confirm(e): api.post("admin/duas/delete.php", {"id": dua.get("id")}); dlg.open = False; self.page.update(
        ); item_type = "سوره" if self._is_quran(dua.get("title", "")) else "دعا"; self._show_success(f"{item_type} حذف شد"); self._reload()
        def close(e): dlg.open = False; self.page.update()
        dlg = ft.AlertDialog(title=ft.Text("حذف", font_family="Vazir", weight=ft.FontWeight.BOLD), content=ft.Text(f"آیا از حذف «{dua.get('title', '')}» اطمینان دارید؟", font_family="Vazir"), actions=[
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
