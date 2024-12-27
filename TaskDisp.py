import customtkinter as ctk
import datetime
import pytz
import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

def update_time(time_var):
    # 現在時刻を取得してフォーマット
    current_datetime = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    time_var.set("現在時刻：" + current_datetime)
    # 1秒ごとに時刻を更新
    root.after(1000, update_time, time_var)

def task_done(task_label):
    # タスクを完了したら、文字色をグレーに変更
    task_label.configure(text=task_label.cget("text") + " (完了)", text_color="gray")

def get_events():
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
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()  # 修正
    events_result = service.events().list(
        calendarId="primary",
        timeMin=now,
        maxResults=10,
        singleEvents=True,
        orderBy="startTime"
    ).execute()
    events = events_result.get("items", [])

    event_list = []
    for event in events:
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
        
        event_list.append(f"開始時間: {start_jst}, 終了時間: {end_jst}, タスク: {event['summary']}")
    
    return event_list

def text_display():
    global root

    # `customtkinter` のテーマを設定
    ctk.set_appearance_mode("System")  # テーマモード ("Light", "Dark", "System")
    ctk.set_default_color_theme("blue")  # カラーテーマ ("blue", "green", "dark-blue")

    # customtkinterのウィンドウを作成
    root = ctk.CTk()
    root.title("タスク管理画面")  # ウィンドウのタイトル
    root.geometry("800x600")  # ウィンドウのサイズ (幅800px, 高さ600px)

    # メインフレーム
    main_frame = ctk.CTkFrame(root)
    main_frame.pack(fill="both", expand=True, padx=30, pady=30)

    # 時刻表示
    time_var = ctk.StringVar()
    time_var.set("現在時刻：" + datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S"))
    time_label = ctk.CTkLabel(main_frame, textvariable=time_var, font=('Helvetica', 20))
    time_label.pack(pady=(0, 30))
    update_time(time_var)

    # Googleカレンダーのイベントを取得して表示
    events = get_events()
    for event in events:
        task_frame = ctk.CTkFrame(main_frame)
        task_frame.pack(pady=10, anchor="center")

        task_label = ctk.CTkLabel(task_frame, text=event, font=("Noto Sans CJK JP", 18))
        task_label.pack(side="left", padx=10)
        task_button = ctk.CTkButton(task_frame, text="完了", command=lambda lbl=task_label: task_done(lbl), width=120)
        task_button.pack(side="left", padx=10)

    root.mainloop()

if __name__ == '__main__':
    text_display()