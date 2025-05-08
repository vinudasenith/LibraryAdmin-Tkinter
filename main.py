import sqlite3
import csv
import tkinter as tk
from tkinter import messagebox
import time
from tkinter import messagebox, ttk

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

    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM Books")
    books = cursor.fetchall()
    connection.close()
    return books

DB_FILE = "database/library.db"


def fetch_students(search_query=""):

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




def delete_book(book_id):

    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()
    cursor.execute("DELETE FROM Books WHERE book_id = ?", (book_id,))
    connection.commit()
    connection.close()


def edit_book(book_id, title=None, author=None, genre=None, year=None, quantity=None):

    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()

    # Check if the book exists
    cursor.execute("SELECT * FROM Books WHERE book_id = ?", (book_id,))
    book = cursor.fetchone()

    if not book:
        messagebox.showerror("Error", f"Book with ID {book_id} not found.")
        connection.close()
        return False

    # Build the update query dynamically
    updates = []
    values = []

    if title:
        updates.append("title = ?")
        values.append(title)
    if author:
        updates.append("author = ?")
        values.append(author)
    if genre:
        updates.append("genre = ?")
        values.append(genre)
    if year:
        updates.append("year = ?")
        values.append(year)
    if quantity:
        updates.append("quantity = ?")
        values.append(quantity)

    if updates:
        query = f"UPDATE Books SET {', '.join(updates)} WHERE book_id = ?"
        values.append(book_id)
        cursor.execute(query, values)
        connection.commit()
        messagebox.showinfo("Success", f"Book with ID {book_id} updated successfully.")

    connection.close()
    return True

def return_book(issue_id, return_date):

    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()

    # Get the book_id for the issued record
    cursor.execute("SELECT book_id FROM IssuedBooks WHERE issue_id = ?", (issue_id,))
    result = cursor.fetchone()
    if result:
        book_id = result[0]
        # Increase the book quantity
        cursor.execute("UPDATE Books SET quantity = quantity + 1 WHERE book_id = ?", (book_id,))
        # Update the return date in the IssuedBooks table
        cursor.execute("UPDATE IssuedBooks SET return_date = ? WHERE issue_id = ?", (return_date, issue_id))
        connection.commit()
        print("Book returned successfully.")
    else:
        print("Invalid issue ID.")

    connection.close()



def add_student(name, email, date_of_birth, student_id):

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




def update_time(label):

    current_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")  # Format: DD-MM-YYYY HH:MM:SS
    label.config(text=f"Date & Time: {current_time}")
    label.after(1000, update_time, label)  # Refresh every second

