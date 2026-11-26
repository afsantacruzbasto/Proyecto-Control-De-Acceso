"""Capa de conexion a la base de datos (patron Singleton).

Centraliza la conexion MySQL para que toda la aplicacion comparta
una unica instancia y ninguna vista hable directamente con la BD.
"""
import pymysql
from pymysql.cursors import DictCursor

from config import DB_CONFIG


class Database:
    """Maneja la conexion unica con el servidor MySQL."""

    _instance = None

    def __init__(self):
        self._connection = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def connect(self):
        """Abre la conexion si no existe o si se perdio."""
        try:
            if self._connection is not None:
                self._connection.ping(reconnect=True)
                return self._connection
        except Exception:
            self._connection = None

        self._connection = pymysql.connect(
            host=DB_CONFIG["host"],
            port=DB_CONFIG["port"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            database=DB_CONFIG["database"],
            charset=DB_CONFIG["charset"],
            cursorclass=DictCursor,
            autocommit=False,
        )
        return self._connection

    def test_connection(self):
        """Verifica la conexion. Devuelve (ok, mensaje)."""
        try:
            conn = self.connect()
            with conn.cursor() as cur:
                cur.execute("SELECT VERSION() AS version, DATABASE() AS db")
                row = cur.fetchone()
            return True, f"Conectado a MySQL {row['version']} - base '{row['db']}'"
        except pymysql.MySQLError as exc:
            return False, f"Error de conexion: {exc}"

    # ---------------------------------------------------------
    # Metodos genericos usados por todos los modelos
    # ---------------------------------------------------------
    def fetch_all(self, query, params=None):
        conn = self.connect()
        with conn.cursor() as cur:
            cur.execute(query, params or ())
            return cur.fetchall()

    def fetch_one(self, query, params=None):
        conn = self.connect()
        with conn.cursor() as cur:
            cur.execute(query, params or ())
            return cur.fetchone()

    def execute(self, query, params=None):
        """INSERT / UPDATE / DELETE. Devuelve el id insertado o filas afectadas."""
        conn = self.connect()
        try:
            with conn.cursor() as cur:
                cur.execute(query, params or ())
                affected = cur.rowcount
                last_id = cur.lastrowid
            conn.commit()
            return last_id if last_id else affected
        except pymysql.MySQLError:
            conn.rollback()
            raise
