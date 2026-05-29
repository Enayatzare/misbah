# ==========================================
# 📁 فایل: src/views/admin/manage_donations.py
# (نسخه نهایی - کارت صندوق مسجد، گزارش مشارکت‌کنندگان، تاریخچه و انتقال)
# ==========================================
import flet as ft
from src.theme import AppTheme
from src.services.api_client import api
from src.utils.formatters import persian_numbers
import asyncio


class ManageDonations:
    def __init__(self, page: ft.Page, on_back):
        self.page = page
        self.on_back = on_back
        self.all_donations = []
        self.all_plans = []
        self.current_donation_page = 1
        self.current_plan_page = 1
        self.per_page = 10
        self.current_tab = "donations"

        

    def build(self):
        header = ft.Container(
            content=ft.Row(
                [
                    ft.IconButton(icon=ft.icons.Icons.ARROW_BACK,
                                  icon_color="#FFFFFF", on_click=self.go_back),
                    ft.Text("مدیریت مشارکت‌های مردمی", size=18, font_family="Vazir",
                            weight=ft.FontWeight.BOLD, color="#FFFFFF"),
                    ft.Container(expand=True),
                    ft.IconButton(icon=ft.icons.Icons.LOGOUT,
                                  icon_color="#FF5252", on_click=self._logout),
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
        page_content = ft.Container(
            content=scrollable, expand=True,
            gradient=ft.LinearGradient(begin=ft.Alignment(
                0, -1), end=ft.Alignment(0, 1), colors=["#0D1B0F", "#1A2F1E", "#0D1B0F"]),
        )
        self.load_data()

        self.page.on_pop = lambda e: self.go_back(e)
        return ft.Column([header, page_content], expand=True, spacing=0)

    def load_data(self):
        result = api.get("admin/financial/list_donations.php")
        if isinstance(result, dict) and result.get("donations"):
            self.all_donations = result["donations"]
        elif isinstance(result, list):
            self.all_donations = result
        else:
            self.all_donations = []

        plans_result = api.get("admin/financial/plans_crud.php")
        self.all_plans = plans_result if isinstance(plans_result, list) else []

        self._display()

    def _display(self):
        pending = sum(1 for d in self.all_donations if d.get(
            "status") == "pending")

        # محاسبه موجودی صندوق مسجد
        fund_transactions = [d for d in self.all_donations if d.get(
            "status") == "rejected_general"]
        fund_total = sum(float(d.get("amount", 0)) for d in fund_transactions)

        # کم کردن برداشت‌ها از صندوق
        withdrawals = [d for d in self.all_donations if d.get(
            "transaction_code", "").startswith("FUND-TRANSFER-")]
        withdrawn_total = sum(float(d.get("amount", 0)) for d in withdrawals)
        fund_total -= withdrawn_total

        content = [
            ft.Container(height=10),
            ft.Row(
                [ft.Icon(ft.icons.Icons.HANDSHAKE, size=24, color=AppTheme.SECONDARY),
                 ft.Text("مدیریت مشارکت‌های مردمی", size=24, font_family="IranNastaliq", color=AppTheme.SECONDARY)],
                alignment=ft.MainAxisAlignment.CENTER, spacing=10,
            ),
            ft.Container(height=8),
            ft.Row([ft.Container(height=1.5, width=60, bgcolor=AppTheme.SECONDARY,
                   border_radius=1)], alignment=ft.MainAxisAlignment.CENTER),
            ft.Container(height=10),
            ft.Text(f"{persian_numbers(str(pending))} تراکنش در انتظار",
                    size=13, font_family="Vazir", color="#FF8F00"),
            ft.Container(height=10),
            # کارت صندوق مسجد
            self._build_fund_card(fund_total, len(fund_transactions)),
            ft.Container(height=15),
        ]

        tabs = [("💰 تراکنش‌ها", "donations"), ("📋 طرح‌ها", "plans")]
        tab_row = ft.Row(spacing=6, alignment=ft.MainAxisAlignment.CENTER)
        for label, tab_id in tabs:
            is_active = self.current_tab == tab_id
            tab_row.controls.append(
                ft.Container(
                    content=ft.Text(label, size=12, font_family="Vazir",
                                    weight=ft.FontWeight.BOLD if is_active else None,
                                    color="#000000" if is_active else "#000000"),
                    padding=ft.Padding(12, 6, 12, 6),
                    bgcolor=AppTheme.SECONDARY if is_active else "#FFFFFF",
                    border_radius=16,
                    on_click=lambda e, t=tab_id: self._switch_tab(t),
                )
            )
        content.append(tab_row)
        content.append(ft.Container(height=15))

        if self.current_tab == "donations":
            self._display_donations(content)
        else:
            self._display_plans(content)

        content.append(ft.Container(height=30))
        self.content_column.controls = content
        self.content_column.alignment = ft.MainAxisAlignment.START
        self.page.update()

    def _switch_tab(self, tab_id: str):
        self.current_tab = tab_id
        self._display()

    def _display_donations(self, content):
        total = len(self.all_donations)
        total_pages = max(1, (total + self.per_page - 1) // self.per_page)
        start = (self.current_donation_page - 1) * self.per_page
        page_donations = self.all_donations[start:start + self.per_page]

        if page_donations:
            for don in page_donations:
                content.append(self._build_donation_card(don))
        else:
            content.append(ft.Text("تراکنشی یافت نشد", size=14,
                           font_family="Vazir", color="#FFFFFF60"))

        if total_pages > 1:
            self._build_pagination(
                content, self.current_donation_page, total_pages, "donation")

    def _display_plans(self, content):
        total = len(self.all_plans)
        total_pages = max(1, (total + self.per_page - 1) // self.per_page)
        start = (self.current_plan_page - 1) * self.per_page
        page_plans = self.all_plans[start:start + self.per_page]

        content.append(
            ft.Button("➕ افزودن طرح جدید", width=250,
                      style=ft.ButtonStyle(
                          bgcolor=AppTheme.PRIMARY, color="#FFFFFF", shape=ft.RoundedRectangleBorder(radius=12)),
                      on_click=lambda e: self._show_plan_form())
        )
        content.append(ft.Container(height=15))

        if page_plans:
            for plan in page_plans:
                content.append(self._build_plan_card(plan))
        else:
            content.append(ft.Text("طرحی یافت نشد", size=14,
                           font_family="Vazir", color="#FFFFFF60"))

        if total_pages > 1:
            self._build_pagination(
                content, self.current_plan_page, total_pages, "plan")

    def _build_pagination(self, content, current_page, total_pages, page_type):
        content.append(ft.Container(height=15))
        pag_row = ft.Row(alignment=ft.MainAxisAlignment.CENTER, spacing=10)
        pag_row.controls.append(
            ft.IconButton(icon=ft.icons.Icons.CHEVRON_RIGHT,
                          icon_color=AppTheme.PRIMARY if current_page > 1 else "#FFFFFF30",
                          on_click=lambda e: self._prev_page(page_type) if current_page > 1 else None)
        )
        pag_row.controls.append(
            ft.Text(f"صفحه {persian_numbers(str(current_page))} از {persian_numbers(str(total_pages))}",
                    size=12, font_family="Vazir", color="#FFFFFF80")
        )
        pag_row.controls.append(
            ft.IconButton(icon=ft.icons.Icons.CHEVRON_LEFT,
                          icon_color=AppTheme.PRIMARY if current_page < total_pages else "#FFFFFF30",
                          on_click=lambda e: self._next_page(page_type) if current_page < total_pages else None)
        )
        content.append(pag_row)

    def _prev_page(self, page_type: str):
        if page_type == "donation" and self.current_donation_page > 1:
            self.current_donation_page -= 1
        elif page_type == "plan" and self.current_plan_page > 1:
            self.current_plan_page -= 1
        self._display()

    def _next_page(self, page_type: str):
        if page_type == "donation":
            self.current_donation_page += 1
        elif page_type == "plan":
            self.current_plan_page += 1
        self._display()

    def _build_plan_card(self, plan: dict):
        title = plan.get("title", "")
        target = float(plan.get("target_amount") or 0)
        current = float(plan.get("current_amount") or 0)

        is_completed = current >= target if target > 0 else False
        card_bg = "#E8F5E9" if is_completed else "#FFFFFF"
        border_color = "#2E7D32" if is_completed else AppTheme.SECONDARY

        content_items = [
            ft.Row([
                ft.Text(title, size=14, font_family="Vazir",
                        weight=ft.FontWeight.BOLD, color=AppTheme.TEXT_PRIMARY),
                ft.Container(expand=True),
                ft.Text(f"{persian_numbers(f'{int(current):,}')} / {persian_numbers(f'{int(target):,}')} تومان",
                        size=11, font_family="Vazir", color=AppTheme.TEXT_HINT),
            ]),
        ]

        if is_completed:
            content_items.append(ft.Text(
                "✅ تکمیل شد", size=11, font_family="Vazir", weight=ft.FontWeight.BOLD, color="#2E7D32"))

        content_items.append(ft.Container(height=4))
        content_items.append(
            ft.Row([
                ft.Container(expand=True),
                ft.IconButton(icon=ft.icons.Icons.EDIT, icon_size=16, icon_color=AppTheme.PRIMARY,
                              on_click=lambda e, p=plan: self._show_plan_form(p)),
                ft.IconButton(icon=ft.icons.Icons.DELETE, icon_size=16, icon_color=AppTheme.ERROR,
                              on_click=lambda e, p=plan: self._delete_plan(p)),
            ])
        )

        return ft.Container(
            content=ft.Column(content_items),
            padding=12, bgcolor=card_bg, border_radius=12,
            border=ft.Border(left=ft.BorderSide(4, border_color)),
            margin=ft.Margin(0, 0, 0, 8),
        )

    def _build_donation_card(self, don: dict):
        user_name = don.get("user_name", "ناشناس")
        plan_title = don.get("plan_title", "")
        amount = float(don.get("amount") or 0)
        status = don.get("status", "pending")
        date = (don.get("created_at") or "")[:10]
        receipt_url = don.get("receipt_image", "")
        transaction_code = don.get("transaction_code", "")
        plan_id = don.get("plan_id")
        plan_exists = any(
            p.get("id") == plan_id for p in self.all_plans) if plan_id else True

        status_map = {
            "completed": ("✅ تأیید شده", AppTheme.PRIMARY),
            "pending": ("⏳ در انتظار", AppTheme.WARNING),
            "rejected": ("❌ رد شده", AppTheme.ERROR),
            "rejected_general": ("🏛 صندوق عمومی", AppTheme.SECONDARY),
        }
        status_text, status_color = status_map.get(
            status, ("⏳ در انتظار", AppTheme.WARNING))

        info_items = [ft.Text(user_name, size=13, font_family="Vazir",
                              weight=ft.FontWeight.BOLD, color=AppTheme.TEXT_PRIMARY)]
        if transaction_code:
            info_items.append(ft.Text(
                f"🏷 کد پیگیری: {transaction_code}", size=10, font_family="Vazir", color=AppTheme.TEXT_HINT))

        card_content = ft.Column([
            ft.Row([
                ft.Container(
                    content=ft.Text(
                        user_name[0] if user_name else "?", size=14, color="#FFFFFF", font_family="Vazir"),
                    width=36, height=36, bgcolor=AppTheme.PRIMARY, border_radius=18,
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Container(width=10),
                ft.Column(info_items, expand=True),
                ft.Container(width=8),
                ft.Text(f"{persian_numbers(f'{int(amount):,}')} تومان", size=13,
                        font_family="Vazir", weight=ft.FontWeight.BOLD, color=AppTheme.PRIMARY),
            ]),
            ft.Container(height=4),
            ft.Row([
                ft.Text(plan_title if plan_exists else f"{plan_title} (طرح حذف شده)", size=11, font_family="Vazir",
                        color=AppTheme.TEXT_HINT if plan_exists else AppTheme.ERROR),
                ft.Container(expand=True),
                ft.Text(status_text, size=10,
                        font_family="Vazir", color=status_color),
            ]),
            ft.Container(height=2),
            ft.Text(date, size=10, font_family="Vazir",
                    color=AppTheme.TEXT_HINT),
        ])

        if status == "rejected_general":
            card_content.controls.append(ft.Container(height=6))
            card_content.controls.append(
                ft.Container(
                    content=ft.Text(
                        "این مبلغ به دلیل تکمیل سقف طرح به صندوق عمومی مسجد منتقل شد و در طرح‌های آتی استفاده خواهد شد.",
                        size=10,
                        font_family="Vazir",
                        color=AppTheme.SECONDARY,
                        text_align=ft.TextAlign.RIGHT,
                    ),
                    bgcolor="#FFF8E1",
                    border_radius=8,
                    padding=ft.Padding(8, 6, 8, 6),
                )
            )

        if receipt_url:
            card_content.controls.append(ft.Container(height=4))
            card_content.controls.append(
                ft.TextButton("📸 مشاهده رسید", on_click=lambda e, u=receipt_url: self._view_receipt(u),
                              style=ft.ButtonStyle(color=AppTheme.PRIMARY, text_style=ft.TextStyle(size=10, font_family="Vazir")))
            )

        if status == "pending" and plan_exists:
            card_content.controls.append(ft.Container(height=6))
            card_content.controls.append(
                ft.Row([
                    ft.Container(expand=True),
                    ft.Button("✅ تأیید", on_click=lambda e, d=don: self._approve(d),
                              style=ft.ButtonStyle(bgcolor=AppTheme.PRIMARY, color="#FFFFFF", shape=ft.RoundedRectangleBorder(radius=8))),
                    ft.Container(width=4),
                    ft.Button("❌ رد", on_click=lambda e, d=don: self._reject(d),
                              style=ft.ButtonStyle(bgcolor=AppTheme.ERROR, color="#FFFFFF", shape=ft.RoundedRectangleBorder(radius=8))),
                ])
            )

        return ft.Container(
            content=card_content,
            padding=12, bgcolor="#FFFFFF", border_radius=12,
            border=ft.Border(left=ft.BorderSide(4, AppTheme.SECONDARY)),
            margin=ft.Margin(0, 0, 0, 8),
        )

    def _build_fund_card(self, total: float, count: int):
        """کارت صندوق عمومی مسجد"""
        total_str = persian_numbers(f"{int(total):,}")
        count_str = persian_numbers(str(count))

        return ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Icon(ft.icons.Icons.ACCOUNT_BALANCE,
                                    size=28, color="#FFFFFF"),
                    width=50, height=50,
                    bgcolor=AppTheme.SECONDARY,
                    border_radius=25,
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Container(width=14),
                ft.Column([
                    ft.Text("🏛 صندوق عمومی مسجد", size=14, font_family="Vazir",
                            weight=ft.FontWeight.BOLD, color="#5D4037"),
                    ft.Text(f"موجودی: {total_str} تومان  |  {count_str} تراکنش",
                            size=11, font_family="Vazir", color="#8D6E63"),
                ], expand=True),
                ft.Icon(ft.icons.Icons.CHEVRON_LEFT,
                        size=20, color="#8D6E63"),
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.Padding(14, 12, 14, 12),
            bgcolor="#FFF8E1",
            border_radius=14,
            border=ft.Border.all(2, AppTheme.SECONDARY),
            shadow=ft.BoxShadow(
                spread_radius=0, blur_radius=8, color="#D4AF3740"),
            on_click=lambda e: self._show_fund_detail(),
        )

    def _show_fund_detail(self):
        """نمایش جزئیات صندوق مسجد با سه زبانه"""
        fund_transactions = [d for d in self.all_donations if d.get(
            "status") == "rejected_general"]

        # محتوای هر زبانه
        self._fund_tab_content = ft.Column(
            [], expand=True, scroll=ft.ScrollMode.AUTO)
        self._fund_tab = "participants"

        def switch_tab(tab_id: str):
            self._fund_tab = tab_id
            self._build_fund_tab_content(fund_transactions)

        tab_row = ft.Row(
            [
                ft.Container(
                    content=ft.Text("👥 مشارکت‌کنندگان", size=11, font_family="Vazir",
                                    weight=ft.FontWeight.BOLD if self._fund_tab ==
                                    "participants" else None,
                                    color="#000000" if self._fund_tab == "participants" else "#000000"),
                    padding=ft.Padding(10, 6, 10, 6),
                    bgcolor=AppTheme.SECONDARY if self._fund_tab == "participants" else "#FFFFFF",
                    border_radius=12,
                    on_click=lambda e: switch_tab("participants"),
                ),
                ft.Container(
                    content=ft.Text("📋 تاریخچه", size=11, font_family="Vazir",
                                    weight=ft.FontWeight.BOLD if self._fund_tab == "history" else None,
                                    color="#000000" if self._fund_tab == "history" else "#000000"),
                    padding=ft.Padding(10, 6, 10, 6),
                    bgcolor=AppTheme.SECONDARY if self._fund_tab == "history" else "#FFFFFF",
                    border_radius=12,
                    on_click=lambda e: switch_tab("history"),
                ),
                ft.Container(
                    content=ft.Text("💸 انتقال", size=11, font_family="Vazir",
                                    weight=ft.FontWeight.BOLD if self._fund_tab == "transfer" else None,
                                    color="#000000" if self._fund_tab == "transfer" else "#000000"),
                    padding=ft.Padding(10, 6, 10, 6),
                    bgcolor=AppTheme.SECONDARY if self._fund_tab == "transfer" else "#FFFFFF",
                    border_radius=12,
                    on_click=lambda e: switch_tab("transfer"),
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=8,
        )

        self._build_fund_tab_content(fund_transactions)

        def close(e):
            self._fund_dlg.open = False
            self.page.update()

        self._fund_dlg = ft.AlertDialog(
            title=ft.Text(""),
            content=ft.Column([
                ft.Text("🏛 صندوق عمومی مسجد", size=18, font_family="Vazir",
                        weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER, color=AppTheme.SECONDARY),
                ft.Container(height=6),
                ft.Row([ft.Container(height=1.5, width=40, bgcolor=AppTheme.SECONDARY,
                       border_radius=1)], alignment=ft.MainAxisAlignment.CENTER),
                ft.Container(height=10),
                tab_row,
                ft.Container(height=10),
                self._fund_tab_content,
            ], width=340, height=420, spacing=0),
            actions=[ft.TextButton("بستن", on_click=close,
                                   style=ft.ButtonStyle(color=AppTheme.SECONDARY))]
        )
        self.page.show_dialog(self._fund_dlg)

    def _build_fund_tab_content(self, fund_transactions: list):
        """ساخت محتوای هر زبانه در دیالوگ صندوق"""
        self._fund_tab_content.controls.clear()

        if self._fund_tab == "participants":
            participants = {}
            for tx in fund_transactions:
                name = tx.get("user_name", "ناشناس")
                amount = float(tx.get("amount", 0))
                if name not in participants:
                    participants[name] = {"total": 0, "count": 0}
                participants[name]["total"] += amount
                participants[name]["count"] += 1

            if participants:
                for name, data in participants.items():
                    total_str = persian_numbers(f"{int(data['total']):,}")
                    count_str = persian_numbers(str(data["count"]))
                    self._fund_tab_content.controls.append(
                        ft.Container(
                            content=ft.Column([
                                ft.Row([
                                    ft.Text(name, size=13, font_family="Vazir",
                                            weight=ft.FontWeight.BOLD, color=AppTheme.TEXT_PRIMARY),
                                    ft.Container(expand=True),
                                    ft.Text(f"{total_str} تومان",
                                            size=12, font_family="Vazir", weight=ft.FontWeight.BOLD,
                                            color=AppTheme.PRIMARY),
                                ]),
                                ft.Text(f"{count_str} تراکنش",
                                        size=10, font_family="Vazir", color=AppTheme.TEXT_HINT),
                            ]),
                            padding=10, bgcolor="#FFFFFF", border_radius=8,
                            margin=ft.Margin(0, 0, 0, 6)
                        )
                    )
            else:
                self._fund_tab_content.controls.append(
                    ft.Text("هنوز مبلغی به صندوق واریز نشده است",
                            size=13, font_family="Vazir", color="#FFFFFF60")
                )

        elif self._fund_tab == "history":
            if fund_transactions:
                for tx in fund_transactions[:30]:
                    user_name = tx.get("user_name", "ناشناس")
                    amount = float(tx.get("amount", 0))
                    date = (tx.get("created_at") or "")[:10]
                    plan_title = tx.get("plan_title", "")
                    amount_str = persian_numbers(f"{int(amount):,}")

                    self._fund_tab_content.controls.append(
                        ft.Container(
                            content=ft.Column([
                                ft.Row([
                                    ft.Text(f"{amount_str} تومان",
                                            size=13, font_family="Vazir", weight=ft.FontWeight.BOLD,
                                            color=AppTheme.TEXT_PRIMARY),
                                    ft.Container(expand=True),
                                    ft.Text(date, size=10, font_family="Vazir",
                                            color=AppTheme.TEXT_HINT),
                                ]),
                                ft.Text(f"از {user_name} - طرح: {plan_title}",
                                        size=10, font_family="Vazir", color=AppTheme.TEXT_HINT),
                            ]),
                            padding=10, bgcolor="#FFFFFF", border_radius=8,
                            margin=ft.Margin(0, 0, 0, 6)
                        )
                    )
            else:
                self._fund_tab_content.controls.append(
                    ft.Text("هنوز مبلغی به صندوق واریز نشده است",
                            size=13, font_family="Vazir", color="#FFFFFF60")
                )

        elif self._fund_tab == "transfer":
            active_plans = [p for p in self.all_plans if float(
                p.get("target_amount", 0)) > float(p.get("current_amount", 0))]

            if not active_plans:
                self._fund_tab_content.controls.append(
                    ft.Column([
                        ft.Text("هیچ طرح فعالی برای انتقال وجود ندارد",
                                size=13, font_family="Vazir", color="#FF2233",
                                text_align=ft.TextAlign.CENTER),
                        ft.Container(height=10),
                        ft.Button("➕ ایجاد طرح جدید", width=200,
                                  style=ft.ButtonStyle(
                                      bgcolor=AppTheme.PRIMARY, color="#FFFFFF",
                                      shape=ft.RoundedRectangleBorder(radius=8)),
                                  on_click=lambda e: self._create_new_plan_from_fund()),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
                )
            else:
                fund_deposits = sum(float(d.get("amount", 0))
                                    for d in fund_transactions)
                fund_withdrawals = sum(float(d.get("amount", 0)) for d in self.all_donations if d.get(
                    "transaction_code", "").startswith("FUND-TRANSFER-"))
                actual_fund_total = fund_deposits - fund_withdrawals
                fund_total_str = persian_numbers(f"{int(actual_fund_total):,}")

                self._transfer_plan_dd = ft.Dropdown(
                    label="انتخاب طرح",
                    options=[ft.dropdown.Option(str(p["id"]), p.get(
                        "title", "")) for p in active_plans],
                    border_radius=10,
                    bgcolor="#FFFFFF",
                )
                self._transfer_amount_field = ft.TextField(
                    label=f"مبلغ (حداکثر {fund_total_str} تومان)",
                    keyboard_type=ft.KeyboardType.NUMBER,
                    border_radius=10,
                    bgcolor="#FFFFFF",
                )
                self._transfer_error = ft.Text(
                    "", color=AppTheme.ERROR, size=11)

                def do_transfer(e):
                    plan_id_str = self._transfer_plan_dd.value
                    amount_str = self._transfer_amount_field.value.strip(
                    ) if self._transfer_amount_field.value else ""

                    self._transfer_error.value = ""

                    if not plan_id_str:
                        self._transfer_error.value = "لطفاً یک طرح انتخاب کنید"
                        self.page.update()
                        return
                    if not amount_str or not amount_str.isdigit() or int(amount_str) <= 0:
                        self._transfer_error.value = "مبلغ معتبر وارد کنید"
                        self.page.update()
                        return
                    if int(amount_str) > actual_fund_total:
                        self._transfer_error.value = f"مبلغ نمی‌تواند بیشتر از موجودی صندوق ({fund_total_str} تومان) باشد"
                        self.page.update()
                        return

                    result = api.post("admin/financial/transfer_from_fund.php", {
                        "plan_id": int(plan_id_str),
                        "amount": int(amount_str)
                    })

                    if result.get("message"):
                        # بستن دیالوگ
                        self._fund_dlg.open = False
                        self.page.update()
                        # نمایش موفقیت در SnackBar اصلی
                        self._show_success(result["message"])
                        # بارگذاری مجدد داده‌ها
                        self.load_data()
                    else:
                        self._transfer_error.value = result.get(
                            "error", "خطا در انتقال")
                        self.page.update()

                self._fund_tab_content.controls.extend([
                    ft.Container(height=5),
                    self._transfer_plan_dd,
                    ft.Container(height=10),
                    self._transfer_amount_field,
                    ft.Container(height=5),
                    self._transfer_error,
                    ft.Container(height=10),
                    ft.Button("ثبت انتقال به طرح", on_click=do_transfer,
                              style=ft.ButtonStyle(bgcolor=AppTheme.PRIMARY, color="#FFFFFF",
                                                   shape=ft.RoundedRectangleBorder(radius=8))),
                ])

        self.page.update()

    def _create_new_plan_from_fund(self):
        """بستن دیالوگ صندوق و باز کردن فرم ایجاد طرح"""
        self._fund_dlg.open = False
        self.page.update()
        # تغییر به تب طرح‌ها و باز کردن فرم
        self.current_tab = "plans"
        self._show_plan_form()

    def _show_plan_form(self, plan=None):
        is_edit = plan is not None
        title_field = ft.TextField(label="عنوان طرح", value=plan.get(
            "title", "") if plan else "", border_radius=10, bgcolor="#FFFFFF")
        target_field = ft.TextField(label="مبلغ هدف (تومان)", value=str(int(float(plan.get("target_amount", 0)))) if plan and plan.get(
            "target_amount") else "", border_radius=10, bgcolor="#FFFFFF", keyboard_type=ft.KeyboardType.NUMBER)
        desc_field = ft.TextField(label="توضیحات", value=plan.get(
            "description", "") if plan else "", border_radius=10, bgcolor="#FFFFFF", max_lines=3, multiline=True)
        msg = ft.Text("", color=AppTheme.ERROR, size=12)

        scrollable_content = ft.ListView(
            controls=[
                title_field,
                ft.Container(height=10),
                target_field,
                ft.Container(height=10),
                desc_field,
                ft.Container(height=10),
                msg,
            ],
            height=350,
            spacing=0,
        )

        def save(e):
            if not title_field.value:
                msg.value = "عنوان الزامی است"
                self.page.update()
                return

            data = {
                "title": title_field.value,
                "description": desc_field.value,
                "target_amount": target_field.value if target_field.value else None
            }

            if is_edit:
                data["id"] = plan.get("id")
                result = api.put("admin/financial/plans_crud.php", data)
            else:
                result = api.post("admin/financial/plans_crud.php", data)

            if result.get("message") or result.get("success"):
                dlg.open = False
                self.page.update()
                self._show_success(
                    "طرح ویرایش شد" if is_edit else "طرح ایجاد شد")
                self._reload()
            else:
                msg.value = result.get("error", "خطا در ذخیره طرح")
                self.page.update()

        def close(e):
            dlg.open = False
            self.page.update()

        dlg = ft.AlertDialog(
            title=ft.Text("ویرایش طرح" if is_edit else "افزودن طرح", font_family="Vazir",
                          weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
            content=ft.Container(
                content=scrollable_content,
                width=320,
                padding=5,
            ),
            actions=[ft.TextButton("انصراف", on_click=close),
                     ft.Button("ذخیره", on_click=save, style=ft.ButtonStyle(bgcolor=AppTheme.PRIMARY, color="#FFFFFF"))],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.show_dialog(dlg)

    def _delete_plan(self, plan: dict):
        def confirm(e):
            for don in self.all_donations:
                if don.get("plan_id") == plan.get("id") and don.get("status") == "pending":
                    api.post("admin/financial/approve.php",
                             {"id": don.get("id"), "action": "reject"})
            api.delete("admin/financial/plans_crud.php",
                       {"id": plan.get("id")})
            dlg.open = False
            self.page.update()
            self._show_success("طرح و تراکنش‌های در انتظار آن حذف شدند")
            self._reload()

        def close(e):
            dlg.open = False
            self.page.update()

        dlg = ft.AlertDialog(
            title=ft.Text("حذف طرح", font_family="Vazir",
                          weight=ft.FontWeight.BOLD),
            content=ft.Text(
                f"آیا از حذف «{plan.get('title', '')}» و تراکنش‌های در انتظار آن اطمینان دارید؟", font_family="Vazir"),
            actions=[ft.TextButton("انصراف", on_click=close),
                     ft.Button("حذف", on_click=confirm, style=ft.ButtonStyle(bgcolor=AppTheme.ERROR, color="#FFFFFF"))],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.show_dialog(dlg)

    def _approve(self, don: dict):
        result = api.post("admin/financial/approve.php",
                          {"id": don.get("id"), "action": "approve"})

        if result.get("excess_amount", 0) > 0:
            approved = persian_numbers(
                f"{int(result['approved_amount']):,}")
            excess = persian_numbers(f"{int(result['excess_amount']):,}")
            msg = f"تأیید شد. {approved} تومان به طرح اضافه و {excess} تومان به صندوق مسجد واریز شد."
        else:
            msg = "تأیید شد. در صورت تکمیل طرح، مبلغ مازاد به صندوق مسجد واریز خواهد شد."

        self._show_success(msg)
        self._reload()

    def _reject(self, don: dict):
        api.post("admin/financial/approve.php",
                 {"id": don.get("id"), "action": "reject"})
        self._show_success("کمک رد شد")
        self._reload()

    def _view_receipt(self, url: str):
        if url:
            full_url = f"http://enayatzare98.ir/{url}"
            asyncio.create_task(self.page.launch_url(full_url))

    def _show_success(self, msg: str):
        snack = ft.SnackBar(
            ft.Text(f"✅ {msg}", font_family="Vazir"), bgcolor=AppTheme.PRIMARY)
        self.page.overlay.append(snack)
        snack.open = True
        self.page.update()
        import time
        time.sleep(2)

    def _reload(self):
        self.page.clean()
        self.page.add(self.build())
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
