
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



def add_book(book_id, title, author, genre, year, quantity):
    """
    Adds a new book to the Books table.

    Parameters:
    - book_id (int): Unique identifier for the book.
    - title (str): The title of the book.
    - author (str): The author of the book.
    - genre (str): The genre of the book.
    - year (int): The publication year of the book.
    - quantity (int): Number of copies available.
    """
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()

    try:
        cursor.execute("""
        INSERT INTO Books (book_id, title, author, genre, year, quantity)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (book_id, title, author, genre, year, quantity))
        connection.commit()
        print("Book added successfully.")
        messagebox.showinfo("Success", "Book added successfully!")
    except sqlite3.IntegrityError:
        print("Error: Book ID must be unique.")
        messagebox.showerror("Error", "Book ID already exists!")
    except Exception as e:
        print(f"Error: {e}")
        messagebox.showerror("Error", f"Failed to add book: {e}")
    finally:
        connection.close()


def show_books():
    """Retrieve and return all books from the Books table."""
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM Books")
    books = cursor.fetchall()
    connection.close()
    return books



def fetch_students(search_query=""):
    """Fetch students from the database and print results for debugging."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    if search_query:
        cursor.execute(
            "SELECT student_id, name, email, date_of_birth FROM Students WHERE student_id LIKE ? OR name LIKE ?",
            (f"%{search_query}%", f"%{search_query}%")
        )
    else:
        cursor.execute("SELECT student_id, name, email, date_of_birth FROM Students")

    students = cursor.fetchall()
    conn.close()

    #print("Fetched Students:", students)  # Debugging print statement
    #return students


def add_student(name, email, date_of_birth, student_id):
    """
    Adds a new student to the Students table.

    Parameters:
    - student_id (int): Unique ID of the student.
    - name (str): The name of the student.
    - email (str): The email of the student (must be unique).
    - date_of_birth (str): The date of birth in YYYY-MM-DD format.
    """
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()

    try:
        cursor.execute("""
        INSERT INTO Students (student_id, name, email, date_of_birth)
        VALUES (?, ?, ?, ?)
        """, (student_id, name, email, date_of_birth))
        connection.commit()
        print("Student added successfully.")
        messagebox.showinfo("Success", "Student added successfully!")
    except sqlite3.IntegrityError:
        print("Error: Student ID or Email must be unique.")
        messagebox.showerror("Error", "Student ID or Email already exists!")
    finally:
        connection.close()


from datetime import datetime

def update_time(label):
    """Update the label with the current date and time."""
    current_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")  # Format: DD-MM-YYYY HH:MM:SS
    label.config(text=f"Date & Time: {current_time}")
    label.after(1000, update_time, label)  # Refresh every second

    







