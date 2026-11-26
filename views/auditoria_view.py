"""Vista del modulo de auditoria de operaciones (Audit Log - HU-10)."""
import tkinter as tk
from tkinter import ttk
from models.audit_model import AuditModel


class AuditoriaView(ttk.Frame):
    def __init__(self, master):
        super().__init__(master, padding=10)
        self.model = AuditModel()
        self._build()
        self.refrescar()

    def _build(self):
        barra = ttk.Frame(self)
        barra.pack(fill="x", pady=(0, 8))
        ttk.Label(barra, text="Registro Inmutable de Auditoria (Audit Log)",
                  font=("Segoe UI", 10, "bold")).pack(side="left")
        ttk.Button(barra, text="Actualizar historial",
                   command=self.refrescar).pack(side="right")

        columnas = ("id", "fecha_hora", "usuario", "accion", "entidad", "detalle")
        self.tabla = ttk.Treeview(self, columns=columnas, show="headings", height=18)
        titulos = {"id": "ID", "fecha_hora": "Fecha y Hora", "usuario": "Operador",
                   "accion": "Accion", "entidad": "Modulo / Tabla", "detalle": "Detalle de la Operacion"}
        anchos = {"id": 45, "fecha_hora": 150, "usuario": 120,
                  "accion": 100, "entidad": 130, "detalle": 420}
        for col in columnas:
            self.tabla.heading(col, text=titulos[col])
            self.tabla.column(col, width=anchos[col], anchor="w")

        scroll = ttk.Scrollbar(self, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=scroll.set)
        self.tabla.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

    def refrescar(self):
        for item in self.tabla.get_children():
            self.tabla.delete(item)
        for row in self.model.listar():
            self.tabla.insert("", "end", values=(
                row["id"], row["fecha_hora"], row["usuario_operador"],
                row["accion"], row["entidad_afectada"], row["detalle"]))