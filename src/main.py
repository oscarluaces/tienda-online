from Services.Tienda_service import TiendaService
from models.Producto import ProductoElectronico, ProductoRopa

def main():
    # Inicializar el servicio de la tienda
    tienda = TiendaService()

    print(">>> 1. Registrando usuarios...")
    # Registrar 3 clientes y 1 administrador
    cliente1 = tienda.registrar_usuario("cliente", "María López", "maria@email.com", "Calle Rosalía de Castro 10")
    cliente2 = tienda.registrar_usuario("cliente", "Carlos Pérez", "carlos@email.com", "Av. Finisterre 45")
    cliente3 = tienda.registrar_usuario("cliente", "Lucía Gómez", "lucia@email.com", "Plaza de Lugo 5")
    admin = tienda.registrar_usuario("administrador", "Admin Principal", "admin@tienda.com")
    
    print(f"Usuarios registrados correctamente. (Admin ID: {admin.id[:8]}...)")

    print("\n>>> 2. Añadiendo productos al inventario...")
    # Crear 5 productos de diferentes categorías
    prod_elec1 = ProductoElectronico("Portátil Gaming", 1200.00, 10, 36)
    prod_elec2 = ProductoElectronico("Auriculares Inalámbricos", 89.99, 50, 24)
    prod_ropa1 = ProductoRopa("Camiseta Algodón", 15.50, 100, "M", "Blanco")
    prod_ropa2 = ProductoRopa("Pantalón Vaquero", 49.99, 30, "L", "Azul Oscuro")
    prod_ropa3 = ProductoRopa("Chaqueta Invierno", 85.00, 15, "M", "Negro")

    # Añadirlos al servicio
    tienda.añadir_producto(prod_elec1)
    tienda.añadir_producto(prod_elec2)
    tienda.añadir_producto(prod_ropa1)
    tienda.añadir_producto(prod_ropa2)
    tienda.añadir_producto(prod_ropa3)

    print("\n>>> 3. Listando inventario inicial...")
    tienda.listar_productos()

    print("\n>>> 4. Simulando realización de pedidos...")
    # Pedido 1: María compra un portátil y una chaqueta
    print("\n[Simulando Pedido 1 - María]")
    pedido1 = tienda.realizar_pedido(cliente1.id, {prod_elec1.id: 1, prod_ropa3.id: 1})
    if pedido1:
        print("¡Pedido realizado con éxito!")
        print(pedido1)

    # Pedido 2: Carlos compra unos auriculares y dos camisetas
    print("\n[Simulando Pedido 2 - Carlos]")
    pedido2 = tienda.realizar_pedido(cliente2.id, {prod_elec2.id: 1, prod_ropa1.id: 2})
    if pedido2:
        print("¡Pedido realizado con éxito!")
        print(pedido2)

    # Pedido 3: María hace otro pedido (unos auriculares extra)
    print("\n[Simulando Pedido 3 - María de nuevo]")
    pedido3 = tienda.realizar_pedido(cliente1.id, {prod_elec2.id: 2})
    if pedido3:
        print("¡Pedido realizado con éxito!")
        print(pedido3)

    print("\n>>> 5. Listando inventario tras los pedidos (Comprobación de stock actualizado)...")
    tienda.listar_productos()

    print("\n>>> 6. Comprobando histórico de pedidos de María...")
    tienda.listar_pedidos_usuario(cliente1.id)

if __name__ == "__main__":
    main()
