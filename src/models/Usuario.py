import uuid

class Usuario:
    '''Clase base para representar un usuario.'''
    def __init__(self, nombre: str, email: str):
        self.id: str = str(uuid.uuid4())
        self.nombre: str = nombre
        self.email: str = email

    def is_admin(self) -> bool:
        '''Indica si el usuario es administrador. Por defecto es False.'''
        return False

class Cliente(Usuario):
    '''Representa a un cliente de la tienda, incluye dirección postal.'''
    def __init__(self, nombre: str, email: str, direccion: str):
        super().__init__(nombre, email)
        self.direccion: str = direccion

class Administrador(Usuario):
    '''Representa a un gestor de la tienda con permisos de administrador.'''
    def __init__(self, nombre: str, email: str):
        super().__init__(nombre, email)

    def is_admin(self) -> bool:
        '''Sobrescribe el método devolviendo True para administradores.'''
        return True
