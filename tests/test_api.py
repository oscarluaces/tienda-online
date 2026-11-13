'''Pruebas de la API con el TestClient de FastAPI.

Ejecutar desde la carpeta del proyecto:  pytest -v
'''

import pytest
from fastapi.testclient import TestClient

from main import app, get_tienda
from Services.Tienda_service import TiendaService


@pytest.fixture
def client():
    servicio = TiendaService()  # tienda vacía para cada test
    app.dependency_overrides[get_tienda] = lambda: servicio
    yield TestClient(app)
    app.dependency_overrides.clear()


def crear_cliente(client, nombre="María", email="maria@email.com"):
    r = client.post(
        "/usuarios",
        json={"nombre": nombre, "email": email, "tipo": "cliente", "direccion": "Calle 1"},
    )
    assert r.status_code == 201, r.text
    return r.json()


def crear_admin(client):
    r = client.post(
        "/usuarios", json={"nombre": "Admin", "email": "admin@tienda.com", "tipo": "administrador"}
    )
    assert r.status_code == 201, r.text
    return r.json()


def crear_producto(client, **extra):
    datos = {"tipo": "generico", "nombre": "Taza", "precio": 5.5, "stock": 10} | extra
    r = client.post("/productos", json=datos)
    assert r.status_code == 201, r.text
    return r.json()


def pedir(client, cliente_id, items):
    return client.post("/pedidos", json={"cliente_id": cliente_id, "items": items})


# ---------------------------------------------------------------------- usuarios
def test_crear_y_obtener_usuarios(client):
    maria = crear_cliente(client)
    assert maria["nombre"] == "María" and maria["es_admin"] is False
    assert set(maria) == {"id", "nombre", "email", "es_admin"}

    admin = crear_admin(client)
    assert admin["es_admin"] is True

    assert client.get(f"/usuarios/{maria['id']}").json() == maria
    assert len(client.get("/usuarios").json()) == 2


def test_usuario_errores(client):
    crear_cliente(client)
    assert client.get("/usuarios/no-existe").status_code == 404
    # email repetido (sin distinguir mayúsculas)
    r = client.post(
        "/usuarios",
        json={"nombre": "Otra", "email": "MARIA@email.com", "tipo": "cliente", "direccion": "x"},
    )
    assert r.status_code == 409
    # cliente sin dirección / email inválido / tipo desconocido
    assert client.post("/usuarios", json={"nombre": "B", "email": "b@x.com", "tipo": "cliente"}).status_code == 422
    assert client.post("/usuarios", json={"nombre": "B", "email": "no-email", "tipo": "administrador"}).status_code == 422
    assert client.post("/usuarios", json={"nombre": "B", "email": "b@x.com", "tipo": "jefe"}).status_code == 422


# --------------------------------------------------------------------- productos
def test_crud_productos(client):
    p = crear_producto(client)
    assert p["tipo"] == "generico" and p["meses_garantia"] is None

    e = crear_producto(client, tipo="electronico", nombre="Portátil", precio=1200, meses_garantia=36)
    assert e["tipo"] == "electronico" and e["meses_garantia"] == 36

    r = crear_producto(client, tipo="ropa", nombre="Camiseta", precio=15.5, talla="M", color="Blanco")
    assert (r["tipo"], r["talla"], r["color"]) == ("ropa", "M", "Blanco")

    assert len(client.get("/productos").json()) == 3
    assert client.get(f"/productos/{e['id']}").json() == e

    assert client.delete(f"/productos/{e['id']}").status_code == 204
    assert client.get(f"/productos/{e['id']}").status_code == 404
    assert client.delete(f"/productos/{e['id']}").status_code == 404


def test_consultar_stock(client):
    p = crear_producto(client, stock=4)
    r = client.get(f"/productos/{p['id']}/stock")
    assert r.status_code == 200
    assert r.json() == {"producto_id": p["id"], "nombre": "Taza", "stock": 4, "disponible": True}
    assert client.get("/productos/no-existe/stock").status_code == 404