def add_books_window():

    window = tk.Toplevel()
    window.title("Add Book")
    window.geometry("350x400")
    window.configure(bg="#f0f0f0")  # Light gray background

    # Header Label
    header = tk.Label(window, text="Add a New Book", font=("Arial", 14, "bold"), bg="#f0f0f0", fg="#333")
    header.pack(pady=10)

    # Create a frame for form fields
    form_frame = tk.Frame(window, bg="#f0f0f0")
    form_frame.pack(padx=20, pady=10, fill="both", expand=True)

    # Function to create labeled entry fields
    def create_field(label_text):
        frame = tk.Frame(form_frame, bg="#f0f0f0")
        frame.pack(fill="x", pady=5)
        label = tk.Label(frame, text=label_text, font=("Arial", 10, "bold"), width=10, anchor="w", bg="#f0f0f0")
        label.pack(side="left", padx=5)
        entry = tk.Entry(frame, width=25, font=("Arial", 10))
        entry.pack(side="right", padx=5)
        return entry

    # Create fields
    book_id_entry = create_field("Book ID:")
    title_entry = create_field("Title:")
    author_entry = create_field("Author:")
    genre_entry = create_field("Genre:")
    year_entry = create_field("Year:")
    quantity_entry = create_field("Quantity:")

    # Submit Button
    submit_button = tk.Button(window, text="Submit", font=("Arial", 11, "bold"), bg="#4CAF50", fg="white",
                              padx=10, pady=5, width=15, command=lambda: submit())
    submit_button.pack(pady=15)

    def submit():
        book_id = book_id_entry.get()
        title = title_entry.get()
        author = author_entry.get()
        genre = genre_entry.get()
        year = year_entry.get()
        quantity = quantity_entry.get()

        if not (book_id and title and author and genre and year and quantity):
            messagebox.showwarning("Warning", "All fields must be filled!")
            return

        try:
            book_id = int(book_id)  # Ensure book_id is an integer
            year = int(year)  # Ensure year is an integer
            quantity = int(quantity)  # Ensure quantity is an integer
            messagebox.showinfo("Success", "Book added successfully!")  # Temporary confirmation
            window.destroy()  # Close the window after submission
        except ValueError:
            messagebox.showerror("Error", "Book ID, Year, and Quantity must be numbers!")


    def submit():
        book_id = book_id_entry.get()
        title = title_entry.get()
        author = author_entry.get()
        genre = genre_entry.get()
        year = year_entry.get()
        quantity = quantity_entry.get()

        if not (book_id and title and author and genre and year and quantity):
            messagebox.showwarning("Warning", "All fields must be filled!")
            return

        try:
            book_id = int(book_id)  # Ensure book_id is an integer
            year = int(year)  # Ensure year is an integer
            quantity = int(quantity)  # Ensure quantity is an integer
            add_book(book_id, title, author, genre, year, quantity)
            window.destroy()  # Close the window after submission
        except ValueError:
            messagebox.showerror("Error", "Book ID, Year, and Quantity must be numbers!")

    submit_button = tk.Button(window, text="Submit", command=submit)
    submit_button.pack()

# Add Student Window


def add_student_window():

    window = tk.Toplevel()
    window.title("Add Student")
    window.geometry("350x300")
    window.configure(bg="#f0f0f0")  # Light gray background

    # Header Label
    header = tk.Label(window, text="Add a New Student", font=("Arial", 14, "bold"), bg="#f0f0f0", fg="#333")
    header.pack(pady=10)

    # Create a frame for form fields
    form_frame = tk.Frame(window, bg="#f0f0f0")
    form_frame.pack(padx=20, pady=10, fill="both", expand=True)

    # Function to create labeled entry fields
    def create_field(label_text):
        frame = tk.Frame(form_frame, bg="#f0f0f0")
        frame.pack(fill="x", pady=5)
        label = tk.Label(frame, text=label_text, font=("Arial", 10, "bold"), width=15, anchor="w", bg="#f0f0f0")
        label.pack(side="left", padx=5)
        entry = tk.Entry(frame, width=25, font=("Arial", 10))
        entry.pack(side="right", padx=5)
        return entry

    # Create fields
    student_id_entry = create_field("Student ID:")
    name_entry = create_field("Name:")
    email_entry = create_field("Email:")
    dob_entry = create_field("Date of Birth:")

    # Submit Button
    submit_button = tk.Button(window, text="Submit", font=("Arial", 11, "bold"), bg="#4CAF50", fg="white",
                              padx=10, pady=5, width=15, command=lambda: submit())
    submit_button.pack(pady=15)

    def submit():
        student_id = student_id_entry.get()
        name = name_entry.get()
        email = email_entry.get()
        date_of_birth = dob_entry.get()

        if not (student_id and name and email and date_of_birth):
            messagebox.showwarning("Warning", "All fields must be filled!")
            return

        try:
            student_id = int(student_id)  # Ensure student_id is an integer
            add_student(name, email, date_of_birth, student_id)
            messagebox.showinfo("Success", "Student added successfully!")
            window.destroy()  # Close the window after submission
        except ValueError:
            messagebox.showerror("Error", "Student ID must be a number!")

    window.mainloop()

