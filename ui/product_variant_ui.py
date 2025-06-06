# update_custom_data_ui.py

import tkinter as tk
from tkinter import ttk, messagebox
from soap.soap_client import DandomainSOAPClient
from ui.product_picture_uploader import launch_picture_uploader

# Constants
PRODUCT_TYPE_OPTIONS = ["original", "refill", "uoriginal"]
COLOR_OPTIONS = [
    "Blå, Rød, Gul",
    "Grå",
    "Ingen farve",
    "Lys Cyan/Blå",
    "Lys Magenta / Rød",
    "Blå",
    "Rød",
    "Gul",
    "Sort",
    "Blå, Rød, Gul, Sort"
]

PRODUCT_TYPE_VALUE_MAP = {
    "original": 0,
    "refill": 1,
    "uoriginal": 2
}

COLOR_VALUE_MAP = {color: i * 10 for i, color in enumerate(COLOR_OPTIONS)}  # Sorting values


class CustomDataUpdateForm:
    def __init__(self, root, product_id=None):
        self.root = root
        self.root.title("Update Product Custom Data")

        self.soap_client = DandomainSOAPClient()

        # Product ID input
        tk.Label(root, text="Product ID").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.product_id_entry = tk.Entry(root)
        self.product_id_entry.grid(row=0, column=1, padx=5, pady=5)

        if product_id:
            self.product_id_entry.insert(0, str(product_id))
            self.product_id_entry.config(state="readonly", disabledbackground="#f0f0f0", disabledforeground="#000")

        # Product Type dropdown
        tk.Label(root, text="Product Type").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.product_type_dropdown = ttk.Combobox(root, values=PRODUCT_TYPE_OPTIONS, state="readonly")
        self.product_type_dropdown.grid(row=1, column=1, padx=5, pady=5)
        self.product_type_dropdown.current(0)

        # Color dropdown
        tk.Label(root, text="Color").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.color_dropdown = ttk.Combobox(root, values=COLOR_OPTIONS, state="readonly")
        self.color_dropdown.grid(row=2, column=1, padx=5, pady=5)
        self.color_dropdown.current(0)

        # Submit
        tk.Button(root, text="Update", command=self.submit).grid(row=3, column=0, columnspan=2, pady=10)

    def submit(self):
        try:
            product_id = int(self.product_id_entry.get().strip())
            product_type_title = self.product_type_dropdown.get()
            color_title = self.color_dropdown.get()
            
            data = [
                {'Id': 4, 'ProductCustomTypeId': 3, 'Title': 'Blå'},
                {'Id': 12, 'ProductCustomTypeId': 3, 'Title': 'Blå, Rød, Gul'},
                {'Id': 8, 'ProductCustomTypeId': 3, 'Title': 'Blå, Rød, Gul, Sort'},
                {'Id': 11, 'ProductCustomTypeId': 3, 'Title': 'Grå'},
                {'Id': 6, 'ProductCustomTypeId': 3, 'Title': 'Gul'},
                {'Id': 13, 'ProductCustomTypeId': 3, 'Title': 'Ingen farve'},
                {'Id': 14, 'ProductCustomTypeId': 1, 'Title': 'Intet valgt'},
                {'Id': 10, 'ProductCustomTypeId': 3, 'Title': 'Lys Cyan / Blå'},
                {'Id': 9, 'ProductCustomTypeId': 3, 'Title': 'Lys Magenta / Rød'},
                {'Id': 1, 'ProductCustomTypeId': 1, 'Title': 'original'},
                {'Id': 3, 'ProductCustomTypeId': 1, 'Title': 'refill'},
                {'Id': 5, 'ProductCustomTypeId': 3, 'Title': 'Rød'},
                {'Id': 7, 'ProductCustomTypeId': 3, 'Title': 'Sort'},
                {'Id': 2, 'ProductCustomTypeId': 1, 'Title': 'uoriginal'}
            ]
            
            type_entry = next((item for item in data if item['ProductCustomTypeId'] == 1 and item['Title'].lower() == product_type_title), None)
            if not type_entry:
                raise ValueError(f"Type '{product_type_title}' not found in data.")
            
            color_entry = next((item for item in data if item['ProductCustomTypeId'] == 3 and item['Title'].strip() == color_title), None)
            if not color_entry:
                raise ValueError(f"Color '{color_title}' not found in data.")
            
            type_custom_data_id = type_entry['Id']
            color_custom_data_id = color_entry['Id']

            response1 = self.soap_client.add_custom_data_to_product(product_id, type_custom_data_id)
            response2 = self.soap_client.add_custom_data_to_product(product_id, color_custom_data_id)
            # --- Update Color ---
                
            print(f"Type ID: {type_custom_data_id}, Color ID: {color_custom_data_id}")
            print(f"SOAP Responses: {response1}, {response2}")
            print(f"Response1: {response1} ({type(response1)}), Response2: {response2} ({type(response2)})")

            if str(response1).lower() == "true" and str(response2).lower() == "true":
                messagebox.showinfo("Success", "Custom data updated! Now upload a product image.")
                launch_picture_uploader(product_id)
        except Exception as e:
            messagebox.showerror("Error", str(e))


# Function to launch the UI externally
def launch_custom_data_ui(product_id=None):
    root = tk.Tk()
    app = CustomDataUpdateForm(root, product_id=product_id)
    root.mainloop()
