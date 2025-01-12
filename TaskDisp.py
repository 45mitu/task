import tkinter as tk
from tkinter import ttk
import datetime
import pytz
import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# GoogleカレンダーAPIのスコープ
SCOPES = ['https://www.googleapis.com/auth/calendar']

# GoogleカレンダーAPIの認証とサービスの取得
def get_calendar_service():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    service = build("calendar", "v3", credentials=creds)
    return service

# Googleカレンダーからイベントを取得
def get_events():
    service = get_calendar_service()
    now = datetime.datetime.utcnow().isoformat() + 'Z'
    events_result = service.events().list(calendarId='primary', timeMin=now,
                                          maxResults=10, singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])
    return events

# Googleカレンダーにイベントを追加
def add_event(start_time, end_time, summary):
    service = get_calendar_service()
    event = {
        'summary': summary,
        'start': {
            'dateTime': start_time,
            'timeZone': 'Asia/Tokyo',
        },
        'end': {
            'dateTime': end_time,
            'timeZone': 'Asia/Tokyo',
        },
    }
    event_result = service.events().insert(calendarId='primary', body=event).execute()
    return event_result

# Googleカレンダーのイベントを更新
def update_event(event_id, start_time, end_time, summary):
    service = get_calendar_service()
    event = service.events().get(calendarId='primary', eventId=event_id).execute()
    event['summary'] = summary
    event['start']['dateTime'] = start_time
    event['end']['dateTime'] = end_time
    updated_event = service.events().update(calendarId='primary', eventId=event_id, body=event).execute()
    return updated_event

# Googleカレンダーのイベントを削除
def delete_event(event_id):
    service = get_calendar_service()
    service.events().delete(calendarId='primary', eventId=event_id).execute()

# メインウィンドウ作成
root = tk.Tk()
root.title("タスク管理")
root.geometry("400x500")  # ウィンドウサイズを調整

# データ表示用のフレームとスクロールバー
data_frame = tk.Frame(root)
data_frame.pack(fill=tk.BOTH, expand=True, pady=10)

canvas = tk.Canvas(data_frame)
scrollbar = ttk.Scrollbar(data_frame, orient=tk.VERTICAL, command=canvas.yview)
scrollable_frame = tk.Frame(canvas)

scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
)
canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

check_buttons = []  # チェックボックスのリスト

# 入力の検証（半角数字のみ）
def validate_input(input_str):
    if input_str == "" or input_str.isdigit():
        return True
    return False

# 全角数字を半角に変換
def convert_to_half_width(event):
    current_text = event.widget.get()
    converted_text = current_text.translate(str.maketrans('０１２３４５６７８９', '0123456789'))
    event.widget.delete(0, tk.END)
    event.widget.insert(0, converted_text)

# データ表示の更新（開始時刻昇順）
def update_display():
    global check_buttons
    check_buttons.clear()  # リストをリセット

    for widget in scrollable_frame.winfo_children():
        widget.destroy()

    events = get_events()
    sorted_events = sorted(events, key=lambda x: x['start'].get('dateTime', x['start'].get('date')))

    for i, event in enumerate(sorted_events, start=1):
        start = event['start'].get('dateTime', event['start'].get('date'))
        end = event['end'].get('dateTime', event['end'].get('date'))
        
        if 'dateTime' in event['start']:
            start_dt = datetime.datetime.fromisoformat(start.replace('Z', '+00:00'))
            end_dt = datetime.datetime.fromisoformat(end.replace('Z', '+00:00'))
            jst = pytz.timezone('Asia/Tokyo')
            start_jst = start_dt.astimezone(jst).strftime('%Y-%m-%d %H:%M:%S')
            end_jst = end_dt.astimezone(jst).strftime('%Y-%m-%d %H:%M:%S')
        else:
            start_jst = start
            end_jst = end
        
        entry_text = f"{i}. 開始時刻: {start_jst}, 終了時刻: {end_jst}, 内容: {event['summary']}"
        row_frame = tk.Frame(scrollable_frame)
        row_frame.pack(fill=tk.X, pady=5)

        check_var = tk.BooleanVar()
        check_button = tk.Checkbutton(row_frame, variable=check_var)
        check_button.grid(row=0, column=0, padx=10)

        label = tk.Label(row_frame, text=entry_text, anchor="w", justify="left")
        label.grid(row=0, column=1, padx=10, sticky="w")

        check_buttons.append((check_var, event['id']))

def delete_selected_data():
    indices_to_delete = [event_id for check_var, event_id in check_buttons if check_var.get()]
    for event_id in indices_to_delete:
        delete_event(event_id)
    update_display()

