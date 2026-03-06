import sqlite3

conn = sqlite3.connect("mvp.db")  # In-memory for MVP
c = conn.cursor()

# Create tables
c.execute("""CREATE TABLE customers (
                id INTEGER PRIMARY KEY, name TEXT, segment TEXT, join_date TEXT
            )""")
c.execute("""CREATE TABLE orders (
                id INTEGER PRIMARY KEY, customer_id INTEGER, amount REAL, order_date TEXT
            )""")
c.execute("""CREATE TABLE support_tickets (
                id INTEGER PRIMARY KEY, customer_id INTEGER, issue TEXT, resolved TEXT, resolution_note TEXT
            )""")

# Sample data
customers = [
    (1, "Alice Smith", "enterprise", "2023-01-10"),
    (2, "Bob Jones", "small", "2023-03-05"),
    (3, "Carol White", "enterprise", "2023-02-20"),
    (4, "Dan Brown", "medium", "2023-01-25"),
    (5, "Eve Black", "enterprise", "2023-03-15"),
]
orders = [
    (1,1,450,"2023-01-15"), (2,2,120,"2023-02-10"), (3,3,700,"2023-03-05"),
    (4,1,200,"2023-03-10"), (5,5,350,"2023-03-20")
]
tickets = [
    (1,1,"Late delivery","yes","Apologized and refunded"),
    (2,3,"Billing error","yes","Corrected invoice"),
    (3,2,"Feature request","no","Pending prioritization"),
    (4,5,"Account access problem","yes","Reset credentials"),
    (5,1,"Refund request","yes","Processed within 5 days")
]

c.executemany("INSERT INTO customers VALUES (?,?,?,?)", customers)
c.executemany("INSERT INTO orders VALUES (?,?,?,?)", orders)
c.executemany("INSERT INTO support_tickets VALUES (?,?,?,?,?)", tickets)
conn.commit()