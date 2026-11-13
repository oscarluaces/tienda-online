import uuid

class Producto:
    '''Clase base para representar un producto en la tienda.'''
    def __init__(self, nombre: str, precio: float, stock: int):
        self.id: str = str(uuid.uuid4())
        self.nombre: str = nombre
        self.precio: float = precio
        self.stock: int = stock

    def hay_stock(self, cantidad: int) -> bool:
        '''Comprueba si hay suficiente stock disponible.'''
        return self.stock >= cantidad

    def actualizar_stock(self, cantidad: int) -> None:
        '''Actualiza el stock del producto (sumar o restar).'''
        self.stock += cantidad

    def __str__(self) -> str:
        return f"Producto: {self.nombre} | Precio: {self.precio:.2f}€ | Stock: {self.stock}"

class ProductoElectronico(Producto):
    '''Producto electrónico que incluye meses de garantía.'''
    def __init__(self, nombre: str, precio: float, stock: int, meses_garantia: int):
        super().__init__(nombre, precio, stock)
        self.meses_garantia: int = meses_garantia

    def __str__(self) -> str:
        return f"{super().__str__()} | Garantía: {self.meses_garantia} meses"

class ProductoRopa(Producto):
    '''Producto de ropa que incluye talla y color.'''
    def __init__(self, nombre: str, precio: float, stock: int, talla: str, color: str):
        super().__init__(nombre, precio, stock)
        self.talla: str = talla
        self.color: str = color

    def __str__(self) -> str:
        return f"{super().__str__()} | Talla: {self.talla} | Color: {self.color}"
