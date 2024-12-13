import sqlite3
from database import initialize_database

# Asynchronous function to save processed orders into the database
async def save_to_database(bot_name, processed_orders):
    conn = sqlite3.connect("bot_results.db")
    cursor = conn.cursor()

    for order in processed_orders:
        # Insert the sales order into the sales_orders table
        cursor.execute('''
            INSERT OR IGNORE INTO sales_orders (sales_order_id, invoice_sent)
            VALUES (?, ?)
        ''', (order['sales_order_id'], order['invoice_sent']))

        # Insert tracking details into the tracking_details table
        for tracking in order['tracking_details']:
            cursor.execute('''
                INSERT INTO tracking_details (sales_order_id, tracking_id, status)
                VALUES (?, ?, ?)
            ''', (order['sales_order_id'], tracking['tracking_id'], tracking['status']))

    conn.commit()
    conn.close()
