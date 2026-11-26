"""Controlador de personas autorizadas: valida datos, carga CSV y registra auditoria."""
import csv
from models.persona_model import PersonaModel
from models.audit_model import AuditModel

TIPOS_PERSONA = ("RESIDENTE", "ESTUDIANTE", "DOCENTE", "ADMINISTRATIVO")


class PersonaController:
    def __init__(self):
        self.model = PersonaModel()
        self.audit = AuditModel()

    def listar(self, filtro=""):
        return self.model.listar(filtro)

    def listar_activas(self):
        return self.model.listar_activas()

    def guardar(self, datos, persona_id=None, operador="admin"):
        error = self._validar(datos)
        if error:
            return False, error
        try:
            if persona_id is None:
                self.model.crear(**datos)
                self.audit.registrar(operador, "INSERT", "personas",
                                     f"Registro persona doc {datos['documento']}")
                return True, "Persona registrada correctamente."
            self.model.actualizar(persona_id, **datos)
            self.audit.registrar(operador, "UPDATE", "personas",
                                 f"Actualizo persona ID {persona_id} (doc {datos['documento']})")
            return True, "Persona actualizada correctamente."
        except Exception as exc:
            if "Duplicate" in str(exc):
                return False, f"Ya existe una persona con el documento {datos['documento']}."
            return False, f"Error al guardar: {exc}"

    def importar_csv(self, ruta_csv, operador="admin"):
        """Carga masiva desde CSV omitiendo documentos duplicados (HU-07)."""
        insertados = 0
        duplicados = 0
        errores = 0
        existentes = {str(p["documento"]).strip() for p in self.model.listar("")}

        with open(ruta_csv, mode="r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for fila in reader:
                doc = str(fila.get("documento", "")).strip()
                nombres = str(fila.get("nombres", "")).strip()
                apellidos = str(fila.get("apellidos", "")).strip()
                tipo = str(fila.get("categoria", fila.get("tipo", "ESTUDIANTE"))).strip().upper()
                if tipo not in TIPOS_PERSONA:
                    tipo = "ESTUDIANTE"
                dep = str(fila.get("dependencia", "General")).strip()
                tel = str(fila.get("telefono", "")).strip()

                if not doc or not nombres or not apellidos:
                    errores += 1
                    continue
                if doc in existentes:
                    duplicados += 1
                    continue
                try:
                    self.model.crear(doc, nombres, apellidos, tipo, dep, tel, 1)
                    existentes.add(doc)
                    insertados += 1
                except Exception:
                    duplicados += 1

        self.audit.registrar(
            operador, "IMPORT_CSV", "personas",
            f"Carga masiva CSV: {insertados} importados, {duplicados} duplicados")
        return True, (f"Proceso de carga masiva finalizado:\n\n"
                      f"• Registros importados exitosamente: {insertados}\n"
                      f"• Registros descartados por duplicidad: {duplicados}\n"
                      f"• Filas con formato invalido: {errores}")

    def eliminar(self, persona_id, operador="admin"):
        try:
            self.model.eliminar(persona_id)
            self.audit.registrar(operador, "DELETE", "personas",
                                 f"Elimino persona ID {persona_id}")
            return True, "Persona eliminada correctamente."
        except Exception as exc:
            if "foreign key" in str(exc).lower():
                return False, ("No se puede eliminar: la persona tiene vehiculos "
                               "o accesos registrados. Marca el registro como inactivo.")
            return False, f"Error al eliminar: {exc}"

    @staticmethod
    def _validar(datos):
        if not datos["documento"].strip():
            return "El documento es obligatorio."
        if not datos["nombres"].strip() or not datos["apellidos"].strip():
            return "Nombres y apellidos son obligatorios."
        if datos["tipo"] not in TIPOS_PERSONA:
            return "Selecciona un tipo valido."
        if not datos["dependencia"].strip():
            return "La dependencia es obligatoria."
        return None