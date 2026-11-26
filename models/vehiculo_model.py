"""Modelo de vehiculos (carros y motos). Implementa el CRUD completo."""
from models.database import Database


class VehiculoModel:
    def __init__(self):
        self.db = Database.get_instance()

    def listar(self, filtro=""):
        query = ("SELECT v.id, v.placa, v.tipo, v.marca, v.color, "
                 "       v.propietario_tipo, v.propietario_id, "
                 "       CASE v.propietario_tipo "
                 "           WHEN 'PERSONA' THEN (SELECT CONCAT(p.nombres, ' ', p.apellidos) "
                 "                                FROM personas p WHERE p.id = v.propietario_id) "
                 "           ELSE (SELECT CONCAT(vi.nombres, ' ', vi.apellidos) "
                 "                 FROM visitantes vi WHERE vi.id = v.propietario_id) "
                 "       END AS propietario "
                 "FROM vehiculos v "
                 "WHERE v.placa LIKE %s OR v.marca LIKE %s "
                 "ORDER BY v.placa")
        like = f"%{filtro}%"
        return self.db.fetch_all(query, (like, like))

    def listar_por_propietario(self, propietario_tipo, propietario_id):
        query = ("SELECT id, placa, tipo, marca, color FROM vehiculos "
                 "WHERE propietario_tipo = %s AND propietario_id = %s ORDER BY placa")
        return self.db.fetch_all(query, (propietario_tipo, propietario_id))

    def obtener(self, vehiculo_id):
        return self.db.fetch_one("SELECT * FROM vehiculos WHERE id = %s", (vehiculo_id,))

    def obtener_por_placa(self, placa):
        return self.db.fetch_one("SELECT * FROM vehiculos WHERE placa = %s",
                                 (placa.upper(),))

    def crear(self, placa, tipo, marca, color, propietario_tipo, propietario_id):
        query = ("INSERT INTO vehiculos (placa, tipo, marca, color, propietario_tipo, "
                 "propietario_id) VALUES (%s, %s, %s, %s, %s, %s)")
        return self.db.execute(query, (placa.upper(), tipo, marca, color,
                                       propietario_tipo, propietario_id))

    def actualizar(self, vehiculo_id, placa, tipo, marca, color,
                   propietario_tipo, propietario_id):
        query = ("UPDATE vehiculos SET placa=%s, tipo=%s, marca=%s, color=%s, "
                 "propietario_tipo=%s, propietario_id=%s WHERE id=%s")
        return self.db.execute(query, (placa.upper(), tipo, marca, color,
                                       propietario_tipo, propietario_id, vehiculo_id))

    def eliminar(self, vehiculo_id):
        return self.db.execute("DELETE FROM vehiculos WHERE id = %s", (vehiculo_id,))