# Generic Form Window
def create_form_window(title, labels, button_text, success_message):
    window = tk.Toplevel()
    window.title(title)
    window.geometry("600x400")
    window.configure(bg="white")

    # Header
    header_frame = tk.Frame(window, bg="#6C8EBF", height=50)
    header_frame.pack(fill="x")
    tk.Label(
        header_frame, text=title.upper(), font=("Arial", 20, "bold"), bg="#6C8EBF", fg="white"
    ).pack(pady=5)

    # Back Button
    back_button = tk.Button(
        window, text="← BACK", font=("Arial", 12), bg="red", fg="white", command=window.destroy
    )
    back_button.place(x=10, y=10)

    # Form
    form_frame = tk.Frame(window, bg="white", padx=20, pady=20)
    form_frame.pack(pady=20)

    entries = {}
    for i, label_text in enumerate(labels):
        tk.Label(
            form_frame, text=label_text, font=("Arial", 14), bg="white"
        ).grid(row=i, column=0, sticky="w", pady=10)

        entry = tk.Entry(form_frame, font=("Arial", 14), width=25)
        entry.grid(row=i, column=1, pady=10)
        entries[label_text] = entry

    # Submit Function
    def submit_action():
        details = {key: entry.get() for key, entry in entries.items()}
        if all(details.values()):
            messagebox.showinfo("Success", success_message)
            window.destroy()
        else:
            messagebox.showerror("Error", "Please fill in all fields!")

    # Reset Form
    def reset_form():
        for entry in entries.values():
            entry.delete(0, tk.END)

    # Buttons
    submit_button = tk.Button(
        form_frame, text=button_text, font=("Arial", 14), bg="#32CD32", fg="white", command=submit_action
    )
    submit_button.grid(row=len(labels), column=0, pady=20)

    reset_button = tk.Button(
        form_frame, text="Reset", font=("Arial", 14), bg="#FFA500", fg="white", command=reset_form
    )
    reset_button.grid(row=len(labels), column=1, pady=20)

# Show Books Window

def fetch_books():

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT book_id, title, author, genre, year, quantity FROM Books")
    books = cursor.fetchall()  # Get all books
    conn.close()
    return books


def show_books_window():
    show_books = tk.Toplevel()
    show_books.title("Library Books")
    show_books.geometry("800x600")
    show_books.configure(bg="white")

    # Header
    header_frame = tk.Frame(show_books, bg="#6C8EBF", height=50)
    header_frame.pack(fill="x")
    tk.Label(header_frame, text="BOOK LIST", font=("Arial", 20, "bold"), bg="#6C8EBF", fg="white").pack(pady=5)

    # Back Button
    back_button = tk.Button(show_books, text="← BACK", font=("Arial", 12), bg="red", fg="white",
                            command=show_books.destroy)
    back_button.place(x=10, y=10)

    # Search Bar
    search_frame = tk.Frame(show_books, bg="white", padx=20, pady=5)
    search_frame.pack(fill="x")

    tk.Label(search_frame, text="Search:", font=("Arial", 12), bg="white").pack(side="left", padx=10)
    search_entry = tk.Entry(search_frame, font=("Arial", 12), width=40)
    search_entry.pack(side="left", padx=5)

    # Table Frame
    table_frame = tk.Frame(show_books, bg="white", padx=20, pady=20)
    table_frame.pack(fill="both", expand=True)

    columns = ("Book ID", "Title", "Author", "Genre", "Year", "Quantity")
    tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)

    # Define columns
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, anchor="center", width=130)

    tree.pack(fill="both", expand=True, side="left")

    # Adding scrollbars
    scrollbar_y = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
    scrollbar_y.pack(side="right", fill="y")
    tree.configure(yscrollcommand=scrollbar_y.set)

    # Fetch and insert actual data from the database
    books = fetch_books()

    def update_table(search_text=""):

        tree.delete(*tree.get_children())  # Clear table
        for book in books:
            if search_text.lower() in book[1].lower() or search_text.lower() in book[
                2].lower() or search_text.lower() in book[3].lower():
                tree.insert("", tk.END, values=book)

    # Search Functionality
    def on_search(event):
        update_table(search_entry.get().strip())

    search_entry.bind("<KeyRelease>", on_search)  # Detects input changes

    update_table()  # Populate table initially


