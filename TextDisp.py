import tkinter as tk
import datetime

def update_time(time_var):
    # 現在時刻を取得してフォーマット
    current_datetime = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    time_var.set("現在時刻：" + current_datetime)
    # 1秒ごとに時刻を更新
    root.after(1000, update_time, time_var)

def task_done(task_label):
    # タスクを完了したら、文字色をグレーに変更
    task_label.config(fg="gray")
    task_label.config(text=task_label.cget("text") + " (完了)")

def text_display():
    global root

    # tkinterのウィンドウを作成
    root = tk.Tk()
    root.title("タスク管理画面")  # ウィンドウのタイトル
    root.geometry("400x300")  # ウィンドウのサイズ (幅400px, 高さ300px)

    # 画面枠設定
    main_frame = tk.Frame(root, bg="white")
    main_frame.grid(row=0, column=0, sticky="nsew")

    # 時刻表示
    time_var = tk.StringVar()
    time_var.set("現在時刻：" + datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S"))
    time_label = tk.Label(main_frame, textvariable=time_var, font=('Helvetica', '10'), fg="black", bg="white")
    time_label.grid(row=0, column=0, columnspan=2, pady=10)

    # タスク1
    task1_label = tk.Label(main_frame, text="タスク1: レポート作成", font=("Noto Sans CJK JP", 12), fg="black", bg="white")
    task1_button = tk.Button(main_frame, text="完了", command=lambda: task_done(task1_label), bg="green", fg="white")

    # 配置
    task1_label.grid(row=1, column=1, padx=10, pady=5, sticky="w")
    task1_button.grid(row=1, column=0, padx=10, pady=5)

    # タスク2
    task2_label = tk.Label(main_frame, text="タスク2: 授業課題", font=("Noto Sans CJK JP", 12), fg="black", bg="white")
    task2_button = tk.Button(main_frame, text="完了", command=lambda: task_done(task2_label), bg="green", fg="white")

    # 配置
    task2_label.grid(row=2, column=1, padx=10, pady=5, sticky="w")
    task2_button.grid(row=2, column=0, padx=10, pady=5)

    # ウィンドウを閉じるボタン
    close_button = tk.Button(main_frame, text="閉じる", command=quit, width=13, bg="red", fg="white")
    close_button.grid(row=3, column=0, columnspan=2, pady=20)

    # 時刻更新
    update_time(time_var)

    # tkinterのメインループを開始
    root.mainloop()

if __name__ == "__main__":
    text_display()
