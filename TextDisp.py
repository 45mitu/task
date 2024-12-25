import tkinter as tk

def display_message():
    # tkinterのウィンドウを作成
    root = tk.Tk()
    root.title("テスト画面表示")  # ウィンドウのタイトル
    root.geometry("400x200")  # ウィンドウのサイズ (幅400px, 高さ200px)

    # ラベルを作成してウィンドウに追加
    tk.Label(root, text="テスト表示", font=("Noto Sans CJK JP", 24), fg="black").pack()

    # tkinterのメインループを開始
    root.mainloop()

if __name__ == "__main__":
    display_message()
