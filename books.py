import tkinter as tk
from tkinter import ttk, messagebox
from database import connect_db

class BooksWindow:
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("Book Management")
        self.window.geometry("1000x600")
        self.create_widgets()
        self.load_books()

    def create_widgets(self):
        form = tk.LabelFrame(self.window, text="Book Details")
        form.pack(fill="x", padx=10, pady=10)
        tk.Label(form, text="Title").grid(row=0, column=0, padx=10, pady=10)
        self.title_entry = tk.Entry(form, width=25)
        self.title_entry.grid(row=0, column=1)
        tk.Label(form, text="Author").grid(row=0, column=2)
        self.author_entry = tk.Entry(form, width=25)
        self.author_entry.grid(row=0, column=3)
        tk.Label(form, text="Category").grid(row=1, column=0, padx=10, pady=10)
        self.category_entry = tk.Entry(form, width=25)
        self.category_entry.grid(row=1, column=1)
        tk.Label(form, text="Quantity").grid(row=1, column=2)
        self.quantity_entry = tk.Entry(form, width=25)
        self.quantity_entry.grid(row=1, column=3)
        button_frame = tk.Frame(form)
        button_frame.grid(row=2, column=0, columnspan=4, pady=10)
        tk.Button(button_frame,text="Add", width=12, command=self.add_book).pack(side="left", padx=5)
        tk.Button(button_frame, text="Update", width=12, command=self.update_book).pack(side="left", padx=5)
        tk.Button(button_frame, text="Delete", width=12, command=self.delete_book).pack(side="left", padx=5)
        tk.Button(button_frame, text="Clear", width=12, command=self.clear_fields).pack(side="left", padx=5)
        search_frame = tk.Frame(self.window)
        search_frame.pack(fill="x", padx=10)
        tk.Label(search_frame, text="Search:").pack(side="left")
        self.search_entry = tk.Entry(search_frame, width=30)
        self.search_entry.pack( side="left", padx=10)
        tk.Button(search_frame, text="Search", command=self.search_books).pack(side="left")
        tk.Button(search_frame, text="Show All", command=self.load_books).pack(side="left", padx=5)
        columns = (
            "ID",
            "Title",
            "Author",
            "Category",
            "Quantity",
            "Available"
        )
        self.tree = ttk.Treeview(self.window, columns=columns, show="headings")

        for column in columns:

            self.tree.heading(
                column,
                text=column
            )

        self.tree.column("ID", width=50)
        self.tree.column("Title", width=220)
        self.tree.column("Author", width=180)
        self.tree.column("Category", width=120)
        self.tree.column("Quantity", width=100)
        self.tree.column("Available", width=100)

        self.tree.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )

        self.tree.bind(
            "<ButtonRelease-1>",
            self.select_book
        )

    def load_books(self, search=""):

        for item in self.tree.get_children():

            self.tree.delete(item)

        conn = connect_db()
        cursor = conn.cursor()

        if search:

            cursor.execute(
                """
                SELECT *
                FROM books
                WHERE title LIKE ?
                OR author LIKE ?
                OR category LIKE ?
                ORDER BY id DESC
                """,
                (
                    "%" + search + "%",
                    "%" + search + "%",
                    "%" + search + "%"
                )
            )

        else:

            cursor.execute(
                "SELECT * FROM books ORDER BY id DESC"
            )

        rows = cursor.fetchall()

        conn.close()

        for row in rows:

            self.tree.insert(
                "",
                "end",
                values=row
            )

    def add_book(self):

        title = self.title_entry.get().strip()
        author = self.author_entry.get().strip()
        category = self.category_entry.get().strip()
        quantity = self.quantity_entry.get().strip()

        if not title or not author or not quantity:

            messagebox.showwarning(
                "Validation",
                "Title, author and quantity are required.",
                parent=self.window
            )

            return

        try:

            quantity = int(quantity)

            if quantity <= 0:
                raise ValueError

        except ValueError:

            messagebox.showerror(
                "Error",
                "Quantity must be a positive number.",
                parent=self.window
            )

            return

        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO books
            (title, author, category, quantity, available)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                title,
                author,
                category,
                quantity,
                quantity
            )
        )

        conn.commit()
        conn.close()

        messagebox.showinfo(
            "Success",
            "Book added successfully.",
            parent=self.window
        )

        self.clear_fields()
        self.load_books()

    def update_book(self):

        selected = self.tree.selection()

        if not selected:

            messagebox.showwarning(
                "Update",
                "Select a book first.",
                parent=self.window
            )

            return

        book_id = self.tree.item(
            selected[0]
        )["values"][0]

        title = self.title_entry.get().strip()
        author = self.author_entry.get().strip()
        category = self.category_entry.get().strip()

        try:

            quantity = int(
                self.quantity_entry.get().strip()
            )

            if quantity <= 0:
                raise ValueError

        except ValueError:

            messagebox.showerror(
                "Error",
                "Invalid quantity.",
                parent=self.window
            )

            return

        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT quantity, available
            FROM books
            WHERE id = ?
            """,
            (book_id,)
        )

        old_quantity, old_available = cursor.fetchone()

        issued = old_quantity - old_available

        if quantity < issued:

            messagebox.showerror(
                "Error",
                f"{issued} copies are currently issued.",
                parent=self.window
            )

            conn.close()

            return

        available = quantity - issued

        cursor.execute(
            """
            UPDATE books
            SET title = ?,
                author = ?,
                category = ?,
                quantity = ?,
                available = ?
            WHERE id = ?
            """,
            (
                title,
                author,
                category,
                quantity,
                available,
                book_id
            )
        )

        conn.commit()
        conn.close()

        self.clear_fields()
        self.load_books()

    def delete_book(self):

        selected = self.tree.selection()

        if not selected:

            messagebox.showwarning(
                "Delete",
                "Select a book first.",
                parent=self.window
            )

            return

        book_id = self.tree.item(
            selected[0]
        )["values"][0]

        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM transactions
            WHERE book_id = ?
            AND status = 'Issued'
            """,
            (book_id,)
        )

        active = cursor.fetchone()[0]

        if active:

            messagebox.showerror(
                "Error",
                "This book is currently issued.",
                parent=self.window
            )

            conn.close()

            return

        answer = messagebox.askyesno(
            "Delete",
            "Delete selected book?",
            parent=self.window
        )

        if answer:

            cursor.execute(
                "DELETE FROM books WHERE id = ?",
                (book_id,)
            )

            conn.commit()

        conn.close()

        self.load_books()

    def select_book(self, event):

        selected = self.tree.selection()

        if not selected:
            return

        values = self.tree.item(
            selected[0]
        )["values"]

        self.clear_fields()

        self.title_entry.insert(0, values[1])
        self.author_entry.insert(0, values[2])
        self.category_entry.insert(0, values[3])
        self.quantity_entry.insert(0, values[4])

    def clear_fields(self):

        self.title_entry.delete(0, tk.END)
        self.author_entry.delete(0, tk.END)
        self.category_entry.delete(0, tk.END)
        self.quantity_entry.delete(0, tk.END)

    def search_books(self):

        search = self.search_entry.get().strip()

        self.load_books(search)