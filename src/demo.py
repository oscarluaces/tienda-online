'''Demo por consola de TiendaService (sin API).

Ejecutar desde la raíz del repositorio:  python src/demo.py

Incorpora el feedback de la Práctica 1:
  - Tres pedidos realizados por tres clientes distintos (María, Carlos y Lucía).
  - Consulta independiente de stock mediante TiendaService.consultar_stock().
'''

from Services.Tienda_service import TiendaService
from Services.excepciones import TiendaError
from models.Producto import ProductoElectronico, ProductoRopa


def mostrar_inventario(tienda: TiendaService) -> None:
    print("--- Inventario de la Tienda ---")
    productos = tienda.listar_productos()
    if not productos:
        print("El inventario está vacío.")
    for producto in productos:
        print(producto)
    print("-------------------------------")


def mostrar_pedidos(tienda: TiendaService, cliente) -> None:
    print(f"--- Histórico de Pedidos de {cliente.nombre} ---")
    pedidos = tienda.listar_pedidos_usuario(cliente.id)
    if not pedidos:
        print("No hay pedidos registrados para este usuario.")
    for pedido in pedidos:
        print(pedido)
        for producto, cantidad in pedido.productos_cantidades.items():
            print(f"    - {producto.nombre} x{cantidad} = {producto.precio * cantidad:.2f}€")


def main():
    tienda = TiendaService()

    print(">>> 1. Registrando usuarios...")
    cliente1 = tienda.registrar_usuario("cliente", "María López", "maria@email.com", "Calle Rosalía de Castro 10")
    cliente2 = tienda.registrar_usuario("cliente", "Carlos Pérez", "carlos@email.com", "Av. Finisterre 45")
    cliente3 = tienda.registrar_usuario("cliente", "Lucía Gómez", "lucia@email.com", "Plaza de Lugo 5")
    admin = tienda.registrar_usuario("administrador", "Admin Principal", "admin@tienda.com")
    print(f"Usuarios registrados: {len(tienda.listar_usuarios())} (Admin ID: {admin.id[:8]}...)")

    print("\n>>> 2. Añadiendo productos al inventario...")
    prod_elec1 = tienda.añadir_producto(ProductoElectronico("Portátil Gaming", 1200.00, 10, 36))
    prod_elec2 = tienda.añadir_producto(ProductoElectronico("Auriculares Inalámbricos", 89.99, 50, 24))
    prod_ropa1 = tienda.añadir_producto(ProductoRopa("Camiseta Algodón", 15.50, 100, "M", "Blanco"))
    prod_ropa2 = tienda.añadir_producto(ProductoRopa("Pantalón Vaquero", 49.99, 30, "L", "Azul Oscuro"))
    prod_ropa3 = tienda.añadir_producto(ProductoRopa("Chaqueta Invierno", 85.00, 15, "M", "Negro"))

    print("\n>>> 3. Inventario inicial")
    mostrar_inventario(tienda)

    print("\n>>> 4. Pedidos de tres clientes distintos")
    print("\n[Pedido 1 - María] 1 Portátil Gaming + 1 Chaqueta Invierno")
    pedido1 = tienda.realizar_pedido(cliente1.id, {prod_elec1.id: 1, prod_ropa3.id: 1})
    print(pedido1)

    print("\n[Pedido 2 - Carlos] 1 Auriculares + 2 Camisetas")
    pedido2 = tienda.realizar_pedido(cliente2.id, {prod_elec2.id: 1, prod_ropa1.id: 2})
    print(pedido2)

    print("\n[Pedido 3 - Lucía] 2 Pantalones Vaqueros + 1 Camiseta")
    pedido3 = tienda.realizar_pedido(cliente3.id, {prod_ropa2.id: 2, prod_ropa1.id: 1})
    print(pedido3)

    print("\n>>> 5. Consulta independiente de stock")
    for producto in (prod_elec1, prod_elec2, prod_ropa1, prod_ropa2, prod_ropa3):
        print(f"Stock de {producto.nombre}: {tienda.consultar_stock(producto.id)} unidades")

    print("\n>>> 6. Casos de error controlados")
    casos = [
        ("Lucía pide 20 portátiles (solo quedan 9)", cliente3.id, {prod_elec1.id: 20}),
        ("El administrador intenta hacer un pedido", admin.id, {prod_ropa1.id: 1}),
        ("Pedido de un producto inexistente", cliente2.id, {"id-inexistente": 1}),
    ]
    for descripcion, id_usuario, productos in casos:
        try:
            tienda.realizar_pedido(id_usuario, productos)
        except TiendaError as e:
            print(f"{descripcion} -> rechazado: {e}")
    print(f"Stock de Portátil Gaming tras los errores: {tienda.consultar_stock(prod_elec1.id)} (sin cambios)")

    print("\n>>> 7. Inventario tras los pedidos")
    mostrar_inventario(tienda)

    print("\n>>> 8. Histórico de pedidos de cada cliente")
    for cliente in (cliente1, cliente2, cliente3):
        mostrar_pedidos(tienda, cliente)
        print()


if __name__ == "__main__":
    main()
