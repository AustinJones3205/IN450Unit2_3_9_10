import tkinter as tk
from tkinter import ttk, messagebox
from business_layer import BusinessLayer

class App(tk.Tk):
    def __init__(self):
        super().__init__()

        # Put your REAL postgres password here
        self.business = BusinessLayer(
            user="postgres",
            password="Spring@2026",
            host="127.0.0.1",
            database="postgres"
        )

        self.title("IN450 Unit 2 - Data Access Application")
        self.geometry("950x650")

        button_frame = ttk.Frame(self)
        button_frame.pack(fill="x", padx=10, pady=10)

        ttk.Button(button_frame, text="Count rows in in450a", command=self.show_count).pack(side="left", padx=5)
        ttk.Button(button_frame, text="List names from in450b", command=self.show_names).pack(side="left", padx=5)

        ttk.Label(self, text="in450a data (preview):").pack(anchor="w", padx=10)
        self.text_a = tk.Text(self, height=14)
        self.text_a.pack(fill="both", expand=True, padx=10)

        ttk.Label(self, text="in450b data (preview):").pack(anchor="w", padx=10, pady=(10, 0))
        self.text_b = tk.Text(self, height=14)
        self.text_b.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.load_previews()

    def load_previews(self):
        self.text_a.delete("1.0", "end")
        self.text_b.delete("1.0", "end")

        a_rows = self.business.get_in450a_preview(limit=25)
        b_rows = self.business.get_in450b_preview(limit=25)

        for row in a_rows:
            self.text_a.insert("end", f"{row}\n")

        for row in b_rows:
            self.text_b.insert("end", f"{row}\n")

    def show_count(self):
        count = self.business.get_count_in450a()
        messagebox.showinfo("Row Count", f"in450a has {count} rows.")

    def show_names(self):
        names = self.business.get_names_in450b()
        messagebox.showinfo("Names from in450b", "\n".join(names[:50]) + ("\n..." if len(names) > 50 else ""))

if __name__ == "__main__":
    App().mainloop()
