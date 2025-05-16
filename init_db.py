import sqlite3
import json
from fastapi import FastAPI

connection = sqlite3.connect("db.sqlite")
cursor = connection.cursor()

        
# Create tables
cursor.execute('''CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY,
                name TEXT,
                phone TEXT
            )''')

cursor.execute('''CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY,
                name TEXT,
                price REAL
            )''')

cursor.execute('''CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY,
                timestamp INTEGER,
                customer_id INTEGER,
                notes TEXT,
                FOREIGN KEY (customer_id) REFERENCES customers(id)
            )''')

cursor.execute('''CREATE TABLE IF NOT EXISTS order_items (
                order_id INTEGER,
                item_id INTEGER,
                FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE ON UPDATE CASCADE,
                FOREIGN KEY (item_id) REFERENCES items(id) ON DELETE CASCADE ON UPDATE CASCADE
            )''')

# Load data from example_orders.json
with open('example_orders.json', 'r') as file:
    data = json.load(file)

# Populate customers table
for order in data:
    customer_name = order['name']
    phone = order['phone']
    
    # Check if customer already exists
    cursor.execute("SELECT id FROM customers WHERE name = ? AND phone = ?", (customer_name, phone))
    existing_customer = cursor.fetchone()

    if existing_customer:
        customer_id = existing_customer[0]
    else:
        # Insert new customer
        customer_id = cursor.execute("INSERT INTO customers (name, phone) VALUES (?, ?)", (customer_name, phone)).lastrowid

    # Populate orders table
    order_id = cursor.execute("INSERT INTO orders (timestamp, customer_id, notes) VALUES (?, ?, ?)", (order['timestamp'], customer_id, order['notes'])).lastrowid

    # Populate items and order_items tables
    for item in order['items']:
        item_name = item['name']
        item_price = item['price']
        
        # Check if item exists
        cursor.execute("SELECT id FROM items WHERE name = ?", (item_name,))
        existing_item = cursor.fetchone()
        
        if existing_item:
            item_id = existing_item[0]  # ID of the existing item
            
            cursor.execute("INSERT INTO order_items (order_id, item_id) VALUES (?, ?)", (order_id, item_id))
        else:
            
            item_id = cursor.execute("INSERT INTO items (name, price) VALUES (?, ?)", (item_name, item_price)).lastrowid
            cursor.execute("INSERT INTO order_items (order_id, item_id) VALUES (?, ?)", (order_id, item_id))
            
            
# Commit changes
connection.commit()

