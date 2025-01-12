import customtkinter as ctk
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

# 現在の時刻を更新する関数
def update_time():
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    time_label.configure(text=now)
    root.after(1000, update_time)  # 1秒ごとに更新

# プレースホルダーを設定する関数
def set_placeholder(entry, placeholder):
    entry.insert(0, placeholder)
    entry.configure(text_color="grey")
    def on_focus_in(event):
        if entry.get() == placeholder:
            entry.delete(0, ctk.END)
            entry.configure(text_color="black")
    def on_focus_out(event):
        if entry.get() == "":
            entry.insert(0, placeholder)
            entry.configure(text_color="grey")
    entry.bind("<FocusIn>", on_focus_in)
    entry.bind("<FocusOut>", on_focus_out)

# メインウィンドウ作成
ctk.set_appearance_mode("Light")  # テーマモード ("Light", "Dark", "System")
ctk.set_default_color_theme("blue")  # カラーテーマ ("blue", "green", "dark-blue")

root = ctk.CTk()
root.title("タスク管理")
root.geometry("1550x870")  # ウィンドウサイズを調整
root.attributes('-fullscreen', True)  # 全画面表示

# 現在の時刻を表示するラベル
time_label = ctk.CTkLabel(root, text="", font=("Helvetica", 24))
time_label.pack(pady=20)
update_time()

# データ表示用のフレームとスクロールバー
data_frame = ctk.CTkFrame(root)
data_frame.pack(fill=ctk.BOTH, expand=True, pady=10)

task_frame = ctk.CTkScrollableFrame(data_frame)
task_frame.pack(side="left",fill=ctk.BOTH,expand=True,pady=10,padx=(0,10))

birthday_frame = ctk.CTkScrollableFrame(data_frame)
birthday_frame.pack(side="right",fill=ctk.BOTH,expand=True,pady=10,padx=(10,0))

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
    event.widget.delete(0, ctk.END)
    event.widget.insert(0, converted_text)

# データ表示の更新（開始時刻昇順）
def update_display():
    global check_buttons
    check_buttons.clear()  # リストをリセット

    for widget in task_frame.winfo_children():
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
            start_jst = start_dt.astimezone(jst).strftime('%Y-%m-%d-%H-%M-%S')
            end_jst = end_dt.astimezone(jst).strftime('%Y-%m-%d %H:%M:%S')
        else:
            start_jst = start
            end_jst = end
        
        start_parts = start_jst.split("-")# -で区切ったそれぞれの時間データをリストに分ける
        if len(start_parts) == 3:# リストの要素数を数えて、時間が設定されてるものと終日のもので分ける
            day_text = start_parts[1] + "/" + start_parts[2] + "  0時"
        else:
            day_text = start_parts[1] + "/" + start_parts[2] + " " + start_parts[3] + "時"
        tasktime_text = f"{day_text}"
        tasksummary_text = f"{event['summary']}"
        entry_text = f"{i}. 開始時刻: {start_jst}, 終了時刻: {end_jst} \n 内容: {event['summary']}"
        row_frame = ctk.CTkFrame(task_frame)
        row_frame.pack(fill=ctk.X, pady=10)

        check_var = ctk.BooleanVar()
        check_button = ctk.CTkCheckBox(row_frame, variable=check_var, text="")
        check_button.grid(row=1, column=0, padx=10)

        timelabel = ctk.CTkLabel(row_frame, text= tasktime_text, anchor="w", justify="left", font=("Helvetica", 16))
        timelabel.grid(row=0, column=1, pady=3, sticky="w")
        tasklabel = ctk.CTkLabel(row_frame, text= tasksummary_text, anchor="e", justify="left", font=("Helvetica", 20))
        tasklabel.grid(row=2, column=2, pady=5, sticky="w")

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
        ctk.messagebox.showerror("エラー", "編集する項目を1つだけ選択してください。")
        return

    selected_event_id = selected_indices[0]
    service = get_calendar_service()
    selected_event = service.events().get(calendarId='primary', eventId=selected_event_id).execute()

    # 新しいウィンドウを開いて編集
    edit_window = ctk.CTkToplevel(root)
    edit_window.title("編集ウィンドウ")
    edit_window.geometry("400x400")

    validate_cmd = (edit_window.register(validate_input), '%P')

    ctk.CTkLabel(edit_window, text="日付 (YYYY-MM-DD)", font=("Helvetica", 16)).pack(pady=5)
    date_entry = ctk.CTkEntry(edit_window, font=("Helvetica", 16))
    date_entry.pack(pady=5)
    date_entry.insert(0, selected_event['start'].get('dateTime', selected_event['start'].get('date')).split('T')[0])

    ctk.CTkLabel(edit_window, text="開始時刻 (HHMM)", font=("Helvetica", 16)).pack(pady=5)
    start_time_entry = ctk.CTkEntry(edit_window, validate='key', validatecommand=validate_cmd, font=("Helvetica", 16))
    start_time_entry.pack(pady=5)
    start_time_entry.insert(0, selected_event['start'].get('dateTime', selected_event['start'].get('date')).split('T')[1][:4])
    start_time_entry.bind("<KeyRelease>", convert_to_half_width)

    ctk.CTkLabel(edit_window, text="終了時刻 (HHMM)", font=("Helvetica", 16)).pack(pady=5)
    end_time_entry = ctk.CTkEntry(edit_window, validate='key', validatecommand=validate_cmd, font=("Helvetica", 16))
    end_time_entry.pack(pady=5)
    end_time_entry.insert(0, selected_event['end'].get('dateTime', selected_event['end'].get('date')).split('T')[1][:4])
    end_time_entry.bind("<KeyRelease>", convert_to_half_width)

    ctk.CTkLabel(edit_window, text="内容", font=("Helvetica", 16)).pack(pady=5)
    content_entry = ctk.CTkEntry(edit_window, font=("Helvetica", 16))
    content_entry.pack(pady=5)
    content_entry.insert(0, selected_event['summary'])

    def save_edited_data():
        date_str = date_entry.get()
        new_start_time = start_time_entry.get()
        new_end_time = end_time_entry.get()
        new_content = content_entry.get()

        if date_str and new_start_time and new_end_time and new_content:
            start_time = datetime.datetime.strptime(f"{date_str} {new_start_time[:2]}:{new_start_time[2:]}", '%Y-%m-%d %H:%M').isoformat()
            end_time = datetime.datetime.strptime(f"{date_str} {new_end_time[:2]}:{new_end_time[2:]}", '%Y-%m-%d %H:%M').isoformat()
            update_event(selected_event_id, start_time, end_time, new_content)
            update_display()
            edit_window.destroy()
        else:
            ctk.CTkLabel(edit_window, text="すべての項目を入力してください！", text_color="red", font=("Helvetica", 16)).pack()

    save_button = ctk.CTkButton(edit_window, text="保存", command=save_edited_data, font=("Helvetica", 16))
    save_button.pack(pady=10)

