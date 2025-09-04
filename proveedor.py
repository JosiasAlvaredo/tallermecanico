import flet as ft
import mysql.connector

def connect_to_db():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            port=3306,
            user="root",
            password="root",
            database="taller_mecanico",
            ssl_disabled=True,
        )
        if connection.is_connected():
            return connection
    except Exception as ex:
        print("Error de conexión:", ex)
        return None

class funcProveedor:
    def __init__(self, page: ft.Page, main_menu_callback):
        self.page = page
        self.main_menu_callback = main_menu_callback
        self.connection = connect_to_db()
        self.cursor = self.connection.cursor() if self.connection else None
        self.mostrar_proveedores()

    def mostrar_proveedores(self):
        self.page.clean()
        header = ft.Row([
            ft.Text("Gestión de Proveedores", size=20, weight="bold"),
            ft.ElevatedButton("Alta", on_click=self.alta_proveedor),
            ft.ElevatedButton("Consulta", on_click=lambda e: self.cargar_tabla()),
            ft.ElevatedButton("<-- Volver", on_click=self.volver_al_menu)
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        self.data_table = self.create_proveedor_table()
        self.page.add(ft.Column([header, self.data_table]))
        self.page.update()

    def create_proveedor_table(self):
        if not self.cursor:
            return ft.Text("No hay conexión a la base de datos")
        self.cursor.execute("SELECT cod_proveedor, nombre_empresa, direccion, telefono, email FROM proveedor ORDER BY nombre_empresa")
        self.all_data = self.cursor.fetchall()
        return ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Código")),
                ft.DataColumn(ft.Text("Nombre Empresa")),
                ft.DataColumn(ft.Text("Dirección")),
                ft.DataColumn(ft.Text("Teléfono")),
                ft.DataColumn(ft.Text("Email")),
                ft.DataColumn(ft.Text("Acciones")),
            ],
            rows=self.get_rows(self.all_data)
        )

    def get_rows(self, proveedores):
        rows = []
        for p in proveedores:
            eliminar_btn = ft.IconButton(icon=ft.Icons.DELETE, on_click=lambda e, prov=p: self.eliminar_proveedor(prov))
            actualizar_btn = ft.IconButton(icon=ft.Icons.EDIT, on_click=lambda e, prov=p: self.actualizar_proveedor(prov))
            rows.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text(str(p[0]))),
                ft.DataCell(ft.Text(p[1])),
                ft.DataCell(ft.Text(p[2])),
                ft.DataCell(ft.Text(p[3])),
                ft.DataCell(ft.Text(p[4])),
                ft.DataCell(ft.Row([eliminar_btn, actualizar_btn]))
            ]))
        return rows

    def alta_proveedor(self, e):
        self.page.clean()
        self.cod_proveedor = ft.TextField(label="Código Proveedor", width=300)
        self.nombre_empresa = ft.TextField(label="Nombre Empresa", width=300)
        self.direccion = ft.TextField(label="Dirección", width=300)
        self.telefono = ft.TextField(label="Teléfono", width=300)
        self.email = ft.TextField(label="Email", width=300)

        btns = ft.Row([
            ft.ElevatedButton("Guardar", on_click=self.guardar_proveedor),
            ft.ElevatedButton("Cancelar", on_click=lambda e: self.mostrar_proveedores())
        ], spacing=10)

        self.page.add(ft.Column([
            ft.Text("Alta de Proveedor", size=20, weight="bold"),
            self.cod_proveedor, self.nombre_empresa, self.direccion, self.telefono, self.email, btns
        ]))
        self.page.update()

    def guardar_proveedor(self, e):
        try:
            self.cursor.execute(
                "INSERT INTO proveedor (cod_proveedor, nombre_empresa, direccion, telefono, email) VALUES (%s,%s,%s,%s,%s)",
                (self.cod_proveedor.value, self.nombre_empresa.value, self.direccion.value, self.telefono.value, self.email.value)
            )
            self.connection.commit()
            self.mostrar_proveedores()
        except Exception as ex:
            print("Error al guardar:", ex)

    def eliminar_proveedor(self, proveedor):
        try:
            self.cursor.execute("DELETE FROM proveedor WHERE cod_proveedor=%s", (proveedor[0],))
            self.connection.commit()
            self.cargar_tabla()
        except Exception as ex:
            print("Error al eliminar:", ex)

    def actualizar_proveedor(self, proveedor):
        self.page.clean()
        self.cod_proveedor = ft.TextField(label="Código Proveedor", value=str(proveedor[0]), width=300, disabled=True)
        self.nombre_empresa = ft.TextField(label="Nombre Empresa", value=proveedor[1], width=300)
        self.direccion = ft.TextField(label="Dirección", value=proveedor[2], width=300)
        self.telefono = ft.TextField(label="Teléfono", value=proveedor[3], width=300)
        self.email = ft.TextField(label="Email", value=proveedor[4], width=300)

        btns = ft.Row([
            ft.ElevatedButton("Guardar Cambios", on_click=self.guardar_cambios_proveedor),
            ft.ElevatedButton("Cancelar", on_click=lambda e: self.mostrar_proveedores())
        ], spacing=10)

        self.page.add(ft.Column([
            ft.Text("Editar Proveedor", size=20, weight="bold"),
            self.cod_proveedor, self.nombre_empresa, self.direccion, self.telefono, self.email, btns
        ]))
        self.page.update()

    def guardar_cambios_proveedor(self, e):
        try:
            self.cursor.execute(
                "UPDATE proveedor SET nombre_empresa=%s, direccion=%s, telefono=%s, email=%s WHERE cod_proveedor=%s",
                (self.nombre_empresa.value, self.direccion.value, self.telefono.value, self.email.value, self.cod_proveedor.value)
            )
            self.connection.commit()
            self.mostrar_proveedores()
        except Exception as ex:
            print("Error al actualizar:", ex)

    def cargar_tabla(self):
        self.data_table.rows = self.get_rows(self.all_data)
        self.page.update()

    def volver_al_menu(self, e):
        self.page.clean()
        self.main_menu_callback(self.page)
