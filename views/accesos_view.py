"""Vista del modulo de control de accesos: entradas, salidas y cupos de parqueadero."""
import tkinter as tk
from tkinter import ttk, messagebox


class AccesosView(ttk.Frame):
    def __init__(self, master, acceso_controller, persona_controller,
                 visitante_controller, usuario):
        super().__init__(master, padding=10)
        self.controller = acceso_controller
        self.personas = persona_controller
        self.visitantes = visitante_controller
        self.usuario = usuario
        self._opciones = []
        self._vehiculos = []
        self._cupos_actuales = {}
        self._build()
        self._cargar_quien_ingresa()
        self.refrescar()

    def _build(self):
        # ---------- Panel de registro de entrada ----------
        entrada = ttk.LabelFrame(self, text=" Registrar ENTRADA ", padding=10)
        entrada.pack(side="left", fill="y", padx=(0, 10))

        # Indicador de cupos (HU-08)
        panel_cupos = ttk.LabelFrame(entrada, text=" Aforo Parqueadero en Tiempo Real ", padding=6)
        panel_cupos.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 8))
        self.lbl_cupos = tk.Label(panel_cupos, text="Cargando cupos...",
                                  font=("Segoe UI", 9, "bold"), fg="#0a7d2c")
        self.lbl_cupos.pack(anchor="w")
        self.lbl_alerta_cupo = tk.Label(panel_cupos, text="",
                                        font=("Segoe UI", 8, "bold"), fg="#b00020")
        self.lbl_alerta_cupo.pack(anchor="w")

        ttk.Label(entrada, text="Quien ingresa*").grid(row=1, column=0, sticky="w", pady=3)
        self.combo_tipo = ttk.Combobox(
            entrada, state="readonly", width=28,
            values=("Persona autorizada", "Visitante"))
        self.combo_tipo.grid(row=1, column=1, pady=3, padx=(8, 0))
        self.combo_tipo.set("Persona autorizada")
        self.combo_tipo.bind("<<ComboboxSelected>>",
                             lambda _e: self._cargar_quien_ingresa())

        ttk.Label(entrada, text="Nombre*").grid(row=2, column=0, sticky="w", pady=3)
        self.combo_persona = ttk.Combobox(entrada, state="readonly", width=28)
        self.combo_persona.grid(row=2, column=1, pady=3, padx=(8, 0))
        self.combo_persona.bind("<<ComboboxSelected>>",
                                lambda _e: self._cargar_vehiculos())

        ttk.Label(entrada, text="Vehiculo (opcional)").grid(row=3, column=0,
                                                            sticky="w", pady=3)
        self.combo_vehiculo = ttk.Combobox(entrada, state="readonly", width=28)
        self.combo_vehiculo.grid(row=3, column=1, pady=3, padx=(8, 0))
        self.combo_vehiculo.bind("<<ComboboxSelected>>",
                                 lambda _e: self._verificar_bloqueo_cupo())

        self.var_motivo = tk.StringVar()
        self.var_destino = tk.StringVar()
        self.var_obs = tk.StringVar()
        ttk.Label(entrada, text="Motivo").grid(row=4, column=0, sticky="w", pady=3)
        ttk.Entry(entrada, textvariable=self.var_motivo, width=30
                  ).grid(row=4, column=1, pady=3, padx=(8, 0))
        ttk.Label(entrada, text="Destino (Torre/Apto, area)").grid(row=5, column=0,
                                                                   sticky="w", pady=3)
        ttk.Entry(entrada, textvariable=self.var_destino, width=30
                  ).grid(row=5, column=1, pady=3, padx=(8, 0))
        ttk.Label(entrada, text="Observaciones").grid(row=6, column=0, sticky="w", pady=3)
        ttk.Entry(entrada, textvariable=self.var_obs, width=30
                  ).grid(row=6, column=1, pady=3, padx=(8, 0))

        self.btn_registrar = ttk.Button(entrada, text="Registrar entrada",
                                        command=self.registrar_entrada)
        self.btn_registrar.grid(row=7, column=0, columnspan=2, pady=(14, 0))

        # ---------- Bitacora ----------
        derecha = ttk.Frame(self)
        derecha.pack(side="left", fill="both", expand=True)

        acciones = ttk.Frame(derecha)
        acciones.pack(fill="x", pady=(0, 6))
        self.var_abiertos = tk.IntVar(value=0)
        ttk.Checkbutton(acciones, text="Mostrar solo quienes estan dentro",
                        variable=self.var_abiertos,
                        command=self.refrescar).pack(side="left")
        ttk.Button(acciones, text="Actualizar",
                   command=self.refrescar).pack(side="left", padx=8)
        ttk.Button(acciones, text="Registrar SALIDA",
                   command=self.registrar_salida).pack(side="left", padx=4)
        ttk.Button(acciones, text="Eliminar registro",
                   command=self.eliminar_registro).pack(side="left", padx=4)

        columnas = ("id", "nombre", "tipo", "placa", "destino", "entrada", "salida")
        self.tabla = ttk.Treeview(derecha, columns=columnas, show="headings", height=18)
        titulos = {"id": "#", "nombre": "Nombre", "tipo": "Tipo", "placa": "Vehiculo",
                   "destino": "Destino", "entrada": "Entrada", "salida": "Salida"}
        anchos = {"id": 45, "nombre": 180, "tipo": 140, "placa": 90,
                  "destino": 130, "entrada": 150, "salida": 150}
        for col in columnas:
            self.tabla.heading(col, text=titulos[col])
            self.tabla.column(col, width=anchos[col], anchor="w")
        scroll = ttk.Scrollbar(derecha, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=scroll.set)
        self.tabla.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

    def _actualizar_panel_cupos(self):
        self._cupos_actuales = self.controller.obtener_cupos_parqueadero()
        c = self._cupos_actuales["CARRO"]
        m = self._cupos_actuales["MOTO"]
        self.lbl_cupos.config(
            text=f"Carros: {c['disp']} disp. ({c['ocupados']}/{c['max']})  |  "
                 f"Motos: {m['disp']} disp. ({m['ocupados']}/{m['max']})",
            fg="#b00020" if c["disp"] == 0 or m["disp"] == 0 else "#0a7d2c"
        )
        self._verificar_bloqueo_cupo()

    def _verificar_bloqueo_cupo(self):
        vidx = self.combo_vehiculo.current()
        if vidx > 0 and self._vehiculos:
            tipo_v = self._vehiculos[vidx - 1]["tipo"]
            disp = self._cupos_actuales.get(tipo_v, {"disp": 1})["disp"]
            if disp <= 0:
                self.lbl_alerta_cupo.config(
                    text=f"ALERTA: Cupos agotados para {tipo_v}. Ingreso bloqueado.")
                self.btn_registrar.config(state="disabled")
                return
        self.lbl_alerta_cupo.config(text="")
        self.btn_registrar.config(state="normal")

    def _tipo_acceso(self):
        return "VISITANTE" if self.combo_tipo.get() == "Visitante" else "PERSONA_AUTORIZADA"

    def _cargar_quien_ingresa(self):
        if self._tipo_acceso() == "PERSONA_AUTORIZADA":
            self._opciones = [(p["id"], f"{p['nombres']} {p['apellidos']} - {p['tipo']}")
                              for p in self.personas.listar_activas()]
        else:
            self._opciones = [(v["id"], f"{v['nombres']} {v['apellidos']} - Doc {v['documento']}")
                              for v in self.visitantes.listar()]
        self.combo_persona["values"] = [t for _i, t in self._opciones]
        self.combo_persona.set("")
        self._cargar_vehiculos()

    def _cargar_vehiculos(self):
        idx = self.combo_persona.current()
        self._vehiculos = []
        if idx >= 0:
            self._vehiculos = self.controller.listar_vehiculos_de(
                self._tipo_acceso(), self._opciones[idx][0])
        valores = ["(a pie / sin vehiculo)"] + [
            f"{v['placa']} - {v['tipo']} {v['marca'] or ''}".strip()
            for v in self._vehiculos]
        self.combo_vehiculo["values"] = valores
        self.combo_vehiculo.set(valores[0])
        self._verificar_bloqueo_cupo()

    def registrar_entrada(self):
        idx = self.combo_persona.current()
        if idx < 0:
            messagebox.showinfo("Accesos", "Selecciona quien ingresa.", parent=self)
            return
        vidx = self.combo_vehiculo.current()
        vehiculo_id = self._vehiculos[vidx - 1]["id"] if vidx > 0 else None
        ok, msg = self.controller.registrar_entrada(
            tipo_acceso=self._tipo_acceso(),
            propietario_id=self._opciones[idx][0],
            vehiculo_id=vehiculo_id,
            motivo=self.var_motivo.get(),
            destino=self.var_destino.get(),
            usuario_id=self.usuario["id"],
            observaciones=self.var_obs.get(),
            operador=self.usuario["username"])
        (messagebox.showinfo if ok else messagebox.showwarning)("Accesos", msg, parent=self)
        if ok:
            self.var_motivo.set("")
            self.var_destino.set("")
            self.var_obs.set("")
            self.refrescar()

    def _acceso_seleccionado(self):
        sel = self.tabla.selection()
        if not sel:
            messagebox.showinfo("Accesos", "Selecciona un registro de la bitacora.", parent=self)
            return None
        return self.tabla.item(sel[0], "values")

    def registrar_salida(self):
        valores = self._acceso_seleccionado()
        if not valores:
            return
        if valores[6] != "--- DENTRO ---":
            messagebox.showinfo("Accesos", "Ese acceso ya tiene salida registrada.", parent=self)
            return
        ok, msg = self.controller.registrar_salida(int(valores[0]), operador=self.usuario["username"])
        (messagebox.showinfo if ok else messagebox.showwarning)("Accesos", msg, parent=self)
        self.refrescar()

    def eliminar_registro(self):
        valores = self._acceso_seleccionado()
        if not valores:
            return
        if not messagebox.askyesno("Accesos", f"Eliminar el acceso #{valores[0]}?", parent=self):
            return
        ok, msg = self.controller.eliminar(int(valores[0]), operador=self.usuario["username"])
        (messagebox.showinfo if ok else messagebox.showwarning)("Accesos", msg, parent=self)
        self.refrescar()

    def refrescar(self):
        for item in self.tabla.get_children():
            self.tabla.delete(item)
        for a in self.controller.listar(solo_abiertos=bool(self.var_abiertos.get())):
            tipo = "Visitante" if a["tipo_acceso"] == "VISITANTE" else "Autorizada"
            vehiculo = f"{a['placa']} ({a['tipo_vehiculo']})" if a["placa"] else "A pie"
            self.tabla.insert("", "end", values=(
                a["id"], a["nombre"], tipo, vehiculo, a["destino"] or "",
                a["fecha_hora_entrada"], a["fecha_hora_salida"] or "--- DENTRO ---"))
        self._actualizar_panel_cupos()