import os
import json
import flet as ft
from src.theme import AppTheme
from src.utils.formatters import persian_numbers

APP_STORAGE_DIR = os.environ.get("FLET_APP_STORAGE_DATA", ".")
STATE_FILE = os.path.join(APP_STORAGE_DIR, "tasbih_state.json")

GOLD_SOFT = "#C9A84C"
GOLD_LIGHT = "#D4AF3760"
GOLD_GLOW = "#D4AF3720"
BG_DARK = "#1A2F1E"

CUSTOM_DHIKRS = [
    "لا حول و لا قوه الا بالله",
    "استغفرالله ربی و اتوب الیه",
    "اللَّهُمَّ اجْعَلْنِی فِی دِرْعِکَ الْحَصِینَةِ الَّتِی تَجْعَلُ فِیهَا مَنْ تَشاء",
    "اللَّهُمَّ , لَکَ الْحَمْدُ وَإِلَیْکَ الْمُشْتَکَی , وَأَنْتَ الْمُسْتَعَانُ",
    "لآ اِلهَ اِلآ اَنتَ سُبحانَکَ اِنّی کُنتُ مِنَ الظالِمینَ",
    "اللهمَّ اغفِر لِلمُومِنینَ وَالمُومِنات والمُسلِمینَ وَالمُسلِمات",
    "اَمَّن یجیبُ المُضطرَّ اِذا دَعاهُ و یکشِفُ السُّوءَ",
    "اِنّی ظَلَمْتُ نَفسْی فَاغْفِرلی",
    "یا ذالجَلال وَالاکرام",
]

CHIP_DATA = [
    ("🌸 تسبیحات حضرت زهرا (س)", "fatima_zahra"),
    ("🤲 صلوات", "salawat"),
    ("📿 تسبیحات امیرالمؤمنین (ع)", "amir_momenin"),
    ("✨ شخصی‌سازی اذکار", "custom"),
]


