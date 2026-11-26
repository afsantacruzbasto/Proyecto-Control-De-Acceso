"""Vista de reportes e historial de accesos con panel grafico analitico (HU-09)."""
import csv
import datetime as dt
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class ReportesView(ttk.Frame):
    def __init__(self, master, acceso_controller):
        super().__init__(master, padding=10)
        self.controller = acceso_controller
        self._build()
        self.generar()

    def _build(self):
        filtros = ttk.LabelFrame(self, text=" Filtros ", padding=8)
        filtros.pack(fill="x", pady=(0, 8))

        hoy = dt.date.today()
        hace_7 = hoy - dt.timedelta(days=7)
        self.var_desde = tk.StringVar(value=hace_7.isoformat())
        self.var_hasta = tk.StringVar(value=hoy.isoformat())

        ttk.Label(filtros, text="Desde (AAAA-MM-DD):").pack(side="left")
        ttk.Entry(filtros, textvariable=self.var_desde, width=12).pack(side="left", padx=6)
        ttk.Label(filtros, text="Hasta:").pack(side="left")
        ttk.Entry(filtros, textvariable=self.var_hasta, width=12).pack(side="left", padx=6)
        ttk.Button(filtros, text="Generar reporte", command=self.generar).pack(side="left", padx=10)
        ttk.Button(filtros, text="Exportar historial a CSV", command=self.exportar_csv).pack(side="left")

        cuerpo = ttk.Frame(self)
        cuerpo.pack(fill="both", expand=True)

        # Izquierda: Tablas resumen
        izquierda = ttk.Frame(cuerpo)
        izquierda.pack(side="left", fill="both", expand=True, padx=(0, 8))
        ttk.Label(izquierda, text="Accesos por dia", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        cols = ("fecha", "total", "visitantes", "autorizados", "con_vehiculo")
        self.tabla_dias = ttk.Treeview(izquierda, columns=cols, show="headings", height=7)
        for col, titulo, ancho in (
                ("fecha", "Fecha", 95), ("total", "Total", 55),
                ("visitantes", "Visitantes", 75), ("autorizados", "Autorizados", 85),
                ("con_vehiculo", "Con vehiculo", 90)):
            self.tabla_dias.heading(col, text=titulo)
            self.tabla_dias.column(col, width=ancho, anchor="center")
        self.tabla_dias.pack(fill="x", pady=4)

        ttk.Label(izquierda, text="Accesos por categoria", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(6, 0))
        self.tabla_categorias = ttk.Treeview(izquierda, columns=("cat", "total"), show="headings", height=5)
        self.tabla_categorias.heading("cat", text="Categoria")
        self.tabla_categorias.heading("total", text="Total")
        self.tabla_categorias.column("cat", width=160)
        self.tabla_categorias.column("total", width=70, anchor="center")
        self.tabla_categorias.pack(fill="x", pady=4)

        # Derecha: Panel Grafico Analitico (HU-09)
        derecha = ttk.LabelFrame(cuerpo, text=" Panel Grafico Analitico de Afluencia ", padding=6)
        derecha.pack(side="left", fill="both", expand=True)

        self.fig = Figure(figsize=(6.2, 4.3), dpi=95)
        self.ax_barras = self.fig.add_subplot(121)
        self.ax_torta = self.fig.add_subplot(122)
        self.canvas = FigureCanvasTkAgg(self.fig, master=derecha)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def generar(self):
        try:
            dt.date.fromisoformat(self.var_desde.get())
            dt.date.fromisoformat(self.var_hasta.get())
        except ValueError:
            messagebox.showwarning("Reportes", "Las fechas deben tener formato AAAA-MM-DD.", parent=self)
            return
        desde, hasta = self.var_desde.get(), self.var_hasta.get()

        for tabla in (self.tabla_dias, self.tabla_categorias):
            for item in tabla.get_children():
                tabla.delete(item)

        for f in self.controller.conteo_por_dia(desde, hasta):
            self.tabla_dias.insert("", "end", values=(
                f["fecha"], f["total"], f["visitantes"], f["autorizados"], f["con_vehiculo"]))

        cats_data = self.controller.conteo_por_tipo_persona(desde, hasta)
        for c in cats_data:
            self.tabla_categorias.insert("", "end", values=(c["categoria"], c["total"]))

        horas_data = self.controller.conteo_por_hora(desde, hasta)
        self._historial = self.controller.listar(desde, hasta)

        # Renderizar graficos
        self.ax_barras.clear()
        self.ax_torta.clear()

        if horas_data:
            horas = [f"{int(h['hora']):02d}:00" for h in horas_data]
            totales_h = [int(h["total"]) for h in horas_data]
            self.ax_barras.bar(horas, totales_h, color="#1f77b4")
            self.ax_barras.set_title("Afluencia por Franja Horaria", fontsize=9, fontweight="bold")
            self.ax_barras.set_ylabel("Ingresos", fontsize=8)
            self.ax_barras.tick_params(axis="x", rotation=45, labelsize=7)

        if cats_data:
            labels = [c["categoria"] for c in cats_data]
            sizes = [int(c["total"]) for c in cats_data]
            self.ax_torta.pie(sizes, labels=labels, autopct="%1.0f%%", textprops={"fontsize": 7})
            self.ax_torta.set_title("Distribucion por Tipo", fontsize=9, fontweight="bold")

        self.fig.tight_layout()
        self.canvas.draw()

    def exportar_csv(self):
        if not getattr(self, "_historial", None):
            messagebox.showinfo("Reportes", "Primero genera el reporte.", parent=self)
            return
        ruta = filedialog.asksaveasfilename(
            parent=self, defaultextension=".csv",
            filetypes=[("CSV", "*.csv")], initialfile="historial_accesos.csv")
        if not ruta:
            return
        with open(ruta, "w", newline="", encoding="utf-8-sig") as fh:
            writer = csv.writer(fh, delimiter=";")
            writer.writerow(["ID", "Nombre", "Tipo", "Placa", "Entrada", "Salida",
                             "Motivo", "Destino", "Registrado por"])
            for a in self._historial:
                writer.writerow([a["id"], a["nombre"],
                                 "Visitante" if a["tipo_acceso"] == "VISITANTE" else "Autorizada",
                                 a["placa"] or "", a["fecha_hora_entrada"],
                                 a["fecha_hora_salida"] or "", a["motivo"] or "",
                                 a["destino"] or "", a["registrado_por"]])
        messagebox.showinfo("Reportes", f"Historial exportado a:\n{ruta}", parent=self)