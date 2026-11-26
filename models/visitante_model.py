"""Modelo de visitantes. Implementa el CRUD completo."""
from models.database import Database


class VisitanteModel:
    def __init__(self):
        self.db = Database.get_instance()

    def listar(self, filtro=""):
        query = ("SELECT id, documento, nombres, apellidos, telefono, empresa "
                 "FROM visitantes "
                 "WHERE documento LIKE %s OR nombres LIKE %s OR apellidos LIKE %s "
                 "ORDER BY apellidos, nombres")
        like = f"%{filtro}%"
        return self.db.fetch_all(query, (like, like, like))

    def obtener(self, visitante_id):
        return self.db.fetch_one("SELECT * FROM visitantes WHERE id = %s", (visitante_id,))

    def obtener_por_documento(self, documento):
        return self.db.fetch_one(
            "SELECT * FROM visitantes WHERE documento = %s", (documento,))

    def crear(self, documento, nombres, apellidos, telefono, empresa):
        query = ("INSERT INTO visitantes (documento, nombres, apellidos, telefono, "
                 "empresa) VALUES (%s, %s, %s, %s, %s)")
        return self.db.execute(query, (documento, nombres, apellidos, telefono, empresa))

    def actualizar(self, visitante_id, documento, nombres, apellidos, telefono, empresa):
        query = ("UPDATE visitantes SET documento=%s, nombres=%s, apellidos=%s, "
                 "telefono=%s, empresa=%s WHERE id=%s")
        return self.db.execute(query, (documento, nombres, apellidos, telefono,
                                       empresa, visitante_id))

    def eliminar(self, visitante_id):
        return self.db.execute("DELETE FROM visitantes WHERE id = %s", (visitante_id,))
