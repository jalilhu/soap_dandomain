import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import requests
import csv
from soap.soap_client import DandomainSOAPClient
from ai_tools.seo_generator import generate_seo_with_ai_for_category
import os

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get API keys from environment
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = DandomainSOAPClient()
if not DEEPSEEK_API_KEY or not GEMINI_API_KEY:
    raise ValueError("API keys are missing in .env file!")

# API Endpoints
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
DEEPSEEK_URL = "https://api.deepseek.com/chat/completions "

# SQLite Setup
conn = sqlite3.connect("products.db")
cursor = conn.cursor()

# Create tables if they don't exist
cursor.execute("""
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY,
        name TEXT
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS product_categories (
        product_id INTEGER,
        category_id INTEGER
    )
""")
conn.commit()


def save_category(name):
    cursor.execute("INSERT INTO categories (id, name) VALUES (NULL, ?)", (name,))
    conn.commit()
    return cursor.lastrowid


def save_relationship(product_id, category_id):
    cursor.execute("INSERT INTO product_categories (product_id, category_id) VALUES (?, ?)",
                   (product_id, category_id))
    conn.commit()


class CategoryEditorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Category Editor")

        # Variables
        self.categories = self.load_categories()
        self.selected_parents = []
        self.generated_data = {}  # Store data for CSV export
        self.ai_choice = tk.StringVar(value="Gemini")  # Default AI

        # UI setup
        self.create_ui()

    def create_ui(self):
        # Search Frame
        search_frame = ttk.Frame(self.root)
        search_frame.pack(pady=10)

        ttk.Label(search_frame, text="Search Categories:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_entry.bind("<KeyRelease>", self.update_suggestions)

        self.suggestion_list = tk.Listbox(self.root, height=5, width=40)
        self.suggestion_list.pack(fill=tk.X, padx=10, pady=5)
        self.suggestion_list.bind("<<ListboxSelect>>", self.on_select)

        # Form Fields
        form_frame = ttk.Frame(self.root)
        form_frame.pack(pady=10, fill=tk.BOTH, expand=True)

        # Title DK
        ttk.Label(form_frame, text="Title DK:").grid(row=0, column=0, sticky="w")
        self.title_entry = ttk.Entry(form_frame, width=60)
        self.title_entry.grid(row=0, column=1, padx=5, pady=2, sticky="ew")

        # Description DK (longer + multi-line)
        ttk.Label(form_frame, text="Description DK:").grid(row=1, column=0, sticky="nw")
        self.description_entry = tk.Text(form_frame, width=60, height=8, font=("Arial", 10))
        self.description_entry.grid(row=1, column=1, padx=5, pady=2, sticky="ew")

        # Description Bottom DK (longer + multi-line)
        ttk.Label(form_frame, text="Description Bottom DK:").grid(row=2, column=0, sticky="nw")
        self.description_bottom_entry = tk.Text(form_frame, width=60, height=6, font=("Arial", 10))
        self.description_bottom_entry.grid(row=2, column=1, padx=5, pady=2, sticky="ew")

        # SEO Title DK
        ttk.Label(form_frame, text="SEO Title DK:").grid(row=3, column=0, sticky="w")
        self.seo_title_entry = ttk.Entry(form_frame, width=60)
        self.seo_title_entry.grid(row=3, column=1, padx=5, pady=2, sticky="ew")

        # SEO Description DK (taller)
        ttk.Label(form_frame, text="SEO Description DK:").grid(row=4, column=0, sticky="nw")
        self.seo_description_entry = tk.Text(form_frame, width=60, height=4, font=("Arial", 10))
        self.seo_description_entry.grid(row=4, column=1, padx=5, pady=2, sticky="ew")

        # SEO Keywords DK
        ttk.Label(form_frame, text="SEO Keywords DK:").grid(row=5, column=0, sticky="w")
        self.seo_keywords_entry = ttk.Entry(form_frame, width=60)
        self.seo_keywords_entry.grid(row=5, column=1, padx=5, pady=2, sticky="ew")

        # SEO Link DK
        ttk.Label(form_frame, text="SEO Link DK:").grid(row=6, column=0, sticky="w")
        self.seo_link_entry = ttk.Entry(form_frame, width=60)
        self.seo_link_entry.grid(row=6, column=1, padx=5, pady=2, sticky="ew")

        # Sorting
        ttk.Label(form_frame, text="Sorting:").grid(row=7, column=0, sticky="w")
        self.sorting_entry = ttk.Entry(form_frame, width=60)
        self.sorting_entry.insert(0, "100")
        self.sorting_entry.grid(row=7, column=1, padx=5, pady=2, sticky="ew")

        # Selected Parents Display
        self.parent_frame = ttk.Frame(self.root)
        self.parent_frame.pack(pady=5, fill=tk.X)

        ttk.Label(self.parent_frame, text="Selected Parent IDs:").pack(side=tk.LEFT)
        self.parent_display = ttk.Frame(self.root)
        self.parent_display.pack(pady=5, fill=tk.X)

        # AI Selection & Generate Button
        ai_frame = ttk.Frame(self.root)
        ai_frame.pack(pady=10)

        ttk.Radiobutton(ai_frame, text="Gemini", variable=self.ai_choice, value="Gemini").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(ai_frame, text="DeepSeek", variable=self.ai_choice, value="DeepSeek").pack(side=tk.LEFT, padx=5)
        ttk.Button(ai_frame, text="Generate SEO with AI", command=self.generate_seo_with_ai).pack(side=tk.LEFT, padx=5)

        # Buttons
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(pady=10)

        ttk.Button(btn_frame, text="Add Category", command=self.add_category).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Export to CSV", command=self.export_to_csv).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Clear Form", command=self.clear_form).pack(side=tk.LEFT, padx=5)

        self.refresh_parent_display()

    def load_categories(self):
        cursor.execute("SELECT category_id, title FROM categories")
        return cursor.fetchall()

    def update_suggestions(self, event=None):
        """Update listbox based on search input"""
        search_term = self.search_var.get().lower()
        self.suggestion_list.delete(0, tk.END)

        if not search_term:
            return
        matches = [f"{cat[1]} ({cat[0]})" for cat in self.categories if search_term in str(cat[1]).lower()]
        for match in matches:
            self.suggestion_list.insert(tk.END, match)

    def on_select(self, event):
        """Handle selection from suggestion list"""
        try:
            index = self.suggestion_list.curselection()[0]
            selected_item = self.suggestion_list.get(index)
            selected_id = int(selected_item.split("(")[1].strip(")"))
            if selected_id not in self.selected_parents:
                self.selected_parents.append(selected_id)
                self.refresh_parent_display()
        except IndexError:
            pass

    def refresh_parent_display(self):
        """Redraw parent display with remove buttons"""
        for widget in self.parent_display.winfo_children():
            widget.destroy()

        for idx, pid in enumerate(self.selected_parents):
            frame = tk.Frame(self.parent_display)
            frame.pack(side=tk.TOP, anchor="w")

            label = tk.Label(frame, text=f"ID {pid}")
            label.pack(side=tk.LEFT)

            remove_btn = tk.Button(frame, text="X", fg="red", width=2,
                                   command=lambda i=idx: self.remove_parent(i))
            remove_btn.pack(side=tk.RIGHT, padx=2)

    def remove_parent(self, index):
        """Remove parent from selected list"""
        del self.selected_parents[index]
        self.refresh_parent_display()

    def generate_seo_with_ai(self):
        title = self.title_entry.get().strip()
        if not title:
            messagebox.showwarning("Missing Title", "Please enter a title first.")
            return

        if self.ai_choice.get() == "Gemini":
            result = generate_seo_with_ai_for_category(title)
        else:
            result = generate_seo_with_ai_for_category(title)

        # Fill fields
        self.seo_title_entry.delete(0, tk.END)
        self.seo_title_entry.insert(0, result.get("seo_title", ""))

        self.seo_description_entry.delete("1.0", tk.END)
        self.seo_description_entry.insert(tk.END, result.get("seo_description", ""))

        self.description_entry.delete("1.0", tk.END)
        self.description_entry.insert(tk.END, result.get("description", ""))

        self.description_bottom_entry.delete("1.0", tk.END)
        bottom_desc = result.get("description", "")[:255] + "..."
        self.description_bottom_entry.insert(tk.END, bottom_desc)

        self.seo_keywords_entry.delete(0, tk.END)
        self.seo_keywords_entry.insert(0, result.get("keywords", "").replace(" ", ""))
        
        self.seo_link_entry.delete(0, tk.END)
        self.seo_link_entry.insert(0, result.get("seo_link", "").replace(" ", "-").lower())

        messagebox.showinfo("AI Generated", "SEO and descriptions have been filled automatically.")


    def collect_category_data_from_ui(self):
        # Required fields
        title = self.title_entry.get().strip()
        description = self.description_entry.get("1.0", "end").strip()
        description_bottom = self.description_bottom_entry.get("1.0", "end").strip()
        seo_title = self.seo_title_entry.get().strip()
        seo_description = self.seo_description_entry.get("1.0", "end").strip()
        seo_keywords = self.seo_keywords_entry.get().strip()
        seo_link = self.seo_link_entry.get().strip()
        sorting_str = self.sorting_entry.get().strip()

        # Convert sorting to int safely
        try:
            sorting = int(sorting_str)
        except ValueError:
            sorting = 100  # default fallback

        # For demo, use fixed LanguageISO and Status
        language_iso = "Dk"
        status = True

        # Choose parent - if multiple parents selected, just pick the first or handle accordingly
        parent_id = self.selected_parents[0] if self.selected_parents else 0  # 0 if no parent

        category_data = {
            "Description": description,
            "DescriptionBottom": description_bottom,
            "Title": title,
            "SeoTitle": seo_title,
            "SeoDescription": seo_description,
            "SeoKeywords": seo_keywords,
            "SeoLink": seo_link,
            "ParentId": parent_id,
            "Status": status,
            "Sorting": sorting,
        }

        # Optional fields: add only if non-empty
        if description_bottom:
            category_data["DescriptionBottom"] = description_bottom
        if seo_title:
            category_data["SeoTitle"] = seo_title
        if seo_description:
            category_data["SeoDescription"] = seo_description
        if seo_keywords:
            category_data["SeoKeywords"] = seo_keywords
        if seo_link:
            category_data["SeoLink"] = seo_link

        
        category_data["LanguageAccess"] = []
        category_data["UserGroupAccessIds"] = []
        category_data["ShowInMenu"] = []
        category_data["SeoCanonical"] = ""
        category_data["LanguageISO"]   = language_iso

        return category_data
    
    def create_new_category(self):
        category_data = self.collect_category_data_from_ui()
        try:
            # The SOAP call expects keyword arguments matching the XSD element names
            print("Creating category with data:", category_data)
            response = client.create_new_category(category_data)
            new_category_id = response
            print(f"New category created with ID: {new_category_id}")
            self.save_to_database(
            category_id=new_category_id,
            title=category_data['Title'],
            parent_id=category_data['ParentId']
        )
            messagebox.showinfo("Success", f"Category created successfully with ID {new_category_id}")
            return new_category_id
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create category: {e}")
            raise

    def add_category(self):
        # Validate required fields
        title = self.title_entry.get().strip()
        if not title:
            messagebox.showwarning("Validation Error", "Title is required.")
            return

        # Call the create category method (assuming self.client is your SOAP client)
        try:
            category_id = self.create_new_category()
            # Optionally save to local DB
            save_category(title)
            messagebox.showinfo("Category Added", f"Category '{title}' added with ID {category_id}.")
            self.clear_form()
        except Exception as e:
            print(f"Error: {e}")

    def clear_form(self, reset_parents=True):
        self.title_entry.delete(0, tk.END)
        self.description_entry.delete("1.0", tk.END)
        self.description_bottom_entry.delete("1.0", tk.END)
        self.seo_title_entry.delete(0, tk.END)
        self.seo_description_entry.delete("1.0", tk.END)
        self.seo_keywords_entry.delete(0, tk.END)
        self.seo_link_entry.delete(0, tk.END)
        self.sorting_entry.delete(0, tk.END)
        self.sorting_entry.insert(0, "100")

        if reset_parents:
            self.selected_parents = []
            self.refresh_parent_display()

    def export_to_csv(self):
        if not self.generated_data:
            messagebox.showwarning("No Data", "No categories to export.")
            return

        filename = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
        if not filename:
            return

        fieldnames = [
            "PARENT_ID", "TITLE_DK", "DESCRIPTION_DK", "DESCRIPTION_BOTTOM_DK",
            "SEO_TITLE_DK", "SEO_DESCRIPTION_DK", "SEO_KEYWORDS_DK", "SEO_LINK_DK", "SORTING"
        ]

        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=";")
            writer.writeheader()
            for row in self.generated_data.values():
                writer.writerow(row)

        messagebox.showinfo("Exported", f"Saved {len(self.generated_data)} categories to CSV.")
        self.generated_data.clear()

    def refresh_parent_display(self):
        for widget in self.parent_display.winfo_children():
            widget.destroy()

        for idx, pid in enumerate(self.selected_parents):
            frame = tk.Frame(self.parent_display)
            frame.pack(side=tk.TOP, anchor="w")

            label = tk.Label(frame, text=f"ID {pid}")
            label.pack(side=tk.LEFT)

            remove_btn = tk.Button(frame, text="X", fg="red", width=2,
                                   command=lambda i=idx: self.remove_parent(i))
            remove_btn.pack(side=tk.RIGHT, padx=2)
    def save_to_database(self,category_id, title, parent_id):
        try:
            # Connect to your SQLite database
            conn = sqlite3.connect("products.db")  # Replace with your actual DB path
            cursor = conn.cursor()

            # Insert the new category
            cursor.execute("""
                INSERT INTO categories (category_id, title, parent_id)
                VALUES (?, ?, ?)
            """, (category_id, title, parent_id))

            # Commit and close
            conn.commit()
            conn.close()
            print("Category saved to local database successfully.")

        except sqlite3.Error as e:
            print("Database error:", e)
        

if __name__ == "__main__":
    root = tk.Tk()
    app = CategoryEditorApp(root)
    root.geometry("700x700")
    root.mainloop()