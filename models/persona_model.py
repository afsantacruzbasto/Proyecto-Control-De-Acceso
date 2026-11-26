"""Modelo de personas autorizadas (residentes, estudiantes, docentes,
personal administrativo). Implementa el CRUD completo."""
from models.database import Database


class PersonaModel:
    def __init__(self):
        self.db = Database.get_instance()

    def listar(self, filtro=""):
        query = ("SELECT id, documento, nombres, apellidos, tipo, dependencia, "
                 "telefono, activo FROM personas "
                 "WHERE documento LIKE %s OR nombres LIKE %s OR apellidos LIKE %s "
                 "ORDER BY apellidos, nombres")
        like = f"%{filtro}%"
        return self.db.fetch_all(query, (like, like, like))

    def listar_activas(self):
        query = ("SELECT id, documento, nombres, apellidos, tipo, dependencia "
                 "FROM personas WHERE activo = 1 ORDER BY apellidos, nombres")
        return self.db.fetch_all(query)

    def obtener(self, persona_id):
        return self.db.fetch_one("SELECT * FROM personas WHERE id = %s", (persona_id,))

    def crear(self, documento, nombres, apellidos, tipo, dependencia, telefono,
              activo=1):
        query = ("INSERT INTO personas (documento, nombres, apellidos, tipo, "
                 "dependencia, telefono, activo) VALUES (%s, %s, %s, %s, %s, %s, %s)")
        return self.db.execute(query, (documento, nombres, apellidos, tipo,
                                       dependencia, telefono, activo))

    def actualizar(self, persona_id, documento, nombres, apellidos, tipo,
                   dependencia, telefono, activo):
        query = ("UPDATE personas SET documento=%s, nombres=%s, apellidos=%s, "
                 "tipo=%s, dependencia=%s, telefono=%s, activo=%s WHERE id=%s")
        return self.db.execute(query, (documento, nombres, apellidos, tipo,
                                       dependencia, telefono, activo, persona_id))

    def eliminar(self, persona_id):
        return self.db.execute("DELETE FROM personas WHERE id = %s", (persona_id,))