def fetch_students(search_query=""):

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
    return students



def show_students_window():

    show_students = tk.Toplevel()
    show_students.title("Student Details")
    show_students.geometry("800x600")
    show_students.configure(bg="white")

    # Header
    header_frame = tk.Frame(show_students, bg="#6C8EBF", height=50)
    header_frame.pack(fill="x")
    tk.Label(header_frame, text="STUDENT LIST", font=("Arial", 20, "bold"), bg="#6C8EBF", fg="white").pack(pady=5)

    # Search Bar
    search_frame = tk.Frame(show_students, bg="white", padx=10, pady=10)
    search_frame.pack(fill="x")

    tk.Label(search_frame, text="Search:", font=("Arial", 14), bg="white").pack(side="left", padx=10)
    search_entry = tk.Entry(search_frame, font=("Arial", 14), width=30)
    search_entry.pack(side="left", padx=10)

    def search_students():
        query = search_entry.get().strip()
        update_student_table(fetch_students(query))

    search_button = tk.Button(search_frame, text="Search", font=("Arial", 12), bg="#FFA500", fg="white", command=search_students)
    search_button.pack(side="left", padx=10)

    # Table Frame
    table_frame = tk.Frame(show_students, bg="white", padx=20, pady=20)
    table_frame.pack(fill="both", expand=True)

    columns = ("Student ID", "Name", "Email", "Date of Birth")
    tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, anchor="center", width=180)

    tree.pack(fill="both", expand=True, side="left")

    # Scrollbars
    scrollbar_y = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
    scrollbar_y.pack(side="right", fill="y")
    tree.configure(yscrollcommand=scrollbar_y.set)

    def update_student_table(data):

        tree.delete(*tree.get_children())  # Clear table

        #print("Updating table with:", data)  # Debugging print statement

        if not data:
            messagebox.showinfo("Info", "No students found!")
        for student in data:
            tree.insert("", tk.END, values=student)

