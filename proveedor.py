import flet as ft
import mysql.connector

#Conexion DB y CRUD
class ProveedorDB:
    def __init__(self):
        try:
            self.connection = mysql.connector.connect(
                host="localhost",
                port=3306,
                user="root",
                password="root",
                database="taller_mecanico",
                ssl_disabled=True
            )
            self.cursor = self.connection.cursor(buffered=True)
        except Exception as ex:
            print("Error de conexión:", ex)
            self.connection = None
            self.cursor = None

    def obtener_todos(self):
        self.cursor.execute("SELECT cod_proveedor, nombre_empresa, direccion, telefono, email FROM proveedor ORDER BY nombre_empresa")
        return self.cursor.fetchall()

    def insertar(self, cod, nombre, direccion, telefono, email):
        self.cursor.execute(
            "INSERT INTO proveedor (cod_proveedor, nombre_empresa, direccion, telefono, email) VALUES (%s,%s,%s,%s,%s)",
            (cod, nombre, direccion, telefono, email)
        )
        self.connection.commit()

    def actualizar(self, cod, nombre, direccion, telefono, email):
        self.cursor.execute(
            "UPDATE proveedor SET nombre_empresa=%s, direccion=%s, telefono=%s, email=%s WHERE cod_proveedor=%s",
            (nombre, direccion, telefono, email, cod)
        )
        self.connection.commit()

    def eliminar(self, cod):
        self.cursor.execute("DELETE FROM proveedor WHERE cod_proveedor=%s", (cod,))
        self.connection.commit()

#UI
class FuncProveedor(ProveedorDB):
    def __init__(self, page: ft.Page, main_menu_callback):
        super().__init__()
        self.page = page
        self.main_menu_callback = main_menu_callback
        self.mostrar_proveedores()

    def mostrar_proveedores(self):
        self.page.clean()
        header = ft.Row([
            ft.Text("Gestión de Proveedores", size=20, weight="bold"),
            ft.ElevatedButton("Alta", on_click=self.alta_proveedor),
            ft.ElevatedButton("Consulta", on_click=self.cargar_tabla),
            ft.ElevatedButton("<-- Volver", on_click=self.volver_al_menu)
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        self.data_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Código")),
                ft.DataColumn(ft.Text("Nombre Empresa")),
                ft.DataColumn(ft.Text("Dirección")),
                ft.DataColumn(ft.Text("Teléfono")),
                ft.DataColumn(ft.Text("Email")),
                ft.DataColumn(ft.Text("Acciones"))
            ],
            rows=[]
        )

        self.page.add(ft.Column([header, self.data_table]))
        self.cargar_tabla(None)

    def cargar_tabla(self, e):
        if not self.cursor:
            self.page.add(ft.Text("No hay conexión a la base de datos"))
            return

        proveedores = self.obtener_todos()
        self.data_table.rows.clear()

        def crear_eliminar(p):
            return lambda e: self.eliminar_proveedor(p[0])

        def crear_modificar(p):
            return lambda e: self.formulario_modificar(p)

        for p in proveedores:
            eliminar_btn = ft.IconButton(icon=ft.Icons.DELETE, tooltip="Eliminar", on_click=crear_eliminar(p))
            modificar_btn = ft.IconButton(icon=ft.Icons.EDIT, tooltip="Modificar", on_click=crear_modificar(p))
            self.data_table.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(str(p[0]))),
                    ft.DataCell(ft.Text(p[1])),
                    ft.DataCell(ft.Text(p[2])),
                    ft.DataCell(ft.Text(p[3])),
                    ft.DataCell(ft.Text(p[4])),
                    ft.DataCell(ft.Row([eliminar_btn, modificar_btn]))
                ])
            )
        self.page.update()

    def alta_proveedor(self, e):
        self.page.clean()
        cod = ft.TextField(label="Código Proveedor", width=300)
        nombre = ft.TextField(label="Nombre Empresa", width=300)
        direccion = ft.TextField(label="Dirección", width=300)
        telefono = ft.TextField(label="Teléfono", width=300)
        email = ft.TextField(label="Email", width=300)

        def guardar(ev):
            self.insertar(cod.value, nombre.value, direccion.value, telefono.value, email.value)
            self.mostrar_proveedores()

        btns = ft.Row([
            ft.ElevatedButton("Guardar", on_click=guardar),
            ft.ElevatedButton("Cancelar", on_click=lambda e: self.mostrar_proveedores())
        ], spacing=10)

        self.page.add(ft.Column([ft.Text("Alta de Proveedor", size=20, weight="bold"), cod, nombre, direccion, telefono, email, btns]))
        self.page.update()

    def formulario_modificar(self, p):
        self.page.clean()
        cod = ft.TextField(label="Código Proveedor", value=str(p[0]), width=300, disabled=True)
        nombre = ft.TextField(label="Nombre Empresa", value=p[1], width=300)
        direccion = ft.TextField(label="Dirección", value=p[2], width=300)
        telefono = ft.TextField(label="Teléfono", value=p[3], width=300)
        email = ft.TextField(label="Email", value=p[4], width=300)

        def guardar(ev):
            self.actualizar(cod.value, nombre.value, direccion.value, telefono.value, email.value)
            self.mostrar_proveedores()

        btns = ft.Row([
            ft.ElevatedButton("Guardar Cambios", on_click=guardar),
            ft.ElevatedButton("Cancelar", on_click=lambda e: self.mostrar_proveedores())
        ], spacing=10)

        self.page.add(ft.Column([ft.Text("Editar Proveedor", size=20, weight="bold"), cod, nombre, direccion, telefono, email, btns]))
        self.page.update()

    def eliminar_proveedor(self, cod):
        self.eliminar(cod)
        self.cargar_tabla(None)

    def volver_al_menu(self, e):
        self.page.clean()
        self.main_menu_callback()