def edit_selected_data():
    """選択した項目を編集"""
    selected_indices = [event_id for check_var, event_id in check_buttons if check_var.get()]
    
    if len(selected_indices) != 1:
        tk.messagebox.showerror("エラー", "編集する項目を1つだけ選択してください。")
        return

    selected_event_id = selected_indices[0]
    service = get_calendar_service()
    selected_event = service.events().get(calendarId='primary', eventId=selected_event_id).execute()

    # 新しいウィンドウを開いて編集
    edit_window = tk.Toplevel(root)
    edit_window.title("編集ウィンドウ")
    edit_window.geometry("300x300")

    validate_cmd = (edit_window.register(validate_input), '%P')

    tk.Label(edit_window, text="開始時刻 (半角数字のみ)").pack(pady=5)
    start_time_entry = tk.Entry(edit_window, validate='key', validatecommand=validate_cmd)
    start_time_entry.pack(pady=5)
    start_time_entry.insert(0, selected_event['start'].get('dateTime', selected_event['start'].get('date')))
    start_time_entry.bind("<KeyRelease>", convert_to_half_width)

    tk.Label(edit_window, text="終了時刻 (半角数字のみ)").pack(pady=5)
    end_time_entry = tk.Entry(edit_window, validate='key', validatecommand=validate_cmd)
    end_time_entry.pack(pady=5)
    end_time_entry.insert(0, selected_event['end'].get('dateTime', selected_event['end'].get('date')))
    end_time_entry.bind("<KeyRelease>", convert_to_half_width)

    tk.Label(edit_window, text="内容").pack(pady=5)
    content_entry = tk.Entry(edit_window)
    content_entry.pack(pady=5)
    content_entry.insert(0, selected_event['summary'])

    def save_edited_data():
        new_start_time = start_time_entry.get()
        new_end_time = end_time_entry.get()
        new_content = content_entry.get()

        if new_start_time and new_end_time and new_content:
            update_event(selected_event_id, new_start_time, new_end_time, new_content)
            update_display()
            edit_window.destroy()
        else:
            tk.Label(edit_window, text="すべての項目を入力してください！", fg="red").pack()

    save_button = tk.Button(edit_window, text="保存", command=save_edited_data)
    save_button.pack(pady=10)

def open_input_window():
    new_window = tk.Toplevel(root)
    new_window.title("入力ウィンドウ")
    new_window.geometry("300x300")

    validate_cmd = (new_window.register(validate_input), '%P')

    tk.Label(new_window, text="開始時刻 (半角数字のみ)").pack(pady=5)
    start_time_entry = tk.Entry(new_window, validate='key', validatecommand=validate_cmd)
    start_time_entry.pack(pady=5)
    start_time_entry.bind("<KeyRelease>", convert_to_half_width)

    tk.Label(new_window, text="終了時刻 (半角数字のみ)").pack(pady=5)
    end_time_entry = tk.Entry(new_window, validate='key', validatecommand=validate_cmd)
    end_time_entry.pack(pady=5)
    end_time_entry.bind("<KeyRelease>", convert_to_half_width)

    tk.Label(new_window, text="内容").pack(pady=5)
    content_entry = tk.Entry(new_window)
    content_entry.pack(pady=5)

    def save_data():
        start_time_str = start_time_entry.get()
        end_time_str = end_time_entry.get()
        content = content_entry.get()
        if start_time_str and end_time_str and content:
            # 開始時間と終了時間をISO 8601形式に変換
            today = datetime.date.today().isoformat()
            start_time = datetime.datetime.strptime(f"{today} {start_time_str[:2]}:{start_time_str[2:]}", '%Y-%m-%d %H:%M').isoformat()
            end_time = datetime.datetime.strptime(f"{today} {end_time_str[:2]}:{end_time_str[2:]}", '%Y-%m-%d %H:%M').isoformat()
            add_event(start_time, end_time, content)
            update_display()
            new_window.destroy()
        else:
            tk.Label(new_window, text="すべての項目を入力してください！", fg="red").pack()

    save_button = tk.Button(new_window, text="保存", command=save_data)
    save_button.pack(pady=10)

button_frame = tk.Frame(root)
button_frame.pack(side=tk.BOTTOM, pady=20)

# 新しいウィンドウを開くボタン
main_button = tk.Button(button_frame, text="タスクの追加", command=open_input_window)
main_button.grid(row=0, column=0, padx=10, pady=5)

# 選択した項目を削除するボタン
delete_button = tk.Button(button_frame, text="選択した項目を削除", command=delete_selected_data)
delete_button.grid(row=0, column=1, padx=10, pady=5)

# 選択した項目を編集するボタン
edit_button = tk.Button(button_frame, text="選択した項目を編集", command=edit_selected_data)
edit_button.grid(row=0, column=2, padx=10, pady=5)

# プログラム起動時にデータを読み込み
update_display()

root.mainloop()