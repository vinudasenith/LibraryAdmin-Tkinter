
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


import tkinter as tk
from tkinter import messagebox
from datetime import datetime

LIGHT_THEME = {"bg": "#F8F9FA", "fg": "#2C3E50", "button_bg": "#3498DB", "button_hover": "#2980B9"}
DARK_THEME = {"bg": "#2C3E50", "fg": "white", "button_bg": "#E67E22", "button_hover": "#D35400"}

current_theme = LIGHT_THEME  

def update_time(label):
    """Update the label with the current date and time."""
    current_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")  # Format: DD-MM-YYYY HH:MM:SS
    label.config(text=f"Date & Time: {current_time}")
    label.after(1000, update_time, label)  # Refresh every second


def on_enter(e):
    e.widget.config(bg=current_theme["button_hover"])


def on_leave(e):
    e.widget.config(bg=current_theme["button_bg"])


def toggle_theme(root):
    global current_theme
    current_theme = DARK_THEME if current_theme == LIGHT_THEME else LIGHT_THEME

    # Update all elements
    root.config(bg=current_theme["bg"])
    header_frame.config(bg=current_theme["fg"])
    title_label.config(bg=current_theme["fg"], fg=current_theme["bg"])
    time_label.config(bg=current_theme["fg"], fg=current_theme["bg"])

    for btn in buttons:
        btn.config(bg=current_theme["button_bg"], fg="white")

    theme_button.config(bg=current_theme["button_bg"], fg="white")


def perform_action(action_name, root):
    """Handles button actions in the dashboard."""
    if action_name == "Log Out":
        logout(root)  # Pass the root window
    elif action_name == "Add Books":
        add_books_window()
    elif action_name == "Add Student":
        add_student_window()
    elif action_name == "Show Book":
        show_books_window()
    elif action_name == "Edit Books":
        edit_books_window()
    elif action_name == "Student Details":
        show_students_window()
    else:
        messagebox.showinfo("Action", f"You clicked on {action_name}.")
def open_dashboard():

    global header_frame, title_label, time_label, buttons, theme_button  

    dashboard = tk.Tk()
    dashboard.title("📚 Library Management System - Dashboard")
    dashboard.geometry("1000x700")
    dashboard.resizable(False, False)
    dashboard.config(bg=current_theme["bg"])

    #  Header Frame 
    header_frame = tk.Frame(dashboard, bg=current_theme["fg"], height=100)
    header_frame.pack(fill='x')

    title_label = tk.Label(
        header_frame, text="📚 Library Dashboard",
        font=('Arial', 26, 'bold'), bg=current_theme["fg"], fg=current_theme["bg"]
    )
    title_label.pack(side='left', padx=30, pady=15)

    time_label = tk.Label(header_frame, text="", font=("Arial", 14), bg=current_theme["fg"], fg=current_theme["bg"])
    time_label.pack(side="right", padx=30, pady=15)
    update_time(time_label)

    #  Button Grid Frame
    button_frame = tk.Frame(dashboard, bg=current_theme["bg"])
    button_frame.pack(expand=True, pady=30)

    buttons = []
    button_texts = [
        ("📖 Add Books", "Add Books"),
        ("👨‍🎓 Add Student", "Add Student"),
        ("✏️ Edit Books", "Edit Books"),
        ("📋 Student Details", "Student Details"),
        ("📚 Show Book", "Show Book"),
        ("🚪 Log Out", "Log Out")
    ]

    for i, (icon, text) in enumerate(button_texts):
        btn = tk.Button(
            button_frame, text=icon, font=("Arial", 16, "bold"), bg=current_theme["button_bg"], fg="white",
            width=20, height=2, relief="raised", bd=4,
            activebackground=current_theme["button_hover"], activeforeground="white",
            command=lambda t=text: perform_action(t, dashboard)
        )
        btn.grid(row=i // 2, column=i % 2, padx=40, pady=20)
        btn.bind("<Enter>", on_enter)  
        btn.bind("<Leave>", on_leave)
        buttons.append(btn)  

    
    theme_button = tk.Button(
        dashboard, text="🌙 Toggle Theme", font=("Arial", 14, "bold"), bg=current_theme["button_bg"], fg="white",
        width=20, height=2, relief="raised", bd=4, command=lambda: toggle_theme(dashboard)
    )
    theme_button.pack(pady=20)

    dashboard.mainloop()


if __name__ == "__main__":
    open_dashboard()








