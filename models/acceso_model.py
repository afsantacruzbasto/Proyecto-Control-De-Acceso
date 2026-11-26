"""Modelo de accesos: bitacora de entradas y salidas."""
from models.database import Database


class AccesoModel:
    def __init__(self):
        self.db = Database.get_instance()

    _SELECT = """
        SELECT a.id, a.tipo_acceso,
               COALESCE(CONCAT(p.nombres, ' ', p.apellidos),
                        CONCAT(vi.nombres, ' ', vi.apellidos)) AS nombre,
               COALESCE(p.documento, vi.documento)            AS documento,
               ve.placa, ve.tipo AS tipo_vehiculo,
               a.motivo, a.destino,
               a.fecha_hora_entrada, a.fecha_hora_salida,
               u.nombre AS registrado_por, a.observaciones,
               a.persona_id, a.visitante_id, a.vehiculo_id
        FROM accesos a
        LEFT JOIN personas   p  ON p.id  = a.persona_id
        LEFT JOIN visitantes vi ON vi.id = a.visitante_id
        LEFT JOIN vehiculos  ve ON ve.id = a.vehiculo_id
        JOIN usuarios u ON u.id = a.registrado_por
    """

    def listar(self, fecha_desde=None, fecha_hasta=None, solo_abiertos=False):
        query = self._SELECT + " WHERE 1=1"
        params = []
        if fecha_desde:
            query += " AND DATE(a.fecha_hora_entrada) >= %s"
            params.append(fecha_desde)
        if fecha_hasta:
            query += " AND DATE(a.fecha_hora_entrada) <= %s"
            params.append(fecha_hasta)
        if solo_abiertos:
            query += " AND a.fecha_hora_salida IS NULL"
        query += " ORDER BY a.fecha_hora_entrada DESC LIMIT 500"
        return self.db.fetch_all(query, tuple(params))

    def acceso_abierto(self, tipo_acceso, persona_id=None, visitante_id=None):
        """Busca un acceso sin salida registrada para esa persona/visitante."""
        if tipo_acceso == "PERSONA_AUTORIZADA":
            query = self._SELECT + (" WHERE a.persona_id = %s "
                                    "AND a.fecha_hora_salida IS NULL "
                                    "ORDER BY a.id DESC LIMIT 1")
            return self.db.fetch_one(query, (persona_id,))
        query = self._SELECT + (" WHERE a.visitante_id = %s "
                                "AND a.fecha_hora_salida IS NULL "
                                "ORDER BY a.id DESC LIMIT 1")
        return self.db.fetch_one(query, (visitante_id,))

    def registrar_entrada(self, tipo_acceso, persona_id, visitante_id, vehiculo_id,
                          motivo, destino, registrado_por, observaciones):
        query = ("INSERT INTO accesos (tipo_acceso, persona_id, visitante_id, "
                 "vehiculo_id, motivo, destino, fecha_hora_entrada, "
                 "registrado_por, observaciones) "
                 "VALUES (%s, %s, %s, %s, %s, %s, NOW(), %s, %s)")
        return self.db.execute(query, (tipo_acceso, persona_id, visitante_id,
                                       vehiculo_id, motivo, destino,
                                       registrado_por, observaciones))

    def registrar_salida(self, acceso_id, observaciones=None):
        if observaciones:
            query = ("UPDATE accesos SET fecha_hora_salida = NOW(), "
                     "observaciones = %s WHERE id = %s AND fecha_hora_salida IS NULL")
            return self.db.execute(query, (observaciones, acceso_id))
        query = ("UPDATE accesos SET fecha_hora_salida = NOW() "
                 "WHERE id = %s AND fecha_hora_salida IS NULL")
        return self.db.execute(query, (acceso_id,))

    def eliminar(self, acceso_id):
        return self.db.execute("DELETE FROM accesos WHERE id = %s", (acceso_id,))

    # ---------------------------------------------------------
    # Consultas para reportes
    # ---------------------------------------------------------
    def conteo_por_dia(self, fecha_desde, fecha_hasta):
        query = ("SELECT DATE(fecha_hora_entrada) AS fecha, COUNT(*) AS total, "
                 "SUM(CASE WHEN tipo_acceso='VISITANTE' THEN 1 ELSE 0 END) AS visitantes, "
                 "SUM(CASE WHEN tipo_acceso='PERSONA_AUTORIZADA' THEN 1 ELSE 0 END) AS autorizados, "
                 "SUM(CASE WHEN vehiculo_id IS NOT NULL THEN 1 ELSE 0 END) AS con_vehiculo "
                 "FROM accesos "
                 "WHERE DATE(fecha_hora_entrada) BETWEEN %s AND %s "
                 "GROUP BY DATE(fecha_hora_entrada) ORDER BY fecha DESC")
        return self.db.fetch_all(query, (fecha_desde, fecha_hasta))

    def conteo_por_tipo_persona(self, fecha_desde, fecha_hasta):
        query = ("SELECT COALESCE(p.tipo, 'VISITANTE') AS categoria, COUNT(*) AS total "
                 "FROM accesos a LEFT JOIN personas p ON p.id = a.persona_id "
                 "WHERE DATE(a.fecha_hora_entrada) BETWEEN %s AND %s "
                 "GROUP BY categoria ORDER BY total DESC")
        return self.db.fetch_all(query, (fecha_desde, fecha_hasta))

    def dentro_actualmente(self):
        """Personas y visitantes que estan dentro (sin salida registrada)."""
        query = self._SELECT + (" WHERE a.fecha_hora_salida IS NULL "
                                "ORDER BY a.fecha_hora_entrada DESC")
        return self.db.fetch_all(query)

    def estado_parqueadero(self):
        """Devuelve cupo maximo y ocupados actuales por tipo de vehiculo."""
        query = """
            SELECT c.tipo_vehiculo, c.cupo_maximo,
                   COUNT(a.id) AS ocupados
            FROM config_parqueadero c
            LEFT JOIN vehiculos v ON v.tipo = c.tipo_vehiculo
            LEFT JOIN accesos a ON a.vehiculo_id = v.id
                                AND a.fecha_hora_salida IS NULL
            GROUP BY c.tipo_vehiculo, c.cupo_maximo
        """
        return self.db.fetch_all(query)

    def conteo_por_hora(self, fecha_desde, fecha_hasta):
        """Agrupa ingresos por hora del dia para el grafico de barras."""
        query = """
            SELECT HOUR(fecha_hora_entrada) AS hora, COUNT(*) AS total
            FROM accesos
            WHERE DATE(fecha_hora_entrada) BETWEEN %s AND %s
            GROUP BY HOUR(fecha_hora_entrada)
            ORDER BY hora ASC
        """
        return self.db.fetch_all(query, (fecha_desde, fecha_hasta))