import sqlite3
from datetime import datetime

DB = "foodgenie.db"


def connect():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    return con


def init_db():
    con = connect()
    cur = con.cursor()

    cur.executescript("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT,
        name TEXT,
        address TEXT DEFAULT ''
    );

    CREATE TABLE IF NOT EXISTS restaurants(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        cuisine TEXT,
        rating REAL,
        delivery_time INTEGER,
        address TEXT,
        active INTEGER DEFAULT 1
    );

    CREATE TABLE IF NOT EXISTS foods(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        restaurant_id INTEGER,
        name TEXT,
        category TEXT,
        price REAL,
        veg INTEGER,
        rating REAL,
        available INTEGER DEFAULT 1,
        stock INTEGER DEFAULT 50
    );

    CREATE TABLE IF NOT EXISTS orders(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        restaurant_id INTEGER,
        total REAL,
        status TEXT,
        address TEXT,
        payment TEXT,
        created_at TEXT,
        assigned_rider INTEGER
    );

    CREATE TABLE IF NOT EXISTS order_items(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER,
        food_id INTEGER,
        qty INTEGER,
        price REAL
    );

    CREATE TABLE IF NOT EXISTS reviews(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        restaurant_id INTEGER,
        rating INTEGER,
        comment TEXT,
        sentiment TEXT,
        created_at TEXT
    );

    CREATE TABLE IF NOT EXISTS coupons(
        code TEXT PRIMARY KEY,
        discount REAL,
        minimum REAL
    );
    """)

    # Users
    if cur.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0:

        users = [
            ("admin", "admin123", "admin", "Administrator", ""),
            ("pizza_hub", "1234", "restaurant", "Pizza Hub Owner", ""),
            ("rider1", "1234", "delivery", "Rider One", ""),
            ("demo", "1234", "customer", "Demo Customer", "Chennai")
        ]

        cur.executemany("""
            INSERT INTO users
            (username,password,role,name,address)
            VALUES(?,?,?,?,?)
        """, users)

    # Restaurants
    if cur.execute("SELECT COUNT(*) FROM restaurants").fetchone()[0] == 0:

        restaurants = [
            ("Pizza Hub", "Italian", 4.6, 30, "Anna Nagar"),
            ("Chennai Spice", "South Indian", 4.5, 25, "T Nagar"),
            ("Burger House", "Fast Food", 4.3, 28, "Velachery"),
            ("Green Bowl", "Healthy", 4.7, 22, "Adyar"),
            ("Biryani Express", "Biryani", 4.4, 35, "Guindy"),
            ("Sweet Treats", "Desserts", 4.6, 20, "Nungambakkam")
        ]

        cur.executemany("""
            INSERT INTO restaurants
            (name,cuisine,rating,delivery_time,address)
            VALUES(?,?,?,?,?)
        """, restaurants)

    # Foods
    if cur.execute("SELECT COUNT(*) FROM foods").fetchone()[0] == 0:

        foods = [

            (1, "Margherita Pizza", "Pizza",
             249, 1, 4.5, 1, 50),

            (1, "Chicken Pizza", "Pizza",
             329, 0, 4.6, 1, 50),

            (1, "Pasta Alfredo", "Pasta",
             279, 1, 4.4, 1, 50),

            (1, "Garlic Bread", "Sides",
             129, 1, 4.3, 1, 80),

            (2, "Masala Dosa", "Breakfast",
             90, 1, 4.6, 1, 80),

            (2, "Paneer Meals", "Meals",
             180, 1, 4.5, 1, 60),

            (2, "Chicken Meals", "Meals",
             220, 0, 4.5, 1, 60),

            (2, "Idli Sambar", "Breakfast",
             70, 1, 4.4, 1, 90),

            (3, "Classic Burger", "Burger",
             179, 1, 4.3, 1, 60),

            (3, "Chicken Burger", "Burger",
             229, 0, 4.5, 1, 60),

            (3, "French Fries", "Sides",
             99, 1, 4.4, 1, 100),

            (4, "Paneer Salad Bowl", "Healthy",
             219, 1, 4.7, 1, 50),

            (4, "Veg Protein Bowl", "Healthy",
             239, 1, 4.6, 1, 50),

            (4, "Fruit Bowl", "Healthy",
             159, 1, 4.5, 1, 60),

            (5, "Chicken Biryani", "Biryani",
             249, 0, 4.6, 1, 70),

            (5, "Mutton Biryani", "Biryani",
             329, 0, 4.5, 1, 50),

            (5, "Veg Biryani", "Biryani",
             199, 1, 4.3, 1, 60),

            (6, "Chocolate Brownie", "Dessert",
             149, 1, 4.7, 1, 70),

            (6, "Ice Cream Sundae", "Dessert",
             129, 1, 4.6, 1, 70)
        ]

        cur.executemany("""
            INSERT INTO foods
            (restaurant_id,name,category,price,veg,
             rating,available,stock)
            VALUES(?,?,?,?,?,?,?,?)
        """, foods)

    # Coupons
    if cur.execute("SELECT COUNT(*) FROM coupons").fetchone()[0] == 0:

        coupons = [
            ("WELCOME50", 50, 250),
            ("FOOD20", 20, 300),
            ("SAVE100", 100, 500)
        ]

        cur.executemany("""
            INSERT INTO coupons
            VALUES(?,?,?)
        """, coupons)

    con.commit()
    con.close()

    # =========================================================
# DATABASE MIGRATION - FIX OLD ORDER_ITEMS TABLE
# =========================================================

def migrate_database():
    conn = connect()
    cur = conn.cursor()

    # Check existing order_items columns
    cur.execute("PRAGMA table_info(order_items)")
    columns = [row[1] for row in cur.fetchall()]

    # Old database may not have quantity column
    if "quantity" not in columns:
        try:
            cur.execute(
                "ALTER TABLE order_items "
                "ADD COLUMN quantity INTEGER DEFAULT 1"
            )
            print("✅ Added missing column: quantity")
        except Exception as e:
            print("Migration warning:", e)

    conn.commit()
    conn.close()


def query(sql, params=()):

    con = connect()

    rows = con.execute(
        sql,
        params
    ).fetchall()

    con.close()

    return rows


def one(sql, params=()):

    con = connect()

    row = con.execute(
        sql,
        params
    ).fetchone()

    con.close()

    return row


def execute(sql, params=()):

    con = connect()

    cur = con.execute(
        sql,
        params
    )

    con.commit()

    last_id = cur.lastrowid

    con.close()

    return last_id