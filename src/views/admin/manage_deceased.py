# ==========================================
# 📁 فایل: src/views/admin/manage_deceased.py
# ==========================================
import flet as ft
from src.theme import AppTheme
from src.services.api_client import api
from src.utils.formatters import persian_numbers


class ManageDeceased:
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
                    ft.Text("مدیریت آگهی ترحیم", size=18, font_family="Vazir",
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
        self.load_data()

        def handle_back(e: ft.KeyboardEvent):
            if e.key in ["Escape", "Back", "GoBack", "ArrowLeft"]:
                self.go_back(e)
        
        self.page.on_keyboard_event = handle_back
        return ft.Column([header, page_content], expand=True, spacing=0)

    def load_data(self):
        result = api.get("social/get_deceased.php")
        self.all_items = result if isinstance(result, list) else []
        self._display(self.all_items)

    def _display(self, items):
        total = len(items)
        total_str = persian_numbers(str(total))
        content = [
            ft.Container(height=10),
            ft.Row([ft.Icon(ft.icons.Icons.FLAG, size=24, color=AppTheme.SECONDARY), ft.Text(
                f"مدیریت آگهی ترحیم ({total_str} مورد)", size=24, font_family="IranNastaliq", color=AppTheme.SECONDARY)], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
            ft.Container(height=15),
            ft.Button("➕ افزودن آگهی جدید", width=250, style=ft.ButtonStyle(bgcolor=AppTheme.PRIMARY,
                      color="#FFFFFF", shape=ft.RoundedRectangleBorder(radius=12)), on_click=lambda e: self._show_form()),
            ft.Container(height=10), self.search_field, ft.Container(
                height=15),
        ]
        if items:
            for item in items:
                content.append(self._build_card(item))
        else:
            content.append(ft.Text("آگهی یافت نشد", size=14,
                           font_family="Vazir", color="#FFFFFF60"))
        content.append(ft.Container(height=30))
        self.content_column.controls = content
        self.content_column.alignment = ft.MainAxisAlignment.START
        self.page.update()

    def _on_search(self, e):
        query = self.search_field.value.strip() if self.search_field.value else ""
        filtered = [d for d in self.all_items if query in str(
            d.get("name", ""))] if query else self.all_items
        self._display(filtered)

    def _build_card(self, item: dict):
        name = item.get("name", "")
        funeral_date = item.get("funeral_date", "")
        memorial_date = item.get("memorial_date", "")
        card_content = [ft.Row([ft.Text(name, size=14, font_family="Vazir", weight=ft.FontWeight.BOLD, color=AppTheme.TEXT_PRIMARY), ft.Container(
            expand=True), ft.Text("مرحوم", size=11, font_family="Vazir", color=AppTheme.TEXT_HINT)]), ft.Container(height=4)]
        if funeral_date:
            card_content.append(ft.Text(
                f"تشییع: {funeral_date}", size=11, font_family="Vazir", color=AppTheme.TEXT_HINT))
        if memorial_date:
            card_content.append(ft.Text(
                f"ختم: {memorial_date}", size=11, font_family="Vazir", color=AppTheme.TEXT_HINT))
        card_content.append(ft.Container(height=4))
        card_content.append(ft.Row([ft.Container(expand=True), ft.IconButton(icon=ft.icons.Icons.EDIT, icon_size=16, icon_color=AppTheme.PRIMARY, on_click=lambda e, i=item: self._show_form(i)),
                                    ft.IconButton(icon=ft.icons.Icons.DELETE, icon_size=16, icon_color=AppTheme.ERROR, on_click=lambda e, i=item: self._delete_item(i))]))
        return ft.Container(content=ft.Column(card_content), padding=12, bgcolor="#FFFFFF", border_radius=12, border=ft.Border(left=ft.BorderSide(4, AppTheme.SECONDARY)), margin=ft.Margin(0, 0, 0, 8))

    def _show_form(self, item=None):
        is_edit = item is not None
        name_field = ft.TextField(label="نام متوفی", value=item.get(
            "name", "") if item else "", border_radius=10, bgcolor="#FFFFFF")
        funeral_date_field = ft.TextField(label="زمان تشییع", hint_text="مثلاً: دوشنبه ۲۰ مهر، ساعت ۹ صبح", value=str(
            item.get("funeral_date", "")) if item else "", border_radius=10, bgcolor="#FFFFFF")
        funeral_loc_field = ft.TextField(label="مکان تشییع", value=item.get(
            "funeral_location", "") if item else "", border_radius=10, bgcolor="#FFFFFF")
        memorial_date_field = ft.TextField(label="زمان ختم", hint_text="مثلاً: دوشنبه ۲۰ مهر، ساعت ۱۶", value=str(
            item.get("memorial_date", "")) if item else "", border_radius=10, bgcolor="#FFFFFF")
        memorial_loc_field = ft.TextField(label="مکان ختم", value=item.get(
            "memorial_location", "") if item else "", border_radius=10, bgcolor="#FFFFFF")
        desc_field = ft.TextField(label="توضیحات", value=item.get(
            "description", "") if item else "", border_radius=10, bgcolor="#FFFFFF", max_lines=3, multiline=True)
        contact_field = ft.TextField(label="شماره تماس", value=item.get(
            "contact_number", "") if item else "", border_radius=10, bgcolor="#FFFFFF")
        msg = ft.Text("", color=AppTheme.ERROR, size=12)

        def save(e):
            if not name_field.value:
                msg.value = "نام الزامی است"
                self.page.update()
                return
            data = {"name": name_field.value, "funeral_date": funeral_date_field.value if funeral_date_field.value else None, "funeral_location": funeral_loc_field.value if funeral_loc_field.value else None,
                    "memorial_date": memorial_date_field.value if memorial_date_field.value else None, "memorial_location": memorial_loc_field.value if memorial_loc_field.value else None,
                    "description": desc_field.value if desc_field.value else None, "contact_number": contact_field.value if contact_field.value else None}
            if is_edit:
                data["id"] = item.get("id")
                result = api.post("admin/deceased/update.php", data)
            else:
                result = api.post("admin/deceased/create.php", data)
            if result.get("message"):
                dlg.open = False
                self.page.update()
                self._show_success(
                    "آگهی ویرایش شد" if is_edit else "آگهی ایجاد شد")
                self._reload()
            else:
                msg.value = result.get("error", "خطا")
                self.page.update()

        def close(e): dlg.open = False; self.page.update()

        dlg = ft.AlertDialog(title=ft.Text("ویرایش آگهی" if is_edit else "افزودن آگهی", font_family="Vazir", weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                             content=ft.Column([name_field, ft.Container(height=8), funeral_date_field, ft.Container(height=8), funeral_loc_field, ft.Container(height=8), memorial_date_field, ft.Container(
                                 height=8), memorial_loc_field, ft.Container(height=8), desc_field, ft.Container(height=8), contact_field, ft.Container(height=8), msg], width=300, scroll=ft.ScrollMode.AUTO, height=400),
                             actions=[ft.TextButton("انصراف", on_click=close), ft.Button("ذخیره", on_click=save, style=ft.ButtonStyle(bgcolor=AppTheme.PRIMARY, color="#FFFFFF"))])
        self.page.show_dialog(dlg)

    def _delete_item(self, item: dict):
        def confirm(e): api.post("admin/deceased/delete.php", {"id": item.get(
            "id")}); dlg.open = False; self.page.update(); self._show_success("آگهی حذف شد"); self._reload()

        def close(e): dlg.open = False; self.page.update()
        dlg = ft.AlertDialog(title=ft.Text("حذف آگهی", font_family="Vazir", weight=ft.FontWeight.BOLD), content=ft.Text(f"آیا از حذف «{item.get('name', '')}» اطمینان دارید؟", font_family="Vazir"), actions=[
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
