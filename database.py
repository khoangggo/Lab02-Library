import psycopg2
from psycopg2 import Error
from datetime import datetime

class Database:
    def __init__(self):
        self.connection = None
        self.cursor = None

    def connect(self, host, database, user, password):
        try:
            self.connection = psycopg2.connect(
                host=host,
                database=database,
                user=user,
                password=password
            )
            self.cursor = self.connection.cursor()
            self.create_tables()
            return True
        except Error as e:
            print(f"Error: {e}")
            return False

    def create_tables(self):
        commands = (
            """
            CREATE TABLE IF NOT EXISTS Categories (
                CategoryID SERIAL PRIMARY KEY,
                CategoryName VARCHAR(100) NOT NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS Books (
                BookID SERIAL PRIMARY KEY,
                Title VARCHAR(200) NOT NULL,
                Author VARCHAR(100),
                PublishedYear INTEGER,
                CategoryID INTEGER REFERENCES Categories(CategoryID)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS Members (
                MemberID SERIAL PRIMARY KEY,
                Name VARCHAR(100) NOT NULL,
                Email VARCHAR(100),
                MembershipDate DATE
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS BorrowRecords (
                RecordID SERIAL PRIMARY KEY,
                BookID INTEGER REFERENCES Books(BookID),
                MemberID INTEGER REFERENCES Members(MemberID),
                BorrowDate DATE,
                ReturnDate DATE
            )
            """
        )
        
        for command in commands:
            self.cursor.execute(command)
        self.connection.commit()

    # Category operations
    def add_category(self, name):
        sql = "INSERT INTO Categories(CategoryName) VALUES(%s) RETURNING CategoryID"
        self.cursor.execute(sql, (name,))
        self.connection.commit()
        return self.cursor.fetchone()[0]

    def get_all_categories(self):
        self.cursor.execute("SELECT * FROM Categories")
        return self.cursor.fetchall()

    def update_category(self, category_id, name):
        sql = "UPDATE Categories SET CategoryName = %s WHERE CategoryID = %s"
        self.cursor.execute(sql, (name, category_id))
        self.connection.commit()

    def delete_category(self, category_id):
        sql = "DELETE FROM Categories WHERE CategoryID = %s"
        self.cursor.execute(sql, (category_id,))
        self.connection.commit()

   
    def add_book(self, title, author, published_year, category_id):
        sql = """INSERT INTO Books(Title, Author, PublishedYear, CategoryID) 
                VALUES(%s, %s, %s, %s) RETURNING BookID"""
        self.cursor.execute(sql, (title, author, published_year, category_id))
        self.connection.commit()
        return self.cursor.fetchone()[0]

    def get_all_books(self):
        sql = """
        SELECT b.*, c.CategoryName, 
               CASE 
                   WHEN br.ReturnDate IS NULL AND br.BorrowDate IS NOT NULL THEN m.Name 
                   ELSE NULL 
               END as BorrowerName
        FROM Books b 
        LEFT JOIN Categories c ON b.CategoryID = c.CategoryID
        LEFT JOIN BorrowRecords br ON b.BookID = br.BookID AND br.ReturnDate IS NULL
        LEFT JOIN Members m ON br.MemberID = m.MemberID
        """
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def get_book_details(self, book_id):
        sql = """
        SELECT b.*, c.CategoryName, m.Name as BorrowerName, m.Email as BorrowerEmail,
               br.BorrowDate
        FROM Books b 
        LEFT JOIN Categories c ON b.CategoryID = c.CategoryID
        LEFT JOIN BorrowRecords br ON b.BookID = br.BookID AND br.ReturnDate IS NULL
        LEFT JOIN Members m ON br.MemberID = m.MemberID
        WHERE b.BookID = %s
        """
        self.cursor.execute(sql, (book_id,))
        return self.cursor.fetchone()

    def update_book(self, book_id, title, author, published_year, category_id):
        sql = """UPDATE Books 
                SET Title = %s, Author = %s, PublishedYear = %s, CategoryID = %s 
                WHERE BookID = %s"""
        self.cursor.execute(sql, (title, author, published_year, category_id, book_id))
        self.connection.commit()

    def delete_book(self, book_id):
        sql = "DELETE FROM Books WHERE BookID = %s"
        self.cursor.execute(sql, (book_id,))
        self.connection.commit()


    def add_member(self, name, email, membership_date):
        sql = """INSERT INTO Members(Name, Email, MembershipDate) 
                VALUES(%s, %s, %s) RETURNING MemberID"""
        self.cursor.execute(sql, (name, email, membership_date))
        self.connection.commit()
        return self.cursor.fetchone()[0]

    def get_all_members(self):
        self.cursor.execute("SELECT * FROM Members")
        return self.cursor.fetchall()

    def update_member(self, member_id, name, email, membership_date):
        sql = """UPDATE Members 
                SET Name = %s, Email = %s, MembershipDate = %s 
                WHERE MemberID = %s"""
        self.cursor.execute(sql, (name, email, membership_date, member_id))
        self.connection.commit()

    def delete_member(self, member_id):
        sql = "DELETE FROM Members WHERE MemberID = %s"
        self.cursor.execute(sql, (member_id,))
        self.connection.commit()


    def borrow_book(self, book_id, member_id):
        sql = """INSERT INTO BorrowRecords(BookID, MemberID, BorrowDate) 
                VALUES(%s, %s, CURRENT_DATE)"""
        self.cursor.execute(sql, (book_id, member_id))
        self.connection.commit()

    def return_book(self, book_id):
        sql = """UPDATE BorrowRecords 
                SET ReturnDate = CURRENT_DATE 
                WHERE BookID = %s AND ReturnDate IS NULL"""
        self.cursor.execute(sql, (book_id,))
        self.connection.commit()

    def is_book_available(self, book_id):
        sql = """SELECT COUNT(*) FROM BorrowRecords 
                WHERE BookID = %s AND ReturnDate IS NULL"""
        self.cursor.execute(sql, (book_id,))
        return self.cursor.fetchone()[0] == 0
    
    def get_borrowed_books(self):
        sql = """
        SELECT b.BookID, b.Title, b.Author, c.CategoryName, 
            m.Name as BorrowerName, m.Email as BorrowerEmail,
            br.BorrowDate
        FROM Books b 
        JOIN BorrowRecords br ON b.BookID = br.BookID
        JOIN Members m ON br.MemberID = m.MemberID
        LEFT JOIN Categories c ON b.CategoryID = c.CategoryID
        WHERE br.ReturnDate IS NULL
        """
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def search_books(self, search_term):
        sql = """
        SELECT b.*, c.CategoryName, 
            CASE 
                WHEN br.ReturnDate IS NULL AND br.BorrowDate IS NOT NULL THEN m.Name 
                ELSE NULL 
            END as BorrowerName
        FROM Books b 
        LEFT JOIN Categories c ON b.CategoryID = c.CategoryID
        LEFT JOIN BorrowRecords br ON b.BookID = br.BookID AND br.ReturnDate IS NULL
        LEFT JOIN Members m ON br.MemberID = m.MemberID
        WHERE LOWER(b.Title) LIKE LOWER(%s)
        OR LOWER(b.Author) LIKE LOWER(%s)
        OR LOWER(c.CategoryName) LIKE LOWER(%s)
        """
        search_pattern = f"%{search_term}%"
        self.cursor.execute(sql, (search_pattern, search_pattern, search_pattern))
        return self.cursor.fetchall()

    def search_members(self, search_term):
        sql = """
        SELECT * FROM Members
        WHERE LOWER(Name) LIKE LOWER(%s)
        OR LOWER(Email) LIKE LOWER(%s)
        """
        search_pattern = f"%{search_term}%"
        self.cursor.execute(sql, (search_pattern, search_pattern))
        return self.cursor.fetchall()
    

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
