# File: ui/main_ui.py
from ai_tools.seo_generator import generate_seo_with_ai
import tkinter as tk
from tkinter import messagebox, ttk
import csv, os
from category_edited import CategoryEditorApp
from .utils import DROPDOWN_OPTIONS, map_display_to_value, OPTION_VALUE_MAPS, OTHER_DATA_FIELDS
from soap.soap_client import DandomainSOAPClient
from category_utils import CategoryAutocomplete
from datetime import datetime
from soap.client import send_product, create_product_variant  # our SOAP handler
import config

# FIELDS = [
#     'Title', 'Status', 'ProducerId', 'UnitId', 'ItemNumber', 'ItemNumberSupplier', 'Ean',
#     'Sorting', 'DateCreated', 'DateUpdated', 'Description', 'DescriptionLong', 'DescriptionShort',
#     'CategoryId', 'SecondaryCategoryIds', 'BuyingPrice', 'Price', 'SeoTitle',
#     'SeoDescription', 'SeoKeywords', 'SeoLink', 'SeoCanonical'
# ]
FIELDS = [
    'Title', 'Status', 'ProducerId', 'Type', 'ItemNumber', 'ItemNumberSupplier', 'Ean',
    'Sorting','Description', 'DescriptionLong', 'DescriptionShort',
    'CategoryId', 'SecondaryCategoryIds', 'BuyingPrice', 'Price', 'SeoTitle',
    'SeoDescription', 'SeoKeywords'
]

DROPDOWN_OPTIONS['TYPE'] = [
    "normal",
    "fileslag",
    "Gavekort der udløser rabatkode",
    "Gavekort uden rabatkode",
    "Udgået",
    "Ring for pris"
]




# Map your form field names to the keys in DROPDOWN_OPTIONS
FIELD_TO_DROPDOWN_KEY = {
    'Status': 'STATUS',
    'ProducerId': 'MANUFACTURER_ID',
    'Type': 'TYPE',
}

# Add these fields to your form fields list for UI:

class ProductUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Dandomain Product Creator")
        self.geometry("800x600")
        self.product_id = None  # Initialize product_id to None
        self.soap_client = DandomainSOAPClient()

        # Create a main container frame
        self.main_container = tk.Frame(self)
        self.main_container.pack(fill="both", expand=True)

        # Create a canvas and scrollbar
        self.canvas = tk.Canvas(self.main_container)
        self.scrollbar = ttk.Scrollbar(self.main_container, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Bind mousewheel scrolling
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.bind("<Destroy>", lambda e: self.canvas.unbind_all("<MouseWheel>"))

        self.entries = {}
        self.create_form()
        self.create_buttons()

    def _on_mousewheel(self, event):
        try:
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        except tk.TclError:
            pass  # Ignore error if canvas not scrollable
    def open_create_category_window(self):
    # For now, just show a messagebox
        category_window = tk.Toplevel()  # Creates a new top-level window
        CategoryEditorApp(category_window)
        messagebox.showinfo("Create Category", "This will open the category creation window.")

    def generate_seo_with_ai(self):
        title = self.title_entry.get().strip()
        if not title:
            messagebox.showwarning("Missing Title", "Please enter a title first.")
            return

        try:
            result = generate_seo_with_ai(title)
        except Exception as e:
            messagebox.showerror("AI Error", str(e))
            return

        self.seo_title_entry.delete(0, tk.END)
        self.seo_title_entry.insert(0, result.get("seo_title", ""))
        
        self.item_number_entry = self.entries.get('ItemNumber')
        self.item_number_entry.insert(tk.END, result.get("item_number", ""))
        self.item_number_supplier_entry = self.entries.get('ItemNumberSupplier')
        self.item_number_supplier_entry.insert(tk.END, result.get("item_number_supplier", ""))
        self.ean_entry = self.entries.get('Ean')
        self.ean_entry.insert(tk.END, result.get("ean", ""))
        
        self.seo_description_entry.delete("1.0", tk.END)
        self.seo_description_entry.insert(tk.END, result.get("seo_description", ""))

        self.description_entry.delete("1.0", tk.END)
        self.description_entry.insert(tk.END, result.get("description", ""))

        self.description_bottom_entry.delete("1.0", tk.END)
        bottom_desc = result.get("description", "")[:255] + "..."
        self.description_bottom_entry.insert(tk.END, bottom_desc)

        self.seo_keywords_entry.delete(0, tk.END)
        self.seo_keywords_entry.insert(0, result.get("keywords", "").replace(" ", ""))

        messagebox.showinfo("AI Generated", "SEO and descriptions have been filled automatically.")

    def create_buttons(self):
        btn_send = tk.Button(self.scrollable_frame, text="Create Product", command=self.send_product)
        btn_send.grid(row=len(FIELDS)+1, column=0, pady=10)

        btn_ai = tk.Button(self.scrollable_frame, text="Generate SEO with AI", command=self.generate_seo_with_ai)
        btn_ai.grid(row=len(FIELDS)+1, column=1, pady=10)

    def create_form(self):
        for idx, field in enumerate(FIELDS):
            label = tk.Label(self.scrollable_frame, text=field)
            label.grid(row=idx, column=0, sticky="w", padx=5, pady=2)

            if field in FIELD_TO_DROPDOWN_KEY:
                dropdown_key = FIELD_TO_DROPDOWN_KEY[field]
                combo = ttk.Combobox(self.scrollable_frame, values=DROPDOWN_OPTIONS[dropdown_key], state="readonly")
                combo.grid(row=idx, column=1, sticky="ew", padx=5, pady=2)
                combo.current(0)
                self.entries[field] = combo
            elif field == 'UnitId':  # Add this specific case
                combo = ttk.Combobox(self.scrollable_frame, values=DROPDOWN_OPTIONS['UNIT_ID'], state="readonly")
                combo.grid(row=idx, column=1, sticky="ew", padx=5, pady=2)
                combo.current(0)
                self.entries[field] = combo
            elif field == 'CategoryId':
    # Replace Entry with CategoryAutocomplete
                self.category_widget = CategoryAutocomplete(self.scrollable_frame, allow_multiple=False, on_select=lambda: None)
                self.category_widget.grid(row=idx, column=1, sticky="ew", padx=5, pady=2)
                self.entries[field] = self.category_widget
                print("Creating the button now...")
                print(f"scrollable_frame = {self.scrollable_frame}")
                print(f"type of scrollable_frame: {type(self.scrollable_frame)}")
                btn_create_category = tk.Button(self.scrollable_frame, text="Create New Category", command=self.open_create_category_window)
                btn_create_category.grid(row=idx, column=2, sticky="ew", padx=5, pady=2)
                btn_create_category.grid(row=idx, column=2, padx=5, pady=2)
            elif field == 'SecondaryCategoryIds':
                self.secondary_categories_widget = CategoryAutocomplete(
                    self.scrollable_frame,
                    allow_multiple=True,
                    on_select=lambda: None
                )
                self.secondary_categories_widget.grid(row=idx, column=1, sticky="ew", padx=5, pady=2)
                self.entries[field] = self.secondary_categories_widget
            elif field == 'Title':
                entry = tk.Entry(self.scrollable_frame)
                entry.grid(row=idx, column=1, sticky="ew", padx=5, pady=2)
                self.entries[field] = entry
                self.title_entry = entry  # Assign directly for AI function

            elif field == 'SeoTitle':
                entry = tk.Entry(self.scrollable_frame)
                entry.grid(row=idx, column=1, sticky="ew", padx=5, pady=2)
                self.entries[field] = entry
                self.seo_title_entry = entry

            elif field == 'SeoDescription':
                entry = tk.Text(self.scrollable_frame, height=3)
                entry.grid(row=idx, column=1, sticky="ew", padx=5, pady=2)
                self.entries[field] = entry
                self.seo_description_entry = entry
            elif field == 'SeoKeywords':
                entry = tk.Entry(self.scrollable_frame)
                entry.grid(row=idx, column=1, sticky="ew", padx=5, pady=2)
                self.entries[field] = entry
                self.seo_keywords_entry = entry
            elif field == 'Description':
                entry = tk.Text(self.scrollable_frame, height=3)
                entry.grid(row=idx, column=1, sticky="ew", padx=5, pady=2)
                self.entries[field] = entry
                self.description_entry = entry
            elif field == 'DescriptionShort':
                entry = tk.Text(self.scrollable_frame, height=3)
                entry.grid(row=idx, column=1, sticky="ew", padx=5, pady=2)
                self.entries[field] = entry
                self.description_bottom_entry = entry  # assuming this is DescriptionShort used at bottom
            elif field == 'DescriptionLong':
                entry = tk.Text(self.scrollable_frame, height=3)
                entry.grid(row=idx, column=1, sticky="ew", padx=5, pady=2)
                self.entries[field] = entry
                self.description_bottom_entry = entry  # assuming this is DescriptionShort used at bottom

            else:
                entry = tk.Entry(self.scrollable_frame)
                entry.grid(row=idx, column=1, sticky="ew", padx=5, pady=2)
                self.entries[field] = entry

        self.grid_columnconfigure(1, weight=1)

    def get_form_data(self):
        data = {}
        for field, widget in self.entries.items():
            try:
                if isinstance(widget, tk.Text):
                    value = widget.get("1.0", tk.END).strip()
                elif isinstance(widget, CategoryAutocomplete):
                    selected_ids = widget.get_selected_ids()
                    if field == 'CategoryId':
                        value = selected_ids[0] if selected_ids else None
                    elif field == 'SecondaryCategoryIds':
                        value = selected_ids if selected_ids else []
                    else:
                        value = None
                else:
                    value = widget.get().strip()# Standard Entry/Combobox

                # Process the value based on field type
                if field in FIELD_TO_DROPDOWN_KEY:
                    dropdown_key = FIELD_TO_DROPDOWN_KEY[field]
                    data[field] = map_display_to_value(dropdown_key, value)
                elif field in ['BuyingPrice', 'Price']:
                    data[field] = float(value.replace(',', '.')) if value else 0.0
                # elif field in ['DateCreated', 'DateUpdated']:
                #     data[field] = value if value else datetime.now().isoformat()
                elif field == 'CategoryId':
                    selected_ids = self.category_widget.get_selected_ids()
                    data[field] = selected_ids[0] if selected_ids else None 

                elif field == 'SecondaryCategoryIds':
                    selected_ids = self.secondary_categories_widget.get_selected_ids()
                    data[field] = selected_ids if selected_ids else []
                    
                elif field in ['BuyingPrice', 'Price']:
                    try:
                        data[field] = float(value.replace(',', '.'))
                    except ValueError:
                        messagebox.showwarning("Invalid Input", f"Invalid value for {field}. Must be a number.")
                        return None

                # elif field in ['DateCreated', 'DateUpdated']:
                #     data[field] = value if value else datetime.now().isoformat()

                else:
                    data[field] = value if value else None
            except Exception as e:
                messagebox.showerror("Error", f"Error processing {field}: {str(e)}")
                return None
       
        data['DescriptionLong'] = data.get('Description', "")
        for key, default_value in OTHER_DATA_FIELDS.items():
            if key not in data:
                print(key)
                print(default_value)
                data[key] = default_value

        return data

    def send_product(self):
        product_data = self.get_form_data()
        print("Sending Product Data:", product_data)  # Debug
        try:
            self.product_id = self.soap_client.create_product(product_data)
            messagebox.showinfo("Success", f"Product created with ID: {self.product_id}")
            self.destroy()


        except Exception as e:
            messagebox.showerror("Error", f"Failed: {str(e)}")

def launch_main_ui():
    app = ProductUI()
    app.mainloop()
    return app.product_id  # Return the created product ID if needed


