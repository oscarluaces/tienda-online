from typing import List, Dict, Optional
from models.Usuario import Usuario, Cliente, Administrador
from models.Producto import Producto, ProductoElectronico, ProductoRopa
from models.Pedido import Pedido
from Services.excepciones import RecursoNoEncontrado, Conflicto, OperacionNoValida


class TiendaService:
    '''Servicio para gestionar centralizadamente la tienda.

    Cambios respecto a la Práctica 1 para poder exponerlo como API REST:
      - Los errores ya no se imprimen con print(): se lanzan excepciones de negocio
        (RecursoNoEncontrado, Conflicto, OperacionNoValida) que main.py traduce a códigos HTTP.
      - Los métodos de listado devuelven los datos en lugar de imprimirlos.
      - Nuevos métodos: obtener_usuario, listar_usuarios, crear_producto,
        obtener_producto y consultar_stock.
    '''
    def __init__(self):
        self.usuarios: Dict[str, Usuario] = {}
        self.productos: Dict[str, Producto] = {}
        self.pedidos: List[Pedido] = []

    # ------------------------------------------------------------------ Usuarios
    def registrar_usuario(self, tipo: str, nombre: str, email: str, direccion: str = "") -> Usuario:
        '''Registra un nuevo usuario en función de su tipo (cliente o administrador).'''
        email_normalizado = email.strip().lower()
        if any(u.email.lower() == email_normalizado for u in self.usuarios.values()):
            raise Conflicto(f"Ya existe un usuario con el email {email_normalizado}")

        tipo_lower = tipo.lower()
        if tipo_lower == "cliente":
            if not direccion or not direccion.strip():
                raise OperacionNoValida("Los clientes deben indicar una dirección postal")
            nuevo_usuario = Cliente(nombre, email_normalizado, direccion)
        elif tipo_lower == "administrador":
            nuevo_usuario = Administrador(nombre, email_normalizado)
        else:
            raise OperacionNoValida(f"Tipo de usuario no válido: {tipo}")

        self.usuarios[nuevo_usuario.id] = nuevo_usuario
        return nuevo_usuario

    def obtener_usuario(self, id_usuario: str) -> Usuario:
        '''Devuelve un usuario concreto o lanza RecursoNoEncontrado.'''
        if id_usuario not in self.usuarios:
            raise RecursoNoEncontrado(f"Usuario {id_usuario} no registrado")
        return self.usuarios[id_usuario]

    def listar_usuarios(self) -> List[Usuario]:
        '''Devuelve la lista de usuarios registrados.'''
        return list(self.usuarios.values())

    def _obtener_cliente(self, id_usuario: str) -> Cliente:
        '''Devuelve el usuario comprobando que sea un cliente.'''
        usuario = self.obtener_usuario(id_usuario)
        if not isinstance(usuario, Cliente):
            raise OperacionNoValida("Solo los clientes pueden realizar y consultar pedidos")
        return usuario

    # ----------------------------------------------------------------- Productos
    def añadir_producto(self, producto: Producto) -> Producto:
        '''Añade un producto al inventario.'''
        if producto.precio <= 0:
            raise OperacionNoValida("El precio debe ser mayor que 0")
        if producto.stock < 0:
            raise OperacionNoValida("El stock no puede ser negativo")
        self.productos[producto.id] = producto
        return producto

    def crear_producto(self, tipo: str, nombre: str, precio: float, stock: int,
                       meses_garantia: Optional[int] = None,
                       talla: Optional[str] = None, color: Optional[str] = None) -> Producto:
        '''Crea el producto del tipo indicado (generico, electronico o ropa) y lo añade.'''
        tipo_lower = tipo.lower()
        if tipo_lower == "generico":
            producto = Producto(nombre, precio, stock)
        elif tipo_lower == "electronico":
            if meses_garantia is None:
                raise OperacionNoValida("Los productos electrónicos requieren meses de garantía")
            producto = ProductoElectronico(nombre, precio, stock, meses_garantia)
        elif tipo_lower == "ropa":
            if not talla or not color:
                raise OperacionNoValida("Los productos de ropa requieren talla y color")
            producto = ProductoRopa(nombre, precio, stock, talla, color)
        else:
            raise OperacionNoValida(f"Tipo de producto no válido: {tipo}")
        return self.añadir_producto(producto)

    def obtener_producto(self, id_producto: str) -> Producto:
        '''Devuelve un producto concreto o lanza RecursoNoEncontrado.'''
        if id_producto not in self.productos:
            raise RecursoNoEncontrado(f"Producto con ID {id_producto} no encontrado")
        return self.productos[id_producto]

    def consultar_stock(self, id_producto: str) -> int:
        '''Consulta independiente del stock disponible de un producto.'''
        return self.obtener_producto(id_producto).stock

    def eliminar_producto(self, id_producto: str) -> None:
        '''Elimina un producto del inventario usando su identificador.'''
        self.obtener_producto(id_producto)  # lanza RecursoNoEncontrado si no existe
        del self.productos[id_producto]

    def listar_productos(self) -> List[Producto]:
        '''Devuelve todos los productos disponibles en la tienda.'''
        return list(self.productos.values())

    # ------------------------------------------------------------------- Pedidos
    def realizar_pedido(self, id_usuario: str, productos_cantidades: Dict[str, int]) -> Pedido:
        '''Genera un pedido verificando existencia de usuario, productos y stock suficiente.

        Primero se valida todo y solo después se descuenta el stock, para que un
        pedido fallido no deje el inventario a medias.
        '''
        usuario = self._obtener_cliente(id_usuario)
        if not productos_cantidades:
            raise OperacionNoValida("El pedido debe incluir al menos un producto")

        productos_pedido: Dict[Producto, int] = {}
        # Verificación de inventario
        for id_prod, cant in productos_cantidades.items():
            if cant <= 0:
                raise OperacionNoValida("La cantidad de cada producto debe ser mayor que 0")
            producto = self.obtener_producto(id_prod)
            if not producto.hay_stock(cant):
                raise OperacionNoValida(
                    f"Stock insuficiente de {producto.nombre}. "
                    f"Solicitado: {cant}, Disponible: {producto.stock}"
                )
            productos_pedido[producto] = cant

        # Si todo es correcto, crear pedido y descontar stock
        for producto, cant in productos_pedido.items():
            producto.actualizar_stock(-cant)

        nuevo_pedido = Pedido(usuario, productos_pedido)
        self.pedidos.append(nuevo_pedido)
        return nuevo_pedido

    def listar_pedidos_usuario(self, id_usuario: str) -> List[Pedido]:
        '''Devuelve los pedidos de un cliente ordenados por fecha (más antiguo primero).'''
        self._obtener_cliente(id_usuario)
        pedidos_usuario = [p for p in self.pedidos if p.cliente.id == id_usuario]
        pedidos_usuario.sort(key=lambda p: p.fecha_pedido)
        return pedidos_usuario
