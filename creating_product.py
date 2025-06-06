import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import csv
from datetime import datetime
from webshop_api import WebshopAPI
import credentials



# All columns from your dataset
COLUMNS = [
    "PRODUCT_ID", "TITLE_DK", "PRODUCT_TYPE", "STATUS", "STOCK", "STOCK_LOW", "STOCK_IN_ORDER",
    "STOCK_DIFFERENCE", "STOCK_LOCATION_PRIMARY", "CALL_FOR_PRICE", "DISABLE_ON_EMPTY",
    "MANUFACTURER_ID", "DELIVERY_ID", "FREIGHT_ID", "OUT_OF_STOCK_BUY", "AUTO_STOCK", "UNIT_ID",
    "NUMBER", "SUPPLIER_NUMBER", "EAN", "PRODUCT_LINK", "URL", "WEIGHT", "FOCUS_FRONTPAGE",
    "FOCUS_CART", "SORTING", "LANGUAGE_LAYERS", "USER_ACCESS", "USERGROUP_ACCESS",
    "RELATED_PRODUCT_IDS", "RELATED_PRODUCT_NUMBERS", "PRODUCT_ADDITIONAL_DATA_TYPES",
    "PDF_FILES", "DATE_ADDED", "DATE_UPDATED", "DELETE", "DESCRIPTION_LIST_DK",
    "DESCRIPTION_LONG_DK", "DESCRIPTION_SHORT_DK", "CATEGORY_ID", "SUB_CATEGORY_ID",
    "CATEGORY_SORTINGS", "LIST_PRICE", "BUY_PRICE", "MIN_AMOUNT", "PRICE", "DISCOUNT",
    "DISCOUNT_TYPE", "DISCOUNT_GROUP", "VAT_GROUP", "PICTURES", "URL_PICTURE",
    "PICTURE_FOLDER", "SEO_TITLE_DK", "SEO_DESCRIPTION_DK", "SEO_KEYWORDS_DK", "SEO_LINK_DK",
    "SEO_CANONICAL_DK", "VARIANT_ID", "VARIANT_TYPES", "CUSTOM_DATA_3_DK", "CUSTOM_DATA_2_DK",
    "CUSTOM_DATA_4_DK", "CUSTOM_DATA_1_DK", "CUSTOM_DATA_5_DK", "CUSTOM_DATA_6_DK",
    "CUSTOM_DATA_7_DK", "CUSTOM_DATA_8_DK", "EXTRA_BUY_CATEGORY_1", "EXTRA_BUY_CATEGORY_2",
    "PRICEINDEX_ANNONSFYND", "PRICEINDEX_EDBPRISER", "PRICEINDEX_FACEBOOK",
    "PRICEINDEX_GOOGLE_ADWORDS", "PRICEINDEX_KELKOO", "PRICEINDEX_MIINTO",
    "PRICEINDEX_PRICERUNNER", "PRICEINDEX_SPAR30", "PRICEINDEX_TRENDSALES",
    "EDBPRISER_ID", "GOOGLE_CATEGORY_ID"
]

# Fields we will fill manually
INPUT_FIELDS = {
    "TITLE_DK": "Title DK",
    
    "NUMBER": "Number",
    "EAN": "EAN",
    "LIST_PRICE": "List Price",
    "BUY_PRICE": "Buy Price",
    "PRICE": "Price",
    "STOCK": "Stock",
    "CUSTOM_DATA_3_DK": "Color",
    "CATEGORY_ID": "Category ID",
    "SEO_TITLE_DK": "SEO Title DK",
    "SEO_DESCRIPTION_DK": "SEO Description DK",
    "SEO_KEYWORDS_DK": "SEO Keywords DK",
    "MANUFACTURER_ID": "Manufacturer",
    "PRODUCT_TYPE": "Product Type",
    "STATUS": "Status",
    "DISABLE_ON_EMPTY": "Disable on Empty"
}

