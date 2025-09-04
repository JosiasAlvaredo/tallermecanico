import flet as ft
import mysql.connector
from usuario import funcUsuario
from cliente import funcCliente
from repuestos import funcRepuesto
from empleado import funcEmpleado
from proveedor import funcProveedor
from ficha_tecnica import funcFichaTecnica
from presupuesto import funcPresupuesto


def connect_to_db():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            port="3306",
            user="root",
            password="root",
            database="taller_mecanico",
            ssl_disabled=True,
        )
        if connection.is_connected():
            print("Conexión exitosa")
            return connection
    except Exception as ex:
        print("Conexión errónea")
        print(ex)
        return None


connection = connect_to_db()


def cliente(e, page: ft.Page):
    funcCliente(page, menu_principal)


def usuario(e, page: ft.Page):
    funcUsuario(page, menu_principal)


def repuesto(e, page: ft.Page):
    funcRepuesto(page, menu_principal)


def proveedor(e, page: ft.Page):
    funcProveedor(page, menu_principal)


def empleado(e, page: ft.Page):
    funcEmpleado(page, menu_principal)


def ficha_tecnica(e, page: ft.Page):
    funcFichaTecnica(page, menu_principal)

def presupuesto(e, page: ft.Page):
    funcPresupuesto(page, menu_principal)





def seleccionar_modulo(e, page):
    if e.control.value == "Cliente":
        cliente(e, page)
    elif e.control.value == "Proveedor":
        proveedor(e, page)
    elif e.control.value == "Repuesto":
        repuesto(e, page)
    elif e.control.value == "Empleado":
        empleado(e, page)
    elif e.control.value == "Usuario":
        usuario(e, page)
    elif e.control.value == "Ficha Técnica":
        ficha_tecnica(e, page)
    elif e.control.value == "Presupuesto":
        presupuesto(e, page)



def menu_principal(page: ft.Page):
    page.clean()
    page.bgcolor = ft.Colors.BLUE_50
    page.title = "Administración de Taller Mecánico"

    cliente_icono = ft.Image(src="Cliente.png", width=28, height=28)
    proveedor_icono = ft.Image(src="proveedor.png", width=28, height=28)
    repuesto_icono = ft.Image(src="alineacion-de-ruedas.png", width=28, height=28)
    empleado_icono = ft.Image(src="recursos-humanos.png", width=28, height=28)
    usuario_icono = ft.Image(src="usuario.png", width=28, height=28)
    ficha_tecnica_icono = ft.Image(src="auto.png", width=28, height=28)
    presupuesto_icono = ft.Image(src="Presupuesto.png", width=28, height=28)

    menu_herramientas = ft.Dropdown(
        label="Módulos",
        options=[
            ft.dropdown.Option("Cliente"),
            ft.dropdown.Option("Proveedor"),
            ft.dropdown.Option("Repuesto"),
            ft.dropdown.Option("Empleado"),
            ft.dropdown.Option("Usuario"),
            ft.dropdown.Option("Ficha Técnica"),
            ft.dropdown.Option("Presupuesto")
        ],
        on_change=lambda e: seleccionar_modulo(e, page),
    )

    boton_cliente = ft.IconButton(
        content=cliente_icono, tooltip="Clientes", on_click=lambda e: cliente(e, page)
    )
    boton_proveedor = ft.IconButton(
        content=proveedor_icono, tooltip="Proveedores", on_click=lambda e: proveedor(e, page)
    )
    boton_repuesto = ft.IconButton(
        content=repuesto_icono, tooltip="Repuestos", on_click=lambda e: repuesto(e, page)
    )
    boton_empleado = ft.IconButton(
        content=empleado_icono, tooltip="Empleados", on_click=lambda e: empleado(e, page)
    )
    boton_ficha_tecnica = ft.IconButton(
        content=ficha_tecnica_icono, tooltip="Ficha Técnica", on_click=lambda e: ficha_tecnica(e, page)
    )
    boton_usuario = ft.IconButton(
        content=usuario_icono, tooltip="Usuarios", on_click=lambda e: usuario(e, page)
    )
    boton_presupuesto = ft.IconButton(
        content=presupuesto_icono, tooltip="Presupuesto", on_click=lambda e: presupuesto(e, page)
    )

    page.add(
        ft.Row(
            controls=[menu_herramientas],
            spacing=10,
        ),
        ft.Row(
            controls=[
                boton_cliente,
                boton_proveedor,
                boton_repuesto,
                boton_empleado,
                boton_ficha_tecnica,
                boton_usuario,
                boton_presupuesto
            ],
            spacing=10,
        ),
    )


def main(page: ft.Page):
    page.window.maximized = True

    page.theme = ft.Theme(
        text_theme=ft.TextTheme(
            body_small=ft.TextStyle(color=ft.Colors.BLACK),
            body_medium=ft.TextStyle(color=ft.Colors.BLACK),
            body_large=ft.TextStyle(color=ft.Colors.BLACK),
            title_small=ft.TextStyle(color=ft.Colors.BLACK),
            title_medium=ft.TextStyle(color=ft.Colors.BLACK),
            title_large=ft.TextStyle(color=ft.Colors.BLACK),
        )
    )

    menu_principal(page)


ft.app(target=main, assets_dir="iconos")
