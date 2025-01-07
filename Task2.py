import tkinter as tk
from tkinter import ttk

# 入力内容を保存するリスト
saved_data = []

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
labels = []  # ラベルのリスト（テキスト変更用）

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
    global check_buttons, labels
    check_buttons.clear()  # リストをリセット
    labels.clear()

    for widget in scrollable_frame.winfo_children():
        widget.destroy()

    sorted_data = sorted(saved_data, key=lambda x: x['開始時刻'])

    for i, entry in enumerate(sorted_data, start=1):
        entry_text = f"{i}. 開始時刻: {entry['開始時刻']}, 終了時刻: {entry['終了時刻']}, 内容: {entry['内容']}"
        row_frame = tk.Frame(scrollable_frame)
        row_frame.pack(fill=tk.X, pady=5)

        check_var = tk.BooleanVar()
        check_button = tk.Checkbutton(row_frame, variable=check_var)
        check_button.grid(row=0, column=0, padx=10)

        label = tk.Label(row_frame, text=entry_text, anchor="w", justify="left")
        label.grid(row=0, column=1, padx=10, sticky="w")

        check_buttons.append((check_var, i-1))
        labels.append(label)

def delete_selected_data():
    global saved_data
    indices_to_delete = [idx for check_var, idx in check_buttons if check_var.get()]
    for index in sorted(indices_to_delete, reverse=True):
        saved_data.pop(index)
    update_display()

def complete_selected_data():
    for check_var, label in zip(check_buttons, labels):
        if check_var[0].get():  # チェックボックスがオンの場合
            label.config(fg="gray")  # ラベルの文字色を灰色に変更

def edit_selected_data():
    selected_indices = [idx for check_var, idx in check_buttons if check_var.get()]
    if len(selected_indices) != 1:
        tk.messagebox.showerror("エラー", "編集する項目を1つだけ選択してください。")
        return

    selected_index = selected_indices[0]
    selected_data = saved_data[selected_index]

    edit_window = tk.Toplevel(root)
    edit_window.title("編集ウィンドウ")
    edit_window.geometry("300x300")

    validate_cmd = (edit_window.register(validate_input), '%P')

    tk.Label(edit_window, text="開始時刻 (半角数字のみ)").pack(pady=5)
    start_time_entry = tk.Entry(edit_window, validate='key', validatecommand=validate_cmd)
    start_time_entry.pack(pady=5)
    start_time_entry.insert(0, selected_data['開始時刻'])
    start_time_entry.bind("<KeyRelease>", convert_to_half_width)

    tk.Label(edit_window, text="終了時刻 (半角数字のみ)").pack(pady=5)
    end_time_entry = tk.Entry(edit_window, validate='key', validatecommand=validate_cmd)
    end_time_entry.pack(pady=5)
    end_time_entry.insert(0, selected_data['終了時刻'])
    end_time_entry.bind("<KeyRelease>", convert_to_half_width)

    tk.Label(edit_window, text="内容").pack(pady=5)
    content_entry = tk.Entry(edit_window)
    content_entry.pack(pady=5)
    content_entry.insert(0, selected_data['内容'])

    def save_edited_data():
        new_start_time = start_time_entry.get()
        new_end_time = end_time_entry.get()
        new_content = content_entry.get()

        if new_start_time and new_end_time and new_content:
            saved_data[selected_index] = {
                "開始時刻": new_start_time,
                "終了時刻": new_end_time,
                "内容": new_content,
            }
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
        start_time = start_time_entry.get()
        end_time = end_time_entry.get()
        content = content_entry.get()
        if start_time and end_time and content:
            entry_data = {"開始時刻": start_time, "終了時刻": end_time, "内容": content}
            saved_data.append(entry_data)
            update_display()
            new_window.destroy()
        else:
            tk.Label(new_window, text="すべての項目を入力してください！", fg="red").pack()

    save_button = tk.Button(new_window, text="保存", command=save_data)
    save_button.pack(pady=10)

button_frame = tk.Frame(root)
button_frame.pack(side=tk.BOTTOM, pady=20)

main_button = tk.Button(button_frame, text="タスクの追加", command=open_input_window)
main_button.grid(row=0, column=0, padx=10, pady=5)

delete_button = tk.Button(button_frame, text="削除", command=delete_selected_data)
delete_button.grid(row=0, column=1, padx=10, pady=5)

edit_button = tk.Button(button_frame, text="編集", command=edit_selected_data)
edit_button.grid(row=0, column=2, padx=10, pady=5)

complete_button = tk.Button(button_frame, text="完了", command=complete_selected_data)
complete_button.grid(row=0, column=3, padx=10, pady=5)

root.mainloop()
