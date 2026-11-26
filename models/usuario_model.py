"""Modelo de usuarios del sistema (autenticacion)."""
import hashlib

from models.database import Database


class UsuarioModel:
    def __init__(self):
        self.db = Database.get_instance()

    @staticmethod
    def _hash(password):
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    def autenticar(self, username, password):
        """Valida credenciales. Devuelve el usuario o None."""
        query = ("SELECT id, username, nombre, rol FROM usuarios "
                 "WHERE username = %s AND password_hash = %s AND activo = 1")
        return self.db.fetch_one(query, (username, self._hash(password)))

    def crear(self, username, password, nombre, rol="VIGILANTE"):
        query = ("INSERT INTO usuarios (username, password_hash, nombre, rol) "
                 "VALUES (%s, %s, %s, %s)")
        return self.db.execute(query, (username, self._hash(password), nombre, rol))
