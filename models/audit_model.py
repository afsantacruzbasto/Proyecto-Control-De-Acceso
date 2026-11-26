"""Modelo de auditoria del sistema (Audit Log)."""
from models.database import Database


class AuditModel:
    def __init__(self):
        self.db = Database.get_instance()

    def registrar(self, usuario_operador, accion, entidad_afectada, detalle):
        query = ("INSERT INTO audit_logs (usuario_operador, accion, "
                 "entidad_afectada, detalle) VALUES (%s, %s, %s, %s)")
        return self.db.execute(query, (usuario_operador, accion,
                                       entidad_afectada, detalle))

    def listar(self, filtro=""):
        query = ("SELECT id, usuario_operador, fecha_hora, accion, "
                 "entidad_afectada, detalle FROM audit_logs "
                 "WHERE usuario_operador LIKE %s OR entidad_afectada LIKE %s "
                 "OR detalle LIKE %s ORDER BY id DESC LIMIT 200")
        like = f"%{filtro}%"
        return self.db.fetch_all(query, (like, like, like))