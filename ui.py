import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from db import connect_db
from category_utils import CategoryAutocomplete

# --- Database functions ---
def fetch_products(filter_text="", category_filter_ids=None, limit=20, offset=0, sort_column="title", sort_order="ASC", hide_no_title=False, hide_no_number=False, hide_no_price=False):
    conn = connect_db()
    cursor = conn.cursor()

    allowed_columns = {
        "id": "products.id",
        "product_id": "products.product_id",
        "title": "products.title",
        "number": "products.number",
        "list_price": "products.list_price",
        "buy_price": "products.buy_price",
        "price": "products.price",
        "stock": "products.stock",
        "color": "products.color"
    }
    sort_column = allowed_columns.get(sort_column, "products.title")
    sort_order = "DESC" if sort_order.upper() == "DESC" else "ASC"

    # Base query (used for both count and main fetch)
    base_query = """
        FROM products
        LEFT JOIN product_categories ON products.id = product_categories.product_id
        LEFT JOIN categories ON categories.id = product_categories.category_id
        WHERE (products.title LIKE ? OR products.number LIKE ?)
    """
    params = [f"%{filter_text}%", f"%{filter_text}%"]

    if category_filter_ids:
        placeholders = ','.join(['?'] * len(category_filter_ids))
        base_query += f" AND categories.id IN ({placeholders})"
        params.extend(category_filter_ids)

    if hide_no_title:
        base_query += " AND products.title IS NOT NULL AND products.title != ''"
    if hide_no_number:
        base_query += " AND products.number IS NOT NULL AND products.number != ''"
    if hide_no_price:
        base_query += " AND products.price IS NOT NULL AND products.price != ''"
    # Count query
    count_query = "SELECT COUNT(DISTINCT products.id) " + base_query
    cursor.execute(count_query, tuple(params))
    total_count = cursor.fetchone()[0]

    # Main fetch query
    full_query = f"""
        SELECT products.id, products.product_id, products.title, products.number,
               products.buy_price, products.price, products.color,
               IFNULL(GROUP_CONCAT(categories.name), '') AS category_names,
               IFNULL(GROUP_CONCAT(categories.id), '') AS category_ids
        {base_query}
        GROUP BY products.id
        ORDER BY {sort_column} {sort_order}
        LIMIT ? OFFSET ?
    """
    full_params = params + [limit, offset]
    cursor.execute(full_query, tuple(full_params))
    rows = cursor.fetchall()

    conn.close()
    return rows, total_count



def insert_product(data):
    if not data.get('title') or not data.get('number'):
        raise ValueError("Title and Number cannot be empty.")

    if not isinstance(data.get('category_ids'), list):
        raise ValueError("Category IDs must be a list.")

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO products (product_id, title, number, list_price, buy_price, price, stock, color)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data['product_id'], data['title'], data['number'], data['list_price'],
        data['buy_price'], data['price'], data['stock'], data['color']
    ))
    product_id = cursor.lastrowid

    for cat_id in data['category_ids']:
        cursor.execute("INSERT INTO product_categories (product_id, category_id) VALUES (?, ?)", (product_id, cat_id))

    conn.commit()
    conn.close()


def update_product(product_id, data):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE products SET title=?, number=?, list_price=?, buy_price=?, price=?, stock=?, color=? WHERE product_id=?",
                   (data['title'], data['number'], data['list_price'], data['buy_price'], data['price'], data['stock'], data['color'], product_id))
    cursor.execute("DELETE FROM product_categories WHERE product_id=(SELECT id FROM products WHERE product_id=?)", (product_id,))
    for cat_id in data['category_ids']:
        cursor.execute("INSERT INTO product_categories (product_id, category_id) VALUES ((SELECT id FROM products WHERE product_id=?), ?)", (product_id, cat_id))
    conn.commit()
    conn.close()

