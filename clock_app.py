import os
import json
import sys
import time
import tkinter as tk
from tkinter import colorchooser, filedialog

try:
    from PIL import Image, ImageTk
except ImportError:
    Image = None
    ImageTk = None

APP_VERSION = 'V0.8'
CONFIG_FILENAME = 'user_state.json'

# ── Dark-themed dialog helpers ──────────────────────────────────────────────


def _center_dialog(dialog: tk.Toplevel, parent: tk.Tk) -> None:
    dialog.update_idletasks()
    pw, ph = parent.winfo_width(), parent.winfo_height()
    px, py = parent.winfo_rootx(), parent.winfo_rooty()
    dw = dialog.winfo_reqwidth()
    dh = dialog.winfo_reqheight()
    dialog.geometry(f'+{px + (pw - dw) // 2}+{py + (ph - dh) // 2}')


def dark_messagebox(
    parent: tk.Tk, title: str, message: str, *,
    error: bool = False, ok_text: str = 'OK',
) -> None:
    d = tk.Toplevel(parent)
    d.title(title)
    d.configure(bg='#0d0d18')
    d.resizable(False, False)
    d.attributes('-topmost', True)
    d.transient(parent)

    body = tk.Frame(d, bg='#0d0d18')
    body.pack(padx=28, pady=22)

    accent = '#e05555' if error else '#6366f1'
    tk.Frame(body, bg=accent, height=3).pack(fill='x', pady=(0, 14))

    tk.Label(
        body, text=message, fg='#d0d0e0', bg='#0d0d18',
        font=('Segoe UI', 11), justify='left', wraplength=440,
    ).pack(pady=(0, 16))

    btn = tk.Button(
        body, text=ok_text, command=d.destroy,
        font=('Segoe UI', 10, 'bold'), fg='#ffffff', bg=accent,
        activeforeground='#ffffff', activebackground='#818cf8',
        relief='flat', padx=28, pady=7, cursor='hand2',
    )
    btn.pack()
    btn.focus_set()

    _center_dialog(d, parent)
    d.grab_set()
    d.bind('<Return>', lambda _e: d.destroy())
    d.bind('<Escape>', lambda _e: d.destroy())
    parent.wait_window(d)


def dark_askstring(
    parent: tk.Tk, title: str, prompt: str, *,
    initialvalue: str = '', ok_text: str = 'OK', cancel_text: str = 'Cancel',
) -> str | None:
    d = tk.Toplevel(parent)
    d.title(title)
    d.configure(bg='#0d0d18')
    d.resizable(False, False)
    d.attributes('-topmost', True)
    d.transient(parent)
    result: list[str | None] = [None]

    body = tk.Frame(d, bg='#0d0d18')
    body.pack(padx=28, pady=22)

    tk.Frame(body, bg='#6366f1', height=3).pack(fill='x', pady=(0, 14))

    tk.Label(
        body, text=prompt, fg='#c8c8e0', bg='#0d0d18', font=('Segoe UI', 11),
    ).pack(anchor='w', pady=(0, 10))

    entry = tk.Entry(
        body, font=('Segoe UI', 13), fg='#e0e0f0', bg='#1a1a28',
        insertbackground='#e0e0f0', relief='flat', bd=0,
        highlightthickness=1, highlightbackground='#2e2e48', highlightcolor='#6366f1',
    )
    entry.insert(0, initialvalue)
    entry.pack(fill='x', ipady=7, pady=(0, 16))
    entry.select_range(0, tk.END)
    entry.focus_set()

    def _ok() -> None:
        result[0] = entry.get()
        d.destroy()

    def _cancel() -> None:
        result[0] = None
        d.destroy()

    row = tk.Frame(body, bg='#0d0d18')
    row.pack(fill='x')
    tk.Button(
        row, text=cancel_text, command=_cancel,
        font=('Segoe UI', 10), fg='#a0a0b8', bg='#1a1a28',
        activeforeground='#ffffff', activebackground='#282844',
        relief='flat', padx=14, pady=6, cursor='hand2',
    ).pack(side='right', padx=(6, 0))
    tk.Button(
        row, text=ok_text, command=_ok,
        font=('Segoe UI', 10, 'bold'), fg='#ffffff', bg='#6366f1',
        activeforeground='#ffffff', activebackground='#818cf8',
        relief='flat', padx=22, pady=6, cursor='hand2',
    ).pack(side='right')

    _center_dialog(d, parent)
    d.grab_set()
    d.bind('<Return>', lambda _e: _ok())
    d.bind('<Escape>', lambda _e: _cancel())
    d.protocol('WM_DELETE_WINDOW', _cancel)
    parent.wait_window(d)
    return result[0]