# Default values for other fields
DEFAULT_VALUES = {
    "PRODUCT_TYPE": 0,
    "STATUS": 1,
    "STOCK_LOW": 0,
    "STOCK_IN_ORDER": 0,
    "STOCK_DIFFERENCE": 0,
    "STOCK_LOCATION_PRIMARY": 0,
    "CALL_FOR_PRICE": 0,
    "DISABLE_ON_EMPTY": 1,
    "DELIVERY_ID": "standard",
    "FREIGHT_ID": "",
    "OUT_OF_STOCK_BUY": 0,
    "AUTO_STOCK": "",
    "UNIT_ID": 1,
    "SUPPLIER_NUMBER": "",
    "EAN": "",
    "PRODUCT_LINK": "",
    "URL": "",
    "WEIGHT": "0\t100",
    "FOCUS_FRONTPAGE": 0,
    "FOCUS_CART": 0,
    "SORTING": 100,
    "LANGUAGE_LAYERS": "DK_1",
    "USER_ACCESS": "",
    "USERGROUP_ACCESS": "",
    "RELATED_PRODUCT_IDS": "",
    "RELATED_PRODUCT_NUMBERS": "",
    "PRODUCT_ADDITIONAL_DATA_TYPES": "",
    "PDF_FILES": "",
    "DATE_ADDED": "0000-00-00 00:00:00",
    "DATE_UPDATED": lambda p: datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "DELETE": "",
    "DESCRIPTION_LIST_DK": "",
    "DESCRIPTION_LONG_DK": "",
    "DESCRIPTION_SHORT_DK": "",
    "SUB_CATEGORY_ID": "",
    "CATEGORY_SORTINGS": "",
    "MIN_AMOUNT": 1,
    "DISCOUNT": "0\t00",
    "DISCOUNT_TYPE": "a",
    "DISCOUNT_GROUP": 0,
    "VAT_GROUP": 0,
    "PICTURES": "",
    "URL_PICTURE": "",
    "PICTURE_FOLDER": "",
    "SEO_TITLE_DK": lambda p: p.get("SEO_TITLE_DK", "") or f"{p.get('TITLE_DK', '')}",
    "SEO_DESCRIPTION_DK": lambda p: p.get("SEO_DESCRIPTION_DK", "") or f"{p.get('TITLE_DK', '')} ",
    "SEO_KEYWORDS_DK": lambda p: p.get("SEO_KEYWORDS_DK", "") or f"{p.get('TITLE_DK', '')}",
    "SEO_LINK_DK": "",
    "SEO_CANONICAL_DK": "",
    "VARIANT_ID": "",
    "VARIANT_TYPES": "",
    "CUSTOM_DATA_2_DK": "",
    "CUSTOM_DATA_4_DK": "",
    "CUSTOM_DATA_1_DK": "",
    "CUSTOM_DATA_5_DK": "",
    "CUSTOM_DATA_6_DK": "",
    "CUSTOM_DATA_7_DK": "",
    "CUSTOM_DATA_8_DK": "",
    "EXTRA_BUY_CATEGORY_1": 0,
    "EXTRA_BUY_CATEGORY_2": 0,
    "PRICEINDEX_ANNONSFYND": 0,
    "PRICEINDEX_EDBPRISER": 0,
    "PRICEINDEX_FACEBOOK": 1,
    "PRICEINDEX_GOOGLE_ADWORDS": 0,
    "PRICEINDEX_KELKOO": 0,
    "PRICEINDEX_MIINTO": 0,
    "PRICEINDEX_PRICERUNNER": 0,
    "PRICEINDEX_SPAR30": 0,
    "PRICEINDEX_TRENDSALES": 0,
    "EDBPRISER_ID": "",
    "GOOGLE_CATEGORY_ID": 356
}


class ProductEntryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Product Entry Form")
        self.scale = 1  # Reduced scale for better visibility
        self.default_font = ("Arial", 12 * self.scale)
        self.root.option_add("*Font", self.default_font)
        
        self.api = WebshopAPI(
            wsdl_url=credentials.WSDL_URL,
            username=credentials.USERNAME,
            password=credentials.PASSWORD,
        )
        
        style = ttk.Style()
        style.configure("TButton", padding=(10 * self.scale, 5 * self.scale))
        self.products = []

        # Input fields
        self.DROPDOWN_OPTIONS = {
            "STATUS": ["Aktiv", "Ikke aktiv"],
            "MANUFACTURER_ID": ["Apple", "Brother", "Canon", "Epson", "HP", "Kompatibel", "Samsung"],
            "PRODUCT_TYPE": ["Original", "Refill", "Uoriginal"]
        }

        # Map display names to actual values
        self.OPTION_VALUE_MAPS = {
            "STATUS": {"Aktiv": 1, "Ikke aktiv": 0},
            "DISABLE_ON_EMPTY": {"Aktiv": 0, "Ikke aktiv": 1},
            "MANUFACTURER_ID": {
                "Apple": 1,
                "Brother": 2,
                "Canon": 3,
                "Epson": 4,
                "HP": 5,
                "Kompatibel": 6,
                "Samsung": 7
            },
            "PRODUCT_TYPE": {"Original": 0, "Refill": 1, "Uoriginal": 2}
        }

        # Create input fields (with dropdowns where applicable)
        self.inputs = {}  # To store both Entry and OptionMenu widgets
        self.tk_vars = {}  # To store StringVar objects

        for idx, (key, label) in enumerate(INPUT_FIELDS.items()):
            tk.Label(root, text=label, width=20 * self.scale).grid(
                row=idx, column=0, sticky="w", padx=5, pady=5
            )

            if key in self.DROPDOWN_OPTIONS:
                # Dropdown field
                var = tk.StringVar()
                self.tk_vars[key] = var
                dropdown = ttk.OptionMenu(root, var, self.DROPDOWN_OPTIONS[key][0], *self.DROPDOWN_OPTIONS[key])
                dropdown.grid(row=idx, column=1, padx=5, pady=5, sticky="ew")
                self.inputs[key] = dropdown
            else:
                # Regular text field
                entry = tk.Entry(root, width=50 * self.scale // 2)
                entry.grid(row=idx, column=1, padx=5, pady=5)
                self.inputs[key] = entry

        # Add and Save buttons
        ttk.Button(root, text="Add Product", command=self.add_product).grid(
            row=len(INPUT_FIELDS), column=0, padx=5, pady=10
        )
        ttk.Button(root, text="Save to CSV", command=self.save_to_csv).grid(
            row=len(INPUT_FIELDS), column=1, padx=5, pady=10
        )
        
        # Adjust window size
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        root.geometry(f"{int(screen_width // 2)}x{int(screen_height // 1.5)}")

    def add_product(self):
        product = {}
        
        
        for key in INPUT_FIELDS:
            if key in self.DROPDOWN_OPTIONS:
                selected_label = self.tk_vars[key].get()
                mapped_value = self.OPTION_VALUE_MAPS[key].get(selected_label, "")
                product[key] = mapped_value
            else:
                product[key] = self.inputs[key].get()
        
        if not product["TITLE_DK"]:
            messagebox.showerror("Error", "Title DK is required.")
            return

        full_product = {}

        # Fill input values
        for key in COLUMNS:
            if key in product:
                full_product[key] = product[key]
            elif key in DEFAULT_VALUES:
                val = DEFAULT_VALUES[key]
                if callable(val):
                    val = val(product)
                full_product[key] = val
            else:
                full_product[key] = ""

        self.products.append(full_product)
        messagebox.showinfo("Success", "Product added!")

        # Clear entries - fixed to use self.inputs
        for key, widget in self.inputs.items():
            if key in self.DROPDOWN_OPTIONS:
                self.tk_vars[key].set(self.DROPDOWN_OPTIONS[key][0])
            else:
                widget.delete(0, tk.END)

    def save_to_csv(self):
        if not self.products:
            messagebox.showerror("Error", "No products to save.")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
        if not file_path:
            return

        with open(file_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=COLUMNS, delimiter=';')
            writer.writeheader()
            writer.writerows(self.products)

        messagebox.showinfo("Success", f"Saved {len(self.products)} products to {file_path}")


if __name__ == "__main__":
    root = tk.Tk()
    app = ProductEntryApp(root)
    root.mainloop()