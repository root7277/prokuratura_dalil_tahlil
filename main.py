import os
import datetime
import sqlite3

# 1️⃣ SQLite bazasiga ulanish (agar mavjud bo'lmasa, avtomatik yaratiladi)
conn = sqlite3.connect("files.db")
cursor = conn.cursor()

# 2️⃣ Jadval yaratish (agar mavjud bo'lmasa)
cursor.execute("""
CREATE TABLE IF NOT EXISTS files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT,
    size INTEGER,
    created TEXT,
    modified TEXT
)
""")

# 3️⃣ Tekshiriladigan papka
folder_path = "/home/kali/Downloads"

# 4️⃣ Fayllarni ko‘rib chiqamiz
for filename in os.listdir(folder_path):
    file_path = os.path.join(folder_path, filename)

    if os.path.isfile(file_path):
        size = os.path.getsize(file_path)
        created = datetime.datetime.fromtimestamp(os.path.getctime(file_path))
        modified = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))

        # Konsolga chiqarish
        print(f"Fayl: {filename}")
        print(f"  Hajmi: {size} bayt")
        print(f"  Yaratilgan: {created}")
        print(f"  Oxirgi o'zgartirilgan: {modified}")
        print("-" * 40)

        # 5️⃣ Bazaga yozish
        cursor.execute("""
        INSERT INTO files (filename, size, created, modified)
        VALUES (?, ?, ?, ?)
        """, (filename, size, str(created), str(modified)))

# 6️⃣ O‘zgarishlarni saqlash va ulanishni yopish
conn.commit()
conn.close()

print("✅ Fayllar haqidagi ma'lumotlar 'files.db' bazasiga saqlandi!")
