import os
import time
import tkinter as tk
from tkinter import colorchooser, filedialog, messagebox, simpledialog

try:
    from PIL import Image, ImageTk
except ImportError:
    Image = None
    ImageTk = None

APP_VERSION = 'V0.7'


class FullscreenClockApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.lang = 'zh'
        self.root.title(self.app_title())
        self.root.geometry('1280x720')
        self.root.minsize(900, 560)
        self.root.attributes('-fullscreen', False)
        self.root.configure(bg='black')

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
        self.time_font_size = 96
        self.text_font_size = 36

        self.bg_path = None
        self.bg_color = '#000000'
        self.bg_photo = None
        self.bg_scale_percent = 100

        self.style_panel = None
        self.time_size_scale = None
        self.text_size_scale = None
        self.bg_size_scale = None
        self.r_scale = None
        self.g_scale = None
        self.b_scale = None
        self._style_swatch = None
        self.toolbar_visible = True
        self.mode_label = None

        self.canvas = tk.Canvas(self.root, highlightthickness=0, bd=0)
        self.canvas.pack(fill='both', expand=True)

        self.time_item = self.canvas.create_text(
            0,
            0,
            text='00:00:00',
            fill=self.text_color,
            font=('Segoe UI', self.time_font_size, 'bold'),
            anchor='center',
        )
        self.desc_item = self.canvas.create_text(
            0,
            0,
            text=self.custom_text,
            fill=self.text_color,
            font=('Segoe UI', self.text_font_size),
            anchor='center',
        )
        self.status_item = self.canvas.create_text(
            20,
            20,
            text=self.version_text(),
            fill=self.text_color,
            font=('Segoe UI', 18),
            anchor='nw',
        )

        # Simulated frosted-glass bar: bright border + muted inner panel.
        self.controls_container = tk.Frame(
            self.root,
            bg='#DDE6EE',
            bd=0,
            highlightthickness=1,
            highlightbackground='#FFFFFF',
        )
        self.controls = tk.Frame(self.controls_container, bg='#2A3440', bd=0, highlightthickness=0)
        self.controls.pack(padx=2, pady=2)
        self.controls_container.place(relx=0.5, rely=1.0, anchor='s', y=-12)
        self.arrow_button = tk.Button(
            self.root,
            text='▲',
            command=lambda: self.set_toolbar_visible(True),
            font=('Segoe UI', 11, 'bold'),
            fg='#FFFFFF',
            bg='#2A3440',
            activeforeground='#FFFFFF',
            activebackground='#3A4858',
            relief='flat',
            borderwidth=0,
            padx=10,
            pady=4,
            cursor='hand2',
        )
        self.build_controls()

        self.bind_hotkeys()
        self.root.bind('<Configure>', self.on_resize)
        self.root.bind('<Escape>', lambda _: self.toggle_fullscreen(False))

        self.redraw_background()
        self.update_font_sizes()
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
            'mode': '模式',
            'set_time': '设时间',
            'style': '样式',
            'reset': '重置',
            'pause_resume': '暂停/继续',
            'fullscreen': '全屏',
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
            'help_title': '帮助',
            'help_text': (
                f'当前版本: {APP_VERSION}\n\n'
                '底部按键可直接操作全部功能。\n\n'
                '快捷键:\n'
                'H 帮助\n'
                'B 背景图片\n'
                'C 背景颜色\n'
                'T 自定义文字\n'
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
            'mode': 'Mode',
            'set_time': 'Set Time',
            'style': 'Style',
            'reset': 'Reset',
            'pause_resume': 'Pause/Resume',
            'fullscreen': 'Fullscreen',
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
            'help_title': 'Help',
            'help_text': (
                f'Current Version: {APP_VERSION}\n\n'
                'Use the bottom toolbar for all features.\n\n'
                'Shortcuts:\n'
                'H Help\n'
                'B Background Image\n'
                'C Background Color\n'
                'T Custom Text\n'
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
            font=('Segoe UI', 11, 'bold'),
            fg='#EAF1F7',
            bg='#2A3440',
            padx=10,
            pady=6,
        )
        self.mode_label.grid(row=0, column=0, padx=(4, 8))

        items = [
            (self.t('help'), self.show_help),
            (self.t('bg_image'), self.select_background_image),
            (self.t('bg_color'), self.select_background_color),
            (self.t('text'), self.edit_custom_text),
            (self.t('mode'), self.switch_mode),
            (self.t('set_time'), self.set_time_value),
            (self.t('style'), self.open_style_panel),
            (self.t('reset'), self.reset_mode_timer),
            (self.t('pause_resume'), self.toggle_pause),
            (self.t('fullscreen'), lambda: self.toggle_fullscreen(True)),
            (self.t('hide_bar'), lambda: self.set_toolbar_visible(False)),
            (self.t('lang_switch'), self.toggle_language),
            (self.t('quit'), self.quit_app),
        ]
        for i, (label, cmd) in enumerate(items):
            btn = tk.Button(
                self.controls,
                text=label,
                command=cmd,
                font=('Segoe UI', 12),
                fg='#FFFFFF',
                bg='#2A3440',
                activeforeground='#FFFFFF',
                activebackground='#3A4858',
                relief='flat',
                borderwidth=0,
                padx=10,
                pady=6,
                cursor='hand2',
            )
            btn.grid(row=0, column=i + 1, padx=2)

    def toggle_language(self) -> None:
        self.lang = 'en' if self.lang == 'zh' else 'zh'
        self.root.title(self.app_title())
        if self.style_panel and self.style_panel.winfo_exists():
            self.style_panel.destroy()
            self.style_panel = None
        self.build_controls()

    def set_toolbar_visible(self, visible: bool) -> None:
        self.toolbar_visible = visible
        if visible:
            self.controls_container.place(relx=0.5, rely=1.0, anchor='s', y=-12)
            self.arrow_button.place_forget()
        else:
            self.controls_container.place_forget()
            self.arrow_button.place(relx=0.5, rely=1.0, anchor='s', y=-8)

    def bind_hotkeys(self) -> None:
        self.root.bind('h', lambda _: self.show_help())
        self.root.bind('H', lambda _: self.show_help())

        self.root.bind('b', lambda _: self.select_background_image())
        self.root.bind('B', lambda _: self.select_background_image())

        self.root.bind('c', lambda _: self.select_background_color())
        self.root.bind('C', lambda _: self.select_background_color())

        self.root.bind('t', lambda _: self.edit_custom_text())
        self.root.bind('T', lambda _: self.edit_custom_text())

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
        messagebox.showinfo(self.t('help_title'), self.t('help_text'))

    def toggle_fullscreen(self, enabled: bool) -> None:
        self.root.attributes('-fullscreen', enabled)

    def quit_app(self) -> None:
        self.running = False
        self.root.destroy()

    def set_mode(self, mode: str) -> None:
        self.mode = mode
        self.paused = False
        self.paused_duration = 0
        self.pause_started_at = None

        if mode == 'countdown':
            seconds = simpledialog.askinteger('倒计时', '请输入倒计时秒数:', minvalue=1)
            if not seconds:
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
            value = simpledialog.askstring('设置时间', '输入显示时间 (HH:MM:SS):')
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
                messagebox.showerror('格式错误', '请使用 HH:MM:SS，例如 08:30:00')
            return

        if self.mode == 'countup':
            seconds = simpledialog.askinteger('正计时', '输入起始秒数:', minvalue=0)
            if seconds is None:
                return
            self.count_start = time.time() - seconds
            self.paused = False
            self.paused_duration = 0
            self.pause_started_at = None
            return

        seconds = simpledialog.askinteger('倒计时', '输入倒计时总秒数:', minvalue=1)
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
        panel.geometry('420x430')
        panel.resizable(False, False)
        panel.configure(bg='#111111')
        panel.attributes('-topmost', True)

        self.style_panel = panel

        header = tk.Label(panel, text=self.t('style_header'), fg='white', bg='#111111', font=('Segoe UI', 12, 'bold'))
        header.pack(anchor='w', padx=16, pady=(12, 6))

        self.time_size_scale = self._create_scale(panel, self.t('time_size'), 24, 240, self.time_font_size, self._apply_style)
        self.text_size_scale = self._create_scale(panel, self.t('text_size'), 12, 120, self.text_font_size, self._apply_style)
        self.bg_size_scale = self._create_scale(panel, self.t('bg_scale'), 20, 300, self.bg_scale_percent, self._apply_style)

        r, g, b = self.hex_to_rgb(self.text_color)
        self.r_scale = self._create_scale(panel, 'R', 0, 255, r, self._apply_style)
        self.g_scale = self._create_scale(panel, 'G', 0, 255, g, self._apply_style)
        self.b_scale = self._create_scale(panel, 'B', 0, 255, b, self._apply_style)

        tk.Label(panel, text=self.t('color_preview'), fg='white', bg='#111111', font=('Segoe UI', 10)).pack(anchor='w', padx=16, pady=(8, 4))
        swatch = tk.Label(panel, text='      ', bg=self.text_color, relief='flat')
        swatch.pack(anchor='w', padx=16, pady=(0, 8))

        self._style_swatch = swatch
        self._apply_style()

        btn_row = tk.Frame(panel, bg='#111111')
        btn_row.pack(fill='x', padx=12, pady=(4, 12))

        tk.Button(
            btn_row,
            text=self.t('close'),
            command=panel.destroy,
            font=('Segoe UI', 10),
            fg='white',
            bg='#222222',
            activeforeground='white',
            activebackground='#333333',
            relief='flat',
            padx=12,
            pady=6,
        ).pack(side='right', padx=4)

        panel.protocol('WM_DELETE_WINDOW', panel.destroy)

    def _create_scale(
        self,
        parent: tk.Toplevel,
        label: str,
        start: int,
        end: int,
        value: int,
        on_change,
    ) -> tk.Scale:
        row = tk.Frame(parent, bg='#111111')
        row.pack(fill='x', padx=12, pady=3)

        top = tk.Frame(row, bg='#111111')
        top.pack(fill='x', padx=4)
        tk.Label(top, text=label, fg='white', bg='#111111', font=('Segoe UI', 10)).pack(side='left')

        entry = tk.Entry(top, width=6, justify='center', font=('Segoe UI', 9))
        entry.pack(side='right')

        scale = tk.Scale(
            row,
            from_=start,
            to=end,
            orient='horizontal',
            showvalue=True,
            fg='white',
            bg='#111111',
            highlightthickness=0,
            troughcolor='#222222',
            activebackground='#4d4d4d',
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
        if not all([self.time_size_scale, self.text_size_scale, self.bg_size_scale, self.r_scale, self.g_scale, self.b_scale]):
            return
        self.time_font_size = int(self.time_size_scale.get())
        self.text_font_size = int(self.text_size_scale.get())
        self.bg_scale_percent = int(self.bg_size_scale.get())
        self.text_color = self.rgb_to_hex(int(self.r_scale.get()), int(self.g_scale.get()), int(self.b_scale.get()))
        if hasattr(self, '_style_swatch') and self._style_swatch is not None:
            self._style_swatch.configure(bg=self.text_color)
        self.update_font_sizes()
        self.redraw_background()

    def update_font_sizes(self) -> None:
        self.canvas.itemconfigure(self.time_item, font=('Segoe UI', self.time_font_size, 'bold'))
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
        self.redraw_background()
        self.position_elements()

    def select_background_image(self) -> None:
        path = filedialog.askopenfilename(
            title='选择背景图片',
            filetypes=[('Image Files', '*.png;*.jpg;*.jpeg;*.bmp;*.gif;*.ppm;*.pgm'), ('All Files', '*.*')],
        )
        if not path:
            return

        if Image is None:
            ext = os.path.splitext(path)[1].lower()
            tk_supported = {'.png', '.gif', '.ppm', '.pgm'}
            if ext not in tk_supported:
                messagebox.showerror(
                    '背景错误',
                    '当前环境未安装 Pillow，仅支持 png/gif/ppm/pgm。\n请安装 Pillow 后使用 jpg/jpeg/bmp。',
                )
                return

        self.bg_path = path
        self.redraw_background()

    def select_background_color(self) -> None:
        chosen = colorchooser.askcolor(title='选择背景颜色')[1]
        if not chosen:
            return
        self.bg_color = chosen
        self.bg_path = None
        self.redraw_background()

    def edit_custom_text(self) -> None:
        text = simpledialog.askstring('自定义文字', '请输入要显示的文字:', initialvalue=self.custom_text)
        if text is None:
            return
        self.custom_text = text
        self.canvas.itemconfigure(self.desc_item, text=self.custom_text)

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
                        raise ValueError('背景图片尺寸无效')

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
                messagebox.showerror('背景错误', f'加载背景失败: {exc}')

        self.canvas.tag_lower('bg')

    def format_hms(self, total_seconds: int) -> str:
        total_seconds = max(total_seconds, 0)
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
        self.canvas.coords(self.time_item, width / 2, height * 0.42)
        self.canvas.coords(self.desc_item, width / 2, height * 0.56)

    def update_ui(self) -> None:
        if not self.running:
            return

        display_time, mode_text = self.get_display_time()
        self.canvas.itemconfigure(self.time_item, text=display_time, fill=self.text_color)
        self.canvas.itemconfigure(self.desc_item, text=self.custom_text, fill=self.text_color)
        self.canvas.itemconfigure(self.status_item, text=self.version_text(), fill=self.text_color)
        if self.mode_label is not None:
            self.mode_label.configure(text=f"{self.t('mode_prefix')}: {mode_text}")

        self.position_elements()
        self.root.after(200, self.update_ui)


def main() -> None:
    root = tk.Tk()
    app = FullscreenClockApp(root)
    app.show_help()
    root.mainloop()


if __name__ == '__main__':
    main()


