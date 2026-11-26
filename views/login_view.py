"""Vista de inicio de sesion."""
import tkinter as tk
from tkinter import ttk, messagebox

from config import APP_TITLE


class LoginView(tk.Frame):
    def __init__(self, master, auth_controller, on_login_ok):
        super().__init__(master, padx=30, pady=30)
        self.auth = auth_controller
        self.on_login_ok = on_login_ok
        self._build()

    def _build(self):
        ttk.Label(self, text=APP_TITLE,
                  font=("Segoe UI", 16, "bold")).pack(pady=(0, 4))
        ttk.Label(self, text="Unidades residenciales, colegios y universidades",
                  foreground="#555").pack(pady=(0, 18))

        form = ttk.Frame(self)
        form.pack()

        ttk.Label(form, text="Usuario:").grid(row=0, column=0, sticky="e", pady=5)
        self.entry_user = ttk.Entry(form, width=28)
        self.entry_user.grid(row=0, column=1, pady=5, padx=(8, 0))

        ttk.Label(form, text="Contrasena:").grid(row=1, column=0, sticky="e", pady=5)
        self.entry_pass = ttk.Entry(form, width=28, show="*")
        self.entry_pass.grid(row=1, column=1, pady=5, padx=(8, 0))

        ttk.Button(self, text="Ingresar", command=self._login,
                   width=20).pack(pady=(18, 6))

        ttk.Label(self, text="Usuario inicial: admin / admin123",
                  foreground="#888", font=("Segoe UI", 8)).pack()

        self.entry_user.focus_set()
        self.master.bind("<Return>", lambda _e: self._login())

    def _login(self):
        ok, result = self.auth.login(self.entry_user.get(), self.entry_pass.get())
        if ok:
            self.master.unbind("<Return>")
            self.on_login_ok(result)
        else:
            messagebox.showerror("Acceso denegado", result, parent=self.master)
            self.entry_pass.delete(0, tk.END)
