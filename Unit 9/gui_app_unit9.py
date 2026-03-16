import logging
import re
import tkinter as tk
from tkinter import messagebox, ttk

import psycopg

from business_layer_unit9 import BusinessLayer


logging.basicConfig(
    filename="security_events.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

MAX_LOGIN_ATTEMPTS = 3
FIELD_MAX_LENGTH = 50
ALLOWED_PATTERN = re.compile(r"^[A-Za-z0-9_.-]+$")


class LoginFrame(ttk.Frame):
    def __init__(self, parent, on_login_success):
        super().__init__(parent)
        self.parent = parent
        self.on_login_success = on_login_success
        self.failed_attempts = 0
        self.locked_out = False

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

        self.login_button = ttk.Button(self, text="Login", command=self.try_login)
        self.login_button.grid(row=4, column=0, columnspan=2, pady=15)

        self.status_label = ttk.Label(self, text="", foreground="red")
        self.status_label.grid(row=5, column=0, columnspan=2, pady=5)

    def validate_text_field(self, value: str, field_name: str) -> bool:
        if not value:
            messagebox.showerror("Login Error", f"{field_name} is required.")
            return False
        if len(value) > FIELD_MAX_LENGTH:
            messagebox.showerror("Login Error", f"{field_name} must be {FIELD_MAX_LENGTH} characters or fewer.")
            return False
        if not ALLOWED_PATTERN.fullmatch(value):
            messagebox.showerror(
                "Login Error",
                f"{field_name} contains invalid characters. Use only letters, numbers, periods, hyphens, and underscores.",
            )
            return False
        return True

    def clear_password(self):
        self.password_entry.delete(0, tk.END)

    def record_failed_attempt(self, user: str):
        self.failed_attempts += 1
        logger.warning("Failed login attempt for user '%s'. Attempt %s of %s.", user, self.failed_attempts, MAX_LOGIN_ATTEMPTS)
        self.clear_password()

        attempts_left = MAX_LOGIN_ATTEMPTS - self.failed_attempts
        if attempts_left <= 0:
            self.locked_out = True
            self.login_button.config(state="disabled")
            self.status_label.config(text="Login locked after too many failed attempts. Restart the app to try again.")
            logger.error("Login locked after repeated failures for user '%s'.", user)
        else:
            self.status_label.config(text=f"Login failed. Attempts remaining: {attempts_left}")

    def try_login(self):
        if self.locked_out:
            return

        server = self.server_entry.get().strip()
        database = self.database_entry.get().strip()
        user = self.user_entry.get().strip()
        password = self.password_entry.get()

        if not self.validate_text_field(server, "Server"):
            return
        if not self.validate_text_field(database, "Database"):
            return
        if not self.validate_text_field(user, "User"):
            return
        if not password:
            messagebox.showerror("Login Error", "Password is required.")
            return
        if len(password) > 128:
            messagebox.showerror("Login Error", "Password is too long.")
            self.clear_password()
            return

        try:
            business = BusinessLayer(server, database, user, password)
            business.test_login()
            self.clear_password()
            logger.info("Successful login for user '%s'.", user)
            self.on_login_success(business)

        except psycopg.OperationalError:
            self.record_failed_attempt(user)
            messagebox.showerror(
                "Login Error",
                "Login failed. Check your credentials and connection settings.",
            )
        except Exception:
            logger.exception("Unexpected error during login for user '%s'.", user)
            self.clear_password()
            messagebox.showerror("Login Error", "An unexpected error occurred during login.")


class MainFrame(ttk.Frame):
    def __init__(self, parent, business):
        super().__init__(parent)
        self.parent = parent
        self.business = business

        ttk.Label(
            self,
            text=f"Logged in as: {self.business.user}",
            font=("Arial", 11, "bold"),
        ).pack(pady=10)

        button_frame = ttk.Frame(self)
        button_frame.pack(pady=10)

        ttk.Button(button_frame, text="Count IN450a", command=self.show_count_a).grid(row=0, column=0, padx=5, pady=5)
        ttk.Button(button_frame, text="List Names from IN450b", command=self.show_names_b).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(button_frame, text="Count IN450c", command=self.show_count_c).grid(row=0, column=2, padx=5, pady=5)
        ttk.Button(button_frame, text="Logout", command=self.logout).grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(self, text="Results:").pack(anchor="w", padx=10)

        self.output_box = tk.Text(self, width=90, height=25)
        self.output_box.pack(fill="both", expand=True, padx=10, pady=10)

    def clear_output(self):
        self.output_box.delete("1.0", "end")

    def safe_error_output(self, message: str):
        self.output_box.insert("end", message)

    def logout(self):
        logger.info("User '%s' logged out.", self.business.user)
        self.business.close()
        self.parent.show_login()

    def show_count_a(self):
        self.clear_output()
        try:
            count = self.business.get_count_in450a()
            self.output_box.insert("end", f"IN450a row count: {count}")
        except psycopg.errors.InsufficientPrivilege:
            logger.warning("Access denied for user '%s' on IN450a.", self.business.user)
            self.safe_error_output("Access denied: this user cannot view IN450a.")
        except Exception:
            logger.exception("Unexpected error while reading IN450a for user '%s'.", self.business.user)
            self.safe_error_output("An unexpected error occurred while retrieving IN450a.")

    def show_names_b(self):
        self.clear_output()
        try:
            names = self.business.get_names_in450b()
            self.output_box.insert("end", "IN450b first and last names:\n\n")
            for name in names:
                self.output_box.insert("end", f"{name}\n")
        except psycopg.errors.InsufficientPrivilege:
            logger.warning("Access denied for user '%s' on IN450b.", self.business.user)
            self.safe_error_output("Access denied: this user cannot view IN450b.")
        except Exception:
            logger.exception("Unexpected error while reading IN450b for user '%s'.", self.business.user)
            self.safe_error_output("An unexpected error occurred while retrieving IN450b.")

    def show_count_c(self):
        self.clear_output()
        try:
            count = self.business.get_count_in450c()
            self.output_box.insert("end", f"IN450c row count: {count}")
        except psycopg.errors.InsufficientPrivilege:
            logger.warning("Access denied for user '%s' on IN450c.", self.business.user)
            self.safe_error_output("Access denied: this user cannot view IN450c.")
        except Exception:
            logger.exception("Unexpected error while reading IN450c for user '%s'.", self.business.user)
            self.safe_error_output("An unexpected error occurred while retrieving IN450c.")


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("IN450 Unit 9 - Secure Programming Features")
        self.geometry("900x650")
        self.current_frame = None
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.show_login()

    def show_login(self):
        if self.current_frame is not None:
            try:
                if hasattr(self.current_frame, "business"):
                    self.current_frame.business.close()
            except Exception:
                logger.exception("Error while closing business session during screen change.")
            self.current_frame.destroy()

        self.current_frame = LoginFrame(self, self.show_main)
        self.current_frame.pack(fill="both", expand=True, padx=20, pady=20)

    def show_main(self, business):
        if self.current_frame is not None:
            self.current_frame.destroy()

        self.current_frame = MainFrame(self, business)
        self.current_frame.pack(fill="both", expand=True, padx=20, pady=20)

    def on_close(self):
        try:
            if self.current_frame is not None and hasattr(self.current_frame, "business"):
                self.current_frame.business.close()
        except Exception:
            logger.exception("Error while closing application.")
        self.destroy()


if __name__ == "__main__":
    app = App()
    app.mainloop()
