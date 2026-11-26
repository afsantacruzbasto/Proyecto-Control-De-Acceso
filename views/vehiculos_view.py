"""Vista CRUD de vehiculos (carros y motos, identificados por placa)."""
import tkinter as tk
from tkinter import ttk, messagebox

from controllers.vehiculo_controller import TIPOS_VEHICULO


class VehiculosView(ttk.Frame):
    def __init__(self, master, controller):
        super().__init__(master, padding=10)
        self.controller = controller
        self.seleccion_id = None
        self._propietarios = []          # [(id, texto)]
        self._build()
        self._cargar_propietarios()
        self.refrescar()

    def _build(self):
        form = ttk.LabelFrame(self, text=" Datos del vehiculo ", padding=10)
        form.pack(side="left", fill="y", padx=(0, 10))

        self.vars = {k: tk.StringVar() for k in ("placa", "marca", "color")}

        ttk.Label(form, text="Placa*").grid(row=0, column=0, sticky="w", pady=3)
        ttk.Entry(form, textvariable=self.vars["placa"], width=30
                  ).grid(row=0, column=1, pady=3, padx=(8, 0))

        ttk.Label(form, text="Tipo*").grid(row=1, column=0, sticky="w", pady=3)
        self.combo_tipo = ttk.Combobox(form, values=TIPOS_VEHICULO, state="readonly",
                                       width=27)
        self.combo_tipo.grid(row=1, column=1, pady=3, padx=(8, 0))
        self.combo_tipo.set("CARRO")

        ttk.Label(form, text="Marca").grid(row=2, column=0, sticky="w", pady=3)
        ttk.Entry(form, textvariable=self.vars["marca"], width=30
                  ).grid(row=2, column=1, pady=3, padx=(8, 0))

        ttk.Label(form, text="Color").grid(row=3, column=0, sticky="w", pady=3)
        ttk.Entry(form, textvariable=self.vars["color"], width=30
                  ).grid(row=3, column=1, pady=3, padx=(8, 0))

        ttk.Label(form, text="Propietario es*").grid(row=4, column=0, sticky="w", pady=3)
        self.combo_tipo_prop = ttk.Combobox(
            form, values=("PERSONA", "VISITANTE"), state="readonly", width=27)
        self.combo_tipo_prop.grid(row=4, column=1, pady=3, padx=(8, 0))
        self.combo_tipo_prop.set("PERSONA")
        self.combo_tipo_prop.bind("<<ComboboxSelected>>",
                                  lambda _e: self._cargar_propietarios())

        ttk.Label(form, text="Propietario*").grid(row=5, column=0, sticky="w", pady=3)
        self.combo_prop = ttk.Combobox(form, state="readonly", width=27)
        self.combo_prop.grid(row=5, column=1, pady=3, padx=(8, 0))

        botones = ttk.Frame(form)
        botones.grid(row=6, column=0, columnspan=2, pady=(12, 0))
        ttk.Button(botones, text="Nuevo", command=self.limpiar).pack(side="left", padx=2)
        ttk.Button(botones, text="Guardar", command=self.guardar).pack(side="left", padx=2)
        ttk.Button(botones, text="Eliminar", command=self.eliminar).pack(side="left", padx=2)

        derecha = ttk.Frame(self)
        derecha.pack(side="left", fill="both", expand=True)

        buscador = ttk.Frame(derecha)
        buscador.pack(fill="x", pady=(0, 6))
        ttk.Label(buscador, text="Buscar por placa/marca:").pack(side="left")
        self.var_buscar = tk.StringVar()
        entry = ttk.Entry(buscador, textvariable=self.var_buscar, width=26)
        entry.pack(side="left", padx=6)
        entry.bind("<KeyRelease>", lambda _e: self.refrescar())

        columnas = ("id", "placa", "tipo", "marca", "color", "propietario")
        self.tabla = ttk.Treeview(derecha, columns=columnas, show="headings", height=18)
        titulos = {"id": "ID", "placa": "Placa", "tipo": "Tipo", "marca": "Marca",
                   "color": "Color", "propietario": "Propietario"}
        anchos = {"id": 40, "placa": 90, "tipo": 70, "marca": 110, "color": 90,
                  "propietario": 220}
        for col in columnas:
            self.tabla.heading(col, text=titulos[col])
            self.tabla.column(col, width=anchos[col], anchor="w")
        scroll = ttk.Scrollbar(derecha, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=scroll.set)
        self.tabla.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        self.tabla.bind("<<TreeviewSelect>>", self._al_seleccionar)

    def _cargar_propietarios(self):
        self._propietarios = self.controller.listar_propietarios(
            self.combo_tipo_prop.get())
        self.combo_prop["values"] = [texto for _id, texto in self._propietarios]
        self.combo_prop.set("")

    def refrescar(self):
        for item in self.tabla.get_children():
            self.tabla.delete(item)
        self._filas = {}
        for v in self.controller.listar(self.var_buscar.get().strip()):
            iid = self.tabla.insert("", "end", values=(
                v["id"], v["placa"], v["tipo"], v["marca"] or "", v["color"] or "",
                v["propietario"] or "(sin propietario)"))
            self._filas[iid] = v

    def _al_seleccionar(self, _event=None):
        sel = self.tabla.selection()
        if not sel:
            return
        v = self._filas.get(sel[0])
        if not v:
            return
        self.seleccion_id = v["id"]
        self.vars["placa"].set(v["placa"])
        self.combo_tipo.set(v["tipo"])
        self.vars["marca"].set(v["marca"] or "")
        self.vars["color"].set(v["color"] or "")
        self.combo_tipo_prop.set(v["propietario_tipo"])
        self._cargar_propietarios()
        for pid, texto in self._propietarios:
            if pid == v["propietario_id"]:
                self.combo_prop.set(texto)
                break

    def limpiar(self):
        self.seleccion_id = None
        for var in self.vars.values():
            var.set("")
        self.combo_tipo.set("CARRO")
        self._cargar_propietarios()
        self.tabla.selection_remove(self.tabla.selection())

    def guardar(self):
        idx = self.combo_prop.current()
        datos = {
            "placa": self.vars["placa"].get(),
            "tipo": self.combo_tipo.get(),
            "marca": self.vars["marca"].get(),
            "color": self.vars["color"].get(),
            "propietario_tipo": self.combo_tipo_prop.get(),
            "propietario_id": self._propietarios[idx][0] if idx >= 0 else None,
        }
        ok, msg = self.controller.guardar(datos, self.seleccion_id)
        if ok:
            messagebox.showinfo("Vehiculos", msg, parent=self)
            self.limpiar()
            self.refrescar()
        else:
            messagebox.showwarning("Vehiculos", msg, parent=self)

    def eliminar(self):
        if self.seleccion_id is None:
            messagebox.showinfo("Vehiculos", "Selecciona un registro de la tabla.",
                                parent=self)
            return
        if not messagebox.askyesno("Vehiculos", "Eliminar el vehiculo seleccionado?",
                                   parent=self):
            return
        ok, msg = self.controller.eliminar(self.seleccion_id)
        (messagebox.showinfo if ok else messagebox.showwarning)("Vehiculos", msg,
                                                                parent=self)
        if ok:
            self.limpiar()
            self.refrescar()