def open_input_window():
    new_window = ctk.CTkToplevel(root)
    new_window.title("入力ウィンドウ")
    new_window.geometry("400x400")

    validate_cmd = (new_window.register(validate_input), '%P')

    ctk.CTkLabel(new_window, text="日付 (YYYY-MM-DD)", font=("Helvetica", 16)).pack(pady=5)
    date_entry = ctk.CTkEntry(new_window, font=("Helvetica", 16))
    date_entry.pack(pady=5)
    set_placeholder(date_entry, "例: 2023-12-31")

    ctk.CTkLabel(new_window, text="開始時刻 (HHMM)", font=("Helvetica", 16)).pack(pady=5)
    start_time_entry = ctk.CTkEntry(new_window, validate='key', validatecommand=validate_cmd, font=("Helvetica", 16))
    start_time_entry.pack(pady=5)
    set_placeholder(start_time_entry, "例: 0900")
    start_time_entry.bind("<KeyRelease>", convert_to_half_width)

    ctk.CTkLabel(new_window, text="終了時刻 (HHMM)", font=("Helvetica", 16)).pack(pady=5)
    end_time_entry = ctk.CTkEntry(new_window, validate='key', validatecommand=validate_cmd, font=("Helvetica", 16))
    end_time_entry.pack(pady=5)
    set_placeholder(end_time_entry, "例: 1700")
    end_time_entry.bind("<KeyRelease>", convert_to_half_width)

    ctk.CTkLabel(new_window, text="内容", font=("Helvetica", 16)).pack(pady=5)
    content_entry = ctk.CTkEntry(new_window, font=("Helvetica", 16))
    content_entry.pack(pady=5)
    set_placeholder(content_entry, "例: 会議")

    def save_data():
        date_str = date_entry.get()
        start_time_str = start_time_entry.get()
        end_time_str = end_time_entry.get()
        content = content_entry.get()
        if date_str and start_time_str and end_time_str and content:
            # 開始時間と終了時間をISO 8601形式に変換
            start_time = datetime.datetime.strptime(f"{date_str} {start_time_str[:2]}:{start_time_str[2:]}", '%Y-%m-%d %H:%M').isoformat()
            end_time = datetime.datetime.strptime(f"{date_str} {end_time_str[:2]}:{end_time_str[2:]}", '%Y-%m-%d %H:%M').isoformat()
            add_event(start_time, end_time, content)
            update_display()
            new_window.destroy()
        else:
            ctk.CTkLabel(new_window, text="すべての項目を入力してください！", text_color="red", font=("Helvetica", 16)).pack()

    save_button = ctk.CTkButton(new_window, text="保存", command=save_data, font=("Helvetica", 16))
    save_button.pack(pady=10)

button_frame = ctk.CTkFrame(root)
button_frame.pack(side=ctk.BOTTOM, pady=20)

# 新しいウィンドウを開くボタン
main_button = ctk.CTkButton(button_frame, text="タスクの追加", command=open_input_window, font=("Helvetica", 16))
main_button.grid(row=0, column=0, padx=10, pady=5)

# 選択した項目を削除するボタン
delete_button = ctk.CTkButton(button_frame, text="選択した項目を削除", command=delete_selected_data, font=("Helvetica", 16))
delete_button.grid(row=0, column=1, padx=10, pady=5)

# 選択した項目を編集するボタン
edit_button = ctk.CTkButton(button_frame, text="選択した項目を編集", command=edit_selected_data, font=("Helvetica", 16))
edit_button.grid(row=0, column=2, padx=10, pady=5)

# プログラム起動時にデータを読み込み
update_display()

root.mainloop()