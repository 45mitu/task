import customtkinter as ctk
import datetime

def update_time(time_var):
    # 現在時刻を取得してフォーマット
    current_datetime = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    time_var.set("現在時刻：" + current_datetime)
    # 1秒ごとに時刻を更新
    root.after(1000, update_time, time_var)

def task_done(task_label):
    # タスクを完了したら、文字色をグレーに変更
    task_label.configure(text=task_label.cget("text") + " (完了)", text_color="gray")

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

    # タスク1: ボタンを左、ラベルを右に配置
    task1_frame = ctk.CTkFrame(main_frame)
    task1_frame.pack(pady=10, anchor="center")

    task1_button = ctk.CTkButton(task1_frame, text="完了", command=lambda: task_done(task1_label), width=120)
    task1_button.pack(side="left", padx=10)
    task1_label = ctk.CTkLabel(task1_frame, text="タスク1: レポート作成", font=("Noto Sans CJK JP", 18))
    task1_label.pack(side="left", padx=10)

    # タスク2: ボタンを左、ラベルを右に配置
    task2_frame = ctk.CTkFrame(main_frame)
    task2_frame.pack(pady=10, anchor="center")

    task2_button = ctk.CTkButton(task2_frame, text="完了", command=lambda: task_done(task2_label), width=120)
    task2_button.pack(side="left", padx=10)
    task2_label = ctk.CTkLabel(task2_frame, text="タスク2: 授業課題", font=("Noto Sans CJK JP", 18))
    task2_label.pack(side="left", padx=10)

    # ウィンドウを閉じるボタン
    close_button = ctk.CTkButton(main_frame, text="閉じる", command=quit, fg_color="red", width=160)
    close_button.pack(pady=30)

    # 時刻更新
    update_time(time_var)

    # customtkinterのメインループを開始
    root.mainloop()

if __name__ == "__main__":
    text_display()
