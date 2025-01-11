import customtkinter as ctk # type: ignore
import time
from typing import Callable

# タイマー機能
class Timer:
    def __init__(self, label):
        self.label = label
        self.time_left = 0
        self.running = False

    def start(self, seconds):
        self.time_left = seconds
        self.running = True
        self.update_timer()

    def update_timer(self):
        if self.running and self.time_left > 0:
            mins, secs = divmod(self.time_left, 60)
            self.label.configure(text=f"タイマー: {mins:02}:{secs:02}")
            self.time_left -= 1
            root.after(1000, self.update_timer)
        elif self.time_left == 0:
            self.label.configure(text="終了")
            self.running = False

    def stop(self):
        self.running = False

    def reset(self):
        self.time_left = 0
        self.running = False
        self.label.configure(text="タイマー: 00:00")

# ストップウォッチ機能
class Stopwatch:
    def __init__(self, label):
        self.label = label
        self.running = False
        self.start_time = 0
        self.elapsed_time = 0

    def start(self):
        if not self.running:
            self.running = True
            self.start_time = time.time() - self.elapsed_time
            self.update_stopwatch()

    def update_stopwatch(self):
        if self.running:
            self.elapsed_time = time.time() - self.start_time
            mins, secs = divmod(int(self.elapsed_time), 60)
            self.label.configure(text=f"ストップウォッチ: {mins:02}:{secs:02}")
            root.after(1000, self.update_stopwatch)

    def stop(self):
        self.running = False

    def reset(self):
        self.running = False
        self.elapsed_time = 0
        self.label.configure(text="ストップウォッチ: 00:00")

# FloatSpinboxクラス
class FloatSpinbox(ctk.CTkFrame):
    def __init__(self, *args,
                 width: int = 100,
                 height: int = 32,
                 step_size: int = 1,
                 command: Callable = None,
                 **kwargs):
        super().__init__(*args, width=width, height=height, **kwargs)

        self.step_size = step_size
        self.command = command

        self.configure(fg_color=("gray78", "gray28"))  # set frame color

        self.grid_columnconfigure((0, 2), weight=0)  # buttons don't expand
        self.grid_columnconfigure(1, weight=1)  # entry expands

        # +ボタンと-ボタンの位置を逆に設定
        self.add_button = ctk.CTkButton(self, text="+", width=height-6, height=height-6,
                                        command=self.add_button_callback)
        self.add_button.grid(row=0, column=0, padx=(3, 0), pady=3)

        self.entry = ctk.CTkEntry(self, width=width-(2*height), height=height-6, border_width=0)
        self.entry.grid(row=0, column=1, columnspan=1, padx=3, pady=3, sticky="ew")

        self.subtract_button = ctk.CTkButton(self, text="-", width=height-6, height=height-6,
                                             command=self.subtract_button_callback)
        self.subtract_button.grid(row=0, column=2, padx=(0, 3), pady=3)

        # default value
        self.entry.insert(0, "0")

    def add_button_callback(self):
        try:
            value = int(self.entry.get()) + self.step_size
            self.entry.delete(0, "end")
            self.entry.insert(0, value)
            if self.command is not None:
                self.command(value)
        except ValueError:
            return

    def subtract_button_callback(self):
        try:
            value = int(self.entry.get()) - self.step_size
            if value < 0:  # Prevent negative values
                value = 0
            self.entry.delete(0, "end")
            self.entry.insert(0, value)
            if self.command is not None:
                self.command(value)
        except ValueError:
            return

    def get(self) -> int:
        try:
            return int(self.entry.get())
        except ValueError:
            return 0

    def set(self, value: int):
        self.entry.delete(0, "end")
        self.entry.insert(0, str(value))


# UI設定
ctk.set_appearance_mode("dark")  # ダークモードに設定
ctk.set_default_color_theme("blue")

root = ctk.CTk()
root.title("タイマーストップウォッチ")
root.geometry("480x250")


# タイマーとストップウォッチセクション
tools_frame = ctk.CTkFrame(root, fg_color="#333333", corner_radius=10)
tools_frame.pack(fill="x", padx=20, pady=10)

# タイマー
timer_label = ctk.CTkLabel(tools_frame, text="タイマー: 00:00", anchor="w", text_color="#FFFFFF", font=("Arial", 16))
timer_label.grid(row=1, column=0, columnspan=5, pady=5, padx=10)

timer = Timer(timer_label)

# 分秒設定スピンボックスを追加
def update_timer_display():
    timer_label.configure(text=f"タイマー: {timer_minutes_spinbox.get():02}:{timer_seconds_spinbox.get():02}")

# 分数設定スピンボックス
timer_minutes_spinbox = FloatSpinbox(tools_frame, width=120, height=40, step_size=1, command=lambda _: update_timer_display())
timer_minutes_spinbox.grid(row=2, column=0, columnspan=2, padx=5, pady=5)

# 秒数設定スピンボックス
timer_seconds_spinbox = FloatSpinbox(tools_frame, width=120, height=40, step_size=1, command=lambda _: update_timer_display())
timer_seconds_spinbox.grid(row=2, column=2, columnspan=2, padx=5, pady=5)

# タイマー制御ボタン（スタート、ストップ、リセット）
timer_start_button = ctk.CTkButton(
    tools_frame, text="スタート", 
    command=lambda: timer.start(timer_minutes_spinbox.get() * 60 + timer_seconds_spinbox.get()), 
    fg_color="#2196F3", hover_color="#1E88E5"
)
timer_start_button.grid(row=3, column=0, padx=2, pady=5)

timer_stop_button = ctk.CTkButton(
    tools_frame, text="ストップ", 
    command=timer.stop, 
    fg_color="#F44336", hover_color="#E53935"
)
timer_stop_button.grid(row=3, column=1, padx=2, pady=5)

timer_reset_button = ctk.CTkButton(
    tools_frame, text="リセット", 
    command=timer.reset, 
    fg_color="#9E9E9E", hover_color="#757575"
)
timer_reset_button.grid(row=3, column=2, padx=2, pady=5)

# ストップウォッチ
stopwatch_label = ctk.CTkLabel(tools_frame, text="ストップウォッチ: 00:00", anchor="w", text_color="#FFFFFF", font=("Arial", 16))
stopwatch_label.grid(row=4, column=0, columnspan=5, pady=5, padx=10)

stopwatch = Stopwatch(stopwatch_label)
stopwatch_start_button = ctk.CTkButton(tools_frame, text="スタート", command=stopwatch.start, fg_color="#2196F3", hover_color="#1E88E5")
stopwatch_start_button.grid(row=5, column=0, padx=2, pady=5)

stopwatch_stop_button = ctk.CTkButton(tools_frame, text="ストップ", command=stopwatch.stop, fg_color="#F44336", hover_color="#E53935")
stopwatch_stop_button.grid(row=5, column=1, padx=2, pady=5)

stopwatch_reset_button = ctk.CTkButton(tools_frame, text="リセット", command=stopwatch.reset, fg_color="#9E9E9E", hover_color="#757575")
stopwatch_reset_button.grid(row=5, column=2, padx=2, pady=5)

root.mainloop()
