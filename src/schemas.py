'''Esquemas Pydantic de la API.

- *Create: datos que envía el cliente (peticiones). FastAPI los valida automáticamente.
- *Read:   datos que devuelve la API (respuestas). Cada uno tiene un método
           desde_dominio() que lo construye a partir de los objetos de la Práctica 1
           (Cliente, ProductoRopa, Pedido...), sin tener que modificar esas clases.
'''

from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, Field, model_validator

from models.Pedido import Pedido
from models.Producto import Producto, ProductoElectronico, ProductoRopa
from models.Usuario import Usuario

EMAIL_REGEX = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"


# ======================================================================= Usuarios
class UsuarioCreate(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=100, examples=["María López"])
    email: str = Field(..., pattern=EMAIL_REGEX, examples=["maria@email.com"])
    tipo: Literal["cliente", "administrador"] = Field(..., examples=["cliente"])
    direccion: Optional[str] = Field(
        default=None,
        min_length=1,
        description="Dirección postal (obligatoria para clientes)",
        examples=["Calle Rosalía de Castro 10"],
    )

    @model_validator(mode="after")
    def cliente_necesita_direccion(self):
        if self.tipo == "cliente" and not self.direccion:
            raise ValueError("Los clientes deben indicar una dirección postal")
        return self


class UsuarioRead(BaseModel):
    id: str
    nombre: str
    email: str
    es_admin: bool

    @classmethod
    def desde_dominio(cls, usuario: Usuario) -> "UsuarioRead":
        return cls(
            id=usuario.id,
            nombre=usuario.nombre,
            email=usuario.email,
            es_admin=usuario.is_admin(),
        )


# ====================================================================== Productos
TipoProducto = Literal["generico", "electronico", "ropa"]


class ProductoCreate(BaseModel):
    tipo: TipoProducto = Field(..., examples=["electronico"])
    nombre: str = Field(..., min_length=1, max_length=100, examples=["Portátil Gaming"])
    precio: float = Field(..., gt=0, examples=[1200.00])
    stock: int = Field(..., ge=0, examples=[10])
    meses_garantia: Optional[int] = Field(
        default=None, ge=0, description="Obligatorio solo para electrónicos", examples=[36]
    )
    talla: Optional[str] = Field(
        default=None, min_length=1, description="Obligatorio solo para ropa", examples=[None]
    )
    color: Optional[str] = Field(
        default=None, min_length=1, description="Obligatorio solo para ropa", examples=[None]
    )

    @model_validator(mode="after")
    def atributos_segun_tipo(self):
        if self.tipo == "electronico":
            if self.meses_garantia is None:
                raise ValueError("Los productos electrónicos requieren 'meses_garantia'")
            if self.talla is not None or self.color is not None:
                raise ValueError("Los productos electrónicos no tienen talla ni color")
        elif self.tipo == "ropa":
            if self.talla is None or self.color is None:
                raise ValueError("Los productos de ropa requieren 'talla' y 'color'")
            if self.meses_garantia is not None:
                raise ValueError("Los productos de ropa no tienen meses de garantía")
        else:  # generico
            if any(v is not None for v in (self.meses_garantia, self.talla, self.color)):
                raise ValueError("Los productos genéricos no admiten meses_garantia, talla ni color")
        return self


class ProductoRead(BaseModel):
    id: str
    tipo: TipoProducto
    nombre: str
    precio: float
    stock: int
    # Atributos opcionales: solo tienen valor según el tipo de producto
    meses_garantia: Optional[int] = None
    talla: Optional[str] = None
    color: Optional[str] = None

    @classmethod
    def desde_dominio(cls, producto: Producto) -> "ProductoRead":
        datos = dict(
            id=producto.id,
            nombre=producto.nombre,
            precio=producto.precio,
            stock=producto.stock,
            tipo="generico",
        )
        if isinstance(producto, ProductoElectronico):
            datos.update(tipo="electronico", meses_garantia=producto.meses_garantia)
        elif isinstance(producto, ProductoRopa):
            datos.update(tipo="ropa", talla=producto.talla, color=producto.color)
        return cls(**datos)


class StockRead(BaseModel):
    producto_id: str
    nombre: str
    stock: int
    disponible: bool


# ======================================================================== Pedidos
class PedidoItemCreate(BaseModel):
    producto_id: str = Field(..., min_length=1)
    cantidad: int = Field(..., gt=0, examples=[1])


class PedidoCreate(BaseModel):
    cliente_id: str = Field(..., min_length=1)
    items: List[PedidoItemCreate] = Field(..., min_length=1)


class PedidoItemRead(BaseModel):
    producto_id: str
    nombre: str
    precio_unitario: float
    cantidad: int
    subtotal: float


class PedidoRead(BaseModel):
    id: str
    fecha: datetime
    cliente_id: str
    cliente_nombre: str
    total: float
    items: List[PedidoItemRead]

    @classmethod
    def desde_dominio(cls, pedido: Pedido) -> "PedidoRead":
        items = [
            PedidoItemRead(
                producto_id=producto.id,
                nombre=producto.nombre,
                precio_unitario=producto.precio,
                cantidad=cantidad,
                subtotal=round(producto.precio * cantidad, 2),
            )
            for producto, cantidad in pedido.productos_cantidades.items()
        ]
        return cls(
            id=pedido.id,
            fecha=pedido.fecha_pedido,
            cliente_id=pedido.cliente.id,
            cliente_nombre=pedido.cliente.nombre,
            total=round(pedido.total, 2),
            items=items,
        )
