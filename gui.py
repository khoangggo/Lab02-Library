import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from datetime import datetime
from tkcalendar import DateEntry

class LibraryManagementSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Library Management System")
        self.root.geometry("800x600")
        self.db = None
        self.setup_login_screen()

    def setup_login_screen(self):
        self.login_frame = ttk.Frame(self.root, padding="20")
        self.login_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        ttk.Label(self.login_frame, text="Database Login").grid(column=0, row=0, columnspan=2)
        
        ttk.Label(self.login_frame, text="Host:").grid(column=0, row=1, sticky=tk.W)
        self.host_entry = ttk.Entry(self.login_frame)
        self.host_entry.grid(column=1, row=1)
        self.host_entry.insert(0, "localhost")

        ttk.Label(self.login_frame, text="Database:").grid(column=0, row=2, sticky=tk.W)
        self.db_entry = ttk.Entry(self.login_frame)
        self.db_entry.grid(column=1, row=2)
        self.db_entry.insert(0, "library-management")

        ttk.Label(self.login_frame, text="User:").grid(column=0, row=3, sticky=tk.W)
        self.user_entry = ttk.Entry(self.login_frame)
        self.user_entry.grid(column=1, row=3)
        self.user_entry.insert(0, "postgres")

        ttk.Label(self.login_frame, text="Password:").grid(column=0, row=4, sticky=tk.W)
        self.pass_entry = ttk.Entry(self.login_frame, show="*")
        self.pass_entry.grid(column=1, row=4)

        ttk.Button(self.login_frame, text="Connect", command=self.connect_db).grid(column=0, row=5, columnspan=2)

    def connect_db(self):
        from database import Database
        self.db = Database()
        if self.db.connect(
            self.host_entry.get(),
            self.db_entry.get(),
            self.user_entry.get(),
            self.pass_entry.get()
        ):
            messagebox.showinfo("Success", "Connected to database successfully!")
            self.login_frame.destroy()
            self.setup_main_screen()
        else:
            messagebox.showerror("Error", "Failed to connect to database")

    def setup_main_screen(self):
        # Cập nhật menu chính
        self.menu_frame = ttk.Frame(self.root, padding="10")
        self.menu_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))

        ttk.Button(self.menu_frame, text="Categories", command=self.show_categories).grid(row=0, column=0, padx=5)
        ttk.Button(self.menu_frame, text="Books", command=self.show_books).grid(row=0, column=1, padx=5)
        ttk.Button(self.menu_frame, text="Members", command=self.show_members).grid(row=0, column=2, padx=5)
        ttk.Button(self.menu_frame, text="Borrow Book", command=self.show_borrow).grid(row=0, column=3, padx=5)
        ttk.Button(self.menu_frame, text="Borrowed Books", command=self.show_borrowed_books).grid(row=0, column=4, padx=5)

        self.content_frame = ttk.Frame(self.root, padding="10")
        self.content_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.show_books()

    def clear_content_frame(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    # Quản lý danh mục
    def show_categories(self):
        self.clear_content_frame()
        
        
        add_frame = ttk.LabelFrame(self.content_frame, text="Add Category", padding="10")
        add_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)

        ttk.Label(add_frame, text="Category Name:").grid(row=0, column=0)
        self.category_name_entry = ttk.Entry(add_frame)
        self.category_name_entry.grid(row=0, column=1)
        ttk.Button(add_frame, text="Add", command=self.add_category).grid(row=0, column=2)

        
        self.categories_tree = ttk.Treeview(self.content_frame, columns=("ID", "Name"), show="headings")
        self.categories_tree.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.categories_tree.heading("ID", text="ID")
        self.categories_tree.heading("Name", text="Name")

        self.refresh_categories()

       
        btn_frame = ttk.Frame(self.content_frame)
        btn_frame.grid(row=2, column=0, pady=5)
        ttk.Button(btn_frame, text="Edit", command=self.edit_category_dialog).grid(row=0, column=0, padx=5)
        ttk.Button(btn_frame, text="Delete", command=self.delete_category).grid(row=0, column=1, padx=5)

    def refresh_categories(self):
        for item in self.categories_tree.get_children():
            self.categories_tree.delete(item)
        categories = self.db.get_all_categories()
        for category in categories:
            self.categories_tree.insert("", tk.END, values=category)

    def add_category(self):
        name = self.category_name_entry.get()
        if name:
            self.db.add_category(name)
            self.category_name_entry.delete(0, tk.END)
            self.refresh_categories()
        else:
            messagebox.showwarning("Warning", "Please enter a category name")

    def edit_category_dialog(self):
        selected = self.categories_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a category to edit")
            return

        category = self.categories_tree.item(selected[0])['values']
        dialog = tk.Toplevel(self.root)
        dialog.title("Edit Category")
        dialog.geometry("300x100")

        ttk.Label(dialog, text="Category Name:").grid(row=0, column=0, padx=5, pady=5)
        name_entry = ttk.Entry(dialog)
        name_entry.grid(row=0, column=1, padx=5, pady=5)
        name_entry.insert(0, category[1])

        def save():
            self.db.update_category(category[0], name_entry.get())
            self.refresh_categories()
            dialog.destroy()

        ttk.Button(dialog, text="Save", command=save).grid(row=1, column=0, columnspan=2, pady=10)

    def delete_category(self):
        selected = self.categories_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a category to delete")
            return

        if messagebox.askyesno("Confirm", "Are you sure you want to delete this category?"):
            category_id = self.categories_tree.item(selected[0])['values'][0]
            self.db.delete_category(category_id)
            self.refresh_categories()

    # Quản lý sách
    def show_books(self):
        self.clear_content_frame()

        
        search_frame = ttk.Frame(self.content_frame)
        search_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)

        ttk.Label(search_frame, text="Search:").grid(row=0, column=0, padx=5)
        self.search_entry = ttk.Entry(search_frame)
        self.search_entry.grid(row=0, column=1, padx=5)
        ttk.Button(search_frame, text="Search", command=self.search_books_action).grid(row=0, column=2, padx=5)
        ttk.Button(search_frame, text="Clear", command=self.refresh_books).grid(row=0, column=3, padx=5)

        # Buttons frame
        btn_frame = ttk.Frame(self.content_frame)
        btn_frame.grid(row=1, column=0, pady=5, sticky=(tk.W, tk.E))
        ttk.Button(btn_frame, text="Add Book", command=self.show_add_book_dialog).grid(row=0, column=0, padx=5)
        ttk.Button(btn_frame, text="Edit Book", command=self.show_edit_book_dialog).grid(row=0, column=1, padx=5)
        ttk.Button(btn_frame, text="Delete Book", command=self.delete_book).grid(row=0, column=2, padx=5)
        ttk.Button(btn_frame, text="View Details", command=self.show_book_details).grid(row=0, column=3, padx=5)
        ttk.Button(btn_frame, text="Return Book", command=self.return_book).grid(row=0, column=4, padx=5)

        
        self.books_tree = ttk.Treeview(self.content_frame, 
            columns=("ID", "Title", "Author", "Year", "Category", "Status"),
            show="headings")
        self.books_tree.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        
        scrollbar = ttk.Scrollbar(self.content_frame, orient=tk.VERTICAL, command=self.books_tree.yview)
        scrollbar.grid(row=2, column=1, sticky=(tk.N, tk.S))
        self.books_tree.configure(yscrollcommand=scrollbar.set)

        self.books_tree.heading("ID", text="ID")
        self.books_tree.heading("Title", text="Title")
        self.books_tree.heading("Author", text="Author")
        self.books_tree.heading("Year", text="Published Year")
        self.books_tree.heading("Category", text="Category")
        self.books_tree.heading("Status", text="Status")

        
        self.books_tree.column("ID", width=50)
        self.books_tree.column("Title", width=200)
        self.books_tree.column("Author", width=150)
        self.books_tree.column("Year", width=100)
        self.books_tree.column("Category", width=100)
        self.books_tree.column("Status", width=150)

        self.refresh_books()

    def search_books_action(self):
        search_term = self.search_entry.get()
        if not search_term:
            self.refresh_books()
            return

        for item in self.books_tree.get_children():
            self.books_tree.delete(item)
        
        books = self.db.search_books(search_term)
        for book in books:
            status = "Available" if book[6] is None else f"Borrowed by {book[6]}"
            self.books_tree.insert("", tk.END, values=(book[0], book[1], book[2], book[3], book[5], status))

    

    def refresh_books(self):
        for item in self.books_tree.get_children():
            self.books_tree.delete(item)
        books = self.db.get_all_books()
        for book in books:
            status = "Available" if book[6] is None else f"Borrowed by {book[6]}"
            self.books_tree.insert("", tk.END, values=(book[0], book[1], book[2], book[3], book[5], status))

    def show_add_book_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Book")
        dialog.geometry("400x250")

        
        categories = self.db.get_all_categories()
        category_names = [cat[1] for cat in categories]
        category_ids = [cat[0] for cat in categories]

        
        ttk.Label(dialog, text="Title:").grid(row=0, column=0, padx=5, pady=5)
        title_entry = ttk.Entry(dialog)
        title_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(dialog, text="Author:").grid(row=1, column=0, padx=5, pady=5)
        author_entry = ttk.Entry(dialog)
        author_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(dialog, text="Published Year:").grid(row=2, column=0, padx=5, pady=5)
        year_entry = ttk.Entry(dialog)
        year_entry.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(dialog, text="Category:").grid(row=3, column=0, padx=5, pady=5)
        category_var = tk.StringVar()
        category_dropdown = ttk.Combobox(dialog, textvariable=category_var, values=category_names)
        category_dropdown.grid(row=3, column=1, padx=5, pady=5)

        def save():
            try:
                cat_index = category_names.index(category_var.get())
                cat_id = category_ids[cat_index]
                self.db.add_book(
                    title_entry.get(),
                    author_entry.get(),
                    int(year_entry.get()),
                    cat_id
                )
                self.refresh_books()
                dialog.destroy()
            except ValueError as e:
                messagebox.showerror("Error", str(e))

        ttk.Button(dialog, text="Save", command=save).grid(row=4, column=0, columnspan=2, pady=10)

    def show_edit_book_dialog(self):
        selected = self.books_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a book to edit")
            return

        book_id = self.books_tree.item(selected[0])['values'][0]
        book_details = self.db.get_book_details(book_id)

        dialog = tk.Toplevel(self.root)
        dialog.title("Edit Book")
        dialog.geometry("400x250")

        
        categories = self.db.get_all_categories()
        category_names = [cat[1] for cat in categories]
        category_ids = [cat[0] for cat in categories]

        
        ttk.Label(dialog, text="Title:").grid(row=0, column=0, padx=5, pady=5)
        title_entry = ttk.Entry(dialog)
        title_entry.grid(row=0, column=1, padx=5, pady=5)
        title_entry.insert(0, book_details[1])

        ttk.Label(dialog, text="Author:").grid(row=1, column=0, padx=5, pady=5)
        author_entry = ttk.Entry(dialog)
        author_entry.grid(row=1, column=1, padx=5, pady=5)
        author_entry.insert(0, book_details[2])

        ttk.Label(dialog, text="Published Year:").grid(row=2, column=0, padx=5, pady=5)
        year_entry = ttk.Entry(dialog)
        year_entry.grid(row=2, column=1, padx=5, pady=5)
        year_entry.insert(0, str(book_details[3]))

        ttk.Label(dialog, text="Category:").grid(row=3, column=0, padx=5, pady=5)
        category_var = tk.StringVar()
        category_dropdown = ttk.Combobox(dialog, textvariable=category_var, values=category_names)
        category_dropdown.grid(row=3, column=1, padx=5, pady=5)
        category_dropdown.set(book_details[5])  # CategoryName

        def save():
            try:
                cat_index = category_names.index(category_var.get())
                cat_id = category_ids[cat_index]
                self.db.update_book(
                    book_id,
                    title_entry.get(),
                    author_entry.get(),
                    int(year_entry.get()),
                    cat_id
                )
                self.refresh_books()
                dialog.destroy()
            except ValueError as e:
                messagebox.showerror("Error", str(e))

        ttk.Button(dialog, text="Save", command=save).grid(row=4, column=0, columnspan=2, pady=10)

    def delete_book(self):
        selected = self.books_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a book to delete")
            return

        if messagebox.askyesno("Confirm", "Are you sure you want to delete this book?"):
            book_id = self.books_tree.item(selected[0])['values'][0]
            self.db.delete_book(book_id)
            self.refresh_books()

    def show_book_details(self):
        selected = self.books_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a book to view details")
            return

        book_id = self.books_tree.item(selected[0])['values'][0]
        book_details = self.db.get_book_details(book_id)

        dialog = tk.Toplevel(self.root)
        dialog.title("Book Details")
        dialog.geometry("400x300")

        details_text = f"""
Title: {book_details[1]}
Author: {book_details[2]}
Published Year: {book_details[3]}
Category: {book_details[5]}

Status: {"Available" if book_details[6] is None else "Borrowed"}
"""
        if book_details[6]:  # If book is borrowed
            details_text += f"""
Borrower Name: {book_details[6]}
Borrower Email: {book_details[7]}
Borrow Date: {book_details[8]}
"""

        text_widget = tk.Text(dialog, wrap=tk.WORD, height=15, width=40)
        text_widget.insert(tk.END, details_text)
        text_widget.config(state=tk.DISABLED)
        text_widget.grid(row=0, column=0, padx=10, pady=10)

    # Quản lý member
    def show_members(self):
        self.clear_content_frame()

        
        search_frame = ttk.Frame(self.content_frame)
        search_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)

        ttk.Label(search_frame, text="Search:").grid(row=0, column=0, padx=5)
        self.member_search_entry = ttk.Entry(search_frame)
        self.member_search_entry.grid(row=0, column=1, padx=5)
        ttk.Button(search_frame, text="Search", command=self.search_members_action).grid(row=0, column=2, padx=5)
        ttk.Button(search_frame, text="Clear", command=self.refresh_members).grid(row=0, column=3, padx=5)

        
        btn_frame = ttk.Frame(self.content_frame)
        btn_frame.grid(row=1, column=0, pady=5, sticky=(tk.W, tk.E))
        ttk.Button(btn_frame, text="Add Member", command=self.show_add_member_dialog).grid(row=0, column=0, padx=5)
        ttk.Button(btn_frame, text="Edit Member", command=self.show_edit_member_dialog).grid(row=0, column=1, padx=5)
        ttk.Button(btn_frame, text="Delete Member", command=self.delete_member).grid(row=0, column=2, padx=5)

        
        self.members_tree = ttk.Treeview(self.content_frame, 
            columns=("ID", "Name", "Email", "Membership Date"),
            show="headings")
        self.members_tree.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.members_tree.heading("ID", text="ID")
        self.members_tree.heading("Name", text="Name")
        self.members_tree.heading("Email", text="Email")
        self.members_tree.heading("Membership Date", text="Membership Date")

        self.refresh_members()

    def search_members_action(self):
        search_term = self.member_search_entry.get()
        if not search_term:
            self.refresh_members()
            return

        for item in self.members_tree.get_children():
            self.members_tree.delete(item)
        
        members = self.db.search_members(search_term)
        for member in members:
            self.members_tree.insert("", tk.END, values=member)

    def show_borrowed_books(self):
        self.clear_content_frame()

        
        ttk.Label(self.content_frame, text="Currently Borrowed Books", font=('Helvetica', 12, 'bold')).grid(row=0, column=0, pady=10)
        
        self.borrowed_books_tree = ttk.Treeview(self.content_frame, 
            columns=("ID", "Title", "Author", "Category", "Borrower", "Email", "Borrow Date"),
            show="headings")
        self.borrowed_books_tree.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        
        scrollbar = ttk.Scrollbar(self.content_frame, orient=tk.VERTICAL, command=self.borrowed_books_tree.yview)
        scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
        self.borrowed_books_tree.configure(yscrollcommand=scrollbar.set)

        
        self.borrowed_books_tree.heading("ID", text="ID")
        self.borrowed_books_tree.heading("Title", text="Title")
        self.borrowed_books_tree.heading("Author", text="Author")
        self.borrowed_books_tree.heading("Category", text="Category")
        self.borrowed_books_tree.heading("Borrower", text="Borrower")
        self.borrowed_books_tree.heading("Email", text="Borrower Email")
        self.borrowed_books_tree.heading("Borrow Date", text="Borrow Date")

       
        self.borrowed_books_tree.column("ID", width=50)
        self.borrowed_books_tree.column("Title", width=200)
        self.borrowed_books_tree.column("Author", width=150)
        self.borrowed_books_tree.column("Category", width=100)
        self.borrowed_books_tree.column("Borrower", width=150)
        self.borrowed_books_tree.column("Email", width=200)
        self.borrowed_books_tree.column("Borrow Date", width=100)

        
        ttk.Button(self.content_frame, text="Return Selected Book", 
                command=self.return_book_from_borrowed).grid(row=2, column=0, pady=10)

        self.refresh_borrowed_books()

    def refresh_borrowed_books(self):
        for item in self.borrowed_books_tree.get_children():
            self.borrowed_books_tree.delete(item)
        
        borrowed_books = self.db.get_borrowed_books()
        for book in borrowed_books:
            self.borrowed_books_tree.insert("", tk.END, values=book)

    def return_book_from_borrowed(self):
        selected = self.borrowed_books_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a book to return")
            return

        book_id = self.borrowed_books_tree.item(selected[0])['values'][0]
        
        if messagebox.askyesno("Confirm Return", "Are you sure you want to return this book?"):
            self.db.return_book(book_id)
            messagebox.showinfo("Success", "Book returned successfully!")
            self.refresh_borrowed_books()

    def refresh_members(self):
        for item in self.members_tree.get_children():
            self.members_tree.delete(item)
        members = self.db.get_all_members()
        for member in members:
            self.members_tree.insert("", tk.END, values=member)

    def show_add_member_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Member")
        dialog.geometry("400x200")

        ttk.Label(dialog, text="Name:").grid(row=0, column=0, padx=5, pady=5)
        name_entry = ttk.Entry(dialog)
        name_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(dialog, text="Email:").grid(row=1, column=0, padx=5, pady=5)
        email_entry = ttk.Entry(dialog)
        email_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(dialog, text="Membership Date:").grid(row=2, column=0, padx=5, pady=5)
        date_entry = DateEntry(dialog, width=12, background='darkblue', foreground='white', borderwidth=2)
        date_entry.grid(row=2, column=1, padx=5, pady=5)

        def save():
            self.db.add_member(
                name_entry.get(),
                email_entry.get(),
                date_entry.get_date()
            )
            self.refresh_members()
            dialog.destroy()

        ttk.Button(dialog, text="Save", command=save).grid(row=3, column=0, columnspan=2, pady=10)

    def show_edit_member_dialog(self):
        selected = self.members_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a member to edit")
            return

        member = self.members_tree.item(selected[0])['values']
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Edit Member")
        dialog.geometry("400x200")

        ttk.Label(dialog, text="Name:").grid(row=0, column=0, padx=5, pady=5)
        name_entry = ttk.Entry(dialog)
        name_entry.grid(row=0, column=1, padx=5, pady=5)
        name_entry.insert(0, member[1])

        ttk.Label(dialog, text="Email:").grid(row=1, column=0, padx=5, pady=5)
        email_entry = ttk.Entry(dialog)
        email_entry.grid(row=1, column=1, padx=5, pady=5)
        email_entry.insert(0, member[2])

        ttk.Label(dialog, text="Membership Date:").grid(row=2, column=0, padx=5, pady=5)
        date_entry = DateEntry(dialog, width=12, background='darkblue', foreground='white', borderwidth=2)
        date_entry.grid(row=2, column=1, padx=5, pady=5)
        # date_entry.set_date(member[3])
        try:
            membership_date = datetime.strptime(member[3], "%Y-%m-%d").date()
            date_entry.set_date(membership_date)
        except ValueError:
            messagebox.showerror("Error", "Invalid date format. Setting default date.")
            date_entry.set_date(datetime.date.today())

        def save():
            self.db.update_member(
                member[0],
                name_entry.get(),
                email_entry.get(),
                date_entry.get_date()
            )
            self.refresh_members()
            dialog.destroy()

        ttk.Button(dialog, text="Save", command=save).grid(row=3, column=0, columnspan=2, pady=10)

    def delete_member(self):
        selected = self.members_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a member to delete")
            return

        if messagebox.askyesno("Confirm", "Are you sure you want to delete this member?"):
            member_id = self.members_tree.item(selected[0])['values'][0]
            self.db.delete_member(member_id)
            self.refresh_members()

    # Quản lý mượn sách
    def show_borrow(self):
        self.clear_content_frame()
        
        # Sách được mượn
        ttk.Label(self.content_frame, text="Available Books").grid(row=0, column=0, pady=5)
        self.borrow_books_tree = ttk.Treeview(self.content_frame, 
            columns=("ID", "Title", "Author", "Category"),
            show="headings", height=10)
        self.borrow_books_tree.grid(row=1, column=0, sticky=(tk.W, tk.E))

        self.borrow_books_tree.heading("ID", text="ID")
        self.borrow_books_tree.heading("Title", text="Title")
        self.borrow_books_tree.heading("Author", text="Author")
        self.borrow_books_tree.heading("Category", text="Category")

        # Thành viên
        ttk.Label(self.content_frame, text="Select Member").grid(row=2, column=0, pady=5)
        self.borrow_members_tree = ttk.Treeview(self.content_frame, 
            columns=("ID", "Name", "Email"),
            show="headings", height=10)
        self.borrow_members_tree.grid(row=3, column=0, sticky=(tk.W, tk.E))

        self.borrow_members_tree.heading("ID", text="ID")
        self.borrow_members_tree.heading("Name", text="Name")
        self.borrow_members_tree.heading("Email", text="Email")

        
        ttk.Button(self.content_frame, text="Borrow Book", command=self.borrow_book).grid(row=4, column=0, pady=10)

        
        ttk.Button(self.content_frame, text="Return Book", command=self.return_book).grid(row=5, column=0, pady=10)

        self.refresh_borrow_lists()

    def refresh_borrow_lists(self):
        
        for item in self.borrow_books_tree.get_children():
            self.borrow_books_tree.delete(item)
        books = self.db.get_all_books()
        for book in books:
            if book[6] is None: 
                self.borrow_books_tree.insert("", tk.END, values=(book[0], book[1], book[2], book[5]))

        
        for item in self.borrow_members_tree.get_children():
            self.borrow_members_tree.delete(item)
        members = self.db.get_all_members()
        for member in members:
            self.borrow_members_tree.insert("", tk.END, values=(member[0], member[1], member[2]))

    def borrow_book(self):
        selected_book = self.borrow_books_tree.selection()
        selected_member = self.borrow_members_tree.selection()

        if not selected_book:
            messagebox.showwarning("Warning", "Please select a book to borrow")
            return
        if not selected_member:
            messagebox.showwarning("Warning", "Please select a member")
            return

        book_id = self.borrow_books_tree.item(selected_book[0])['values'][0]
        member_id = self.borrow_members_tree.item(selected_member[0])['values'][0]

        if self.db.is_book_available(book_id):
            self.db.borrow_book(book_id, member_id)
            messagebox.showinfo("Success", "Book borrowed successfully!")
            self.refresh_borrow_lists()
            self.refresh_books()  
        else:
            messagebox.showerror("Error", "Book is not available for borrowing")

    def return_book(self):
        selected_book = self.books_tree.selection()
        if not selected_book:
            messagebox.showwarning("Warning", "Please select a book to return")
            return

        book_id = self.books_tree.item(selected_book[0])['values'][0]
        
        if not self.db.is_book_available(book_id):
            self.db.return_book(book_id)
            messagebox.showinfo("Success", "Book returned successfully!")
            self.refresh_books()
            if hasattr(self, 'borrow_books_tree'):
                self.refresh_borrow_lists()
        else:
            messagebox.showerror("Error", "This book is not currently borrowed")

def main():
    root = tk.Tk()
    app = LibraryManagementSystem(root)
    root.mainloop()

if __name__ == "__main__":
    main()