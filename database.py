import sqlite3

# Function to initialize the database
def initialize_database():
    conn = sqlite3.connect("bot_results.db")
    cursor = conn.cursor()

    # Create table to store sales orders
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sales_orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sales_order_id TEXT NOT NULL UNIQUE,
            invoice_sent BOOLEAN NOT NULL
        )
    ''')

    # Create table to store tracking details
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tracking_details (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sales_order_id TEXT NOT NULL,
            tracking_id TEXT NOT NULL,
            status TEXT NOT NULL,
            FOREIGN KEY (sales_order_id) REFERENCES sales_orders(sales_order_id)
        )
    ''')

    conn.commit()
    conn.close()

# Call the initialization function when the module is imported
initialize_database()
