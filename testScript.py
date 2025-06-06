import sqlite3

# Connect to your database
conn = sqlite3.connect("products.db")
cursor = conn.cursor()

# Step 1: Insert test categories
test_categories = ["Electronics", "Books", "Clothing"]

for category in test_categories:
    cursor.execute("INSERT OR IGNORE INTO categories (name) VALUES (?)", (category,))

# Fetch their IDs
cursor.execute("SELECT id, name FROM categories WHERE name IN (?, ?, ?)", test_categories)
category_data = cursor.fetchall()
category_ids = [row[0] for row in category_data]

print("Test categories with IDs:", category_data)

# Step 2: Insert a new product
cursor.execute("""
    INSERT INTO products (product_id, title, number, list_price, buy_price, price, stock, color)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
""", ("TEST001", "Sample Product", "NUM001", 150.0, 120.0, 130.0, 50, "Black"))

product_id = cursor.lastrowid
print("Inserted product with ID:", product_id)

# Step 3: Link product with categories
for cat_id in category_ids:
    cursor.execute("""
        INSERT INTO product_categories (product_id, category_id)
        VALUES (?, ?)
    """, (product_id, cat_id))

print("Linked product to categories:", category_ids)

conn.commit()
conn.close()
