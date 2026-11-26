"""Ventana principal: menu de modulos en pestanas y barra de estado."""
import tkinter as tk
from tkinter import ttk

from config import APP_TITLE, APP_VERSION
from models.database import Database
from views.personas_view import PersonasView
from views.visitantes_view import VisitantesView
from views.vehiculos_view import VehiculosView
from views.accesos_view import AccesosView
from views.reportes_view import ReportesView
from views.auditoria_view import AuditoriaView


class MainView(tk.Frame):
    def __init__(self, master, usuario, controllers):
        super().__init__(master)
        self.usuario = usuario
        self.controllers = controllers
        self._build()

    def _build(self):
        # Encabezado
        header = ttk.Frame(self, padding=(12, 8))
        header.pack(fill="x")
        ttk.Label(header, text=APP_TITLE,
                  font=("Segoe UI", 14, "bold")).pack(side="left")
        ttk.Label(header,
                  text=f"  Usuario: {self.usuario['nombre']} ({self.usuario['rol']})",
                  foreground="#555").pack(side="left", padx=12)

        # Pestañas = modulos del sistema
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=10, pady=(0, 6))

        self.tab_accesos = AccesosView(notebook, self.controllers["acceso"],
                                       self.controllers["persona"],
                                       self.controllers["visitante"],
                                       self.usuario)
        self.tab_personas = PersonasView(notebook, self.controllers["persona"])
        self.tab_visitantes = VisitantesView(notebook, self.controllers["visitante"])
        self.tab_vehiculos = VehiculosView(notebook, self.controllers["vehiculo"])
        self.tab_reportes = ReportesView(notebook, self.controllers["acceso"])
        self.tab_auditoria = AuditoriaView(notebook)

        notebook.add(self.tab_accesos, text=" Control de Accesos ")
        notebook.add(self.tab_personas, text=" Personas Autorizadas ")
        notebook.add(self.tab_visitantes, text=" Visitantes ")
        notebook.add(self.tab_vehiculos, text=" Vehiculos ")
        notebook.add(self.tab_reportes, text=" Reportes ")
        notebook.add(self.tab_auditoria, text=" Auditoria ")

        # Barra de estado: evidencia la conexion con la base de datos
        ok, msg = Database.get_instance().test_connection()
        color = "#0a7d2c" if ok else "#b00020"
        barra = ttk.Frame(self, padding=(12, 4))
        barra.pack(fill="x", side="bottom")
        ttk.Label(barra, text=f"v{APP_VERSION}", foreground="#888").pack(side="right")
        ttk.Label(barra, text="\u25CF " + msg,
                  foreground=color).pack(side="left")