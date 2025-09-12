import sqlite3

def search_by_name(name):
    cursor.execute("SELECT * FROM files WHERE filename LIKE ?", ('%' + name + '%',))
    results = cursor.fetchall()
    return results

def search_by_extension(extension):
    cursor.execute("SELECT * FROM files WHERE filename LIKE ?", ('%' + extension,))
    results = cursor.fetchall()
    return results

def get_largest_file():
    cursor.execute("SELECT * FROM files ORDER BY size DESC LIMIT 1")
    result = cursor.fetchone()
    return result

def get_recent_files(limit=5):
    cursor.execute("SELECT * FROM files ORDER BY created DESC LIMIT ?", (limit,))
    results = cursor.fetchall()
    return results


if __name__ == "__main__":
    # Bazaga ulanamiz
    conn = sqlite3.connect("files.db")
    cursor = conn.cursor()

    while True:
        print("\n📂 Fayl qidiruv tizimi")
        print("1. Fayl nomi bo‘yicha qidirish")
        print("2. Fayl kengaytmasi bo‘yicha qidirish (.pdf, .txt ...)")
        print("3. Eng katta faylni ko‘rish")
        print("4. Yaqinda yaratilgan fayllar")
        print("5. Chiqish")

        choice = input("Tanlang (1-5): ")

        if choice == "1":
            name = input("Fayl nomini kiriting: ")
            results = search_by_name(name)
            for row in results:
                print(row)

        elif choice == "2":
            ext = input("Kengaytma kiriting (masalan: .pdf): ")
            results = search_by_extension(ext)
            for row in results:
                print(row)

        elif choice == "3":
            result = get_largest_file()
            print("Eng katta fayl:", result)

        elif choice == "4":
            results = get_recent_files()
            print("Yaqinda yaratilgan fayllar:")
            for row in results:
                print(row)

        elif choice == "5":
            print("Chiqildi ✅")
            break
        else:
            print("Noto‘g‘ri tanlov!")
    
    conn.close()
