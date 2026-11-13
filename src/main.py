'''Punto de entrada de la API REST de la Tienda Online (capa de exposición).

Ejecutar desde la raíz del repositorio:
    uvicorn main:app --app-dir src --reload
y abrir http://127.0.0.1:8000/docs
'''

from typing import Dict, List

from fastapi import Depends, FastAPI, Request, status
from fastapi.responses import JSONResponse

from schemas import (
    PedidoCreate,
    PedidoRead,
    ProductoCreate,
    ProductoRead,
    StockRead,
    UsuarioCreate,
    UsuarioRead,
)
from Services.Tienda_service import TiendaService
from Services.excepciones import Conflicto, OperacionNoValida, RecursoNoEncontrado

app = FastAPI(
    title="Tienda Online API",
    description="Práctica 2 - Arquitectura del Software. API REST sobre TiendaService.",
    version="2.0.0",
)

# ------------------------------------------------------------------------------
# Instancia única del servicio (los datos viven en memoria mientras corre la API)
# y dependencia para inyectarla en los endpoints.
# ------------------------------------------------------------------------------
tienda = TiendaService()


def get_tienda() -> TiendaService:
    return tienda


# ------------------------------------------------------------------------------
# Traducción de las excepciones de negocio a códigos HTTP.
# Todas las respuestas de error tienen el mismo formato: {"detail": "..."}
# ------------------------------------------------------------------------------
@app.exception_handler(RecursoNoEncontrado)
def manejar_no_encontrado(request: Request, exc: RecursoNoEncontrado):
    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"detail": str(exc)})


@app.exception_handler(Conflicto)
def manejar_conflicto(request: Request, exc: Conflicto):
    return JSONResponse(status_code=status.HTTP_409_CONFLICT, content={"detail": str(exc)})


@app.exception_handler(OperacionNoValida)
def manejar_operacion_no_valida(request: Request, exc: OperacionNoValida):
    return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exc)})


# ====================================================================== Usuarios
@app.post(
    "/usuarios",
    response_model=UsuarioRead,
    status_code=status.HTTP_201_CREATED,
    tags=["Usuarios"],
    responses={409: {"description": "Email ya registrado"}},
)
def crear_usuario(datos: UsuarioCreate, servicio: TiendaService = Depends(get_tienda)):
    usuario = servicio.registrar_usuario(
        tipo=datos.tipo,
        nombre=datos.nombre,
        email=datos.email,
        direccion=datos.direccion or "",
    )
    return UsuarioRead.desde_dominio(usuario)


@app.get("/usuarios", response_model=List[UsuarioRead], tags=["Usuarios"])
def listar_usuarios(servicio: TiendaService = Depends(get_tienda)):
    return [UsuarioRead.desde_dominio(u) for u in servicio.listar_usuarios()]


@app.get(
    "/usuarios/{usuario_id}",
    response_model=UsuarioRead,
    tags=["Usuarios"],
    responses={404: {"description": "Usuario no encontrado"}},
)
def obtener_usuario(usuario_id: str, servicio: TiendaService = Depends(get_tienda)):
    return UsuarioRead.desde_dominio(servicio.obtener_usuario(usuario_id))


# ===================================================================== Productos
@app.post(
    "/productos",
    response_model=ProductoRead,
    status_code=status.HTTP_201_CREATED,
    tags=["Productos"],
)
def crear_producto(datos: ProductoCreate, servicio: TiendaService = Depends(get_tienda)):
    producto = servicio.crear_producto(**datos.model_dump())
    return ProductoRead.desde_dominio(producto)


@app.get("/productos", response_model=List[ProductoRead], tags=["Productos"])
def listar_productos(servicio: TiendaService = Depends(get_tienda)):
    return [ProductoRead.desde_dominio(p) for p in servicio.listar_productos()]


@app.get(
    "/productos/{producto_id}",
    response_model=ProductoRead,
    tags=["Productos"],
    responses={404: {"description": "Producto no encontrado"}},
)
def obtener_producto(producto_id: str, servicio: TiendaService = Depends(get_tienda)):
    return ProductoRead.desde_dominio(servicio.obtener_producto(producto_id))


@app.get(
    "/productos/{producto_id}/stock",
    response_model=StockRead,
    tags=["Productos"],
    responses={404: {"description": "Producto no encontrado"}},
)
def consultar_stock(producto_id: str, servicio: TiendaService = Depends(get_tienda)):
    stock = servicio.consultar_stock(producto_id)
    producto = servicio.obtener_producto(producto_id)
    return StockRead(producto_id=producto_id, nombre=producto.nombre, stock=stock, disponible=stock > 0)


@app.delete(
    "/productos/{producto_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Productos"],
    responses={404: {"description": "Producto no encontrado"}},
)
def eliminar_producto(producto_id: str, servicio: TiendaService = Depends(get_tienda)):
    servicio.eliminar_producto(producto_id)
    # 204 No Content: la respuesta no lleva cuerpo


# ======================================================================= Pedidos
@app.post(
    "/pedidos",
    response_model=PedidoRead,
    status_code=status.HTTP_201_CREATED,
    tags=["Pedidos"],
    responses={
        400: {"description": "Stock insuficiente o el usuario no es cliente"},
        404: {"description": "Cliente o producto no encontrado"},
    },
)
def crear_pedido(datos: PedidoCreate, servicio: TiendaService = Depends(get_tienda)):
    # TiendaService recibe un diccionario {id_producto: cantidad}.
    # Si un producto aparece en varias líneas se suman sus cantidades.
    productos_cantidades: Dict[str, int] = {}
    for item in datos.items:
        productos_cantidades[item.producto_id] = productos_cantidades.get(item.producto_id, 0) + item.cantidad

    pedido = servicio.realizar_pedido(datos.cliente_id, productos_cantidades)
    return PedidoRead.desde_dominio(pedido)


@app.get(
    "/usuarios/{cliente_id}/pedidos",
    response_model=List[PedidoRead],
    tags=["Pedidos"],
    responses={
        400: {"description": "El usuario no es cliente"},
        404: {"description": "Cliente no encontrado"},
    },
)
def pedidos_de_cliente(cliente_id: str, servicio: TiendaService = Depends(get_tienda)):
    return [PedidoRead.desde_dominio(p) for p in servicio.listar_pedidos_usuario(cliente_id)]
