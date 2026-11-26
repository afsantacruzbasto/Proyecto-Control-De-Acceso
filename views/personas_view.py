"""Vista CRUD de personas autorizadas con carga masiva CSV (HU-07)."""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from controllers.persona_controller import TIPOS_PERSONA


class PersonasView(ttk.Frame):
    def __init__(self, master, controller):
        super().__init__(master, padding=10)
        self.controller = controller
        self.seleccion_id = None
        self._build()
        self.refrescar()

    def _build(self):
        # ---- Formulario (izquierda) ----
        form = ttk.LabelFrame(self, text=" Datos de la persona ", padding=10)
        form.pack(side="left", fill="y", padx=(0, 10))

        self.vars = {k: tk.StringVar() for k in
                     ("documento", "nombres", "apellidos", "dependencia", "telefono")}
        campos = [("Documento*", "documento"), ("Nombres*", "nombres"),
                  ("Apellidos*", "apellidos"),
                  ("Dependencia* (Torre/Apto, programa)", "dependencia"),
                  ("Telefono", "telefono")]
        for i, (label, key) in enumerate(campos):
            ttk.Label(form, text=label).grid(row=i, column=0, sticky="w", pady=3)
            ttk.Entry(form, textvariable=self.vars[key], width=30
                      ).grid(row=i, column=1, pady=3, padx=(8, 0))

        ttk.Label(form, text="Tipo*").grid(row=5, column=0, sticky="w", pady=3)
        self.combo_tipo = ttk.Combobox(form, values=TIPOS_PERSONA, state="readonly",
                                       width=27)
        self.combo_tipo.grid(row=5, column=1, pady=3, padx=(8, 0))
        self.combo_tipo.set("RESIDENTE")

        self.var_activo = tk.IntVar(value=1)
        ttk.Checkbutton(form, text="Activo (puede ingresar)",
                        variable=self.var_activo).grid(row=6, column=1,
                                                       sticky="w", pady=3)

        botones = ttk.Frame(form)
        botones.grid(row=7, column=0, columnspan=2, pady=(12, 0))
        ttk.Button(botones, text="Nuevo", command=self.limpiar).pack(side="left", padx=2)
        ttk.Button(botones, text="Guardar", command=self.guardar).pack(side="left", padx=2)
        ttk.Button(botones, text="Eliminar", command=self.eliminar).pack(side="left", padx=2)

        ttk.Button(form, text="Importar CSV (Carga Masiva)",
                   command=self.cargar_csv).grid(row=8, column=0, columnspan=2,
                                                 pady=(8, 0), sticky="ew")

        # ---- Tabla (derecha) ----
        derecha = ttk.Frame(self)
        derecha.pack(side="left", fill="both", expand=True)

        buscador = ttk.Frame(derecha)
        buscador.pack(fill="x", pady=(0, 6))
        ttk.Label(buscador, text="Buscar:").pack(side="left")
        self.var_buscar = tk.StringVar()
        entry = ttk.Entry(buscador, textvariable=self.var_buscar, width=30)
        entry.pack(side="left", padx=6)
        entry.bind("<KeyRelease>", lambda _e: self.refrescar())

        columnas = ("id", "documento", "nombres", "apellidos", "tipo",
                    "dependencia", "telefono", "activo")
        self.tabla = ttk.Treeview(derecha, columns=columnas, show="headings", height=18)
        titulos = {"id": "ID", "documento": "Documento", "nombres": "Nombres",
                   "apellidos": "Apellidos", "tipo": "Tipo",
                   "dependencia": "Dependencia", "telefono": "Telefono",
                   "activo": "Activo"}
        anchos = {"id": 40, "documento": 90, "nombres": 110, "apellidos": 110,
                  "tipo": 120, "dependencia": 170, "telefono": 100, "activo": 55}
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
        for p in self.controller.listar(self.var_buscar.get().strip()):
            self.tabla.insert("", "end", values=(
                p["id"], p["documento"], p["nombres"], p["apellidos"], p["tipo"],
                p["dependencia"], p["telefono"] or "", "Si" if p["activo"] else "No"))

    def _al_seleccionar(self, _event=None):
        sel = self.tabla.selection()
        if not sel:
            return
        v = self.tabla.item(sel[0], "values")
        self.seleccion_id = int(v[0])
        self.vars["documento"].set(v[1])
        self.vars["nombres"].set(v[2])
        self.vars["apellidos"].set(v[3])
        self.combo_tipo.set(v[4])
        self.vars["dependencia"].set(v[5])
        self.vars["telefono"].set(v[6])
        self.var_activo.set(1 if v[7] == "Si" else 0)

    def limpiar(self):
        self.seleccion_id = None
        for var in self.vars.values():
            var.set("")
        self.combo_tipo.set("RESIDENTE")
        self.var_activo.set(1)
        self.tabla.selection_remove(self.tabla.selection())

    def guardar(self):
        datos = {k: v.get() for k, v in self.vars.items()}
        datos["tipo"] = self.combo_tipo.get()
        datos["activo"] = self.var_activo.get()
        ok, msg = self.controller.guardar(datos, self.seleccion_id)
        if ok:
            messagebox.showinfo("Personas", msg, parent=self)
            self.limpiar()
            self.refrescar()
        else:
            messagebox.showwarning("Personas", msg, parent=self)

    def cargar_csv(self):
        ruta = filedialog.askopenfilename(
            parent=self,
            title="Seleccionar archivo CSV de personas",
            filetypes=[("Archivos CSV", "*.csv")])
        if not ruta:
            return
        ok, msg = self.controller.importar_csv(ruta)
        messagebox.showinfo("Carga Masiva CSV (HU-07)", msg, parent=self)
        self.refrescar()

    def eliminar(self):
        if self.seleccion_id is None:
            messagebox.showinfo("Personas", "Selecciona un registro de la tabla.",
                                parent=self)
            return
        if not messagebox.askyesno("Personas", "Eliminar el registro seleccionado?",
                                   parent=self):
            return
        ok, msg = self.controller.eliminar(self.seleccion_id)
        (messagebox.showinfo if ok else messagebox.showwarning)("Personas", msg,
                                                                parent=self)
        if ok:
            self.limpiar()
            self.refrescar()