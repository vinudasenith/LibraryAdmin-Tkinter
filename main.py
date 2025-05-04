
import sqlite3
import csv

DB_FILE = "database/library.db"
BOOKS_CSV = "Books.csv"
STUDENTS_CSV = "Students.csv"
def initialize_database():
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Books (
        book_id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        author TEXT NOT NULL,
        genre TEXT,
        year INTEGER,
        quantity INTEGER NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Students (
        student_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        date_of_birth TEXT
    )
    """)

    connection.commit()
    connection.close()

def insert_books_from_csv():
    with open(BOOKS_CSV, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        for row in reader:
            try:
                book_id = row.get('book_id', '').strip()
                title = row.get('title', '').strip()
                author = row.get('author', '').strip()
                genre = row.get('genre', '').strip()

                year_str = row.get('year', '').strip()
                year = int(year_str) if year_str else None

                quantity_str = row.get('quantity', '').strip()
                quantity = int(quantity_str) if quantity_str else 0

                if not book_id or not title or not author:
                    continue

                cursor.execute("SELECT COUNT(*) FROM Books WHERE book_id = ?", (book_id,))
                if cursor.fetchone()[0] > 0:
                    continue

                cursor.execute("""
                    INSERT INTO Books (book_id, title, author, genre, year, quantity)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (book_id, title, author, genre, year, quantity))
            except sqlite3.IntegrityError:
                pass
            except KeyError:
                pass

        conn.commit()
        conn.close()


def insert_students_from_csv():
    with open(STUDENTS_CSV, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)

        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        for row in reader:
            try:
                name = row.get('name', '').strip()
                email = row.get('email', '').strip()
                date_of_birth = row.get('date_of_birth', '').strip()

                if not name or not email:
                    continue

                cursor.execute("SELECT COUNT(*) FROM Students WHERE email = ?", (email,))
                if cursor.fetchone()[0] > 0:
                    continue

                cursor.execute("""
                    INSERT INTO Students (name, email, date_of_birth)
                    VALUES (?, ?, ?)
                """, (name, email, date_of_birth))
            except sqlite3.IntegrityError:
                pass
            except KeyError:
                pass

        conn.commit()
        conn.close()

def remove_duplicate_students():
    seen_emails = set()
    unique_rows = []

    with open(STUDENTS_CSV, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            email = row.get('email', '').strip()
            if email not in seen_emails:
                seen_emails.add(email)
                unique_rows.append(row)

    with open(STUDENTS_CSV, 'w', encoding='utf-8', newline='') as file:
        fieldnames = ['student_id', 'name', 'email', 'date_of_birth']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(unique_rows)


def initialize_database():
    insert_books_from_csv()
    insert_students_from_csv()
    remove_duplicate_students()


