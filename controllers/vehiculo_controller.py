"""Controlador de vehiculos (carros y motos)."""
from models.vehiculo_model import VehiculoModel
from models.persona_model import PersonaModel
from models.visitante_model import VisitanteModel

TIPOS_VEHICULO = ("CARRO", "MOTO")


class VehiculoController:
    def __init__(self):
        self.model = VehiculoModel()
        self.personas = PersonaModel()
        self.visitantes = VisitanteModel()

    def listar(self, filtro=""):
        return self.model.listar(filtro)

    def listar_propietarios(self, propietario_tipo):
        """Lista opciones de propietario para el formulario."""
        if propietario_tipo == "PERSONA":
            return [(p["id"], f"{p['nombres']} {p['apellidos']} ({p['documento']})")
                    for p in self.personas.listar_activas()]
        return [(v["id"], f"{v['nombres']} {v['apellidos']} ({v['documento']})")
                for v in self.visitantes.listar()]

    def guardar(self, datos, vehiculo_id=None):
        error = self._validar(datos)
        if error:
            return False, error
        # Valida la integridad de la relacion polimorfica
        existe = (self.personas.obtener(datos["propietario_id"])
                  if datos["propietario_tipo"] == "PERSONA"
                  else self.visitantes.obtener(datos["propietario_id"]))
        if not existe:
            return False, "El propietario seleccionado no existe."
        try:
            if vehiculo_id is None:
                self.model.crear(**datos)
                return True, "Vehiculo registrado correctamente."
            self.model.actualizar(vehiculo_id, **datos)
            return True, "Vehiculo actualizado correctamente."
        except Exception as exc:
            if "Duplicate" in str(exc):
                return False, f"Ya existe un vehiculo con la placa {datos['placa'].upper()}."
            return False, f"Error al guardar: {exc}"

    def eliminar(self, vehiculo_id):
        try:
            self.model.eliminar(vehiculo_id)
            return True, "Vehiculo eliminado correctamente."
        except Exception as exc:
            return False, f"Error al eliminar: {exc}"

    @staticmethod
    def _validar(datos):
        placa = datos["placa"].strip()
        if not placa:
            return "La placa es obligatoria."
        if datos["tipo"] == "MOTO":
            if not (4 <= len(placa) <= 6):
                return "La placa de la moto debe tener entre 4 y 6 caracteres (ej: XYZ12F)."
        elif not (5 <= len(placa) <= 7):
            return "La placa del carro debe tener entre 5 y 7 caracteres (ej: ABC123)."
        if not datos["propietario_id"]:
            return "Selecciona el propietario del vehiculo."
        return None
