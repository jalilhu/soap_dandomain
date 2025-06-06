import xml.etree.ElementTree as ET
from db import connect_db, create_tables
import time
from soap.soap_client import DandomainSOAPClient

client = DandomainSOAPClient()

def parse_and_store_categories():
    conn = connect_db()
    create_tables(conn)
    cursor = conn.cursor()

    try:
        start = time.time()
        print("Calling SOAP API to get categories...")
        categories = client.get_category_all()
        end = time.time()
        print(f"Done! Fetched {len(categories)} categories in {end - start:.2f} seconds.")
    except Exception as e:
        print(f"Could not fetch categories: {e}")
        return

    for cat in categories:
        cat_id = getattr(cat, "Id", None)
        name = getattr(cat, "Title", "").strip()
        parent_id = getattr(cat, "ParentId", None)

        if cat_id:
            cursor.execute("""
                INSERT INTO categories (category_id, title, parent_id)
                VALUES (?, ?, ?)
            """, (int(cat_id), name, int(parent_id) if parent_id else None))

    conn.commit()
    conn.close()

if __name__ == "__main__":
    parse_and_store_categories()