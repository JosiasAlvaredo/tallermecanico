import flet as ft
from cliente import FuncCliente, ClienteDB
from repuestos import FuncRepuesto, RepuestoDB
from empleado import FuncEmpleado, EmpleadoDB
from proveedor import FuncProveedor, ProveedorDB
from ficha_tecnica import FuncFichaTecnica, FichaTecnicaDB
from presupuesto import FuncPresupuesto, PresupuestoDB
from usuario import FuncUsuario, UsuarioDB

class TallerMecanicoApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.estado_usuario = {"nombre": None}
        self.modulos = {
            "Cliente": lambda: FuncCliente(self.page, ClienteDB(), volver_callback=self.menu_principal).mostrar_clientes(),
            "Proveedor": lambda: FuncProveedor(self.page, self.menu_principal),
            "Repuesto": lambda: FuncRepuesto(self.page, self.menu_principal),
            "Empleado": lambda: FuncEmpleado(self.page, self.menu_principal),
            "Ficha Técnica": lambda: FuncFichaTecnica(self.page, self.menu_principal),
            "Presupuesto": lambda: FuncPresupuesto(self.page, self.menu_principal),
        }
        self.mostrar_login()

    def mostrar_login(self):
        self.page.clean()
        FuncUsuario(self.page, self.login_exitoso, self.estado_usuario)

    def login_exitoso(self):
        self.menu_principal()

    def seleccionar_modulo(self, e):
        modulo = e.control.value
        if modulo in self.modulos:
            self.modulos[modulo]()

    def crear_boton(self, icono_path, tooltip, callback):
        icono = ft.Image(src=icono_path, width=28, height=28)
        return ft.IconButton(content=icono, tooltip=tooltip, on_click=callback)

    def menu_principal(self, e=None):
        self.page.clean()
        self.page.bgcolor = ft.Colors.BLUE_50
        self.page.title = "Administración de Taller Mecánico"

        sesion_texto = ft.Text(f"Sesión iniciada: {self.estado_usuario['nombre']}", size=14, weight="bold")

        menu_administracion = ft.Dropdown(
            label="Administración",
            width=220,
            options=[
                ft.dropdown.Option("Ficha Técnica"),
                ft.dropdown.Option("Presupuesto"),
            ],
            on_change=self.seleccionar_modulo,
        )

        menu_herramientas = ft.Dropdown(
            label="Herramientas",
            width=200,
            options=[
                ft.dropdown.Option("Cliente"),
                ft.dropdown.Option("Proveedor"),
                ft.dropdown.Option("Repuesto"),
                ft.dropdown.Option("Empleado"),
            ],
            on_change=self.seleccionar_modulo,
        )

        boton_cliente = self.crear_boton("Cliente.png", "Clientes", lambda e: self.modulos["Cliente"]())
        boton_proveedor = self.crear_boton("proveedor.png", "Proveedores", lambda e: self.modulos["Proveedor"]())
        boton_repuesto = self.crear_boton("alineacion-de-ruedas.png", "Repuestos", lambda e: self.modulos["Repuesto"]())
        boton_empleado = self.crear_boton("recursos-humanos.png", "Empleados", lambda e: self.modulos["Empleado"]())
        boton_ficha_tecnica = self.crear_boton("auto.png", "Ficha Técnica", lambda e: self.modulos["Ficha Técnica"]())
        boton_presupuesto = self.crear_boton("Presupuesto.png", "Presupuesto", lambda e: self.modulos["Presupuesto"]())

        boton_cerrar_sesion = ft.ElevatedButton(
            text="Cerrar sesión",
            icon=ft.Icons.LOGOUT,
            on_click=lambda e: self.cerrar_sesion()
        )

        self.page.add(
            ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            menu_herramientas,
                            menu_administracion,
                            ft.Container(expand=True),
                            sesion_texto,
                            boton_cerrar_sesion,
                        ],
                        alignment="spaceBetween",
                    ),
                    ft.Row(
                        controls=[
                            boton_cliente,
                            boton_proveedor,
                            boton_repuesto,
                            boton_empleado,
                            boton_ficha_tecnica,
                            boton_presupuesto,
                        ],
                        spacing=10,
                    ),
                ],
                spacing=20,
            )
        )

    def cerrar_sesion(self):
        self.estado_usuario["nombre"] = None
        self.mostrar_login()

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
    TallerMecanicoApp(page)

ft.app(target=main, assets_dir="iconos")
