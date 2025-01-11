import customtkinter as ctk
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os
import datetime
import time

# # GoogleカレンダーAPIのスコープ
# SCOPES = ['https://www.googleapis.com/auth/calendar.events']

# def get_calendar_service():
#     creds = None
#     if os.path.exists("token.json"):
#         creds = Credentials.from_authorized_user_file("token.json", SCOPES)
#     if not creds or not creds.valid:
#         if creds and creds.expired and creds.refresh_token:
#             creds.refresh(Request())
#         else:
#             flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
#             creds = flow.run_local_server(port=0)
#         with open("token.json", "w") as token:
#             token.write(creds.to_json())
#     service = build("calendar", "v3", credentials=creds)
#     return service

# def get_events():
#     service = get_calendar_service()
#     now = datetime.datetime.utcnow().isoformat() + 'Z'
#     events_result = service.events().list(
#         calendarId='primary',
#         timeMin=now,
#         maxResults=10,
#         singleEvents=True,
#         orderBy='startTime'
#     ).execute()
#     return events_result.get('items', [])

# def delete_event(event_id):
#     service = get_calendar_service()
#     service.events().delete(calendarId='primary', eventId=event_id).execute()

# def update_event(event_id, start_time, end_time, summary):
#     service = get_calendar_service()
#     event = service.events().get(calendarId='primary', eventId=event_id).execute()
#     event['start']['dateTime'] = start_time
#     event['end']['dateTime'] = end_time
#     event['summary'] = summary
#     service.events().update(calendarId='primary', eventId=event_id, body=event).execute()

# # タスクリストとチェックボックス管理
# check_vars = []

# def update_event_list():
#     """
#     タスクリストを更新し、チェックボックス付きで表示。
#     """
#     for widget in scrollable_frame.winfo_children():
#         widget.destroy()
#     check_vars.clear()
#     events = get_events()
#     for event in events:
#         start = event['start'].get('dateTime', event['start'].get('date'))
#         end = event['end'].get('dateTime', event['end'].get('date'))
#         summary = event['summary']
#         event_id = event['id']

#         task_frame = ctk.CTkFrame(scrollable_frame, fg_color="#333333", corner_radius=10)  # 背景色を暗く
#         task_frame.pack(fill="x", pady=5, padx=5)

#         check_var = ctk.BooleanVar()
#         check_vars.append((check_var, event_id))

#         check_button = ctk.CTkCheckBox(task_frame, variable=check_var, text="", fg_color="#555555")  # チェックボックスの色を調整
#         check_button.pack(side="left", padx=10)

#         task_label = ctk.CTkLabel(task_frame, text=f"{start} - {end} : {summary}", anchor="w", text_color="#FFFFFF")  # テキスト色を白に
#         task_label.pack(side="left", padx=10)

# def open_add_task_window():
#     """
#     新規タスク追加ウィンドウを表示。
#     """
#     def save_task():
#         start = start_time_entry.get()
#         end = end_time_entry.get()
#         summary = summary_entry.get()

#         try:
#             today = datetime.date.today()
#             if len(start) == 4:
#                 start = f"{today}T{start[:2]}:{start[2:]}:00"
#             if len(end) == 4:
#                 end = f"{today}T{end[:2]}:{end[2:]}:00"

#             start_dt = datetime.datetime.fromisoformat(start)
#             end_dt = datetime.datetime.fromisoformat(end)

#             if start_dt >= end_dt:
#                 ctk.CTkLabel(add_task_window, text="開始時刻は終了時刻より前にしてください。", text_color="red").pack()
#                 return

#             service = get_calendar_service()
#             service.events().insert(calendarId='primary', body={
#                 'summary': summary,
#                 'start': {'dateTime': start, 'timeZone': 'Asia/Tokyo'},
#                 'end': {'dateTime': end, 'timeZone': 'Asia/Tokyo'}
#             }).execute()

#             update_event_list()
#             add_task_window.destroy()
#         except ValueError:
#             ctk.CTkLabel(add_task_window, text="時刻形式が正しくありません。HHMM形式またはISO形式で入力してください。", text_color="red").pack()

#     add_task_window = ctk.CTkToplevel(root)
#     add_task_window.title("新規タスク追加")
#     add_task_window.geometry("400x300")

#     ctk.CTkLabel(add_task_window, text="開始時刻 (HHMM形式)").pack(pady=5)
#     start_time_entry = ctk.CTkEntry(add_task_window)
#     start_time_entry.pack(pady=5)

