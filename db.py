import sqlite3

def connect_db(db_name="products.db"):
    conn = sqlite3.connect(db_name)
    return conn

def create_tables(conn):
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS categories")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_id INTEGER,
            title TEXT,
            parent_id INTEGER
        )
    """)

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER,
        title TEXT,
        number TEXT,
        list_price REAL,
        buy_price REAL,
        price REAL,
        stock INTEGER,
        color TEXT,
        category_id INTEGER,
        FOREIGN KEY (category_id) REFERENCES categories (id)
    )
    ''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS product_categories (
        product_id   INTEGER,
        category_id  INTEGER,
        PRIMARY KEY (product_id, category_id),
        FOREIGN KEY (product_id)   REFERENCES products(id),
        FOREIGN KEY (category_id)  REFERENCES categories(id)
    )
    ''')

    conn.commit()

