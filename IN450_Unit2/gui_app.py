import tkinter as tk
from tkinter import ttk, messagebox
import psycopg

from business_layer import BusinessLayer


class LoginFrame(ttk.Frame):
    def __init__(self, parent, on_login_success):
        super().__init__(parent)
        self.parent = parent
        self.on_login_success = on_login_success

        ttk.Label(self, text="Server:").grid(row=0, column=0, padx=10, pady=10, sticky="e")
        ttk.Label(self, text="Database:").grid(row=1, column=0, padx=10, pady=10, sticky="e")
        ttk.Label(self, text="User:").grid(row=2, column=0, padx=10, pady=10, sticky="e")
        ttk.Label(self, text="Password:").grid(row=3, column=0, padx=10, pady=10, sticky="e")

        self.server_entry = ttk.Entry(self, width=30)
        self.database_entry = ttk.Entry(self, width=30)
        self.user_entry = ttk.Entry(self, width=30)
        self.password_entry = ttk.Entry(self, width=30, show="*")

        self.server_entry.grid(row=0, column=1, padx=10, pady=10)
        self.database_entry.grid(row=1, column=1, padx=10, pady=10)
        self.user_entry.grid(row=2, column=1, padx=10, pady=10)
        self.password_entry.grid(row=3, column=1, padx=10, pady=10)

        self.server_entry.insert(0, "127.0.0.1")
        self.database_entry.insert(0, "postgres")

        ttk.Button(self, text="Login", command=self.try_login).grid(
            row=4, column=0, columnspan=2, pady=15
        )

    def try_login(self):
        server = self.server_entry.get().strip()
        database = self.database_entry.get().strip()
        user = self.user_entry.get().strip()
        password = self.password_entry.get()

        if not server or not database or not user or not password:
            messagebox.showerror("Login Error", "All login fields are required.")
            return

        try:
            business = BusinessLayer(server, database, user, password)
            business.test_login()
            self.on_login_success(business)

        except psycopg.OperationalError:
            messagebox.showerror(
                "Login Error",
                "Could not connect to the database. Check server, database, username, and password."
            )
        except Exception as exc:
            messagebox.showerror("Login Error", f"Unexpected error:\n{exc}")


class MainFrame(ttk.Frame):
    def __init__(self, parent, business):
        super().__init__(parent)
        self.parent = parent
        self.business = business

        ttk.Label(
            self,
            text=f"Logged in as: {self.business.user}",
            font=("Arial", 11, "bold")
        ).pack(pady=10)

        button_frame = ttk.Frame(self)
        button_frame.pack(pady=10)

        ttk.Button(
            button_frame,
            text="Count IN450a",
            command=self.show_count_a
        ).grid(row=0, column=0, padx=5, pady=5)

        ttk.Button(
            button_frame,
            text="List Names from IN450b",
            command=self.show_names_b
        ).grid(row=0, column=1, padx=5, pady=5)

        ttk.Button(
            button_frame,
            text="Count IN450c",
            command=self.show_count_c
        ).grid(row=0, column=2, padx=5, pady=5)

        ttk.Button(
            button_frame,
            text="Logout",
            command=self.parent.show_login
        ).grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(self, text="Results:").pack(anchor="w", padx=10)

        self.output_box = tk.Text(self, width=90, height=25)
        self.output_box.pack(fill="both", expand=True, padx=10, pady=10)

    def clear_output(self):
        self.output_box.delete("1.0", "end")

    def show_count_a(self):
        self.clear_output()
        try:
            count = self.business.get_count_in450a()
            self.output_box.insert("end", f"IN450a row count: {count}")
        except psycopg.errors.InsufficientPrivilege:
            self.output_box.insert("end", "Access denied: this user cannot view IN450a.")
        except Exception as exc:
            self.output_box.insert("end", f"Error: {exc}")

    def show_names_b(self):
        self.clear_output()
        try:
            names = self.business.get_names_in450b()
            self.output_box.insert("end", "IN450b first and last names:\n\n")
            for name in names:
                self.output_box.insert("end", f"{name}\n")
        except psycopg.errors.InsufficientPrivilege:
            self.output_box.insert("end", "Access denied: this user cannot view IN450b.")
        except Exception as exc:
            self.output_box.insert("end", f"Error: {exc}")

    def show_count_c(self):
        self.clear_output()
        try:
            count = self.business.get_count_in450c()
            self.output_box.insert("end", f"IN450c row count: {count}")
        except psycopg.errors.InsufficientPrivilege:
            self.output_box.insert("end", "Access denied: this user cannot view IN450c.")
        except Exception as exc:
            self.output_box.insert("end", f"Error: {exc}")


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("IN450 Unit 3 - Secure Data Access Application")
        self.geometry("900x650")
        self.current_frame = None
        self.show_login()

    def show_login(self):
        if self.current_frame is not None:
            self.current_frame.destroy()

        self.current_frame = LoginFrame(self, self.show_main)
        self.current_frame.pack(fill="both", expand=True, padx=20, pady=20)

    def show_main(self, business):
        if self.current_frame is not None:
            self.current_frame.destroy()

        self.current_frame = MainFrame(self, business)
        self.current_frame.pack(fill="both", expand=True, padx=20, pady=20)


if __name__ == "__main__":
    app = App()
    app.mainloop()