#     ctk.CTkLabel(add_task_window, text="終了時刻 (HHMM形式)").pack(pady=5)
#     end_time_entry = ctk.CTkEntry(add_task_window)
#     end_time_entry.pack(pady=5)

#     ctk.CTkLabel(add_task_window, text="タスク内容").pack(pady=5)
#     summary_entry = ctk.CTkEntry(add_task_window)
#     summary_entry.pack(pady=5)

#     save_button = ctk.CTkButton(add_task_window, text="保存", command=save_task)
#     save_button.pack(pady=20)

# def delete_selected_tasks():
#     """
#     選択されたタスクを削除。
#     """
#     for check_var, event_id in check_vars:
#         if check_var.get():
#             delete_event(event_id)
#     update_event_list()

# def edit_selected_task():
#     """
#     選択されたタスクを編集するウィンドウを表示。
#     """
#     selected_tasks = [(var, event_id) for var, event_id in check_vars if var.get()]
#     if len(selected_tasks) != 1:
#         ctk.CTkLabel(root, text="編集対象は1つだけ選択してください。", text_color="red").pack()
#         return

#     _, selected_event_id = selected_tasks[0]
#     service = get_calendar_service()
#     event = service.events().get(calendarId='primary', eventId=selected_event_id).execute()
#     current_start = event['start'].get('dateTime', '')
#     current_end = event['end'].get('dateTime', '')
#     current_summary = event['summary']

#     edit_window = ctk.CTkToplevel(root)
#     edit_window.title("タスク編集")
#     edit_window.geometry("400x300")

#     ctk.CTkLabel(edit_window, text="開始時刻").pack(pady=5)
#     start_time_entry = ctk.CTkEntry(edit_window)
#     start_time_entry.insert(0, current_start)
#     start_time_entry.pack(pady=5)

#     ctk.CTkLabel(edit_window, text="終了時刻").pack(pady=5)
#     end_time_entry = ctk.CTkEntry(edit_window)
#     end_time_entry.insert(0, current_end)
#     end_time_entry.pack(pady=5)

#     ctk.CTkLabel(edit_window, text="タスク内容").pack(pady=5)
#     summary_entry = ctk.CTkEntry(edit_window)
#     summary_entry.insert(0, current_summary)
#     summary_entry.pack(pady=5)

#     def save_edited_task():
#         new_start = start_time_entry.get()
#         new_end = end_time_entry.get()
#         new_summary = summary_entry.get()

#         try:
#             update_event(selected_event_id, new_start, new_end, new_summary)
#             update_event_list()
#             edit_window.destroy()
#         except Exception as e:
#             print(e)

#     save_button = ctk.CTkButton(edit_window, text="保存", command=save_edited_task)
#     save_button.pack(pady=20)

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
            self.label.configure(text="タイマー終了!")
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

# UI設定
ctk.set_appearance_mode("dark")  # ダークモードに設定
ctk.set_default_color_theme("blue")

root = ctk.CTk()
root.title("タスク管理アプリ")
root.geometry("600x900")

# # ヘッダーセクション
# header = ctk.CTkLabel(root, text="デスクトップアプリ", font=("Arial", 24, "bold"), text_color="#FFFFFF")
# header.pack(pady=10)

# # タスクリストフレーム
# task_frame = ctk.CTkFrame(root, corner_radius=10, fg_color="#333333")  # 背景色を暗く
# task_frame.pack(fill="both", expand=True, padx=10, pady=10)

# scrollable_frame = ctk.CTkScrollableFrame(task_frame, width=200, height=300, fg_color="#333333")  # 背景色を暗く
# scrollable_frame.pack(fill="both", expand=True, padx=10, pady=10)

# update_event_list()

# # ボタンフレーム
# button_frame = ctk.CTkFrame(root, fg_color="#333333", corner_radius=10, width=250)  # 背景色を暗く
# button_frame.pack(expand=True, padx=10, pady=10)

# add_task_button = ctk.CTkButton(button_frame, text="タスク追加", command=open_add_task_window, width=150, fg_color="#4CAF50", hover_color="#45A049")
# add_task_button.grid(row=0, column=0, pady=5, padx=10)

# delete_task_button = ctk.CTkButton(button_frame, text="選択タスク削除", command=delete_selected_tasks, width=150, fg_color="#F44336", hover_color="#E53935")
# delete_task_button.grid(row=0, column=1, pady=5, padx=10)

# edit_task_button = ctk.CTkButton(button_frame, text="選択タスク編集", command=edit_selected_task, width=150, fg_color="#8E8E93", hover_color="#45A049")
# edit_task_button.grid(row=0, column=2, pady=5, padx=10)

