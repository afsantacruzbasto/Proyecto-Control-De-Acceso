"""Vista CRUD de visitantes."""
import tkinter as tk
from tkinter import ttk, messagebox


class VisitantesView(ttk.Frame):
    def __init__(self, master, controller):
        super().__init__(master, padding=10)
        self.controller = controller
        self.seleccion_id = None
        self._build()
        self.refrescar()

    def _build(self):
        form = ttk.LabelFrame(self, text=" Datos del visitante ", padding=10)
        form.pack(side="left", fill="y", padx=(0, 10))

        self.vars = {k: tk.StringVar() for k in
                     ("documento", "nombres", "apellidos", "telefono", "empresa")}
        campos = [("Documento*", "documento"), ("Nombres*", "nombres"),
                  ("Apellidos*", "apellidos"), ("Telefono", "telefono"),
                  ("Empresa / procedencia", "empresa")]
        for i, (label, key) in enumerate(campos):
            ttk.Label(form, text=label).grid(row=i, column=0, sticky="w", pady=3)
            ttk.Entry(form, textvariable=self.vars[key], width=30
                      ).grid(row=i, column=1, pady=3, padx=(8, 0))

        botones = ttk.Frame(form)
        botones.grid(row=5, column=0, columnspan=2, pady=(12, 0))
        ttk.Button(botones, text="Nuevo", command=self.limpiar).pack(side="left", padx=2)
        ttk.Button(botones, text="Guardar", command=self.guardar).pack(side="left", padx=2)
        ttk.Button(botones, text="Eliminar", command=self.eliminar).pack(side="left", padx=2)

        derecha = ttk.Frame(self)
        derecha.pack(side="left", fill="both", expand=True)

        buscador = ttk.Frame(derecha)
        buscador.pack(fill="x", pady=(0, 6))
        ttk.Label(buscador, text="Buscar:").pack(side="left")
        self.var_buscar = tk.StringVar()
        entry = ttk.Entry(buscador, textvariable=self.var_buscar, width=30)
        entry.pack(side="left", padx=6)
        entry.bind("<KeyRelease>", lambda _e: self.refrescar())

        columnas = ("id", "documento", "nombres", "apellidos", "telefono", "empresa")
        self.tabla = ttk.Treeview(derecha, columns=columnas, show="headings", height=18)
        titulos = {"id": "ID", "documento": "Documento", "nombres": "Nombres",
                   "apellidos": "Apellidos", "telefono": "Telefono",
                   "empresa": "Empresa"}
        anchos = {"id": 40, "documento": 100, "nombres": 130, "apellidos": 130,
                  "telefono": 110, "empresa": 170}
        for col in columnas:
            self.tabla.heading(col, text=titulos[col])
            self.tabla.column(col, width=anchos[col], anchor="w")
        scroll = ttk.Scrollbar(derecha, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=scroll.set)
        self.tabla.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        self.tabla.bind("<<TreeviewSelect>>", self._al_seleccionar)

    def refrescar(self):
        for item in self.tabla.get_children():
            self.tabla.delete(item)
        for v in self.controller.listar(self.var_buscar.get().strip()):
            self.tabla.insert("", "end", values=(
                v["id"], v["documento"], v["nombres"], v["apellidos"],
                v["telefono"] or "", v["empresa"] or ""))

    def _al_seleccionar(self, _event=None):
        sel = self.tabla.selection()
        if not sel:
            return
        v = self.tabla.item(sel[0], "values")
        self.seleccion_id = int(v[0])
        self.vars["documento"].set(v[1])
        self.vars["nombres"].set(v[2])
        self.vars["apellidos"].set(v[3])
        self.vars["telefono"].set(v[4])
        self.vars["empresa"].set(v[5])

    def limpiar(self):
        self.seleccion_id = None
        for var in self.vars.values():
            var.set("")
        self.tabla.selection_remove(self.tabla.selection())

    def guardar(self):
        datos = {k: v.get() for k, v in self.vars.items()}
        ok, msg = self.controller.guardar(datos, self.seleccion_id)
        if ok:
            messagebox.showinfo("Visitantes", msg, parent=self)
            self.limpiar()
            self.refrescar()
        else:
            messagebox.showwarning("Visitantes", msg, parent=self)

    def eliminar(self):
        if self.seleccion_id is None:
            messagebox.showinfo("Visitantes", "Selecciona un registro de la tabla.",
                                parent=self)
            return
        if not messagebox.askyesno("Visitantes", "Eliminar el registro seleccionado?",
                                   parent=self):
            return
        ok, msg = self.controller.eliminar(self.seleccion_id)
        (messagebox.showinfo if ok else messagebox.showwarning)("Visitantes", msg,
                                                                parent=self)
        if ok:
            self.limpiar()
            self.refrescar()