# Issue Book Window
def edit_books_window():

    edit_books = tk.Toplevel()
    edit_books.title("Edit Book")
    edit_books.geometry("500x450")
    edit_books.configure(bg="white")

    # Header
    header_frame = tk.Frame(edit_books, bg="#6C8EBF", height=50)
    header_frame.pack(fill="x")
    tk.Label(
        header_frame, text="EDIT BOOK", font=("Arial", 18, "bold"), bg="#6C8EBF", fg="white"
    ).pack(pady=10)

    # Form Frame
    form_frame = tk.Frame(edit_books, bg="white", padx=20, pady=20)
    form_frame.pack(pady=20)

    # Book ID Input
    tk.Label(form_frame, text="Enter Book ID:", font=("Arial", 12), bg="white").grid(row=0, column=0, sticky="w",
                                                                                     pady=5)
    book_id_entry = tk.Entry(form_frame, font=("Arial", 12), width=25)
    book_id_entry.grid(row=0, column=1, pady=5)

    # Book Details Form (Initially Empty)
    labels = ["Title:", "Author:", "Genre:", "Year:", "Quantity:"]
    entries = {}

    for i, label_text in enumerate(labels, 1):
        tk.Label(form_frame, text=label_text, font=("Arial", 12), bg="white").grid(row=i, column=0, sticky="w",
                                                                                   pady=5)
        entry = tk.Entry(form_frame, font=("Arial", 12), width=25)
        entry.grid(row=i, column=1, pady=5)
        entries[label_text] = entry

    # Function to Fetch Book Details
    def fetch_book_details():
        book_id = book_id_entry.get().strip()
        if not book_id.isdigit():
            messagebox.showwarning("Invalid Input", "Book ID must be a number!")
            return

        connection = sqlite3.connect(DB_FILE)
        cursor = connection.cursor()
        cursor.execute("SELECT title, author, genre, year, quantity FROM Books WHERE book_id = ?", (book_id,))
        book = cursor.fetchone()
        connection.close()

        if book:
            # Populate fields
            for entry, value in zip(entries.values(), book):
                entry.delete(0, tk.END)
                entry.insert(0, value)
        else:
            messagebox.showerror("Error", f"Book with ID {book_id} not found.")

    # Function to Submit Edits
    def submit_edit():
        book_id = book_id_entry.get().strip()
        if not book_id.isdigit():
            messagebox.showwarning("Invalid Input", "Book ID must be a number!")
            return

        book_id = int(book_id)
        updates = {label: entry.get().strip() for label, entry in entries.items()}

        # Convert numeric fields
        try:
            updates["Year:"] = int(updates["Year:"]) if updates["Year:"] else None
            updates["Quantity:"] = int(updates["Quantity:"]) if updates["Quantity:"] else None
        except ValueError:
            messagebox.showerror("Error", "Year and Quantity must be numbers!")
            return

        # Call edit_book function
        edit_book(book_id, updates["Title:"], updates["Author:"], updates["Genre:"], updates["Year:"],
                  updates["Quantity:"])

    # Buttons
    tk.Button(form_frame, text="Search", font=("Arial", 12, "bold"), bg="#FFA500", fg="white",
              command=fetch_book_details).grid(row=0, column=2, padx=10)

    submit_button = tk.Button(edit_books, text="Update Book", font=("Arial", 12, "bold"), bg="#4CAF50", fg="white",
                              width=20, pady=5, command=submit_edit)
    submit_button.pack(pady=10)

    back_button = tk.Button(edit_books, text="Back", font=("Arial", 12, "bold"), bg="red", fg="white",
                            width=10, command=edit_books.destroy)
    back_button.pack(pady=5)
    # Update Book Function
    def update_book():
        book_id = book_id_entry.get()
        title = entries["Book Title:"].get()
        author = entries["Author:"].get()
        stock = entries["Stock:"].get()

        if book_id and title and author and stock:
            try:
                import sqlite3
                conn = sqlite3.connect("library.db")
                cursor = conn.cursor()

                # Update book details in the database
                cursor.execute(
                    "UPDATE books SET title = ?, author = ?, stock = ? WHERE book_id = ?",
                    (title, author, stock, book_id)
                )
                conn.commit()

                messagebox.showinfo("Success", "Book details updated successfully!")
                edit_books.destroy()
                conn.close()
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {e}")
        else:
            messagebox.showerror("Error", "Please fill in all required fields!")

    # Buttons
    search_button = tk.Button(
        form_frame, text="Search", font=("Arial", 14), bg="#32CD32", fg="white", command=fetch_books()
    )
    search_button.grid(row=0, column=2, padx=10, pady=10)

    submit_button = tk.Button(
        form_frame, text="Update", font=("Arial", 14), bg="#32CD32", fg="white", command=update_book
    )
    submit_button.grid(row=len(labels)+1, column=0, pady=20)

    # Reset Form
    def reset_form():
        book_id_entry.delete(0, tk.END)
        for entry in entries.values():
            entry.delete(0, tk.END)

    reset_button = tk.Button(
        form_frame, text="Reset", font=("Arial", 14), bg="#FFA500", fg="white", command=reset_form
    )
    reset_button.grid(row=len(labels)+1, column=1, pady=20)


# Login Function

def logout(root):

    confirm = messagebox.askyesno("Logout", "Are you sure you want to log out?")
    if confirm:
        messagebox.showinfo("Logout", "You have been logged out.")
        root.destroy()  # Close dashboard
        restart_login()  # Return to login screen

