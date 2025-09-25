import os
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog

def download_file(tree, cursor):
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("⚠️", "Avval faylni tanlang!")
        return

    item = tree.item(selected[0])
    file_id = item["values"][0]

    # Parol so‘ralsin (masalan: dxa_01)
    code = simpledialog.askstring("🔑 Kod", "Yuklab olish kodi:")
    if code != "dxa_01":
        messagebox.showerror("❌", "Noto‘g‘ri kod!")
        return

    cursor.execute("SELECT filename, filedata FROM files WHERE id=?", (file_id,))
    row = cursor.fetchone()

    if row and row[1]:
        filename, filedata = row

        # Qayerga saqlashni so‘raymiz
        save_path = filedialog.asksaveasfilename(initialfile=filename)
        if save_path:
            with open(save_path, "wb") as f:
                f.write(filedata)
            messagebox.showinfo("✅", f"Fayl yuklab olindi:\n{save_path}")
    else:
        messagebox.showerror("❌", "Fayl ma’lumotlari topilmadi!")