def dark_askinteger(
    parent: tk.Tk, title: str, prompt: str, *,
    minvalue: int | None = None, initialvalue: str = '',
    ok_text: str = 'OK', cancel_text: str = 'Cancel',
) -> int | None:
    d = tk.Toplevel(parent)
    d.title(title)
    d.configure(bg='#0d0d18')
    d.resizable(False, False)
    d.attributes('-topmost', True)
    d.transient(parent)
    result: list[int | None] = [None]

    body = tk.Frame(d, bg='#0d0d18')
    body.pack(padx=28, pady=22)

    tk.Frame(body, bg='#6366f1', height=3).pack(fill='x', pady=(0, 14))

    tk.Label(
        body, text=prompt, fg='#c8c8e0', bg='#0d0d18', font=('Segoe UI', 11),
    ).pack(anchor='w', pady=(0, 10))

    entry = tk.Entry(
        body, font=('Segoe UI', 13), fg='#e0e0f0', bg='#1a1a28',
        insertbackground='#e0e0f0', relief='flat', bd=0,
        highlightthickness=1, highlightbackground='#2e2e48', highlightcolor='#6366f1',
    )
    entry.insert(0, str(initialvalue))
    entry.pack(fill='x', ipady=7, pady=(0, 6))
    entry.select_range(0, tk.END)
    entry.focus_set()

    error_lbl = tk.Label(
        body, text='', fg='#e05555', bg='#0d0d18', font=('Segoe UI', 9),
    )
    error_lbl.pack(anchor='w', pady=(0, 6))

    def _ok() -> None:
        raw = entry.get().strip()
        is_cn = any(ord(c) > 127 for c in ok_text)
        try:
            val = int(raw)
        except ValueError:
            error_lbl.configure(text='请输入有效整数' if is_cn else 'Please enter a valid integer')
            entry.configure(highlightbackground='#e05555', highlightcolor='#e05555')
            return
        if minvalue is not None and val < minvalue:
            error_lbl.configure(text=f'最小值为 {minvalue}' if is_cn else f'Minimum value is {minvalue}')
            entry.configure(highlightbackground='#e05555', highlightcolor='#e05555')
            return
        result[0] = val
        d.destroy()

    def _cancel() -> None:
        result[0] = None
        d.destroy()

    row = tk.Frame(body, bg='#0d0d18')
    row.pack(fill='x', pady=(6, 0))
    tk.Button(
        row, text=cancel_text, command=_cancel,
        font=('Segoe UI', 10), fg='#a0a0b8', bg='#1a1a28',
        activeforeground='#ffffff', activebackground='#282844',
        relief='flat', padx=14, pady=6, cursor='hand2',
    ).pack(side='right', padx=(6, 0))
    tk.Button(
        row, text=ok_text, command=_ok,
        font=('Segoe UI', 10, 'bold'), fg='#ffffff', bg='#6366f1',
        activeforeground='#ffffff', activebackground='#818cf8',
        relief='flat', padx=22, pady=6, cursor='hand2',
    ).pack(side='right')

    _center_dialog(d, parent)
    d.grab_set()
    d.bind('<Return>', lambda _e: _ok())
    d.bind('<Escape>', lambda _e: _cancel())
    d.protocol('WM_DELETE_WINDOW', _cancel)
    parent.wait_window(d)
    return result[0]


class FullscreenClockApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.lang = 'zh'
        self.root.title(self.app_title())
        self.root.geometry('1280x720')
        self.root.minsize(900, 560)
        self.root.attributes('-fullscreen', False)
        self.is_fullscreen = False
        self.root.configure(bg='#080811')

        self.running = True
        self.paused = False
        self.mode = 'clock'  # clock | countup | countdown

        self.count_start = None
        self.countdown_total = 0
        self.pause_started_at = None
        self.paused_duration = 0
        self.clock_offset_seconds = 0

        self.custom_text = '全屏桌面时钟'
        self.text_color = '#FFFFFF'
        self.desc_color = '#9494b8'
        self.time_font_size = 120
        self.text_font_size = 32

        self.bg_path = None
        self.bg_color = '#080811'
        self.bg_photo = None
        self.bg_scale_percent = 100
        self.time_font_family = 'Segoe UI'
        self.time_bold = False
        self.time_shadow = True
        self.load_user_state()

        self.style_panel = None
        self.time_size_scale = None
        self.text_size_scale = None
        self.bg_size_scale = None
        self.r_scale = None
        self.g_scale = None
        self.b_scale = None
        self._style_swatch = None
        self.toolbar_visible = True
        self._toolbar_anim_id = None
        self.mode_label = None
        self._last_time_key = None
        self._last_desc_key = None
        self._last_status_key = None
        self._last_mode_label_text = None
        self._toolbar_buttons: list[tk.Button] = []
        self._last_size = (0, 0)

        self.canvas = tk.Canvas(self.root, highlightthickness=0, bd=0)
        self.canvas.pack(fill='both', expand=True)

        time_font = self._time_font()
        shadow_state = 'normal' if self.time_shadow else 'hidden'
        self.time_shadow_item = self.canvas.create_text(
            0,
            0,
            text='00:00:00',
            fill='#000000',
            font=time_font,
            anchor='center',
            state=shadow_state,
        )
        self.time_item = self.canvas.create_text(
            0,
            0,
            text='00:00:00',
            fill=self.text_color,
            font=time_font,
            anchor='center',
        )
        self.desc_item = self.canvas.create_text(
            0,
            0,
            text=self.custom_text,
            fill=self.desc_color,
            font=('Segoe UI', self.text_font_size),
            anchor='center',
        )
        self.status_item = self.canvas.create_text(
            28,
            24,
            text=self.version_text(),
            fill='#5a5a7a',
            font=('Segoe UI', 13),
            anchor='nw',
        )

        # Frosted-glass toolbar: translucent-like border + dark inner panel.
        self.controls_container = tk.Frame(
            self.root,
            bg='#2e2e48',
            bd=0,
            highlightthickness=0,
        )
        self.controls_container_inner = tk.Frame(
            self.controls_container,
            bg='#14141e',
            bd=0,
            highlightthickness=0,
        )
        self.controls_container_inner.pack(padx=1, pady=1)
        self.controls = tk.Frame(self.controls_container_inner, bg='#14141e', bd=0, highlightthickness=0)
        self.controls.pack(padx=4, pady=3)
        self.controls_container.place(relx=0.5, rely=1.0, anchor='s', y=-16)
        self._toolbar_target_y = -16
        self.arrow_button = tk.Button(
            self.root,
            text='▲',
            command=lambda: self.set_toolbar_visible(True),
            font=('Segoe UI', 10),
            fg='#b0b0c8',
            bg='#14141e',
            activeforeground='#ffffff',
            activebackground='#282844',
            relief='flat',
            borderwidth=0,
            padx=12,
            pady=3,
            cursor='hand2',
        )
        self.build_controls()

        self.bind_hotkeys()
        self.root.bind('<Configure>', self.on_resize)
        self.root.bind('<Escape>', lambda _: self.toggle_fullscreen() if self.is_fullscreen else None)

        self.redraw_background()
        self.apply_time_font()
        self.update_ui()

    def app_title(self) -> str:
        if self.lang == 'en':
            return f'Fullscreen Desktop Clock {APP_VERSION}'
        return f'全屏桌面时钟 {APP_VERSION}'

    def version_text(self) -> str:
        if self.lang == 'en':
            return f'Version: {APP_VERSION}'
        return f'版本: {APP_VERSION}'

    def t(self, key: str) -> str:
        zh = {
            'mode_prefix': '模式',
            'mode_clock': '当前时间',
            'mode_countup': '正计时',
            'mode_countdown': '倒计时',
            'state_running': '运行',
            'state_paused': '暂停',
            'state_done': '结束',
            'help': '帮助',
            'bg_image': '背景图',
            'bg_color': '背景色',
            'text': '文字',
            'desc_color': '文字颜色',
            'mode': '模式',
            'set_time': '设时间',
            'style': '样式',
            'reset': '重置',
            'pause_resume': '暂停/继续',
            'fullscreen': '全屏',
            'exit_fullscreen': '退出全屏',
            'hide_bar': '隐藏栏',
            'quit': '退出',
            'lang_switch': 'EN',
            'style_title': '样式滑块',
            'style_header': '字号 / 字体颜色(RGB) / 背景缩放',
            'time_size': '时间字号',
            'text_size': '文字字号',
            'bg_scale': '背景缩放(%)',
            'color_preview': '颜色预览',
            'close': '关闭',
            'time_font_label': '时间字体',
            'time_bold_label': '粗体',
            'time_shadow_label': '投影',
            'desc_color_label': '文字颜色',
            'desc_color_pick': '选择',
            'desc_color_reset': '还原',
            'dialog_ok': '确定',
            'dialog_cancel': '取消',
            'dialog_countdown_prompt': '请输入倒计时秒数:',
            'dialog_countup_prompt': '输入起始秒数:',
            'dialog_set_time_prompt': '输入显示时间 (HH:MM:SS):',
            'dialog_time_error': '格式错误',
            'dialog_time_error_msg': '请使用 HH:MM:SS，例如 08:30:00',
            'dialog_custom_text_prompt': '请输入要显示的文字:',
            'dialog_bg_error': '背景错误',
            'dialog_bg_pillow_msg': '当前环境未安装 Pillow，仅支持 png/gif/ppm/pgm。\n请安装 Pillow 后使用 jpg/jpeg/bmp。',
            'dialog_bg_load_fail': '加载背景失败',
            'dialog_bg_invalid_size': '背景图片尺寸无效',
            'dialog_bg_file_title': '选择背景图片',
            'dialog_bg_color_title': '选择背景颜色',
            'help_title': '帮助',
            'help_text': (
                f'当前版本: {APP_VERSION}\n\n'
                '底部按键可直接操作全部功能。\n\n'
                '快捷键:\n'
                'H 帮助\n'
                'B 背景图片\n'
                'C 背景颜色\n'
                'T 自定义文字\n'
                'L 文字颜色\n'
                'F 打开样式滑块（字号/颜色/背景缩放）\n'
                'M 切换模式\n'
                'R 重置计时\n'
                'S 暂停/继续\n'
                '底栏可点“隐藏栏”，隐藏后只保留箭头\n'
                'Esc 退出全屏\n'
                'Q 退出程序\n'
            ),
        }
        en = {
            'mode_prefix': 'Mode',
            'mode_clock': 'Clock',
            'mode_countup': 'Count Up',
            'mode_countdown': 'Count Down',
            'state_running': 'Running',
            'state_paused': 'Paused',
            'state_done': 'Done',
            'help': 'Help',
            'bg_image': 'Image',
            'bg_color': 'Color',
            'text': 'Text',
            'desc_color': 'Text Clr',
            'mode': 'Mode',
            'set_time': 'Set Time',
            'style': 'Style',
            'reset': 'Reset',
            'pause_resume': 'Pause/Resume',
            'fullscreen': 'Fullscreen',
            'exit_fullscreen': 'Exit Fullscreen',
            'hide_bar': 'Hide Bar',
            'quit': 'Quit',
            'lang_switch': '中文',
            'style_title': 'Style Controls',
            'style_header': 'Font Size / RGB Color / Background Scale',
            'time_size': 'Time Size',
            'text_size': 'Text Size',
            'bg_scale': 'Background Scale (%)',
            'color_preview': 'Color Preview',
            'close': 'Close',
            'time_font_label': 'Time Font',
            'time_bold_label': 'Bold',
            'time_shadow_label': 'Shadow',
            'desc_color_label': 'Text Color',
            'desc_color_pick': 'Pick',
            'desc_color_reset': 'Reset',
            'dialog_ok': 'OK',
            'dialog_cancel': 'Cancel',
            'dialog_countdown_prompt': 'Enter countdown seconds:',
            'dialog_countup_prompt': 'Enter starting seconds:',
            'dialog_set_time_prompt': 'Enter display time (HH:MM:SS):',
            'dialog_time_error': 'Format Error',
            'dialog_time_error_msg': 'Please use HH:MM:SS, e.g. 08:30:00',
            'dialog_custom_text_prompt': 'Enter text to display:',
            'dialog_bg_error': 'Background Error',
            'dialog_bg_pillow_msg': 'Pillow is not installed. Only png/gif/ppm/pgm are supported.\nPlease install Pillow for jpg/jpeg/bmp support.',
            'dialog_bg_load_fail': 'Failed to load background',
            'dialog_bg_invalid_size': 'Invalid background image size',
            'dialog_bg_file_title': 'Select Background Image',
            'dialog_bg_color_title': 'Select Background Color',
            'help_title': 'Help',
            'help_text': (
                f'Current Version: {APP_VERSION}\n\n'
                'Use the bottom toolbar for all features.\n\n'
                'Shortcuts:\n'
                'H Help\n'
                'B Background Image\n'
                'C Background Color\n'
                'T Custom Text\n'
                'L Text Color\n'
                'F Style Controls (font/color/scale)\n'
                'M Switch Mode\n'
                'R Reset Timer\n'
                'S Pause/Resume\n'
                'Use "Hide Bar" to collapse toolbar to one arrow\n'
                'Esc Exit Fullscreen\n'
                'Q Quit\n'
            ),
        }
        table = en if self.lang == 'en' else zh
        return table[key]

    def build_controls(self) -> None:
        for widget in self.controls.winfo_children():
            widget.destroy()

        self.mode_label = tk.Label(
            self.controls,
            text=f"{self.t('mode_prefix')}: {self.t('mode_clock')}",
            font=('Segoe UI', 10, 'bold'),
            fg='#d8d8f0',
            bg='#14141e',
            padx=8,
            pady=4,
        )
        self.mode_label.grid(row=0, column=0, padx=(2, 6))

        items = [
            (self.t('help'), self.show_help),
            (self.t('bg_image'), self.select_background_image),
            (self.t('bg_color'), self.select_background_color),
            (self.t('text'), self.edit_custom_text),
            (self.t('desc_color'), self.edit_desc_color),
            (self.t('mode'), self.switch_mode),
            (self.t('set_time'), self.set_time_value),
            (self.t('style'), self.open_style_panel),
            (self.t('reset'), self.reset_mode_timer),
            (self.t('pause_resume'), self.toggle_pause),
            (self.t('fullscreen'), self.toggle_fullscreen),
            (self.t('hide_bar'), lambda: self.set_toolbar_visible(False)),
            (self.t('lang_switch'), self.toggle_language),
            (self.t('quit'), self.quit_app),
        ]
        self._toolbar_buttons.clear()
        for i, (label, cmd) in enumerate(items):
            btn = tk.Button(
                self.controls,
                text=label,
                command=cmd,
                font=('Segoe UI', 10),
                fg='#c8c8e0',
                bg='#1a1a28',
                activeforeground='#ffffff',
                activebackground='#282844',
                relief='flat',
                borderwidth=0,
                padx=10,
                pady=4,
                cursor='hand2',
            )
            btn.grid(row=0, column=i + 1, padx=1)
            self._toolbar_buttons.append(btn)

    def toggle_language(self) -> None:
        self.lang = 'en' if self.lang == 'zh' else 'zh'
        self.root.title(self.app_title())
        self._last_status_key = None
        self._last_mode_label_text = None
        if self.style_panel and self.style_panel.winfo_exists():
            self.style_panel.destroy()
            self.style_panel = None

        toolbar_keys = [
            'help', 'bg_image', 'bg_color', 'text', 'desc_color', 'mode', 'set_time',
            'style', 'reset', 'pause_resume', 'fullscreen', 'hide_bar', 'lang_switch', 'quit',
        ]
        for btn, key in zip(self._toolbar_buttons, toolbar_keys):
            if key == 'fullscreen':
                continue  # handled by _update_fullscreen_btn
            btn.configure(text=self.t(key))
        self._update_fullscreen_btn()

        if self.mode_label is not None:
            _, mode_text = self.get_display_time()
            mode_label_text = f"{self.t('mode_prefix')}: {mode_text}"
            self.mode_label.configure(text=mode_label_text)
            self._last_mode_label_text = mode_label_text

    def set_toolbar_visible(self, visible: bool) -> None:
        self.toolbar_visible = visible
        if hasattr(self, '_toolbar_anim_id') and self._toolbar_anim_id:
            self.root.after_cancel(self._toolbar_anim_id)
            self._toolbar_anim_id = None

        if visible:
            self._animate_toolbar_in(0)
        else:
            self._animate_toolbar_out(0)

    def _animate_toolbar_in(self, step: int) -> None:
        total_steps = 10
        if step == 0:
            self.controls_container.place(relx=0.5, rely=1.0, anchor='s', y=80)
        if step < total_steps:
            t = step / (total_steps - 1)
            eased = 1 - (1 - t) ** 3
            y = 80 - int(96 * eased)
            self.controls_container.place(relx=0.5, rely=1.0, anchor='s', y=y)
            self.arrow_button.place_forget()
            self._toolbar_anim_id = self.root.after(16, lambda: self._animate_toolbar_in(step + 1))
        else:
            self.controls_container.place(relx=0.5, rely=1.0, anchor='s', y=-16)
            self._toolbar_target_y = -16

    def _animate_toolbar_out(self, step: int) -> None:
        total_steps = 10
        if step == 0:
            self.arrow_button.place(relx=0.5, rely=1.0, anchor='s', y=80)
        if step < total_steps:
            t = step / (total_steps - 1)
            eased = t ** 3
            bar_y = -16 + int(96 * eased)
            arrow_y = 80 - int(88 * eased)
            self.controls_container.place(relx=0.5, rely=1.0, anchor='s', y=bar_y)
            self.arrow_button.place(relx=0.5, rely=1.0, anchor='s', y=arrow_y)
            self._toolbar_anim_id = self.root.after(16, lambda: self._animate_toolbar_out(step + 1))
        else:
            self.controls_container.place_forget()
            self.arrow_button.place(relx=0.5, rely=1.0, anchor='s', y=-8)
            self._toolbar_target_y = -16

    def bind_hotkeys(self) -> None:
        self.root.bind('h', lambda _: self.show_help())
        self.root.bind('H', lambda _: self.show_help())

        self.root.bind('b', lambda _: self.select_background_image())
        self.root.bind('B', lambda _: self.select_background_image())

        self.root.bind('c', lambda _: self.select_background_color())
        self.root.bind('C', lambda _: self.select_background_color())

        self.root.bind('t', lambda _: self.edit_custom_text())
        self.root.bind('T', lambda _: self.edit_custom_text())

        self.root.bind('l', lambda _: self.edit_desc_color())
        self.root.bind('L', lambda _: self.edit_desc_color())

        self.root.bind('f', lambda _: self.open_style_panel())
        self.root.bind('F', lambda _: self.open_style_panel())

        self.root.bind('m', lambda _: self.switch_mode())
        self.root.bind('M', lambda _: self.switch_mode())

        self.root.bind('r', lambda _: self.reset_mode_timer())
        self.root.bind('R', lambda _: self.reset_mode_timer())

        self.root.bind('s', lambda _: self.toggle_pause())
        self.root.bind('S', lambda _: self.toggle_pause())

        self.root.bind('q', lambda _: self.quit_app())
        self.root.bind('Q', lambda _: self.quit_app())

    def show_help(self) -> None:
        dark_messagebox(self.root, self.t('help_title'), self.t('help_text'),
                        ok_text=self.t('dialog_ok'))

    def toggle_fullscreen(self) -> None:
        self.is_fullscreen = not self.is_fullscreen
        self.root.attributes('-fullscreen', self.is_fullscreen)
        self._update_fullscreen_btn()

    def _update_fullscreen_btn(self) -> None:
        if self._toolbar_buttons and len(self._toolbar_buttons) > 10:
            btn = self._toolbar_buttons[10]
            if self.is_fullscreen:
                btn.configure(text=self.t('exit_fullscreen'))
            else:
                btn.configure(text=self.t('fullscreen'))

    def quit_app(self) -> None:
        self.running = False
        self.save_user_state()
        self.root.destroy()

    def runtime_dir(self) -> str:
        if getattr(sys, 'frozen', False):
            return os.path.dirname(sys.executable)
        return os.path.dirname(os.path.abspath(__file__))

    def state_path(self) -> str:
        return os.path.join(self.runtime_dir(), CONFIG_FILENAME)

    def load_user_state(self) -> None:
        path = self.state_path()
        if not os.path.exists(path):
            return
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            text = data.get('custom_text')
            image_path = data.get('bg_path')
            if isinstance(text, str):
                self.custom_text = text
            if isinstance(image_path, str) and os.path.exists(image_path):
                self.bg_path = image_path
            if isinstance(data.get('time_font_family'), str):
                self.time_font_family = data['time_font_family']
            if isinstance(data.get('time_bold'), bool):
                self.time_bold = data['time_bold']
            if isinstance(data.get('time_shadow'), bool):
                self.time_shadow = data['time_shadow']
            if isinstance(data.get('desc_color'), str) and data['desc_color'].startswith('#'):
                self.desc_color = data['desc_color']
        except Exception as e:
            print(f"[Full-Screen-Clock] WARNING: Failed to load user_state.json: {e}",
                  file=sys.__stdout__ if sys.__stdout__ else sys.stderr)
            return

    def save_user_state(self) -> None:
        path = self.state_path()
        data = {
            'custom_text': self.custom_text,
            'bg_path': self.bg_path,
            'time_font_family': self.time_font_family,
            'time_bold': self.time_bold,
            'time_shadow': self.time_shadow,
            'desc_color': self.desc_color,
        }
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception:
            return

    def set_mode(self, mode: str) -> None:
        self.mode = mode
        self.paused = False
        self.paused_duration = 0
        self.pause_started_at = None

        if mode == 'countdown':
            seconds = dark_askinteger(self.root, self.t('mode_countdown'),
                                       self.t('dialog_countdown_prompt'),
                                       minvalue=1, ok_text=self.t('dialog_ok'),
                                       cancel_text=self.t('dialog_cancel'))
            if seconds is None:
                self.mode = 'clock'
                self.count_start = None
                return
            self.countdown_total = seconds
            self.count_start = time.time()
        elif mode == 'countup':
            self.count_start = time.time()
        else:
            self.count_start = None

    def switch_mode(self) -> None:
        if self.mode == 'clock':
            self.set_mode('countup')
        elif self.mode == 'countup':
            self.set_mode('countdown')
        else:
            self.set_mode('clock')

    def set_time_value(self) -> None:
        if self.mode == 'clock':
            value = dark_askstring(self.root, self.t('set_time'),
                                    self.t('dialog_set_time_prompt'),
                                    ok_text=self.t('dialog_ok'),
                                    cancel_text=self.t('dialog_cancel'))
            if not value:
                return
            try:
                parts = value.split(':')
                if len(parts) != 3:
                    raise ValueError
                hh, mm, ss = [int(x) for x in parts]
                if not (0 <= hh <= 23 and 0 <= mm <= 59 and 0 <= ss <= 59):
                    raise ValueError
                now = time.localtime()
                now_seconds = now.tm_hour * 3600 + now.tm_min * 60 + now.tm_sec
                target_seconds = hh * 3600 + mm * 60 + ss
                self.clock_offset_seconds = target_seconds - now_seconds
            except ValueError:
                dark_messagebox(self.root, self.t('dialog_time_error'),
                                self.t('dialog_time_error_msg'), error=True,
                                ok_text=self.t('dialog_ok'))
            return

        if self.mode == 'countup':
            seconds = dark_askinteger(self.root, self.t('mode_countup'),
                                       self.t('dialog_countup_prompt'),
                                       minvalue=0, ok_text=self.t('dialog_ok'),
                                       cancel_text=self.t('dialog_cancel'))
            if seconds is None:
                return
            self.count_start = time.time() - seconds
            self.paused = False
            self.paused_duration = 0
            self.pause_started_at = None
            return

        seconds = dark_askinteger(self.root, self.t('mode_countdown'),
                                   self.t('dialog_countdown_prompt'),
                                   minvalue=1, ok_text=self.t('dialog_ok'),
                                   cancel_text=self.t('dialog_cancel'))
        if seconds is None:
            return
        self.countdown_total = seconds
        self.count_start = time.time()
        self.paused = False
        self.paused_duration = 0
        self.pause_started_at = None

    def open_style_panel(self) -> None:
        if self.style_panel and self.style_panel.winfo_exists():
            self.style_panel.lift()
            self.style_panel.focus_force()
            return

        panel = tk.Toplevel(self.root)
        panel.title(self.t('style_title'))
        panel.geometry('420x580')
        panel.resizable(False, False)
        panel.configure(bg='#0d0d18')
        panel.attributes('-topmost', True)

        self.style_panel = panel

        header = tk.Label(panel, text=self.t('style_header'), fg='#e0e0f0', bg='#0d0d18', font=('Segoe UI', 12, 'bold'))
        header.pack(anchor='w', padx=16, pady=(14, 8))

        self.time_size_scale = self._create_scale(panel, self.t('time_size'), 24, 240, self.time_font_size, self._apply_style)
        self.text_size_scale = self._create_scale(panel, self.t('text_size'), 12, 120, self.text_font_size, self._apply_style)
        self.bg_size_scale = self._create_scale(panel, self.t('bg_scale'), 20, 300, self.bg_scale_percent, self._apply_style)

        # ── Font family ──
        tk.Label(panel, text=self.t('time_font_label'), fg='#c8c8e0', bg='#0d0d18',
                 font=('Segoe UI', 10)).pack(anchor='w', padx=16, pady=(8, 4))

        fonts_row = tk.Frame(panel, bg='#0d0d18')
        fonts_row.pack(fill='x', padx=16, pady=(0, 4))
        available_fonts = ['Segoe UI', 'Microsoft YaHei', 'Consolas', 'Cascadia Mono',
                           'Arial', 'Georgia', 'Times New Roman', 'Impact', 'Courier New']
        self._font_var = tk.StringVar(value=self.time_font_family)
        mb = tk.Menubutton(fonts_row, textvariable=self._font_var,
                           font=('Segoe UI', 10), fg='#e0e0f0', bg='#1a1a28',
                           activeforeground='#ffffff', activebackground='#282844',
                           relief='flat', padx=10, pady=5, cursor='hand2',
                           direction='below', indicatoron=True)
        mb.pack(side='left')
        font_menu = tk.Menu(mb, tearoff=0, font=('Segoe UI', 10),
                            bg='#1a1a28', fg='#e0e0f0',
                            activebackground='#282844', activeforeground='#ffffff')
        for fn in available_fonts:
            font_menu.add_command(
                label=fn,
                command=lambda f=fn: (self._font_var.set(f), self._apply_style()),
            )
        mb.configure(menu=font_menu)

        # ── Bold / Shadow toggles ──
        toggles_row = tk.Frame(panel, bg='#0d0d18')
        toggles_row.pack(fill='x', padx=16, pady=(6, 0))

        self._bold_var = tk.BooleanVar(value=self.time_bold)
        tk.Checkbutton(
            toggles_row, text=self.t('time_bold_label'), variable=self._bold_var,
            command=self._apply_style,
            font=('Segoe UI', 10), fg='#c8c8e0', bg='#0d0d18',
            selectcolor='#1a1a28', activebackground='#0d0d18',
            activeforeground='#ffffff',
        ).pack(side='left', padx=(0, 20))

        self._shadow_var = tk.BooleanVar(value=self.time_shadow)
        tk.Checkbutton(
            toggles_row, text=self.t('time_shadow_label'), variable=self._shadow_var,
            command=self._apply_style,
            font=('Segoe UI', 10), fg='#c8c8e0', bg='#0d0d18',
            selectcolor='#1a1a28', activebackground='#0d0d18',
            activeforeground='#ffffff',
        ).pack(side='left')

        # ── RGB ──
        r, g, b = self.hex_to_rgb(self.text_color)
        self.r_scale = self._create_scale(panel, 'R', 0, 255, r, self._apply_style)
        self.g_scale = self._create_scale(panel, 'G', 0, 255, g, self._apply_style)
        self.b_scale = self._create_scale(panel, 'B', 0, 255, b, self._apply_style)

        # ── Color preview ──
        tk.Label(panel, text=self.t('color_preview'), fg='#a0a0b8', bg='#0d0d18',
                 font=('Segoe UI', 10)).pack(anchor='w', padx=16, pady=(10, 4))
        swatch_frame = tk.Frame(panel, bg='#1a1a28', bd=0, highlightthickness=0)
        swatch_frame.pack(anchor='w', padx=16, pady=(0, 8))
        swatch = tk.Label(swatch_frame, text='        ', bg=self.text_color, relief='flat', padx=8, pady=6)
        swatch.pack(padx=2, pady=2)

        self._style_swatch = swatch
        self._apply_style()

        btn_row = tk.Frame(panel, bg='#0d0d18')
        btn_row.pack(fill='x', padx=12, pady=(4, 12))

        tk.Button(
            btn_row,
            text=self.t('close'),
            command=_on_style_panel_close,
            font=('Segoe UI', 10),
            fg='#c8c8e0',
            bg='#1a1a28',
            activeforeground='#ffffff',
            activebackground='#282844',
            relief='flat',
            padx=14,
            pady=5,
        ).pack(side='right', padx=4)

        def _on_style_panel_close() -> None:
            self._style_swatch = None
            self._font_var = None
            self._bold_var = None
            self._shadow_var = None
            self.style_panel = None
            if panel.winfo_exists():
                panel.destroy()

        panel.protocol('WM_DELETE_WINDOW', _on_style_panel_close)

    def _create_scale(
        self,
        parent: tk.Toplevel,
        label: str,
        start: int,
        end: int,
        value: int,
        on_change,
    ) -> tk.Scale:
        row = tk.Frame(parent, bg='#0d0d18')
        row.pack(fill='x', padx=12, pady=3)

        top = tk.Frame(row, bg='#0d0d18')
        top.pack(fill='x', padx=4)
        tk.Label(top, text=label, fg='#c8c8e0', bg='#0d0d18', font=('Segoe UI', 10)).pack(side='left')

        entry = tk.Entry(
            top, width=6, justify='center', font=('Segoe UI', 9),
            fg='#e0e0f0', bg='#1a1a28', insertbackground='#e0e0f0',
            relief='flat', bd=0, highlightthickness=0,
        )
        entry.pack(side='right')

        scale = tk.Scale(
            row,
            from_=start,
            to=end,
            orient='horizontal',
            showvalue=True,
            fg='#e0e0f0',
            bg='#0d0d18',
            highlightthickness=0,
            troughcolor='#1a1a28',
            activebackground='#3a3a55',
            length=370,
        )
        scale.set(value)
        scale.pack(fill='x', padx=2)

        entry.insert(0, str(value))

        def on_scale_change(v: str) -> None:
            entry.delete(0, tk.END)
            entry.insert(0, str(int(float(v))))
            on_change()

        def apply_entry(_event=None) -> None:
            raw = entry.get().strip()
            try:
                n = int(raw)
            except ValueError:
                n = int(scale.get())
            n = max(start, min(end, n))
            scale.set(n)
            entry.delete(0, tk.END)
            entry.insert(0, str(n))
            on_change()

        scale.configure(command=on_scale_change)
        entry.bind('<Return>', apply_entry)
        entry.bind('<FocusOut>', apply_entry)
        return scale

    def _apply_style(self, _event=None) -> None:
        if not all([self.time_size_scale, self.text_size_scale, self.bg_size_scale,
                     self.r_scale, self.g_scale, self.b_scale]):
            return
        self.time_font_size = int(self.time_size_scale.get())
        self.text_font_size = int(self.text_size_scale.get())
        self.bg_scale_percent = int(self.bg_size_scale.get())
        self.text_color = self.rgb_to_hex(int(self.r_scale.get()), int(self.g_scale.get()), int(self.b_scale.get()))

        if hasattr(self, '_font_var') and self._font_var is not None:
            self.time_font_family = self._font_var.get()
        if hasattr(self, '_bold_var') and self._bold_var is not None:
            self.time_bold = self._bold_var.get()
        if hasattr(self, '_shadow_var') and self._shadow_var is not None:
            self.time_shadow = self._shadow_var.get()

        if hasattr(self, '_style_swatch') and self._style_swatch is not None:
            self._style_swatch.configure(bg=self.text_color)
        self.apply_time_font()
        self.redraw_background()
        self.save_user_state()

    def _time_font(self) -> tuple:
        weight = 'bold' if self.time_bold else 'normal'
        return (self.time_font_family, self.time_font_size, weight)

    def apply_time_font(self) -> None:
        font = self._time_font()
        state = 'normal' if self.time_shadow else 'hidden'
        self.canvas.itemconfigure(self.time_shadow_item, font=font, state=state)
        self.canvas.itemconfigure(self.time_item, font=font)
        self.canvas.itemconfigure(self.desc_item, font=('Segoe UI', self.text_font_size))

    def reset_mode_timer(self) -> None:
        if self.mode in ('countup', 'countdown'):
            self.count_start = time.time()
            self.paused = False
            self.paused_duration = 0
            self.pause_started_at = None

    def toggle_pause(self) -> None:
        if self.mode not in ('countup', 'countdown'):
            return

        if not self.paused:
            self.paused = True
            self.pause_started_at = time.time()
        else:
            self.paused = False
            if self.pause_started_at is not None:
                self.paused_duration += time.time() - self.pause_started_at
            self.pause_started_at = None

    def on_resize(self, _event=None) -> None:
        new_size = (self.root.winfo_width(), self.root.winfo_height())
        if new_size == self._last_size:
            return
        self._last_size = new_size
        if hasattr(self, '_resize_after_id') and self._resize_after_id:
            self.root.after_cancel(self._resize_after_id)
        self._resize_after_id = self.root.after(100, self._flush_resize)

    def _flush_resize(self) -> None:
        self._resize_after_id = None
        self.redraw_background()
        self.position_elements()

    def select_background_image(self) -> None:
        path = filedialog.askopenfilename(
            title=self.t('dialog_bg_file_title'),
            filetypes=[('Image Files', '*.png;*.jpg;*.jpeg;*.bmp;*.gif;*.ppm;*.pgm'), ('All Files', '*.*')],
        )
        if not path:
            return

        if Image is None:
            ext = os.path.splitext(path)[1].lower()
            tk_supported = {'.png', '.gif', '.ppm', '.pgm'}
            if ext not in tk_supported:
                dark_messagebox(self.root, self.t('dialog_bg_error'),
                                self.t('dialog_bg_pillow_msg'), error=True,
                                ok_text=self.t('dialog_ok'))
                return

        self.bg_path = path
        self.save_user_state()
        self.redraw_background()

    def select_background_color(self) -> None:
        chosen = colorchooser.askcolor(title=self.t('dialog_bg_color_title'))[1]
        if not chosen:
            return
        self.bg_color = chosen
        self.bg_path = None
        self.save_user_state()
        self.redraw_background()

    def edit_custom_text(self) -> None:
        text = dark_askstring(self.root, self.t('text'),
                               self.t('dialog_custom_text_prompt'),
                               initialvalue=self.custom_text,
                               ok_text=self.t('dialog_ok'),
                               cancel_text=self.t('dialog_cancel'))
        if text is None:
            return
        self.custom_text = text
        self._last_desc_key = None
        self.save_user_state()

    def edit_desc_color(self) -> None:
        chosen = colorchooser.askcolor(title=self.t('desc_color'),
                                       initialcolor=self.desc_color)[1]
        if not chosen:
            return
        self.desc_color = chosen
        self._last_desc_key = None
        self.save_user_state()

    def redraw_background(self) -> None:
        width = max(self.root.winfo_width(), 1)
        height = max(self.root.winfo_height(), 1)

        self.canvas.configure(bg=self.bg_color)
        self.canvas.delete('bg')

        if self.bg_path:
            try:
                if Image is not None:
                    img = Image.open(self.bg_path)
                    src_w, src_h = img.size
                    if src_w <= 0 or src_h <= 0:
                        raise ValueError(self.t('dialog_bg_invalid_size'))

                    base_scale = max(width / src_w, height / src_h)
                    final_scale = base_scale * (self.bg_scale_percent / 100.0)
                    dst_w = max(int(src_w * final_scale), 1)
                    dst_h = max(int(src_h * final_scale), 1)

                    img = img.resize((dst_w, dst_h), Image.Resampling.LANCZOS)
                    self.bg_photo = ImageTk.PhotoImage(img)
                    x = (width - dst_w) // 2
                    y = (height - dst_h) // 2
                    self.canvas.create_image(x, y, image=self.bg_photo, anchor='nw', tags='bg')
                else:
                    img = tk.PhotoImage(file=self.bg_path)
                    self.bg_photo = img
                    self.canvas.create_image(width / 2, height / 2, image=self.bg_photo, anchor='center', tags='bg')
            except Exception as exc:
                self.bg_path = None
                dark_messagebox(self.root, self.t('dialog_bg_error'),
                                f'{self.t("dialog_bg_load_fail")}: {exc}', error=True,
                                ok_text=self.t('dialog_ok'))

        self.canvas.tag_lower('bg')

    def format_hms(self, total_seconds: int) -> str:
        total_seconds = max(total_seconds, 0)
        total_seconds = min(total_seconds, 359999)  # cap at 99:59:59
        h = total_seconds // 3600
        m = (total_seconds % 3600) // 60
        s = total_seconds % 60
        return f'{h:02d}:{m:02d}:{s:02d}'

    @staticmethod
    def hex_to_rgb(color: str) -> tuple[int, int, int]:
        color = color.lstrip('#')
        if len(color) != 6:
            return 255, 255, 255
        return int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16)

    @staticmethod
    def rgb_to_hex(r: int, g: int, b: int) -> str:
        return f'#{r:02X}{g:02X}{b:02X}'

    def get_display_time(self) -> tuple[str, str]:
        if self.mode == 'clock':
            ts = time.time() + self.clock_offset_seconds
            return time.strftime('%H:%M:%S', time.localtime(ts)), self.t('mode_clock')

        if self.count_start is None:
            self.count_start = time.time()

        if self.paused:
            elapsed = int((self.pause_started_at or time.time()) - self.count_start - self.paused_duration)
            state = self.t('state_paused')
        else:
            elapsed = int(time.time() - self.count_start - self.paused_duration)
            state = self.t('state_running')

        if self.mode == 'countup':
            return self.format_hms(elapsed), f"{self.t('mode_countup')} ({state})"

        remain = self.countdown_total - elapsed
        if remain <= 0:
            return '00:00:00', f"{self.t('mode_countdown')} ({self.t('state_done')})"
        return self.format_hms(remain), f"{self.t('mode_countdown')} ({state})"

    def position_elements(self) -> None:
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        shadow_offset = 3 + self.time_font_size * 0.008
        self.canvas.coords(self.time_shadow_item, width / 2 + shadow_offset, height * 0.42 + shadow_offset)
        self.canvas.coords(self.time_item, width / 2, height * 0.42)
        self.canvas.coords(self.desc_item, width / 2, height * 0.56)

    def update_ui(self) -> None:
        if not self.running:
            return

        display_time, mode_text = self.get_display_time()
        time_key = (display_time, self.text_color)
        if time_key != self._last_time_key:
            self.canvas.itemconfigure(self.time_item, text=display_time, fill=self.text_color)
            self.canvas.itemconfigure(self.time_shadow_item, text=display_time)
            self._last_time_key = time_key

        desc_key = (self.custom_text, self.desc_color)
        if desc_key != self._last_desc_key:
            self.canvas.itemconfigure(self.desc_item, text=self.custom_text, fill=self.desc_color)
            self._last_desc_key = desc_key

        status_text = self.version_text()
        if status_text != self._last_status_key:
            self.canvas.itemconfigure(self.status_item, text=status_text)
            self._last_status_key = status_text

        mode_label_text = f"{self.t('mode_prefix')}: {mode_text}"
        if self.mode_label is not None:
            if mode_label_text != self._last_mode_label_text:
                self.mode_label.configure(text=mode_label_text)
                self._last_mode_label_text = mode_label_text

        self.root.after(200, self.update_ui)


def main() -> None:
    root = tk.Tk()
    app = FullscreenClockApp(root)
    app.show_help()
    root.mainloop()


if __name__ == '__main__':
    main()