def restart_login():

    root = tk.Tk()
    root.title("Library Management System - Login")
    root.geometry("900x600")
    root.resizable(False, False)
    root.config(bg="#E3F2FD")  # Soft Blue Background

    #  Canvas Background
    canvas = tk.Canvas(root, width=900, height=600, bg="#E3F2FD", highlightthickness=0)
    canvas.pack(fill="both", expand=True)

    #  Login Frame
    login_frame = tk.Frame(root, bg="white", padx=40, pady=40, relief="raised", bd=5)
    login_frame.place(relx=0.5, rely=0.5, anchor="center")

    tk.Label(login_frame, text="🔐 Login System", font=("Arial", 22, "bold"), bg="white", fg="#2C3E50").grid(row=0,
                                                                                                            column=0,
                                                                                                            columnspan=2,
                                                                                                            pady=15)

    tk.Label(login_frame, text="👤 Username:", font=("Arial", 14), bg="white", fg="#2C3E50").grid(row=1, column=0,
                                                                                                 sticky="w", pady=10)
    username_entry = tk.Entry(login_frame, font=("Arial", 14), width=22, relief="solid", bd=2)
    username_entry.grid(row=1, column=1, pady=10, padx=10)

    tk.Label(login_frame, text="🔑 Password:", font=("Arial", 14), bg="white", fg="#2C3E50").grid(row=2, column=0,
                                                                                                 sticky="w", pady=10)

    # Password Entry with Toggle Button
    password_frame = tk.Frame(login_frame, bg="white")
    password_frame.grid(row=2, column=1, pady=10, padx=10)

    password_entry = tk.Entry(password_frame, font=("Arial", 14), width=20, show="*", relief="solid", bd=2)
    password_entry.pack(side="left")

    #  Password Toggle Button
    toggle_button = tk.Button(password_frame, text="👁️", font=("Arial", 10), bg="white", relief="flat",
                              command=lambda: toggle_password(password_entry))
    toggle_button.pack(side="right")

    #  Login Button
    login_button = tk.Button(login_frame, text="🚀 Login", font=("Arial", 14, "bold"), bg="#3498DB", fg="white",
                             width=20,
                             relief="flat", bd=3, activebackground="#2980B9",
                             command=lambda: login(root, username_entry, password_entry))
    login_button.grid(row=3, column=0, columnspan=2, pady=20)

    root.mainloop()


def toggle_password(entry):

    if entry.cget("show") == "*":
        entry.config(show="")
    else:
        entry.config(show="*")


def login(root, username_entry, password_entry):

    username = username_entry.get()
    password = password_entry.get()
    if username == "admin" and password == "admin":
        root.destroy()  # Close login window
        open_dashboard()  # Open dashboard
    else:
        messagebox.showerror("❌ Error", "Invalid Username or Password")



#  Light & Dark Theme Colors
LIGHT_THEME = {"bg": "#F8F9FA", "fg": "#2C3E50", "button_bg": "#3498DB", "button_hover": "#2980B9"}
DARK_THEME = {"bg": "#2C3E50", "fg": "white", "button_bg": "#E67E22", "button_hover": "#D35400"}

current_theme = LIGHT_THEME  # Default theme


def update_time(label):

    current_time = time.strftime("%Y-%m-%d %H:%M:%S")
    label.config(text=current_time)
    label.after(1000, lambda: update_time(label))  # ✅ Fixed update_time issue


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

    global header_frame, title_label, time_label, buttons, theme_button  # Reference UI elements for theme switching

    dashboard = tk.Tk()
    dashboard.title("📚 Library Management System - Dashboard")
    dashboard.geometry("1000x700")
    dashboard.resizable(False, False)
    dashboard.config(bg=current_theme["bg"])

    #  Header Frame (Dynamic Theme)
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
        btn.bind("<Enter>", on_enter)  # Hover effect
        btn.bind("<Leave>", on_leave)
        buttons.append(btn)  # Store buttons for theme update

    #  Theme Toggle Button
    theme_button = tk.Button(
        dashboard, text="🌙 Toggle Theme", font=("Arial", 14, "bold"), bg=current_theme["button_bg"], fg="white",
        width=20, height=2, relief="raised", bd=4, command=lambda: toggle_theme(dashboard)
    )
    theme_button.pack(pady=20)

    dashboard.mainloop()

restart_login()

