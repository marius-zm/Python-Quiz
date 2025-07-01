import tkinter as tk
from tkinter import ttk, messagebox
from lib.functions import center_window
from style import init_style
import json, os


class Login(tk.Tk):
    def __init__(self):
        super().__init__()
        self.width = 400
        self.height = 200

        self.title("Login")
        self.resizable(False, False)

        init_style()

        # GUI
        self.grid_rowconfigure([0, 1, 2], weight=1)
        self.grid_columnconfigure([0, 1], weight=1)

        ttk.Label(self, text="Username:").grid(
            row=0, column=0, sticky="e", padx=5, pady=5
        )
        ttk.Label(self, text="Password:").grid(
            row=1, column=0, sticky="e", padx=5, pady=5
        )

        self.input_username = ttk.Entry(self)
        self.input_username.grid(row=0, column=1, padx=5, pady=5)
        self.input_password = ttk.Entry(self, show="*")
        self.input_password.grid(row=1, column=1, padx=5, pady=5)

        ttk.Button(
            self,
            text="Login",
            command=lambda: self.login_user(
                self.input_username.get(), self.input_password.get()
            ),
        ).grid(row=2, column=1, pady=10)

        self.bind(
            "<Return>",
            lambda e: self.login_user(
                self.input_username.get(), self.input_password.get()
            ),
        )
        self.input_username.focus()

        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Statusvariablen für die Authentifizierung
        self.authenticated = False
        self.current_user = {"name": None, "id": None}

        # Dateipfad für Benutzerdaten
        self.user_data_file = "users.json"
        self._check_create_user_data_file()

    def _check_create_user_data_file(self):
        """Überprüft, ob die users.json existiert, und erstellt sie ggf. mit Beispieldaten."""
        if not os.path.exists(self.user_data_file):
            default_users = [
                {"id": 1, "username": "admin", "password": "password123"},
                {"id": 2, "username": "user", "password": "pass"},
            ]
            try:
                with open(self.user_data_file, "w", encoding="utf-8") as f:
                    json.dump(default_users, f, indent=4)
                messagebox.showinfo(
                    "Info",
                    f"'{self.user_data_file}' wurde mit Standardbenutzern erstellt.",
                )
            except IOError as e:
                messagebox.showerror(
                    "Fehler", f"Konnte '{self.user_data_file}' nicht erstellen: {e}"
                )
                self.quit()

    def get_users_from_file(self):
        """Lädt Benutzerdaten aus der JSON-Datei."""
        try:
            with open(self.user_data_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            messagebox.showerror(
                "Fehler", f"Die Datei '{self.user_data_file}' wurde nicht gefunden."
            )
            return []
        except json.JSONDecodeError:
            messagebox.showerror(
                "Fehler",
                f"Die Datei '{self.user_data_file}' ist keine gültige JSON-Datei.",
            )
            return []

    def on_closing(self):
        """Fragt vor dem Beenden der Anwendung nach Bestätigung."""
        if messagebox.askokcancel(
            "Beenden", "Möchten Sie die Anwendung wirklich beenden?"
        ):
            self.quit()

    def login_user(self, username, password):
        """Versucht den Benutzer anhand der JSON-Datei zu authentifizieren."""
        users = self.get_users_from_file()
        found_user = None

        for user_data in users:
            if user_data.get("username") == username:
                found_user = user_data
                break

        if found_user and found_user.get("password") == password:
            self.current_user["name"] = found_user["username"]
            self.current_user["id"] = found_user["id"]
            self.authenticated = True
            messagebox.showinfo("Login erfolgreich", f"Willkommen, {username}!")
            self.destroy()
        else:
            messagebox.showerror(
                "Login fehlgeschlagen", "Falscher Benutzername oder Passwort."
            )

    def run(self):
        """Zentriert das Fenster und startet die Tkinter-Hauptschleife."""
        center_window(self, self.width, self.height)
        self.mainloop()
