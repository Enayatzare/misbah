# ==========================================
# 📁 فایل: src/views/home/donations_page.py
# (نسخه نهایی - گروه‌بندی صحیح تراکنش‌ها و نمایش مبلغ مازاد)
# ==========================================
import flet as ft
from src.theme import AppTheme
from src.services.api_client import api
from src.utils.formatters import persian_numbers
import segno
import io
import base64
import jdatetime
import random


class DonationsPage:
    def __init__(self, page: ft.Page, on_back, user: dict):
        self.page = page
        self.on_back = on_back
        self.user = user

        

    def build(self):
        header = ft.Container(
            content=ft.Row(
                [
                    ft.IconButton(icon=ft.Icons.ARROW_BACK,
                                  icon_color="#FFFFFF", on_click=self.go_back),
                    ft.Text("مشارکت‌های مردمی", size=18, font_family="Vazir",
                            weight=ft.FontWeight.BOLD, color="#FFFFFF"),
                ],
                alignment=ft.MainAxisAlignment.START,
            ),
            padding=ft.Padding(15, 35, 15, 15), bgcolor="#0D1B0F",
        )

        self.content_column = ft.Column(
            [ft.Container(height=50), ft.ProgressBar(
                width=80, color=AppTheme.SECONDARY)],
            alignment=ft.MainAxisAlignment.CENTER,
        )
        scrollable = ft.ListView(
            controls=[self.content_column], expand=True, padding=20)
        page_content = ft.Container(content=scrollable, expand=True, gradient=ft.LinearGradient(
            begin=ft.Alignment(0, -1), end=ft.Alignment(0, 1), colors=["#0D1B0F", "#1A2F1E", "#0D1B0F"]))
        self.load_donations()

        def handle_back(e: ft.KeyboardEvent):
            if e.key in ["Escape", "Back", "GoBack", "ArrowLeft"]:
                self.go_back(e)
        
        self.page.on_keyboard_event = handle_back
        return ft.Column([header, page_content], expand=True, spacing=0)

    def go_back(self, e):
        self.on_back()

    def load_donations(self):
        result = api.get("financial/get_plans.php")
        if isinstance(result, list) and len(result) > 0:
            items = [
                ft.Container(height=10),
                ft.Row([ft.Icon(ft.Icons.HANDSHAKE, size=28, color=AppTheme.SECONDARY),
                        ft.Text("مشارکت‌های مردمی", size=32, font_family="IranNastaliq", color=AppTheme.SECONDARY)],
                       alignment=ft.MainAxisAlignment.CENTER, spacing=10),
                ft.Container(height=5),
                ft.Row([ft.Container(height=1.5, width=60, bgcolor=AppTheme.SECONDARY,
                       border_radius=1)], alignment=ft.MainAxisAlignment.CENTER),
                ft.Container(height=5),
                ft.Text(
                    "طرح‌های مشارکت در امور مسجد", size=14, font_family="Vazir", color="#FFFFFF80"),

                ft.Container(height=15),
                ft.Container(content=ft.Column([
                    ft.Text("وَأَنفِقُوا مِن مَّا رَزَقْنَاكُم", size=16, font_family="Vazir",
                            color=AppTheme.TEXT_PRIMARY, text_align=ft.TextAlign.CENTER),
                    ft.Container(height=4), ft.Text("انفاق کنید از آنچه روزیتان دادیم", size=12,
                                                    font_family="Vazir", color=AppTheme.TEXT_HINT, text_align=ft.TextAlign.CENTER),
                    ft.Container(height=2), ft.Text("سوره منافقون - ۱۰", size=10, font_family="Vazir",
                                                    color=AppTheme.TEXT_HINT, text_align=ft.TextAlign.CENTER),
                ]), padding=ft.Padding(16, 12, 16, 12), bgcolor="#F8F4E8", border_radius=12, border=ft.Border.all(1, AppTheme.SECONDARY), margin=ft.Margin(0, 10, 0, 20)),
            ]
            for plan in result:
                items.append(self._build_plan_card(plan))
            items.append(ft.Container(height=10))
            items.append(ft.Container(content=ft.Row([ft.Icon(ft.Icons.HISTORY, size=20, color=AppTheme.PRIMARY), ft.Text("تاریخچه مشارکت‌های من", size=14, font_family="Vazir", weight=ft.FontWeight.BOLD, color=AppTheme.PRIMARY)],
                         alignment=ft.MainAxisAlignment.CENTER, spacing=8), padding=ft.Padding(16, 12, 16, 12), bgcolor="#FFFFFF", border_radius=14, border=ft.Border(left=ft.BorderSide(4, AppTheme.SECONDARY)), on_click=self._show_history))
            items.append(ft.Container(height=20))
            self.content_column.controls = items
            self.content_column.alignment = ft.MainAxisAlignment.START
        else:
            self.content_column.controls = [ft.Container(height=60), ft.Icon(ft.Icons.VOLUNTEER_ACTIVISM, size=50, color="#FFFFFF40"), ft.Container(
                height=10), ft.Text("طرح کمک مالی فعالی وجود ندارد", size=15, font_family="Vazir", color="#FFFFFFAA")]
            self.content_column.alignment = ft.MainAxisAlignment.CENTER
        self.page.update()

    def _build_plan_card(self, plan: dict):
        title = plan.get("title", "")
        target = plan.get("target_amount", 0)
        current = plan.get("current_amount", 0)
        progress = plan.get("progress", 0)
        description = plan.get("description", "")
        target_str = persian_numbers(
            f"{int(float(target)):,}") if target else "۰"
        current_str = persian_numbers(
            f"{int(float(current)):,}") if current else "۰"
        progress_str = persian_numbers(f"{progress:.1f}") if progress else "۰"
        progress_color = "#E53935" if progress < 40 else (
            "#EF6C00" if progress < 70 else "#2E7D32")
        is_completed = float(current) >= float(
            target) if target and float(target) > 0 else False
        card_bg = "#E8F5E9" if is_completed else "#FFFFFF"
        border_color = "#2E7D32" if is_completed else AppTheme.SECONDARY
        progress_bar = ft.Container(content=ft.Container(
            width=f"{progress}%", bgcolor=progress_color, border_radius=4, height=8), bgcolor="#F5F5F5", border_radius=4, height=8)
        desc_col = ft.Column([ft.Text(title, size=16, font_family="Vazir",
                             weight=ft.FontWeight.BOLD, color=AppTheme.TEXT_PRIMARY)], expand=True)
        if description:
            desc_col.controls.append(ft.Text(
                description, size=12, font_family="Vazir", color=AppTheme.TEXT_SECONDARY))
        if is_completed:
            desc_col.controls.append(ft.Text(
                "✅ تکمیل شد", size=11, font_family="Vazir", weight=ft.FontWeight.BOLD, color="#2E7D32"))

        return ft.Container(content=ft.Column([
            ft.Row([ft.Container(content=ft.Icon(ft.Icons.HANDSHAKE, size=22, color="#FFFFFF"), width=44, height=44,
                   bgcolor=AppTheme.PRIMARY, border_radius=22, alignment=ft.Alignment(0, 0)), ft.Container(width=12), desc_col]),
            ft.Container(height=12), ft.Row([ft.Text(f"{progress_str}٪", size=12, font_family="Vazir", weight=ft.FontWeight.BOLD, color=progress_color), ft.Container(
                expand=True), ft.Text(f"{current_str} / {target_str} تومان", size=11, font_family="Vazir", color=AppTheme.TEXT_HINT)]),
            ft.Container(height=6), progress_bar, ft.Container(height=12),
            ft.Button("✅ تکمیل شده" if is_completed else "می‌خواهم کمک کنم 🤝", width=200, height=40,
                      style=ft.ButtonStyle(bgcolor="#AAAAAA" if is_completed else AppTheme.PRIMARY,
                                           color="#FFFFFF", shape=ft.RoundedRectangleBorder(radius=20)),
                      on_click=None if is_completed else lambda e, p=plan: self._show_donate_form(p)),
        ]), padding=16, bgcolor=card_bg, border_radius=14, border=ft.Border(left=ft.BorderSide(4, border_color)), margin=ft.Margin(0, 0, 0, 16), shadow=ft.BoxShadow(spread_radius=0, blur_radius=8, color="#00000010"))

    def _show_donate_form(self, plan: dict):
        title = plan.get("title", "")
        plan_id = plan.get("id", 0)
        amount_field = ft.TextField(
            label="مبلغ (تومان)", keyboard_type=ft.KeyboardType.NUMBER, border_radius=10, bgcolor="#FFFFFF")
        desc_field = ft.TextField(
            label="توضیحات (اختیاری)", border_radius=10, bgcolor="#FFFFFF", max_lines=2)
        error_text = ft.Text("", color=AppTheme.ERROR, size=12)
        loading = ft.ProgressBar(
            visible=False, color=AppTheme.PRIMARY, height=2)

        def submit_donation(e):
            amount = amount_field.value.strip() if amount_field.value else ""
            if not amount or not amount.isdigit() or int(amount) <= 0:
                error_text.value = "مبلغ معتبر وارد کنید"
                self.page.update()
                return
            loading.visible = True
            error_text.value = ""
            self.page.update()
            today = jdatetime.date.today()
            shamsi_date = f"{today.year:04d}{today.month:02d}{today.day:02d}"
            transaction_code = f"MSJ-{shamsi_date}-{random.randint(1000, 9999)}"
            data = {"plan_id": plan_id, "amount": int(
                amount), "description": desc_field.value if desc_field.value else "", "transaction_code": transaction_code}
            result = api.post("financial/make_donation.php", data)
            loading.visible = False
            if result.get("transaction_code"):
                dlg.open = False
                self.page.update()
                self._show_success(result.get(
                    "transaction_code", ""), int(amount))
            else:
                error_text.value = result.get("error", "خطا در ثبت")
                self.page.update()

        def close_dlg(e):
            dlg.open = False
            self.page.update()

        dlg = ft.AlertDialog(
            title=ft.Text(f"کمک به {title}", font_family="Vazir",
                          weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
            content=ft.Column([amount_field, ft.Container(
                height=10), desc_field, ft.Container(height=8), error_text, loading], width=280),
            actions=[ft.TextButton("انصراف", on_click=close_dlg), ft.Button("ثبت کمک", on_click=submit_donation, style=ft.ButtonStyle(bgcolor=AppTheme.PRIMARY, color="#FFFFFF", shape=ft.RoundedRectangleBorder(radius=8)))])
        self.page.show_dialog(dlg)

    def _show_success(self, code: str, amount: int):
        card_number = "۵۳۳۰-۱۶۳۴-۰۷۱۲-۶۳۹۶"

        qr_data = f"شماره کارت: {card_number}\nمبلغ: {amount} تومان\nکد پیگیری: {code}"
        qr = segno.make_qr(qr_data)
        buffer = io.BytesIO()
        qr.save(buffer, kind='png', scale=8)
        qr_base64 = base64.b64encode(buffer.getvalue()).decode()

        dlg = ft.AlertDialog(
            title=ft.Text("✅ با موفقیت ثبت شد", font_family="Vazir",
                          weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER,
                          color=AppTheme.PRIMARY),
            content=ft.Column([
                ft.Text(f"مبلغ: {persian_numbers(str(amount))} تومان",
                        size=14, font_family="Vazir"),
                ft.Container(height=10),
                ft.Text(f"📱 شماره کارت مسجد:", size=12, font_family="Vazir",
                        color=AppTheme.TEXT_HINT, text_align=ft.TextAlign.CENTER),
                ft.Text(card_number, size=16, font_family="Vazir", weight=ft.FontWeight.BOLD,
                        color=AppTheme.TEXT_PRIMARY, text_align=ft.TextAlign.CENTER),
                ft.Container(height=15),
                ft.Text("لطفاْ کد پیگیری خود را کپی کنید.", size=12, font_family="Vazir",
                        color=AppTheme.TEXT_SECONDARY, text_align=ft.TextAlign.CENTER),
                ft.TextField(
                    value=code,
                    read_only=True,
                    bgcolor="#FFFFFF",
                    border_radius=8,
                    text_style=ft.TextStyle(
                        font_family="Vazir", weight=ft.FontWeight.BOLD, size=16),
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Container(height=10),
                ft.Image(
                    src=f"data:image/png;base64,{qr_base64}", width=150, height=150),
                ft.Container(height=10),
                ft.Text("لطفاْ کد پیگیری زیر را هنگام واریز در توضیحات بانکی وارد کنید", size=12,
                        font_family="Vazir", color=AppTheme.TEXT_HINT, text_align=ft.TextAlign.CENTER),
                ft.Container(height=5),
                ft.Text("مبلغ، پس از تأیید مدیر سیستم، در طرح منظور خواهد شد",
                        size=12, font_family="Vazir", color=AppTheme.TEXT_HINT),
            ], width=300, horizontal_alignment=ft.CrossAxisAlignment.CENTER, scroll=ft.ScrollMode.AUTO),
            actions=[ft.TextButton(
                "باشه", on_click=lambda e: self._close_dlg(dlg))],
        )
        self.page.show_dialog(dlg)

    def _close_dlg(self, dlg):
        dlg.open = False
        self.page.update()

    def _show_history(self, e):
        result = api.get("financial/get_user_history.php")
        if result.get("transactions"):
            transactions = result["transactions"]

            # گروه‌بندی تراکنش‌ها: جفت کردن اصلی و مازاد
            groups = {}  # کلید: transaction_code اصلی
            for tx in transactions:
                code = tx.get("transaction_code", "")
                if code.endswith("-GENERAL"):
                    base_code = code.replace("-GENERAL", "")
                    if base_code not in groups:
                        groups[base_code] = {"main": None, "extra": None}
                    groups[base_code]["extra"] = tx
                else:
                    base_code = code
                    if base_code not in groups:
                        groups[base_code] = {"main": None, "extra": None}
                    groups[base_code]["main"] = tx

            items = [
                ft.Text("تاریخچه مشارکت‌های من", size=16, font_family="Vazir",
                        weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER, color=AppTheme.PRIMARY),
                ft.Divider(height=20, color="#E0E0E0")
            ]

            for base_code, group in groups.items():
                main_tx = group["main"]
                extra_tx = group["extra"]

                if not main_tx:
                    continue

                main_amount = float(main_tx.get("amount", 0))
                main_status = main_tx.get("status", "pending")
                plan_title = main_tx.get("plan_title", "")
                extra_amount = float(extra_tx.get(
                    "amount", 0)) if extra_tx else 0
                total_amount = main_amount + extra_amount  # مبلغ کل واریزی کاربر

                # تعیین وضعیت نمایشی
                if main_status == "completed":
                    status_text = "✅ تأیید شده"
                    status_color = AppTheme.PRIMARY
                    bg_color = "#E8F5E9" if extra_amount == 0 else "#FFF8E1"
                elif main_status == "rejected":
                    status_text = "❌ رد شده"
                    status_color = AppTheme.ERROR
                    bg_color = "#FFEBEE"
                else:
                    status_text = "⏳ در انتظار"
                    status_color = AppTheme.WARNING
                    bg_color = "#FFF3E0"

                # ساخت کارت
                card_content = []

                # ردیف اول: مبلغ کل واریزی و وضعیت
                card_content.append(
                    ft.Row([
                        ft.Text(f"مجموع: {persian_numbers(f'{int(total_amount):,}')} تومان",
                                size=13, font_family="Vazir", weight=ft.FontWeight.BOLD,
                                color=AppTheme.TEXT_PRIMARY),
                        ft.Container(expand=True),
                        ft.Text(status_text, size=11, font_family="Vazir",
                                color=status_color, weight=ft.FontWeight.BOLD),
                    ])
                )

                # نام طرح
                if plan_title:
                    card_content.append(ft.Container(height=2))
                    card_content.append(
                        ft.Text(plan_title, size=10, font_family="Vazir",
                                color=AppTheme.TEXT_HINT)
                    )

                # اگر تأیید شده، تفکیک مبلغ
                if main_status == "completed":
                    card_content.append(ft.Container(height=6))
                    card_content.append(
                        ft.Row([
                            ft.Text("✅ تأیید برای طرح:", size=11, font_family="Vazir",
                                    color=AppTheme.PRIMARY),
                            ft.Container(expand=True),
                            ft.Text(f"{persian_numbers(f'{int(main_amount):,}')} تومان", size=12,
                                    font_family="Vazir", weight=ft.FontWeight.BOLD,
                                    color=AppTheme.PRIMARY),
                        ])
                    )

                    # اگر مازاد به صندوق رفته
                    if extra_amount > 0:
                        card_content.append(ft.Container(height=4))
                        card_content.append(
                            ft.Row([
                                ft.Text("🕌 واریز به صندوق مسجد:", size=11, font_family="Vazir",
                                        color=AppTheme.SECONDARY),
                                ft.Container(expand=True),
                                ft.Text(f"{persian_numbers(f'{int(extra_amount):,}')} تومان", size=12,
                                        font_family="Vazir", weight=ft.FontWeight.BOLD,
                                        color=AppTheme.SECONDARY),
                            ])
                        )
                        card_content.append(ft.Container(height=4))
                        card_content.append(
                            ft.Text(
                                "به دلیل تکمیل سقف طرح، این مبلغ به صندوق عمومی مسجد منتقل شد و در طرح‌های آتی استفاده خواهد شد.",
                                size=9, font_family="Vazir",
                                color=AppTheme.TEXT_HINT,
                                text_align=ft.TextAlign.RIGHT
                            )
                        )
                elif main_status == "rejected":
                    card_content.append(ft.Container(height=4))
                    card_content.append(
                        ft.Text("این کمک تأیید نشد. لطفاً با مدیریت مسجد تماس بگیرید.",
                                size=10, font_family="Vazir", color=AppTheme.ERROR)
                    )
                else:
                    card_content.append(ft.Container(height=4))
                    card_content.append(
                        ft.Text("در انتظار تأیید مدیر سیستم",
                                size=10, font_family="Vazir", color=AppTheme.WARNING)
                    )

                items.append(ft.Container(
                    content=ft.Column(card_content),
                    padding=12,
                    bgcolor=bg_color,
                    border_radius=10,
                    border=ft.Border(left=ft.BorderSide(
                        4, AppTheme.SECONDARY)),
                    margin=ft.Margin(0, 0, 0, 8)
                ))
        else:
            items = [ft.Text("تاکنون کمکی ثبت نکرده‌اید", size=14,
                             font_family="Vazir", color=AppTheme.TEXT_HINT)]

        def close(e):
            dlg.open = False
            self.page.update()

        dlg = ft.AlertDialog(
            title=ft.Text("📋 تاریخچه مشارکت‌ها", font_family="Vazir",
                          weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
            content=ft.Column(items, width=320, height=350,
                              scroll=ft.ScrollMode.AUTO),
            actions=[ft.TextButton("بستن", on_click=close)])
        self.page.show_dialog(dlg)
