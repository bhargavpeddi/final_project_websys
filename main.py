from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from datetime import datetime
import sqlite3

# -------------------- Database Setup --------------------

# Connect to SQLite DB file
db_conn = sqlite3.connect("db.sqlite", check_same_thread=False)
db_cursor = db_conn.cursor()

# Create tables if they don't exist
db_cursor.execute("""
CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    price REAL NOT NULL
)
""")
db_cursor.execute("""
CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    phone INTEGER NOT NULL
)
""")
db_cursor.execute("""
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp INTEGER NOT NULL,
    customer_id INTEGER NOT NULL,
    notes TEXT,
    FOREIGN KEY(customer_id) REFERENCES customers(id)
)
""")
db_conn.commit()

# -------------------- Request Models --------------------

class Product(BaseModel):
    name: str
    price: float

class Buyer(BaseModel):
    name: str
    phone: int

class Purchase(BaseModel):
    customer_id: int
    notes: str

# -------------------- FastAPI App Setup --------------------

app = FastAPI()

# Redirect to docs on base URL access
@app.get("/", include_in_schema=False)
def redirect_home():
    return RedirectResponse("/docs")

# -------------------- Product Endpoints --------------------

@app.post("/products")
def create_product(product: Product):
    db_cursor.execute("INSERT INTO items (name, price) VALUES (?, ?)", (product.name, product.price))
    db_conn.commit()
    return {"product_id": db_cursor.lastrowid, **product.dict()}

@app.get("/products/{product_id}")
def retrieve_product(product_id: int):
    db_cursor.execute("SELECT * FROM items WHERE id=?", (product_id,))
    result = db_cursor.fetchone()
    if not result:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"id": result[0], "name": result[1], "price": result[2]}

@app.put("/products/{product_id}")
def modify_product(product_id: int, product: Product):
    db_cursor.execute("UPDATE items SET name=?, price=? WHERE id=?", (product.name, product.price, product_id))
    db_conn.commit()
    return {"id": product_id, **product.dict()}

@app.delete("/products/{product_id}")
def delete_product(product_id: int):
    db_cursor.execute("DELETE FROM items WHERE id=?", (product_id,))
    db_conn.commit()
    return {"message": "Product removed"}

# -------------------- Buyer Endpoints --------------------

@app.post("/buyers")
def register_buyer(buyer: Buyer):
    db_cursor.execute("INSERT INTO customers (name, phone) VALUES (?, ?)", (buyer.name, buyer.phone))
    db_conn.commit()
    return {"buyer_id": db_cursor.lastrowid, **buyer.dict()}

@app.get("/buyers/{buyer_id}")
def get_buyer(buyer_id: int):
    db_cursor.execute("SELECT * FROM customers WHERE id=?", (buyer_id,))
    data = db_cursor.fetchone()
    if not data:
        raise HTTPException(status_code=404, detail="Buyer not found")
    return {"id": data[0], "name": data[1], "phone": data[2]}

@app.put("/buyers/{buyer_id}")
def update_buyer(buyer_id: int, buyer: Buyer):
    db_cursor.execute("UPDATE customers SET name=?, phone=? WHERE id=?", (buyer.name, buyer.phone, buyer_id))
    db_conn.commit()
    return {"id": buyer_id, **buyer.dict()}

@app.delete("/buyers/{buyer_id}")
def remove_buyer(buyer_id: int):
    db_cursor.execute("SELECT 1 FROM orders WHERE customer_id=?", (buyer_id,))
    if db_cursor.fetchone():
        raise HTTPException(status_code=400, detail="Delete related orders first.")
    db_cursor.execute("DELETE FROM customers WHERE id=?", (buyer_id,))
    db_conn.commit()
    return {"message": "Buyer removed"}

# -------------------- Purchase Endpoints --------------------

@app.post("/purchases")
def place_order(purchase: Purchase):
    timestamp = int(datetime.utcnow().timestamp())
    db_cursor.execute(
        "INSERT INTO orders (timestamp, customer_id, notes) VALUES (?, ?, ?)",
        (timestamp, purchase.customer_id, purchase.notes)
    )
    db_conn.commit()
    return {
        "order_id": db_cursor.lastrowid,
        "timestamp": timestamp,
        "customer_id": purchase.customer_id,
        "notes": purchase.notes
    }

@app.get("/purchases/{order_id}")
def get_order(order_id: int):
    db_cursor.execute("SELECT * FROM orders WHERE id=?", (order_id,))
    order = db_cursor.fetchone()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return {
        "id": order[0],
        "timestamp": order[1],
        "customer_id": order[2],
        "notes": order[3]
    }

@app.put("/purchases/{order_id}")
def update_order(order_id: int, purchase: Purchase):
    timestamp = int(datetime.utcnow().timestamp())
    db_cursor.execute(
        "UPDATE orders SET timestamp=?, customer_id=?, notes=? WHERE id=?",
        (timestamp, purchase.customer_id, purchase.notes, order_id)
    )
    db_conn.commit()
    return {
        "id": order_id,
        "timestamp": timestamp,
        "customer_id": purchase.customer_id,
        "notes": purchase.notes
    }

@app.delete("/purchases/{order_id}")
def cancel_order(order_id: int):
    db_cursor.execute("DELETE FROM orders WHERE id=?", (order_id,))
    db_conn.commit()
    return {"message": "Order successfully cancelled"}
