import os
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import openpyxl
import datetime

# --- Global baza ---
conn = None
cursor = None
db_path = "files.db"

def connect_db(path):
    """Baza bilan ulanish yoki yangi yaratish"""
    global conn, cursor, db_path
    db_path = path
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            size INTEGER,
            created TEXT,
            modified TEXT
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

# --- Fayl qo‘shish ---
def add_file():
    file_path = filedialog.askopenfilename(title="Fayl tanlang")
    if file_path:
        filename = os.path.basename(file_path)
        size = os.path.getsize(file_path)
        created = datetime.datetime.fromtimestamp(os.path.getctime(file_path))
        modified = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))

        cursor.execute("INSERT INTO files (filename, size, created, modified) VALUES (?, ?, ?, ?)",
                       (filename, size, created, modified))
        conn.commit()
        refresh_table()
        messagebox.showinfo("✅", f"{filename} bazaga qo‘shildi!")

# --- Faylni tahrirlash ---
def edit_file():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("⚠️", "Avval jadvaldan faylni tanlang!")
        return

    item = tree.item(selected[0])
    file_id = item["values"][0]
    old_name = item["values"][1]

    # Yangi nom kiritish oynasi
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
        messagebox.showwarning("⚠️", "Avval jadvaldan faylni tanlang!")
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
    cursor.execute("SELECT * FROM files WHERE filename LIKE ?", ('%' + name + '%',))
    results = cursor.fetchall()
    show_results(results)

def search_by_extension():
    ext = entry.get()
    cursor.execute("SELECT * FROM files WHERE filename LIKE ?", ('%' + ext,))
    results = cursor.fetchall()
    show_results(results)

def get_largest_file():
    cursor.execute("SELECT * FROM files ORDER BY size DESC LIMIT 1")
    result = cursor.fetchall()
    show_results(result)

def get_recent_files():
    cursor.execute("SELECT * FROM files ORDER BY created DESC LIMIT 5")
    results = cursor.fetchall()
    show_results(results)

# --- Jadvalni yangilash ---
def refresh_table():
    cursor.execute("SELECT * FROM files")
    results = cursor.fetchall()
    show_results(results)

# --- Natijalarni ko‘rsatish ---
def show_results(results):
    for row in tree.get_children():
        tree.delete(row)
    for row in results:
        tree.insert("", tk.END, values=row)

# --- Excelga eksport ---
def export_to_excel():
    cursor.execute("SELECT * FROM files")
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

# --- GUI oynasi ---
root = tk.Tk()
root.title("📂 Fayl qidiruv tizimi")
root.geometry("950x550")

# Menyu
menubar = tk.Menu(root)
db_menu = tk.Menu(menubar, tearoff=0)
db_menu.add_command(label="Yangi baza yaratish", command=create_new_db)
db_menu.add_command(label="Mavjud bazani ochish", command=open_existing_db)
menubar.add_cascade(label="Baza", menu=db_menu)

export_menu = tk.Menu(menubar, tearoff=0)
export_menu.add_command(label="Excelga eksport", command=export_to_excel)
menubar.add_cascade(label="Eksport", menu=export_menu)

root.config(menu=menubar)

# Qidiruv paneli
frame = tk.Frame(root)
frame.pack(pady=10)

entry = tk.Entry(frame, width=40)
entry.grid(row=0, column=0, padx=5)

btn_name = tk.Button(frame, text="🔎 Nomi bo‘yicha qidirish", command=search_by_name)
btn_name.grid(row=0, column=1, padx=5)

btn_ext = tk.Button(frame, text="📄 Kengaytma bo‘yicha qidirish", command=search_by_extension)
btn_ext.grid(row=0, column=2, padx=5)

btn_largest = tk.Button(frame, text="📦 Eng katta fayl", command=get_largest_file)
btn_largest.grid(row=1, column=1, pady=5)

btn_recent = tk.Button(frame, text="🕒 Yaqinda yaratilgan", command=get_recent_files)
btn_recent.grid(row=1, column=2, pady=5)

btn_add = tk.Button(frame, text="➕ Fayl qo‘shish", command=add_file)
btn_add.grid(row=2, column=0, pady=5)

btn_edit = tk.Button(frame, text="✏️ Tahrirlash", command=edit_file)
btn_edit.grid(row=2, column=1, pady=5)

btn_delete = tk.Button(frame, text="🗑 O‘chirish", command=delete_file)
btn_delete.grid(row=2, column=2, pady=5)

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