class TasbihPage:
    def __init__(self, page: ft.Page, on_back):
        self.page = page
        self.on_back = on_back

        self.current_count = 0
        self.dhikr_type = "fatima_zahra"
        self.stage = 1
        self.target = 34
        self.dhikr_text = "الله اکبر"
        self.is_active = True
        self.custom_dhikr = CUSTOM_DHIKRS[0]

        self._load_state()

    def build(self):
        header = ft.Container(
            content=ft.Row(
                [
                    ft.IconButton(
                        icon=ft.icons.Icons.ARROW_BACK,
                        icon_color="#FFFFFF",
                        on_click=self.go_back,
                    ),
                    ft.Text(
                        "ذکر شمار",
                        size=18,
                        font_family="Vazir",
                        weight=ft.FontWeight.BOLD,
                        color="#FFFFFF",
                    ),
                ],
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.Padding(15, 35, 15, 15),
            bgcolor="#0D1B0F",
            border_radius=ft.BorderRadius(0, 0, 20, 20),
        )

        chips_row = ft.Row(
            [
                self._build_chip(label, dhikr_type)
                for label, dhikr_type in CHIP_DATA
            ],
            spacing=8,
        )
        chips_container = ft.Row(
            [chips_row],
            scroll=ft.ScrollMode.AUTO,
        )

        self.dhikr_label = ft.Text(
            value=self.dhikr_text,
            size=28,
            font_family="Vazir",
            color=GOLD_SOFT,
            text_align=ft.TextAlign.CENTER,
        )

        self.count_display = ft.Text(
            value=persian_numbers(str(self.current_count)),
            size=96,
            font_family="IranNastaliq",
            weight=ft.FontWeight.BOLD,
            color=GOLD_SOFT,
            text_align=ft.TextAlign.CENTER,
        )

        self.progress_text = ft.Text(
            value=f"{persian_numbers(str(self.current_count))} / {persian_numbers(str(self.target))}",
            size=16,
            font_family="Vazir",
            color="#FFFFFF60",
            text_align=ft.TextAlign.CENTER,
        )

        self.main_circle = ft.Container(
            content=ft.Column(
                [
                    self.count_display,
                    ft.Container(height=8),
                    self.progress_text,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=0,
            ),
            width=220,
            height=220,
            border_radius=110,
            border=ft.Border.all(2, GOLD_LIGHT),
            gradient=ft.LinearGradient(
                begin=ft.Alignment(-1, -1),
                end=ft.Alignment(1, 1),
                colors=["#152A1E", "#0D2015", "#152A1E"],
            ),
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=20,
                color=GOLD_GLOW,
            ),
            on_click=self._increment,
            ink=True,
            animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
        )

        self.progress_ring = ft.ProgressRing(
            value=self.current_count / self.target if self.target else 0,
            width=240,
            height=240,
            stroke_width=5,
            color=GOLD_LIGHT,
            bgcolor="#FFFFFF08",
        )

        circle_with_progress = ft.Stack(
            [
                ft.Container(
                    content=self.progress_ring,
                    alignment=ft.Alignment(0, 0),
                    width=240,
                    height=240,
                ),
                ft.Container(
                    content=self.main_circle,
                    alignment=ft.Alignment(0, 0),
                    width=220,
                    height=220,
                ),
            ],
            alignment=ft.Alignment(0, 0),
        )

        self.stop_btn = self._build_glass_btn(
            ft.icons.Icons.PAUSE_CIRCLE if self.is_active else ft.icons.Icons.PLAY_CIRCLE,
            "توقف" if self.is_active else "شروع",
            self._toggle_stop,
            "#EF535040" if not self.is_active else "#FFFFFF08",
        )

        controls = [
            self._build_glass_btn(ft.icons.Icons.REFRESH, "بازنشانی", self._reset, "#FFFFFF08"),
            self.stop_btn,
        ]
        if self.dhikr_type != "custom":
            controls.insert(0, self._build_glass_btn(ft.icons.Icons.SETTINGS, "هدف", self._show_target_dialog, "#FFFFFF08"))

        controls_row = ft.Row(
            controls,
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=24,
        )

        content_col = ft.Column(
            [
                ft.Container(height=10),
                chips_container,
                ft.Container(height=15),
                self.dhikr_label,
                ft.Container(height=15),
                circle_with_progress,
                ft.Container(height=30),
                controls_row,
                ft.Container(height=30),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

        scrollable = ft.ListView(
            controls=[content_col],
            expand=True,
            padding=20,
        )

        page_content = ft.Container(
            content=scrollable,
            expand=True,
            gradient=ft.LinearGradient(
                begin=ft.Alignment(0, -1),
                end=ft.Alignment(0, 1),
                colors=["#0D1B0F", "#0A1508", "#0D1B0F"],
            ),
        )

        return ft.Column([header, page_content], expand=True, spacing=0)

    def _build_chip(self, label: str, dhikr_type: str):
        is_selected = self.dhikr_type == dhikr_type
        return ft.Container(
            content=ft.Text(
                label,
                size=10,
                font_family="Vazir",
                weight=ft.FontWeight.BOLD if is_selected else ft.FontWeight.NORMAL,
                color=GOLD_SOFT if is_selected else "#FFFFFF80",
                text_align=ft.TextAlign.CENTER,
                no_wrap=True,
            ),
            padding=ft.Padding(14, 8, 14, 8),
            border_radius=20,
            border=ft.Border.all(1.5, GOLD_SOFT if is_selected else "#FFFFFF30"),
            bgcolor=BG_DARK if is_selected else "#0D1B0F",
            on_click=lambda e, t=dhikr_type: self._on_chip_click(t),
            ink=True,
        )

    def _build_glass_btn(self, icon, tooltip: str, on_click, bgcolor: str):
        return ft.IconButton(
            icon=icon,
            icon_size=26,
            icon_color=GOLD_SOFT,
            tooltip=tooltip,
            on_click=on_click,
            style=ft.ButtonStyle(
                bgcolor=bgcolor,
                shape=ft.RoundedRectangleBorder(radius=14),
                padding=10,
            ),
        )

    def _on_chip_click(self, dhikr_type: str):
        if dhikr_type == "custom":
            self.dhikr_type = "custom"
            self._reset(None)
            self._setup_dhikr()
            self._save_state()
            self.page.clean()
            self.page.add(self.build())
            self.page.update()
            self._show_custom_dialog()
        else:
            self._change_type(dhikr_type)

    def _change_type(self, dhikr_type: str):
        self.dhikr_type = dhikr_type
        self._reset(None)
        self._setup_dhikr()
        self._save_state()
        self.page.clean()
        self.page.add(self.build())
        self.page.update()

    def _setup_dhikr(self):
        if self.dhikr_type == "fatima_zahra":
            self.stage = 1
            self.target = 34
            self.dhikr_text = "الله اکبر"
        elif self.dhikr_type == "salawat":
            self.target = 100
            self.dhikr_text = "اللهم صل علی محمد و آل محمد"
        elif self.dhikr_type == "amir_momenin":
            self.stage = 1
            self.target = 10
            self.dhikr_text = "سبحان الله"
        else:
            self.target = 100
            self.dhikr_text = self.custom_dhikr
        self.current_count = 0
        self.is_active = True

    def _increment(self, e):
        if not self.is_active or self.current_count >= self.target:
            return
        self.current_count += 1
        self._update_ui()
        self._save_state()
        if self.current_count == self.target:
            self._on_complete()

    def _on_complete(self):
        if self.dhikr_type == "fatima_zahra":
            if self.stage == 1:
                self.stage = 2
                self.target = 33
                self.dhikr_text = "الحمدلله"
                self.current_count = 0
                self._show_snack(f"مرحله {persian_numbers('1')} کامل! اکنون {persian_numbers('33')} مرتبه الحمدلله")
            elif self.stage == 2:
                self.stage = 3
                self.target = 33
                self.dhikr_text = "سبحان الله"
                self.current_count = 0
                self._show_snack(f"مرحله {persian_numbers('2')} کامل! اکنون {persian_numbers('33')} مرتبه سبحان الله")
            else:
                self.is_active = False
                self._show_snack("✅ تسبیحات حضرت زهرا (س) کامل شد 🤲")
        elif self.dhikr_type == "amir_momenin":
            texts = ["سبحان الله", "الحمدلله", "الله اکبر", "لا اله الا الله"]
            if self.stage < 4:
                self.stage += 1
                self.target = 10
                self.dhikr_text = texts[self.stage - 1]
                self.current_count = 0
                self._show_snack(f"مرحله {persian_numbers(str(self.stage))} از {persian_numbers('4')}: {self.dhikr_text}")
            else:
                self.is_active = False
                self._show_snack("✅ تسبیحات امیرالمؤمنین (ع) کامل شد 🤲")
        else:
            self.is_active = False
            self._show_snack("✅ ذکر کامل شد 🤲")
        self._update_ui()
        self._save_state()

    def _reset(self, e):
        self.current_count = 0
        self.is_active = True
        if self.dhikr_type == "fatima_zahra":
            self.stage = 1
            self.target = 34
            self.dhikr_text = "الله اکبر"
        elif self.dhikr_type == "amir_momenin":
            self.stage = 1
            self.target = 10
            self.dhikr_text = "سبحان الله"
        self._update_ui()
        self._save_state()

    def _toggle_stop(self, e):
        self.is_active = not self.is_active
        self._update_ui()

    def _show_target_dialog(self, e):
        self._show_settings_dialog()

    def _show_custom_dialog(self):
        self._show_settings_dialog()

    def _show_settings_dialog(self):
        target_field = ft.TextField(
            label="تعداد هدف",
            value=persian_numbers(str(self.target)),
            keyboard_type=ft.KeyboardType.NUMBER,
            border_color=GOLD_SOFT,
            focused_border_color=GOLD_SOFT,
            bgcolor=BG_DARK,
            border_radius=10,
            color="#FFFFFF",
        )
        msg = ft.Text("", color=AppTheme.ERROR, size=12)

        dlg_content = [target_field, ft.Container(height=10)]

        if self.dhikr_type == "custom":
            dd_value = self.custom_dhikr if self.custom_dhikr in CUSTOM_DHIKRS else CUSTOM_DHIKRS[0]

            dhikr_dd = ft.Dropdown(
                label="انتخاب ذکر",
                value=dd_value,
                options=[ft.dropdown.Option(d) for d in CUSTOM_DHIKRS],
                border_color=GOLD_SOFT,
                focused_border_color=GOLD_SOFT,
                bgcolor="#FFFDE7",
                border_radius=10,
                color="#4E342E",
                text_style=ft.TextStyle(size=12, font_family="Vazir"),
            )
            dlg_content.append(dhikr_dd)
            dlg_content.append(ft.Container(height=5))

            dlg_content.append(
                ft.Text(
                    "اگر ذکر مورد نظر در لیست نیست، آن را در فیلد زیر وارد کنید:",
                    size=11,
                    font_family="Vazir",
                    color="#FFFFFF60",
                )
            )
            dlg_content.append(ft.Container(height=5))

            custom_field = ft.TextField(
                hint_text="ذکر مورد نظر را وارد کنید",
                value="" if self.custom_dhikr in CUSTOM_DHIKRS else self.custom_dhikr,
                border_color=GOLD_SOFT,
                focused_border_color=GOLD_SOFT,
                bgcolor=BG_DARK,
                border_radius=10,
                color="#FFFFFF",
                hint_style=ft.TextStyle(size=11, font_family="Vazir", color="#FFFFFF40"),
            )
            dlg_content.append(custom_field)

        dlg_content.append(msg)

        def save(e):
            try:
                new_target = int(target_field.value)
                if new_target > 0:
                    self.target = new_target
                    if self.dhikr_type == "custom":
                        if custom_field.value:
                            self.custom_dhikr = custom_field.value
                        elif dhikr_dd.value:
                            self.custom_dhikr = dhikr_dd.value
                        else:
                            self.custom_dhikr = CUSTOM_DHIKRS[0]
                        self.dhikr_text = self.custom_dhikr
                    self.current_count = 0
                    self._update_ui()
                    self._save_state()
                    dlg.open = False
                    self.page.update()
                else:
                    msg.value = "عدد باید بزرگتر از صفر باشد"
                    self.page.update()
            except:
                msg.value = "یک عدد معتبر وارد کنید"
                self.page.update()

        dlg = ft.AlertDialog(
            bgcolor="#0D1B0F",
            inset_padding=ft.Padding(0, 0, 0, 120),
            title=ft.Text(
                "تنظیمات ذکر" if self.dhikr_type == "custom" else "تنظیم هدف",
                font_family="Vazir",
                weight=ft.FontWeight.BOLD,
                color=GOLD_SOFT,
                text_align=ft.TextAlign.CENTER,
            ),
            content=ft.Column(dlg_content, width=300, height=400, scroll=ft.ScrollMode.AUTO),
            actions=[
                ft.TextButton("انصراف", on_click=lambda e: self._close_dialog(dlg),
                              style=ft.ButtonStyle(color="#FFFFFF60")),
                ft.Button("ذخیره", on_click=save,
                          style=ft.ButtonStyle(bgcolor=AppTheme.PRIMARY, color="#FFFFFF")),
            ],
            actions_alignment=ft.MainAxisAlignment.CENTER,
        )
        self.page.show_dialog(dlg)

    def _close_dialog(self, dlg):
        dlg.open = False
        self.page.update()

    def _show_snack(self, message: str):
        snack = ft.SnackBar(
            content=ft.Text(message, font_family="Vazir"),
            bgcolor=AppTheme.PRIMARY,
            duration=3000,
        )
        self.page.overlay.append(snack)
        snack.open = True
        self.page.update()

    def _update_ui(self):
        self.count_display.value = persian_numbers(str(self.current_count))
        self.dhikr_label.value = self.dhikr_text
        self.progress_text.value = f"{persian_numbers(str(self.current_count))} / {persian_numbers(str(self.target))}"
        self.progress_ring.value = self.current_count / self.target if self.target else 0
        self.count_display.color = AppTheme.PRIMARY if self.current_count >= self.target else GOLD_SOFT

        if self.is_active:
            self.stop_btn.icon = ft.icons.Icons.PAUSE_CIRCLE
            self.stop_btn.tooltip = "توقف"
            self.stop_btn.style = ft.ButtonStyle(
                bgcolor="#FFFFFF08",
                shape=ft.RoundedRectangleBorder(radius=14),
                padding=10,
            )
        else:
            self.stop_btn.icon = ft.icons.Icons.PLAY_CIRCLE
            self.stop_btn.tooltip = "شروع"
            self.stop_btn.style = ft.ButtonStyle(
                bgcolor="#EF535040",
                shape=ft.RoundedRectangleBorder(radius=14),
                padding=10,
            )

        self.page.update()

    def _load_state(self):
        try:
            if os.path.exists(STATE_FILE):
                with open(STATE_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.current_count = data.get("current_count", 0)
                    self.dhikr_type = data.get("dhikr_type", "fatima_zahra")
                    self.stage = data.get("stage", 1)
                    self.target = data.get("target", 34)
                    self.dhikr_text = data.get("dhikr_text", "الله اکبر")
                    self.is_active = data.get("is_active", True)
                    self.custom_dhikr = data.get("custom_dhikr", CUSTOM_DHIKRS[0])
        except:
            pass

    def _save_state(self):
        try:
            os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
            data = {
                "current_count": self.current_count,
                "dhikr_type": self.dhikr_type,
                "stage": self.stage,
                "target": self.target,
                "dhikr_text": self.dhikr_text,
                "is_active": self.is_active,
                "custom_dhikr": self.custom_dhikr,
            }
            with open(STATE_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except:
            pass

    def go_back(self, e):
        self.on_back()