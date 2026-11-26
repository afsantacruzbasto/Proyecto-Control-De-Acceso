"""Controlador de accesos: registro de entradas, salidas, cupos y reportes."""
from models.acceso_model import AccesoModel
from models.persona_model import PersonaModel
from models.visitante_model import VisitanteModel
from models.vehiculo_model import VehiculoModel
from models.audit_model import AuditModel


class AccesoController:
    def __init__(self):
        self.model = AccesoModel()
        self.personas = PersonaModel()
        self.visitantes = VisitanteModel()
        self.vehiculos = VehiculoModel()
        self.audit = AuditModel()

    def listar(self, fecha_desde=None, fecha_hasta=None, solo_abiertos=False):
        return self.model.listar(fecha_desde, fecha_hasta, solo_abiertos)

    def listar_vehiculos_de(self, tipo_acceso, propietario_id):
        tipo_prop = "PERSONA" if tipo_acceso == "PERSONA_AUTORIZADA" else "VISITANTE"
        return self.vehiculos.listar_por_propietario(tipo_prop, propietario_id)

    def obtener_cupos_parqueadero(self):
        datos = self.model.estado_parqueadero()
        res = {"CARRO": {"max": 10, "ocupados": 0, "disp": 10},
               "MOTO": {"max": 15, "ocupados": 0, "disp": 15}}
        for r in datos:
            t = r["tipo_vehiculo"]
            m = int(r["cupo_maximo"])
            o = int(r["ocupados"])
            res[t] = {"max": m, "ocupados": o, "disp": max(0, m - o)}
        return res

    def registrar_entrada(self, tipo_acceso, propietario_id, vehiculo_id,
                          motivo, destino, usuario_id, observaciones="",
                          operador="admin"):
        if not propietario_id:
            return False, "Selecciona la persona o el visitante que ingresa."
        persona_id = propietario_id if tipo_acceso == "PERSONA_AUTORIZADA" else None
        visitante_id = propietario_id if tipo_acceso == "VISITANTE" else None

        abierto = self.model.acceso_abierto(tipo_acceso, persona_id, visitante_id)
        if abierto:
            return False, (f"Ya tiene una entrada sin salida registrada "
                           f"(acceso #{abierto['id']}). Registra primero la salida.")

        if vehiculo_id:
            veh = self.vehiculos.obtener(vehiculo_id)
            if veh:
                cupos = self.obtener_cupos_parqueadero()
                info = cupos.get(veh["tipo"], {"disp": 1})
                if info["disp"] <= 0:
                    return False, (f"AFORO COMPLETO: No hay cupos disponibles para "
                                   f"{veh['tipo']} ({info['ocupados']}/{info['max']}).")

        try:
            self.model.registrar_entrada(tipo_acceso, persona_id, visitante_id,
                                         vehiculo_id or None, motivo, destino,
                                         usuario_id, observaciones)
            self.audit.registrar(operador, "ENTRADA", "accesos",
                                 f"Ingreso {tipo_acceso} ID {propietario_id}")
            return True, "Entrada registrada correctamente."
        except Exception as exc:
            return False, f"Error al registrar la entrada: {exc}"

    def registrar_salida(self, acceso_id, observaciones=None, operador="admin"):
        try:
            affected = self.model.registrar_salida(acceso_id, observaciones)
            if affected == 0:
                return False, "El acceso ya tiene salida registrada."
            self.audit.registrar(operador, "SALIDA", "accesos",
                                 f"Salida registrada acceso #{acceso_id}")
            return True, "Salida registrada correctamente."
        except Exception as exc:
            return False, f"Error al registrar la salida: {exc}"

    def eliminar(self, acceso_id, operador="admin"):
        try:
            self.model.eliminar(acceso_id)
            self.audit.registrar(operador, "DELETE", "accesos",
                                 f"Elimino acceso #{acceso_id}")
            return True, "Registro de acceso eliminado."
        except Exception as exc:
            return False, f"Error al eliminar: {exc}"

    def conteo_por_dia(self, fecha_desde, fecha_hasta):
        return self.model.conteo_por_dia(fecha_desde, fecha_hasta)

    def conteo_por_tipo_persona(self, fecha_desde, fecha_hasta):
        return self.model.conteo_por_tipo_persona(fecha_desde, fecha_hasta)

    def conteo_por_hora(self, fecha_desde, fecha_hasta):
        return self.model.conteo_por_hora(fecha_desde, fecha_hasta)

    def dentro_actualmente(self):
        return self.model.dentro_actualmente()