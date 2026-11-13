import uuid
from datetime import datetime
from typing import Dict
from models.Usuario import Cliente
from models.Producto import Producto

class Pedido:
    '''Clase que representa un pedido realizado por un cliente.'''
    def __init__(self, cliente: Cliente, productos_cantidades: Dict[Producto, int]):
        self.id: str = str(uuid.uuid4())
        self.cliente: Cliente = cliente
        self.productos_cantidades: Dict[Producto, int] = productos_cantidades
        self.fecha_pedido: datetime = datetime.now()
        self.total: float = self._calcular_total()

    def _calcular_total(self) -> float:
        '''Calcula el importe total de la compra en función de precios y cantidades.'''
        total = 0.0
        for producto, cantidad in self.productos_cantidades.items():
            total += producto.precio * cantidad
        return total

    def __str__(self) -> str:
        # Resumen legible del pedido
        return f"Pedido ID: {self.id[:8]}... | Fecha: {self.fecha_pedido.strftime('%Y-%m-%d %H:%M:%S')} | Cliente: {self.cliente.nombre} | Total: {self.total:.2f}€"
