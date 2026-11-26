"""Controlador de visitantes: valida datos y usa el modelo."""
from models.visitante_model import VisitanteModel


class VisitanteController:
    def __init__(self):
        self.model = VisitanteModel()

    def listar(self, filtro=""):
        return self.model.listar(filtro)

    def guardar(self, datos, visitante_id=None):
        error = self._validar(datos)
        if error:
            return False, error
        try:
            if visitante_id is None:
                self.model.crear(**datos)
                return True, "Visitante registrado correctamente."
            self.model.actualizar(visitante_id, **datos)
            return True, "Visitante actualizado correctamente."
        except Exception as exc:
            if "Duplicate" in str(exc):
                return False, f"Ya existe un visitante con el documento {datos['documento']}."
            return False, f"Error al guardar: {exc}"

    def eliminar(self, visitante_id):
        try:
            self.model.eliminar(visitante_id)
            return True, "Visitante eliminado correctamente."
        except Exception as exc:
            if "foreign key" in str(exc).lower():
                return False, ("No se puede eliminar: el visitante tiene vehiculos "
                               "o accesos registrados.")
            return False, f"Error al eliminar: {exc}"

    @staticmethod
    def _validar(datos):
        if not datos["documento"].strip():
            return "El documento es obligatorio."
        if not datos["nombres"].strip() or not datos["apellidos"].strip():
            return "Nombres y apellidos son obligatorios."
        return None