def delete_product(product_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM product_categories WHERE product_id=(SELECT id FROM products WHERE product_id=?)", (product_id,))
    cursor.execute("DELETE FROM products WHERE product_id=?", (product_id,))
    conn.commit()
    conn.close()

# --- UI Setup ---
class ProductApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Product Management")

        self.limit = 20
        self.offset = 0
        self.sort_column = "title"
        self.sort_order = "ASC"
        self.category_filter_ids = []

        self.create_widgets()
        self.populate_treeview()
        
    def apply_filters(self):
        self.category_filter_ids = self.category_box.get_selected_ids()
        self.offset = 0  # Reset pagination
        self.populate_treeview()
    
        if hasattr(self, 'category_box'):
            selected_names = self.category_box.get_selected_names()
            self.selected_categories_listbox.delete(0, tk.END)
            for name in selected_names:
                self.selected_categories_listbox.insert(tk.END, name)
    
    def add_category(self):
        # Prompt user for new category name
        name = simpledialog.askstring("Add Category", "Enter new category name:")
        if not name:
            messagebox.showwarning("Cancelled", "No category name entered.")
            return

        name = name.strip()
        conn = connect_db()
        cursor = conn.cursor()

        # Check for exact duplicate (case-insensitive)
        cursor.execute(
            "SELECT id, name FROM categories WHERE LOWER(name) = LOWER(?)",
            (name.lower(),)
        )
        existing = cursor.fetchone()
        if existing:
            messagebox.showerror(
                "Duplicate Category",
                f"A category named '{existing[1]}' (ID {existing[0]}) already exists."
            )
            conn.close()
            return

        # Find similar categories
        cursor.execute(
            "SELECT id, name FROM categories WHERE name LIKE ?",
            (f"%{name}%",)
        )
        similars = cursor.fetchall()
        if similars:
            sim_list = "\n".join(f"{cid}: {cname}" for cid, cname in similars)
            proceed = messagebox.askyesno(
                "Similar Categories Found",
                f"Found similar categories:\n{sim_list}\n\nDo you still want to add '{name}'?"
            )
            if not proceed:
                conn.close()
                return

        # Insert the new category
        cursor.execute(
            "INSERT INTO categories (name) VALUES (?)",
            (name,)
        )
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", f"Category '{name}' added.")

    def create_widgets(self):
        self.search_var = tk.StringVar()

        self.count_label = tk.Label(self.root, text="Total Products: 0")
        self.count_label.pack(anchor='w', padx=10, pady=(0, 5))

        self.hide_no_title = tk.BooleanVar()
        self.hide_no_number = tk.BooleanVar()
        self.hide_no_price = tk.BooleanVar()

        search_frame = tk.Frame(self.root)
        search_frame.pack(fill='x', padx=10, pady=5)
        self.selected_categories_label = tk.Label(self.root, text="Selected Categories:")

        self.selected_categories_label.pack(anchor='w', padx=10)

        self.selected_categories_listbox = tk.Listbox(self.root, height=4)
        self.selected_categories_listbox.pack(fill='x', padx=10, pady=(0, 10))
        
      
        tk.Checkbutton(search_frame, text="Hide products without title", variable=self.hide_no_title, command=self.populate_treeview).pack(side='left', padx=10)
        tk.Checkbutton(search_frame, text="Hide products without number", variable=self.hide_no_number, command=self.populate_treeview).pack(side='left')
        tk.Checkbutton(search_frame, text="Hide products without price", variable=self.hide_no_price, command=self.populate_treeview).pack(side='left')
        tk.Label(search_frame, text="Search:").pack(side='left')
        tk.Entry(search_frame, textvariable=self.search_var).pack(side='left', padx=5)

        # Category filter
        # tk.Label(search_frame, text="Filter by Category:").pack(side='left', padx=(10, 0))
        # self.category_box = CategoryAutocomplete(search_frame)
        # self.category_box.pack(side='left', padx=5)

        # tk.Button(search_frame, text="Apply Filters", command=self.apply_filters).pack(side='left', padx=5)

        tk.Button(search_frame, text="Search", command=self.populate_treeview).pack(side='left')


        self.tree = ttk.Treeview(self.root, columns=("ID", "Product ID", "Title", "Number", "Buy Price", "Price", "Color", "Categories", "Category IDs"), show='headings')
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col, command=lambda c=col: self.sort_by_column(c))
        self.tree.pack(fill='both', expand=True, padx=10, pady=5)

        btn_frame = tk.Frame(self.root)
        btn_frame.pack(fill='x', padx=10, pady=5)
        tk.Button(btn_frame, text="Add Category", command=self.add_category).pack(side='left', padx=5)
        tk.Button(btn_frame, text="Add Product", command=self.add_product).pack(side='left')
        tk.Button(btn_frame, text="Edit Product", command=self.edit_product).pack(side='left', padx=5)
        tk.Button(btn_frame, text="Delete Product", command=self.delete_selected_product).pack(side='left')
        tk.Button(btn_frame, text="Next Page", command=self.next_page).pack(side='right')
        tk.Button(btn_frame, text="Previous Page", command=self.prev_page).pack(side='right', padx=5)

    def populate_treeview(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        products, total_count = fetch_products(
            filter_text=self.search_var.get(),
            category_filter_ids=self.category_filter_ids,
            limit=self.limit,
            offset=self.offset,
            sort_column=self.sort_column,
            sort_order=self.sort_order,
            hide_no_title=self.hide_no_title.get(),
            hide_no_number=self.hide_no_number.get(),
            hide_no_price=self.hide_no_price.get()
        )

        self.count_label.config(text=f"Total Products: {total_count}")

        print(f"Fetched {len(products)} products")  # <-- Add this line

        for prod in products:
            print(prod)  # <-- Print the actual data too
            self.tree.insert('', 'end', values=prod)

    def sort_by_column(self, col):
        col = col.lower().replace(" ", "_")
        if self.sort_column == col:
            self.sort_order = "DESC" if self.sort_order == "ASC" else "ASC"
        else:
            self.sort_column = col
            self.sort_order = "ASC"
        self.populate_treeview()

    def next_page(self):
        self.offset += self.limit
        self.populate_treeview()

    def prev_page(self):
        if self.offset >= self.limit:
            self.offset -= self.limit
            self.populate_treeview()

    def get_selected_product(self):
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a product.")
            return None
        return self.tree.item(selected)['values']

    def add_product(self):
        ProductForm(self.root, callback=self.populate_treeview)

    def edit_product(self):
        data = self.get_selected_product()
        if not data:
            return
        category_ids = []
        if len(data) >= 9:
            ids_str = data[8] or ''
            category_ids = [int(i) for i in ids_str.split(',') if i]
        product_data = {
            'product_id': data[1],
            'title': data[2],
            'number': data[3],
            'buy_price': data[4],
            'price': data[5],
            'stock': data[6],
            'color': data[7],
            'category_ids': category_ids
        }
        ProductForm(self.root, product_data, self.populate_treeview)

    def delete_selected_product(self):
        data = self.get_selected_product()
        if data:
            if messagebox.askyesno("Confirm Delete", f"Delete product {data[2]}?"):
                delete_product(data[1])
                self.populate_treeview()

class ProductForm(tk.Toplevel):
    def __init__(self, parent, product_data=None, callback=None):
        super().__init__(parent)
        self.title("Product Form")
        self.geometry("600x300")
        self.callback = callback
        self.product_data = product_data

        self.inputs = {}
        fields = [
            ("Product ID", 'product_id'),
            ("Title", 'title'),
            ("Number", 'number'),
            ("List Price", 'list_price'),
            ("Buy Price", 'buy_price'),
            ("Price", 'price'),
            ("Stock", 'stock'),
            ("Color", 'color')
        ]

        for idx, (label, key) in enumerate(fields):
            tk.Label(self, text=label).grid(row=idx, column=0, padx=5, pady=2, sticky='e')
            entry = tk.Entry(self, width=40)
            entry.grid(row=idx, column=1, padx=5, pady=2)
            self.inputs[key] = entry

        # --- Categories ---
        # Category Autocomplete
        row_idx = len(fields)
        tk.Label(self, text="Categories").grid(row=len(fields), column=0, sticky='ne', padx=5)
        frame = tk.Frame(self)
        frame.grid(row=len(fields), column=1, sticky='w', padx=5)
        self.cat_box = CategoryAutocomplete(frame, allow_multiple=True, on_select=self.update_selected_categories)
        self.cat_box.pack(fill='x')
        
        self.selected_categories_listbox = tk.Listbox(self, height=4)
        self.selected_categories_listbox.grid(row=row_idx+1, column=1, sticky='w', padx=5)
        
        if self.product_data.get('product_id'):
            for key, entry in self.inputs.items():
                val = self.product_data.get(key)
                if val is not None:
                    entry.insert(0, val)
            if self.product_data.get('category_ids'):
                self.cat_box.set_initial_selection(self.product_data['category_ids'])
                self.update_selected_categories()
        tk.Button(self, text="Save", command=self.save_product).grid(row=len(fields)+1, column=0, columnspan=2, pady=10)


        # --- Save button ---
        tk.Button(self, text="Save", command=self.save_product).grid(row=len(fields)+1, column=0, columnspan=2, pady=10)

        # --- Prefill if editing ---
        if product_data:
            for key, entry in self.inputs.items():
                entry.insert(0, product_data.get(key, ""))
            self.cat_box.set_initial_selection(product_data.get('category_ids', []))
            self.update_selected_categories()

    def update_selected_categories(self):
        selected = self.cat_box.get_selected_names()
        self.selected_categories_listbox.delete(0, tk.END)
        for name in selected:
            self.selected_categories_listbox.insert(tk.END, name)

    def save_product(self):
        data = {k: e.get() for k, e in self.inputs.items()}
        data['category_ids'] = self.cat_box.get_selected_ids()
        if self.product_data.get('product_id'):
            update_product(self.product_data['product_id'], data)
        else:
            insert_product(data)
        if self.callback:
            self.callback()
        self.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ProductApp(root)
    root.mainloop()