@pytest.mark.parametrize(
    "datos",
    [
        {"tipo": "electronico", "nombre": "TV", "precio": 100, "stock": 1},  # sin garantía
        {"tipo": "ropa", "nombre": "Pantalón", "precio": 20, "stock": 1, "talla": "L"},  # sin color
        {"tipo": "generico", "nombre": "Taza", "precio": 5, "stock": 1, "talla": "M"},  # atributo sobrante
        {"tipo": "generico", "nombre": "Taza", "precio": -5, "stock": 1},  # precio negativo
        {"tipo": "generico", "nombre": "Taza", "precio": 5, "stock": -1},  # stock negativo
        {"tipo": "mueble", "nombre": "Silla", "precio": 5, "stock": 1},  # tipo desconocido
    ],
)
def test_producto_invalido(client, datos):
    assert client.post("/productos", json=datos).status_code == 422


# ----------------------------------------------------------------------- pedidos
def test_tres_pedidos_de_clientes_distintos(client):
    maria = crear_cliente(client, "María", "maria@email.com")
    carlos = crear_cliente(client, "Carlos", "carlos@email.com")
    lucia = crear_cliente(client, "Lucía", "lucia@email.com")
    portatil = crear_producto(client, tipo="electronico", nombre="Portátil", precio=1200, stock=10, meses_garantia=36)
    camiseta = crear_producto(client, tipo="ropa", nombre="Camiseta", precio=15.5, stock=100, talla="M", color="Blanco")

    r1 = pedir(client, maria["id"], [{"producto_id": portatil["id"], "cantidad": 1}])
    r2 = pedir(client, carlos["id"], [{"producto_id": camiseta["id"], "cantidad": 2}])
    r3 = pedir(client, lucia["id"], [
        {"producto_id": portatil["id"], "cantidad": 1},
        {"producto_id": camiseta["id"], "cantidad": 1},
    ])
    assert [r.status_code for r in (r1, r2, r3)] == [201, 201, 201]

    p3 = r3.json()
    assert p3["cliente_id"] == lucia["id"] and p3["cliente_nombre"] == "Lucía"
    assert p3["total"] == 1215.5
    assert {"producto_id": camiseta["id"], "nombre": "Camiseta", "precio_unitario": 15.5,
            "cantidad": 1, "subtotal": 15.5} in p3["items"]

    # stock actualizado y consultable
    assert client.get(f"/productos/{portatil['id']}/stock").json()["stock"] == 8
    assert client.get(f"/productos/{camiseta['id']}/stock").json()["stock"] == 97

    # cada cliente ve solo sus pedidos
    for cliente, pedido in ((maria, r1), (carlos, r2), (lucia, r3)):
        historial = client.get(f"/usuarios/{cliente['id']}/pedidos").json()
        assert [p["id"] for p in historial] == [pedido.json()["id"]]


def test_pedido_errores(client):
    maria = crear_cliente(client)
    taza = crear_producto(client, stock=3)
    admin = crear_admin(client)

    assert pedir(client, "no-existe", [{"producto_id": taza["id"], "cantidad": 1}]).status_code == 404
    assert pedir(client, maria["id"], [{"producto_id": "no-existe", "cantidad": 1}]).status_code == 404
    assert pedir(client, admin["id"], [{"producto_id": taza["id"], "cantidad": 1}]).status_code == 400
    assert pedir(client, maria["id"], [{"producto_id": taza["id"], "cantidad": 4}]).status_code == 400
    # mismo producto repetido en dos líneas: 2 + 2 > 3
    assert pedir(client, maria["id"], [{"producto_id": taza["id"], "cantidad": 2}] * 2).status_code == 400
    assert pedir(client, maria["id"], []).status_code == 422
    assert pedir(client, maria["id"], [{"producto_id": taza["id"], "cantidad": 0}]).status_code == 422

    # ningún pedido fallido ha tocado el stock ni el historial
    assert client.get(f"/productos/{taza['id']}/stock").json()["stock"] == 3
    assert client.get(f"/usuarios/{maria['id']}/pedidos").json() == []
    assert client.get("/usuarios/no-existe/pedidos").status_code == 404
    assert client.get(f"/usuarios/{admin['id']}/pedidos").status_code == 400


def test_pedido_atomico(client):
    '''Si una línea falla, no se descuenta stock de las demás.'''
    maria = crear_cliente(client)
    a = crear_producto(client, nombre="A", stock=5)
    b = crear_producto(client, nombre="B", stock=1)
    r = pedir(client, maria["id"], [
        {"producto_id": a["id"], "cantidad": 2},
        {"producto_id": b["id"], "cantidad": 5},
    ])
    assert r.status_code == 400
    assert client.get(f"/productos/{a['id']}/stock").json()["stock"] == 5
