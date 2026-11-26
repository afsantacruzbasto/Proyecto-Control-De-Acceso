"""Controlador de autenticacion."""
from models.usuario_model import UsuarioModel


class AuthController:
    def __init__(self):
        self.model = UsuarioModel()
        self.usuario_actual = None

    def login(self, username, password):
        if not username.strip() or not password:
            return False, "Ingresa usuario y contrasena."
        usuario = self.model.autenticar(username.strip(), password)
        if usuario is None:
            return False, "Usuario o contrasena incorrectos."
        self.usuario_actual = usuario
        return True, usuario

    def logout(self):
        self.usuario_actual = None
