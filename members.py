import tkinter as tk
from tkinter import ttk, messagebox
from database import connect_db

class MembersWindow:
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("Member Management")
        self.window.geometry("1000x600")
        self.create_widgets()
        self.load_members()

    def create_widgets(self):
        form = tk.LabelFrame(self.window, text="Member Details")
        form.pack(fill="x", padx=10, pady=10)
        tk.Label(form, text="Name").grid(row=0, column=0, padx=10, pady=10)
        self.name_entry = tk.Entry(form, width=25)
        self.name_entry.grid(row=0, column=1)
        tk.Label(form, text="Phone").grid(row=0, column=2)
        self.phone_entry = tk.Entry(form, width=25)
        self.phone_entry.grid(row=0, column=3)
        tk.Label(form, text="Email").grid(row=1, column=0, padx=10, pady=10)
        self.email_entry = tk.Entry(form, width=25)
        self.email_entry.grid(row=1, column=1)
        tk.Label(form, text="Address").grid(row=1, column=2)
        self.address_entry = tk.Entry(form, width=25)
        self.address_entry.grid(row=1, column=3)
        buttons = tk.Frame(form)
        buttons.grid(row=2, column=0, columnspan=4, pady=10)
        tk.Button( buttons, text="Add", width=12, command=self.add_member).pack(side="left", padx=5)
        tk.Button(buttons, text="Update", width=12, command=self.update_member).pack(side="left", padx=5)
        tk.Button(buttons, text="Delete", width=12, command=self.delete_member).pack(side="left", padx=5)
        tk.Button(buttons, text="Clear", width=12, command=self.clear_fields).pack(side="left", padx=5)
        search_frame = tk.Frame(self.window)
        search_frame.pack(fill="x", padx=10)
        tk.Label(search_frame, text="Search:").pack(side="left")
        self.search_entry = tk.Entry(search_frame, width=30)
        self.search_entry.pack(side="left", padx=10)
        tk.Button(search_frame, text="Search", command=self.search_members).pack(side="left")
        tk.Button(search_frame, text="Show All", command=self.load_members).pack(side="left", padx=5)
        columns = (
            "ID",
            "Name",
            "Phone",
            "Email",
            "Address"
        )
        self.tree = ttk.Treeview(self.window, columns=columns, show="headings")
        for column in columns:
            self.tree.heading(column, text=column)
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)
        self.tree.bind("<ButtonRelease-1>", self.select_member)

    def load_members(self, search=""):
        for item in self.tree.get_children():
            self.tree.delete(item)
        conn = connect_db()
        cursor = conn.cursor()

        if search:
            cursor.execute(
                """
                SELECT *
                FROM members
                WHERE name LIKE ?
                OR phone LIKE ?
                OR email LIKE ?
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
                "SELECT * FROM members ORDER BY id DESC"
            )
        rows = cursor.fetchall()
        conn.close()

        for row in rows:
            self.tree.insert("", "end", values=row)

    def add_member(self):
        name = self.name_entry.get().strip()
        phone = self.phone_entry.get().strip()
        email = self.email_entry.get().strip()
        address = self.address_entry.get().strip()
        if not name:
            messagebox.showwarning(
                "Validation",
                "Name is required.",
                parent=self.window
            )
            return
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO members
            (name, phone, email, address)
            VALUES (?, ?, ?, ?)
            """,
            (
                name,
                phone,
                email,
                address
            )
        )
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Member added successfully.", parent=self.window)
        self.clear_fields()
        self.load_members()

    def update_member(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Update", "Select a member first.", parent=self.window)
            return
        member_id = self.tree.item(
            selected[0]
        )["values"][0]
        name = self.name_entry.get().strip()
        phone = self.phone_entry.get().strip()
        email = self.email_entry.get().strip()
        address = self.address_entry.get().strip()

        if not name:
            return
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE members
            SET name = ?,
                phone = ?,
                email = ?,
                address = ?
            WHERE id = ?
            """,
            (
                name,
                phone,
                email,
                address,
                member_id
            )
        )

        conn.commit()
        conn.close()
        self.clear_fields()
        self.load_members()

    def delete_member(self):
        selected = self.tree.selection()
        if not selected:
            return
        member_id = self.tree.item(
            selected[0]
        )["values"][0]
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT COUNT(*)
            FROM transactions
            WHERE member_id = ?
            AND status = 'Issued'
            """,
            (member_id,)
        )
        active = cursor.fetchone()[0]
        if active:
            messagebox.showerror("Error", "Member has an issued book.", parent=self.window)
            conn.close()
            return
        answer = messagebox.askyesno("Delete", "Delete selected member?", parent=self.window)
        if answer:
            cursor.execute(
                "DELETE FROM members WHERE id = ?",
                (member_id,)
            )
            conn.commit()
        conn.close()
        self.load_members()

    def select_member(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        values = self.tree.item(
            selected[0]
        )["values"]
        self.clear_fields()
        self.name_entry.insert(0, values[1])
        self.phone_entry.insert(0, values[2])
        self.email_entry.insert(0, values[3])
        self.address_entry.insert(0, values[4])

    def clear_fields(self):
        self.name_entry.delete(0, tk.END)
        self.phone_entry.delete(0, tk.END)
        self.email_entry.delete(0, tk.END)
        self.address_entry.delete(0, tk.END)

    def search_members(self):
        self.load_members(
            self.search_entry.get().strip()
        )




        