import flet as ft
import mysql.connector

def connect_to_db():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            port=3306,
            user='root',
            password='root',
            database='taller_mecanico',
            ssl_disabled=True
        )
        if connection.is_connected():
            print('Conexión exitosa')
            return connection
    except Exception as ex:
        print('Conexión errónea')
        print(ex)
        return None


class funcCliente:
    def __init__(self, page: ft.Page, main_menu_callback):
        self.page = page
        self.main_menu_callback = main_menu_callback
        self.connection = connect_to_db()
        self.cursor = self.connection.cursor(buffered=True) if self.connection else None
        self.mostrar_clientes()

    def mostrar_clientes(self):
        self.page.clean()
        header = ft.Row(
            controls=[
                ft.Text("Gestión de Clientes", size=20, weight="bold"),
                ft.ElevatedButton(text="Alta", on_click=self.formulario_alta),
                ft.ElevatedButton(text="Consulta", on_click=self.cargar_tabla),
                ft.ElevatedButton(text="<-- Volver", on_click=self.volver_al_menu),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER
        )

        self.data_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Apellido")),
                ft.DataColumn(ft.Text("Nombres")),
                ft.DataColumn(ft.Text("DNI")),
                ft.DataColumn(ft.Text("Dirección")),
                ft.DataColumn(ft.Text("Teléfono")),
                ft.DataColumn(ft.Text("Código Cliente")),
                ft.DataColumn(ft.Text("Acciones")),
            ],
            rows=[]
        )

        self.page.add(header, self.data_table)
        self.cargar_tabla(None)

    def cargar_tabla(self, e):
        if not self.cursor:
            self.page.add(ft.Text("No hay conexión a la base de datos"))
            return

        try:
            self.cursor.execute("""
                SELECT per.apellido, per.nombre, per.dni,
                per.direccion, per.tele_contac, c.cod_cliente
                FROM persona per
                INNER JOIN cliente c ON per.dni = c.dni
                ORDER BY per.apellido
            """)
            datos = self.cursor.fetchall()
        except Exception as ex:
            self.page.add(ft.Text(f"Error al cargar datos: {ex}"))
            return

        self.data_table.rows.clear()

        def crear_eliminar(cliente):
            return lambda e: self.eliminar_cliente(cliente)

        def crear_modificar(cliente):
            return lambda e: self.formulario_modificar(cliente)

        for cliente in datos:
            eliminar_btn = ft.IconButton(icon=ft.Icons.DELETE, tooltip="Eliminar",
                on_click=crear_eliminar(cliente))
            actualizar_btn = ft.IconButton(icon=ft.Icons.EDIT, tooltip="Modificar",
                on_click=crear_modificar(cliente))

            self.data_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(cliente[0])),
                        ft.DataCell(ft.Text(cliente[1])),
                        ft.DataCell(ft.Text(str(cliente[2]))),
                        ft.DataCell(ft.Text(cliente[3])),
                        ft.DataCell(ft.Text(cliente[4])),
                        ft.DataCell(ft.Text(str(cliente[5]))),
                        ft.DataCell(ft.Row([eliminar_btn, actualizar_btn]))
                    ]
                )
            )
        self.page.update()

    def formulario_alta(self, e):
        self.page.clean()
        apellido = ft.TextField(label="Apellido")
        nombre = ft.TextField(label="Nombre")
        dni = ft.TextField(label="DNI")
        direccion = ft.TextField(label="Dirección")
        telefono = ft.TextField(label="Teléfono")
        cod_cliente = ft.TextField(label="Código Cliente")

        def guardar_datos(ev):
            try:
                self.cursor.execute(
                    "INSERT INTO persona (apellido, nombre, dni, direccion, tele_contac) VALUES (%s,%s,%s,%s,%s)",
                    (apellido.value, nombre.value, dni.value, direccion.value, telefono.value)
                )
                self.cursor.execute(
                    "INSERT INTO cliente (cod_cliente, dni) VALUES (%s,%s)",
                    (cod_cliente.value, dni.value)
                )
                self.connection.commit()
                self.mostrar_clientes()
            except Exception as ex:
                self.page.add(ft.Text(f"Error al guardar: {ex}"))
                self.connection.rollback()

        self.page.add(
            ft.Column([
                ft.Text("Alta de Cliente", size=20, weight="bold"),
                apellido, nombre, dni, direccion, telefono, cod_cliente,
                ft.Row([
                    ft.ElevatedButton(text="Guardar", on_click=guardar_datos),
                    ft.ElevatedButton(text="Cancelar", on_click=lambda e: self.mostrar_clientes())
                ])
            ])
        )

    def formulario_modificar(self, cliente):
        self.page.clean()
        apellido = ft.TextField(label="Apellido", value=cliente[0])
        nombre = ft.TextField(label="Nombre", value=cliente[1])
        dni = ft.TextField(label="DNI", value=str(cliente[2]), disabled=True)
        direccion = ft.TextField(label="Dirección", value=cliente[3])
        telefono = ft.TextField(label="Teléfono", value=cliente[4])
        cod_cliente = ft.TextField(label="Código Cliente", value=str(cliente[5]))

        def actualizar_datos(ev):
            try:
                self.cursor.execute(
                    "UPDATE persona SET apellido=%s, nombre=%s, direccion=%s, tele_contac=%s WHERE dni=%s",
                    (apellido.value, nombre.value, direccion.value, telefono.value, dni.value)
                )
                self.cursor.execute(
                    "UPDATE cliente SET cod_cliente=%s WHERE dni=%s",
                    (cod_cliente.value, dni.value)
                )
                self.connection.commit()
                self.mostrar_clientes()
            except Exception as ex:
                self.page.add(ft.Text(f"Error al actualizar: {ex}"))
                self.connection.rollback()

        self.page.add(
            ft.Column([
                ft.Text("Modificar Cliente", size=20, weight="bold"),
                apellido, nombre, dni, direccion, telefono, cod_cliente,
                ft.Row([
                    ft.ElevatedButton(text="Actualizar", on_click=actualizar_datos),
                    ft.ElevatedButton(text="Cancelar", on_click=lambda e: self.mostrar_clientes())
                ])
            ])
        )

    def eliminar_cliente(self, cliente):
        dni = cliente[2]
        try:
            self.cursor.execute("DELETE FROM cliente WHERE dni=%s", (dni,))
            self.cursor.execute("DELETE FROM persona WHERE dni=%s", (dni,))
            self.connection.commit()
            self.cargar_tabla(None)
        except Exception as ex:
            self.page.add(ft.Text(f"Error al eliminar: {ex}"))
            self.connection.rollback()

    def volver_al_menu(self, e):
        self.page.clean()
        self.main_menu_callback(self.page)
