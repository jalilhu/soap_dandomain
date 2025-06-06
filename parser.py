import xml.etree.ElementTree as ET
from db import connect_db, create_tables

def parse_and_store(xml_path):
    conn = connect_db()
    create_tables(conn)
    cursor = conn.cursor()

    tree = ET.parse(xml_path)
    root = tree.getroot()

    for product in root.findall("PRODUCT"):
        product_id = product.findtext("PRODUCT_ID")
        title = product.findtext("TITLE_DK", "").strip()
        number = product.findtext("NUMBER", "").strip()
        list_price = product.findtext("LIST_PRICE", "0").replace(",", ".")
        buy_price = product.findtext("BUY_PRICE", "0").replace(",", ".")
        price = product.findtext("PRICE", "0").replace(",", ".")
        stock = product.findtext("STOCK", "0")
        color = product.findtext("CUSTOM_DATA_3_DK", "").strip()

        category_id = product.findtext("CATEGORY_ID", "").strip()

        # Insert category if not exists
        cursor.execute("SELECT id FROM categories WHERE name = ?", (category_id,))
        cat_row = cursor.fetchone()
        if cat_row:
            cat_id = cat_row[0]
        else:
            cursor.execute("INSERT INTO categories (name) VALUES (?)", (category_id,))
            cat_id = cursor.lastrowid

        # Insert product
        cursor.execute('''
            INSERT INTO products 
                (product_id, title, number, list_price, buy_price, price, stock, color)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
            product_id, title, number,
            float(list_price), float(buy_price), float(price),
            int(stock), color
        
        ))
        product_row_id = cursor.lastrowid
        
        cursor.execute("""
            INSERT OR IGNORE INTO product_categories
                (product_id, category_id)
            VALUES (?, ?)
        """, (product_row_id, cat_id))
   
    conn.commit()
    conn.close()

if __name__ == "__main__":
    parse_and_store("product_240425-10h38m24s.xml")