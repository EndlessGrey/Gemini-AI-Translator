import tkinter as tk
from tkinter import scrolledtext, messagebox, filedialog
import google.generativeai as genai
import time
import os

genai.configure(api_key="YOUR_APIKEY")  #APIキーを入れてください
model = genai.GenerativeModel('gemini-1.5-flash-latest')

translation_history = []

MAX_CHAR_COUNT = 500

default_save_dir = os.path.expanduser("~/Downloads")
default_file_name = "TranslateResult.txt"

def update_char_count(event=None):
    current_length = len(input_text.get("1.0", tk.END).strip())
    char_count_label.config(text=f"文字数: {current_length}/{MAX_CHAR_COUNT}")
    if current_length > MAX_CHAR_COUNT:
        char_count_label.config(fg="red")
    else:
        char_count_label.config(fg="black")

def clear_input():
    input_text.delete("1.0", tk.END)
    update_char_count()

def translate_text():
    user_input = input_text.get("1.0", tk.END).strip()
    current_length = len(user_input)

    if not user_input:
        messagebox.showwarning("Input Error", "翻訳する文章を入力してください。")
        return

    if current_length > MAX_CHAR_COUNT:
        messagebox.showwarning("Input Error", f"入力文字数が{MAX_CHAR_COUNT}文字を超えています。")
        return

    try:
        output_text.delete("1.0", tk.END)

        prompt = f"次の文章をフォーマットを崩さずに日本語に訳し、訳された文のみを答えよ: {user_input}"
        response = model.generate_content(prompt)
        translated_text = response.text.strip()

        output_text.insert(tk.END, translated_text + "\n\n")

        translation_history.append((user_input, translated_text))

        translate_button.config(state=tk.DISABLED)
        for i in range(5, 0, -1):
            translate_button.config(text=f"Wait {i} seconds")
            translate_button.update()
            time.sleep(1)
    except Exception as e:
        messagebox.showerror("API Error", f"An error occurred: {str(e)}")
    finally:
        translate_button.config(text="翻訳", state=tk.NORMAL)
        update_char_count()

def show_history():
    history_window = tk.Toplevel(root)
    history_window.title("翻訳履歴")

    history_text = scrolledtext.ScrolledText(history_window, height=20, width=60, state=tk.NORMAL)
    history_text.pack(pady=5)

    for original, translated in translation_history:
        history_text.insert(tk.END, f"元文章: {original}\n翻訳文: {translated}\n\n")
    
    close_button = tk.Button(history_window, text="閉じる", command=history_window.destroy)
    close_button.pack(pady=5)

def save_to_file():
    output_content = output_text.get("1.0", tk.END).strip()
    if not output_content:
        messagebox.showwarning("Save Error", "保存する内容がありません。")
        return

    file_path = filedialog.asksaveasfilename(
        initialdir=default_save_dir,
        initialfile=default_file_name,
        title="保存先を選択",
        defaultextension=".txt",
        filetypes=(("Text files", "*.txt"), ("All files", "*.*"))
    )

    if file_path:
        try:
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(output_content)
            messagebox.showinfo("Save Successful", f"翻訳結果を保存しました: {file_path}")
        except Exception as e:
            messagebox.showerror("Save Error", f"ファイルの保存中にエラーが発生しました: {str(e)}")


root = tk.Tk()
root.title("Gemini AI Translator")
root.geometry("550x750")

input_label = tk.Label(root, text="訳したい文章を入力してください:")
input_label.pack(pady=5)

input_frame = tk.Frame(root)
input_frame.pack(pady=5)

input_text = tk.Text(input_frame, height=16, width=60)
input_text.pack(side=tk.LEFT)
input_text.bind("<KeyRelease>", update_char_count)

clear_button = tk.Button(input_frame, text="✕", command=clear_input)
clear_button.pack(side=tk.RIGHT)

char_count_label = tk.Label(root, text=f"文字数: 0/{MAX_CHAR_COUNT}", fg="black")
char_count_label.pack(pady=5)

translate_button = tk.Button(root, text="翻訳", command=translate_text)
translate_button.pack(pady=5)

output_label = tk.Label(root, text="翻訳結果:")
output_label.pack(pady=5)

output_text = scrolledtext.ScrolledText(root, height=20, width=60, state=tk.NORMAL)
output_text.pack(pady=5)

save_button = tk.Button(root, text="翻訳結果を保存", command=save_to_file)
save_button.pack(pady=5)

history_button = tk.Button(root, text="翻訳履歴を見る", command=show_history)
history_button.pack(pady=5)

root.mainloop()
