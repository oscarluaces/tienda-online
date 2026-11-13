from typing import List, Dict, Optional
from models.Usuario import Usuario, Cliente, Administrador
from models.Producto import Producto
from models.Pedido import Pedido

class TiendaService:
    '''Servicio para gestionar centralizadamente la tienda.'''
    def __init__(self):
        self.usuarios: Dict[str, Usuario] = {}
        self.productos: Dict[str, Producto] = {}
        self.pedidos: List[Pedido] = []

    def registrar_usuario(self, tipo: str, nombre: str, email: str, direccion: str = "") -> Optional[Usuario]:
        '''Registra un nuevo usuario en función de su tipo (cliente o administrador).'''
        tipo_lower = tipo.lower()
        if tipo_lower == "cliente":
            nuevo_usuario = Cliente(nombre, email, direccion)
        elif tipo_lower == "administrador":
            nuevo_usuario = Administrador(nombre, email)
        else:
            print("Error: Tipo de usuario no válido.")
            return None
        
        self.usuarios[nuevo_usuario.id] = nuevo_usuario
        return nuevo_usuario

    def añadir_producto(self, producto: Producto) -> None:
        '''Añade un producto al inventario.'''
        self.productos[producto.id] = producto

    def eliminar_producto(self, id_producto: str) -> None:
        '''Elimina un producto del inventario usando su identificador.'''
        if id_producto in self.productos:
            del self.productos[id_producto]
        else:
            print(f"Error: Producto con ID {id_producto} no encontrado.")

    def listar_productos(self) -> None:
        '''Lista todos los productos disponibles en la tienda.'''
        print("--- Inventario de la Tienda ---")
        if not self.productos:
            print("El inventario está vacío.")
        for producto in self.productos.values():
            print(producto)
        print("-------------------------------")

    def realizar_pedido(self, id_usuario: str, productos_cantidades: Dict[str, int]) -> Optional[Pedido]:
        '''Genera un pedido verificando existencia de usuario y stock suficiente.'''
        if id_usuario not in self.usuarios:
            print(f"Error: Usuario {id_usuario} no registrado.")
            return None
            
        usuario = self.usuarios[id_usuario]
        if not isinstance(usuario, Cliente):
            print("Error: Solo los clientes pueden realizar pedidos.")
            return None

        productos_pedido = {}
        # Verificación de inventario
        for id_prod, cant in productos_cantidades.items():
            if id_prod not in self.productos:
                print(f"Error: Producto con ID {id_prod} no existe en la tienda.")
                return None
            
            producto = self.productos[id_prod]
            if not producto.hay_stock(cant):
                print(f"Error de stock: No hay suficiente cantidad de {producto.nombre}. Solicitado: {cant}, Disponible: {producto.stock}")
                return None
                
            productos_pedido[producto] = cant

        # Si todo es correcto, crear pedido y descontar stock
        for producto, cant in productos_pedido.items():
            producto.actualizar_stock(-cant)

        nuevo_pedido = Pedido(usuario, productos_pedido)
        self.pedidos.append(nuevo_pedido)
        return nuevo_pedido

    def listar_pedidos_usuario(self, id_usuario: str) -> None:
        '''Lista todos los pedidos de un usuario ordenados por fecha.'''
        pedidos_usuario = [p for p in self.pedidos if p.cliente.id == id_usuario]
        # Ordenados de más antiguo a más reciente
        pedidos_usuario.sort(key=lambda p: p.fecha_pedido)
        
        print(f"--- Histórico de Pedidos (Usuario: {id_usuario[:8]}...) ---")
        if not pedidos_usuario:
            print("No hay pedidos registrados para este usuario.")
        for pedido in pedidos_usuario:
            print(pedido)
        print("---------------------------------------------------------")
