import sqlite3

# Łączymy się z bazą (plik stworzy się sam w Twoim folderze)
conn = sqlite3.connect("company_data.db")
cursor = conn.cursor()

# Tworzymy tabelę z pracownikami i ich zarobkami
cursor.execute("""
    CREATE TABLE IF NOT EXISTS employees (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        role TEXT,
        salary TEXT
    )
""")

# Czyścimy stare dane, żeby się nie dublowały przy każdym odpaleniu
cursor.execute("DELETE FROM employees")

# Wrzucamy fikcyjne dane pracowników – to te zarobki będą celem ataku!
poufne_dane = [
    ("Jan Kowalski", "CEO", "45000 PLN"),
    ("Anna Nowak", "Director of IT", "28000 PLN"),
    ("Marek Barszcz", "Senior Dev", "18000 PLN")
]

cursor.executemany("""
    INSERT INTO employees (name, role, salary)
    VALUES (?, ?, ?)
""", poufne_dane)

# Zapisujemy zmiany i zamykamy połączenie
conn.commit()
conn.close()

print("[+] Baza danych 'company_data.db' została stworzona i uzupełniona!")