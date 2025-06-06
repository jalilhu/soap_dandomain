import tkinter as tk
from tkinter import ttk
from db import connect_db

class CategoryAutocomplete(tk.Frame):
    def __init__(self, master=None, allow_multiple=True, on_select=None):
        super().__init__(master)
        self.selected_ids = []
        self.on_select = on_select

        self.entry_var = tk.StringVar()
        self.entry = tk.Entry(self, textvariable=self.entry_var)
        self.entry.pack(fill='x')
        self.entry.bind('<KeyRelease>', self.on_keyrelease)
        self.entry.bind('<Return>', self.select_from_listbox)

        self.listbox = tk.Listbox(self, height=5, selectmode=tk.MULTIPLE)
        self.listbox.pack(fill='x')
        self.listbox.bind('<Double-Button-1>', self.select_from_listbox)

        self.selected_frame = tk.Frame(self)
        self.selected_frame.pack(fill='x')

    def on_keyrelease(self, event):
        search = self.entry_var.get()
        if len(search) < 2:
            self.listbox.delete(0, tk.END)
            return

        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT category_id, title FROM categories WHERE title LIKE ? LIMIT 10", (f"%{search}%",))
        results = cursor.fetchall()
        conn.close()

        self.listbox.delete(0, tk.END)
        for cid, name in results:
            self.listbox.insert(tk.END, f"{cid}: {name}")
    def remove_category(self, cid, frame):
        if cid in self.selected_ids:
            self.selected_ids.remove(cid)
            frame.destroy()
            if self.on_select:
                self.on_select()

    def select_from_listbox(self, event=None):
        selections = self.listbox.curselection()
        for index in selections:
            item = self.listbox.get(index)
            cid, name = item.split(': ', 1)
            cid = int(cid)
            if cid not in self.selected_ids:
                self.selected_ids.append(cid)
                frame = tk.Frame(self.selected_frame)
                frame.pack(fill='x', anchor='w', pady=1)

                label = tk.Label(frame, text=f"{name} ({cid})")
                label.pack(side='left')

                remove_btn = tk.Button(frame, text="✕", command=lambda c=cid, f=frame: self.remove_category(c, f), width=2)
                remove_btn.pack(side='right')
        self.entry_var.set("")
        self.listbox.delete(0, tk.END)

        if self.on_select:
            self.on_select()

    def get_selected_names(self):
        conn = connect_db()
        cursor = conn.cursor()
        if not self.selected_ids:
            return []
        placeholders = ','.join('?' for _ in self.selected_ids)
        cursor.execute(f"SELECT name FROM categories WHERE id IN ({placeholders})", self.selected_ids)
        names = [row[0] for row in cursor.fetchall()]
        conn.close()
        return names

    def get_selected_ids(self):
        return self.selected_ids

    def set_initial_selection(self, ids):
        conn = connect_db()
        cursor = conn.cursor()
        placeholders = ','.join('?' for _ in ids)
        cursor.execute(f"SELECT id, name FROM categories WHERE id IN ({placeholders})", ids)
        results = cursor.fetchall()
        conn.close()

        self.selected_ids = ids
        for cid, name in results:
            tk.Label(self.selected_frame, text=f"{name} ({cid})").pack(anchor='w')
