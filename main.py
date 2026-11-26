"""Punto de entrada de la aplicacion.

Sistema de Control de Acceso para unidades residenciales, colegios
y universidades (visitantes y vehiculos).

Arquitectura MVC:
  - Modelo:      models/      (conexion MySQL y acceso a datos)
  - Vista:       views/       (interfaz grafica Tkinter)
  - Controlador: controllers/ (validaciones y logica de negocio)

Ejecutar:  python main.py
"""
import tkinter as tk
from tkinter import messagebox

from config import APP_TITLE
from models.database import Database
from controllers.auth_controller import AuthController
from controllers.persona_controller import PersonaController
from controllers.visitante_controller import VisitanteController
from controllers.vehiculo_controller import VehiculoController
from controllers.acceso_controller import AccesoController
from views.login_view import LoginView
from views.main_view import MainView


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("1080x640")
        self.minsize(1000, 600)

        # 1. Verificar conexion con la base de datos antes de iniciar
        ok, msg = Database.get_instance().test_connection()
        if not ok:
            messagebox.showerror(
                "Sin conexion a la base de datos",
                f"{msg}\n\nVerifica que MySQL este activo y los datos de "
                f"config.py sean correctos.")
            self.destroy()
            return

        # 2. Controladores (capa de logica)
        self.auth = AuthController()
        self.controllers = {
            "persona": PersonaController(),
            "visitante": VisitanteController(),
            "vehiculo": VehiculoController(),
            "acceso": AccesoController(),
        }

        # 3. Mostrar login
        self._mostrar_login()

    def _limpiar(self):
        for widget in self.winfo_children():
            widget.destroy()

    def _mostrar_login(self):
        self._limpiar()
        self.geometry("420x320")
        LoginView(self, self.auth, self._mostrar_principal).pack(
            fill="both", expand=True)

    def _mostrar_principal(self, usuario):
        self._limpiar()
        self.geometry("1080x640")
        MainView(self, usuario, self.controllers).pack(fill="both", expand=True)


if __name__ == "__main__":
    App().mainloop()