# タイマーとストップウォッチセクション
tools_frame = ctk.CTkFrame(root, fg_color="#333333", corner_radius=10)
tools_frame.pack(fill="x", padx=20, pady=10)

# タイマー
timer_label = ctk.CTkLabel(tools_frame, text="タイマー: 00:00", anchor="w", text_color="#FFFFFF", font=("Arial", 16))
timer_label.grid(row=1, column=0, columnspan=5, pady=5, padx=10)

timer = Timer(timer_label)

# 分数と秒数のエントリ
timer_minutes = ctk.IntVar(value=0)
timer_seconds = ctk.IntVar(value=0)

def update_timer_display():
    timer_label.configure(text=f"タイマー: {timer_minutes.get():02}:{timer_seconds.get():02}")

def increment_minutes():
    timer_minutes.set(timer_minutes.get() + 1)
    update_timer_display()

def decrement_minutes():
    if timer_minutes.get() > 0:
        timer_minutes.set(timer_minutes.get() - 1)
    update_timer_display()

def increment_seconds():
    if timer_seconds.get() < 59:
        timer_seconds.set(timer_seconds.get() + 1)
    else:
        increment_minutes()
        timer_seconds.set(0)
    update_timer_display()

def decrement_seconds():
    if timer_seconds.get() > 0:
        timer_seconds.set(timer_seconds.get() - 1)
    elif timer_minutes.get() > 0:
        decrement_minutes()
        timer_seconds.set(59)
    update_timer_display()

# 分秒ボタンを隣接して表示、縦の余白を設定しつつ横の余白をなくす
ctk.CTkButton(tools_frame, text="+分", command=increment_minutes, width=50, fg_color="#4CAF50", hover_color="#45A049").grid(row=2, column=0, padx=2, pady=5)
ctk.CTkButton(tools_frame, text="-分", command=decrement_minutes, width=50, fg_color="#F44336", hover_color="#E53935").grid(row=2, column=1, padx=2, pady=5)
ctk.CTkButton(tools_frame, text="+秒", command=increment_seconds, width=50, fg_color="#4CAF50", hover_color="#45A049").grid(row=2, column=2, padx=2, pady=5)
ctk.CTkButton(tools_frame, text="-秒", command=decrement_seconds, width=50, fg_color="#F44336", hover_color="#E53935").grid(row=2, column=3, padx=2, pady=5)

# 分秒ボタンの列の幅設定を削除して、ボタンのサイズを固定
tools_frame.grid_columnconfigure(0, weight=0)
tools_frame.grid_columnconfigure(1, weight=0)
tools_frame.grid_columnconfigure(2, weight=0)
tools_frame.grid_columnconfigure(3, weight=0)

timer_start_button = ctk.CTkButton(tools_frame, text="スタート", command=lambda: timer.start(timer_minutes.get() * 60 + timer_seconds.get()), fg_color="#2196F3", hover_color="#1E88E5")
timer_start_button.grid(row=3, column=0, padx=2, pady=5)

timer_stop_button = ctk.CTkButton(tools_frame, text="ストップ", command=timer.stop, fg_color="#FFC107", hover_color="#FFB300")
timer_stop_button.grid(row=3, column=1, padx=2, pady=5)

timer_reset_button = ctk.CTkButton(tools_frame, text="リセット", command=timer.reset, fg_color="#9E9E9E", hover_color="#757575")
timer_reset_button.grid(row=3, column=2, padx=2, pady=5)

# ストップウォッチ
stopwatch_label = ctk.CTkLabel(tools_frame, text="ストップウォッチ: 00:00", anchor="w", text_color="#FFFFFF", font=("Arial", 16))
stopwatch_label.grid(row=4, column=0, columnspan=5, pady=5, padx=10)

stopwatch = Stopwatch(stopwatch_label)
stopwatch_start_button = ctk.CTkButton(tools_frame, text="スタート", command=stopwatch.start, fg_color="#2196F3", hover_color="#1E88E5")
stopwatch_start_button.grid(row=5, column=0, padx=2, pady=5)

stopwatch_stop_button = ctk.CTkButton(tools_frame, text="ストップ", command=stopwatch.stop, fg_color="#FFC107", hover_color="#FFB300")
stopwatch_stop_button.grid(row=5, column=1, padx=2, pady=5)

stopwatch_reset_button = ctk.CTkButton(tools_frame, text="リセット", command=stopwatch.reset, fg_color="#9E9E9E", hover_color="#757575")
stopwatch_reset_button.grid(row=5, column=2, padx=2, pady=5)

root.mainloop()
