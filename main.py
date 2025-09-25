import os
import datetime
import sqlite3

# SQLite bazasiga ulanish
conn = sqlite3.connect("files.db")
cursor = conn.cursor()

# Jadval yaratish (agar mavjud bo‘lmasa)
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

# Tekshiriladigan papka
folder_path = "/home/kali/Downloads"

# Fayllarni ko‘rib chiqamiz
for filename in os.listdir(folder_path):
    file_path = os.path.join(folder_path, filename)

    if os.path.isfile(file_path):
        size = os.path.getsize(file_path)
        created = datetime.datetime.fromtimestamp(os.path.getctime(file_path))
        modified = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))

        # Fayl mazmunini o‘qish
        with open(file_path, "rb") as f:
            filedata = f.read()

        # Konsolga chiqarish
        print(f"Fayl: {filename}")
        print(f"  Hajmi: {size} bayt")
        print(f"  Yaratilgan: {created}")
        print(f"  Oxirgi o‘zgartirilgan: {modified}")
        print("-" * 40)

        # Bazaga yozish
        cursor.execute("""
        INSERT INTO files (filename, size, created, modified, filedata)
        VALUES (?, ?, ?, ?, ?)
        """, (filename, size, str(created), str(modified), filedata))

# O‘zgarishlarni saqlash va ulanishni yopish
conn.commit()
conn.close()

print("✅ Fayllar bazaga saqlandi (metadata + mazmuni bilan)!")
