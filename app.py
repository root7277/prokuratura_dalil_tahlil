import os
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import openpyxl
import datetime
from download_file import download_file

# --- Global baza ---
conn = None
cursor = None
db_path = "files.db"

def connect_db(path):
    """Baza bilan ulanish yoki yangi yaratish"""
    global conn, cursor, db_path
    
    if conn:  # agar eski ulanish ochiq bo‘lsa, yopamiz
        conn.close()

    db_path = path
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            size INTEGER,
            created TEXT,
            modified TEXT,
            filedata BLOB
        )
    """)
    conn.commit()


# --- Baza yaratish ---
def create_new_db():
    path = filedialog.asksaveasfilename(defaultextension=".db",
                                        filetypes=[("SQLite files", "*.db")])
    if path:
        connect_db(path)
        refresh_table()
        messagebox.showinfo("✅", f"Yangi baza yaratildi:\n{path}")

# --- Mavjud bazani ochish ---
def open_existing_db():
    path = filedialog.askopenfilename(filetypes=[("SQLite files", "*.db")])
    if path:
        connect_db(path)
        refresh_table()
        messagebox.showinfo("✅", f"Baza ulandi:\n{path}")

# --- Bazani o‘chirish ---
def delete_database():
    """Bazani tanlab o‘chirish"""
    path = filedialog.askopenfilename(
        title="O‘chirish uchun bazani tanlang",
        filetypes=[("SQLite Database", "*.db"), ("Barcha fayllar", "*.*")]
    )
    if not path:
        return  # foydalanuvchi bekor qilgan

    if os.path.exists(path):
        try:
            os.remove(path)
            messagebox.showinfo("✅ Muvaffaqiyatli", f"Baza o‘chirildi:\n{path}")
        except Exception as e:
            messagebox.showerror("❌ Xatolik", f"Bazani o‘chirib bo‘lmadi:\n{e}")
    else:
        messagebox.showwarning("⚠️ Topilmadi", "Bunday fayl mavjud emas.")


# --- Fayl qo‘shish ---
def add_file():
    file_path = filedialog.askopenfilename(title="Fayl tanlang")
    if file_path:
        filename = os.path.basename(file_path)
        size = os.path.getsize(file_path)
        
        # Sana va vaqtni matn (string) sifatida yozamiz
        created = datetime.datetime.fromtimestamp(os.path.getctime(file_path)).isoformat()
        modified = datetime.datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()

        with open(file_path, "rb") as f:
            filedata = f.read()

        cursor.execute(
            "INSERT INTO files (filename, size, created, modified, filedata) VALUES (?, ?, ?, ?, ?)",
            (filename, size, created, modified, filedata)
        )
        conn.commit()
        refresh_table()
        messagebox.showinfo("✅", f"{filename} bazaga qo‘shildi!")


# --- Faylni tahrirlash ---
def edit_file():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("⚠️", "Avval faylni tanlang!")
        return

    item = tree.item(selected[0])
    file_id = item["values"][0]
    old_name = item["values"][1]

    new_name = tk.simpledialog.askstring("✏️ Faylni tahrirlash", f"Yangi nom kiriting (oldingi: {old_name})")
    if new_name:
        cursor.execute("UPDATE files SET filename=? WHERE id=?", (new_name, file_id))
        conn.commit()
        refresh_table()
        messagebox.showinfo("✅", "Fayl nomi yangilandi!")

# --- Faylni o‘chirish ---
def delete_file():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("⚠️", "Avval faylni tanlang!")
        return

    item = tree.item(selected[0])
    file_id = item["values"][0]

    confirm = messagebox.askyesno("🗑 O‘chirish", "Haqiqatan ham ushbu faylni o‘chirmoqchimisiz?")
    if confirm:
        cursor.execute("DELETE FROM files WHERE id=?", (file_id,))
        conn.commit()
        refresh_table()
        messagebox.showinfo("✅", "Fayl o‘chirildi!")

# --- Qidiruv funksiyalari ---
def search_by_name():
    name = entry.get()
    cursor.execute("SELECT id, filename, size, created, modified FROM files WHERE filename LIKE ?", ('%' + name + '%',))
    results = cursor.fetchall()
    show_results(results)

def search_by_extension():
    ext = entry.get()
    cursor.execute("SELECT id, filename, size, created, modified FROM files WHERE filename LIKE ?", ('%' + ext,))
    results = cursor.fetchall()
    show_results(results)

def get_largest_file():
    cursor.execute("SELECT id, filename, size, created, modified FROM files ORDER BY size DESC LIMIT 1")
    result = cursor.fetchall()
    show_results(result)

def get_recent_files():
    cursor.execute("SELECT id, filename, size, created, modified FROM files ORDER BY created DESC LIMIT 5")
    results = cursor.fetchall()
    show_results(results)

# --- Jadvalni yangilash ---
def refresh_table():
    cursor.execute("SELECT id, filename, size, created, modified FROM files")
    results = cursor.fetchall()
    show_results(results)

# --- Natijalarni ko‘rsatish ---
def show_results(results):
    for row in tree.get_children():
        tree.delete(row)
    for row in results:
        tree.insert("", tk.END, values=row)

# --- Excelga eksport ---
'''
def export_to_excel():
    cursor.execute("SELECT id, filename, size, created, modified FROM files")
    data = cursor.fetchall()
    
    if not data:
        messagebox.showwarning("⚠️", "Bazada ma’lumot yo‘q!")
        return

    path = filedialog.asksaveasfilename(defaultextension=".xlsx",
                                        filetypes=[("Excel files", "*.xlsx")])
    if not path:
        return

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(["ID", "Fayl nomi", "Hajmi", "Yaratilgan", "O‘zgartirilgan"])

    for row in data:
        ws.append(row)

    wb.save(path)
    messagebox.showinfo("✅", f"Ma’lumotlar Excel fayliga eksport qilindi:\n{path}")
    '''

# --- GUI oynasi ---
root = tk.Tk()
root.title("📂 Fayl qidiruv tizimi")
root.geometry("1000x600")

# Qidiruv paneli
frame = tk.Frame(root)
frame.pack(pady=10)

entry = tk.Entry(frame, width=40)
entry.grid(row=0, column=0, padx=5)

btn_name = tk.Button(frame, text="🔎 Fayl nomi bo‘yicha qidirish", command=search_by_name)
btn_name.grid(row=0, column=1, padx=5)

btn_ext = tk.Button(frame, text="📄 Fayllarni kengaytmasi bo‘yicha qidirish", command=search_by_extension)
btn_ext.grid(row=0, column=2, padx=5)

btn_largest = tk.Button(frame, text="📦 Eng katta fayl", command=get_largest_file)
btn_largest.grid(row=1, column=1, pady=5)

btn_recent = tk.Button(frame, text="🕒 Yaqinda yaratilgan fayl", command=get_recent_files)
btn_recent.grid(row=1, column=2, pady=5)

btn_add = tk.Button(frame, text="➕ Yangi fayl qo‘shish", command=add_file)
btn_add.grid(row=2, column=0, pady=5)

btn_edit = tk.Button(frame, text="✏️ Fayl nomini tahrirlash", command=edit_file)
btn_edit.grid(row=2, column=1, pady=5)

btn_delete = tk.Button(frame, text="🗑 Faylni o‘chirish", command=delete_file)
btn_delete.grid(row=2, column=2, pady=5)

btn_download = tk.Button(frame, text="⬇️ Yuklab olish", command=lambda: download_file(tree, cursor))
btn_download.grid(row=2, column=3, pady=5)

# 🔹 Baza bilan ishlash tugmalari
btn_newdb = tk.Button(frame, text="🆕 Yangi baza yaratish", command=create_new_db)
btn_newdb.grid(row=3, column=0, pady=5)

btn_opendb = tk.Button(frame, text="📂 Mavjud bazani ochish", command=open_existing_db)
btn_opendb.grid(row=3, column=1, pady=5)

btn_deldb = tk.Button(frame, text="❌ Bazani o‘chirish", command=delete_database)
btn_deldb.grid(row=3, column=2, pady=5)

# Jadval
columns = ("ID", "Fayl nomi", "Hajmi", "Yaratilgan", "O‘zgartirilgan")
tree = ttk.Treeview(root, columns=columns, show="headings")

for col in columns:
    tree.heading(col, text=col)

tree.pack(fill=tk.BOTH, expand=True)

# Ilova startida default bazaga ulanadi
connect_db(db_path)
refresh_table()

root.mainloop()
