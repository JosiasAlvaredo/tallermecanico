import flet as ft
import mysql.connector

#Conexion DB y CRUD
class ClienteDB:
    def __init__(self):
        self.connection = self.conectar()
        self.cursor = self.connection.cursor(buffered=True) if self.connection else None

    def conectar(self):
        try:
            conn = mysql.connector.connect(
                host='localhost',
                port=3306,
                user='root',
                password='root',
                database='taller_mecanico',
                ssl_disabled=True
            )
            if conn.is_connected():
                print("Conexión exitosa a la DB")
                return conn
        except Exception as e:
            print("Error al conectar DB:", e)
            return None

    def cerrar(self):
        if self.cursor:
            self.cursor.close()
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("Conexión cerrada")

    def listar(self):
        self.cursor.execute("""
            SELECT per.apellido, per.nombre, per.dni, per.direccion, per.tele_contac, c.cod_cliente
            FROM persona per
            INNER JOIN cliente c ON per.dni = c.dni
            ORDER BY per.apellido
        """)
        return self.cursor.fetchall()

    def insertar(self, apellido, nombre, dni, direccion, telefono, cod_cliente):
        self.cursor.execute(
            "INSERT INTO persona (apellido, nombre, dni, direccion, tele_contac) VALUES (%s,%s,%s,%s,%s)",
            (apellido, nombre, dni, direccion, telefono)
        )
        self.cursor.execute(
            "INSERT INTO cliente (cod_cliente, dni) VALUES (%s,%s)",
            (cod_cliente, dni)
        )
        self.connection.commit()

    def actualizar(self, apellido, nombre, direccion, telefono, cod_cliente, dni):
        self.cursor.execute(
            "UPDATE persona SET apellido=%s, nombre=%s, direccion=%s, tele_contac=%s WHERE dni=%s",
            (apellido, nombre, direccion, telefono, dni)
        )
        self.cursor.execute(
            "UPDATE cliente SET cod_cliente=%s WHERE dni=%s",
            (cod_cliente, dni)
        )
        self.connection.commit()

    def eliminar(self, dni):
        self.cursor.execute("DELETE FROM cliente WHERE dni=%s", (dni,))
        self.cursor.execute("DELETE FROM persona WHERE dni=%s", (dni,))
        self.connection.commit()


#UI
class FuncCliente:
    def __init__(self, page: ft.Page, db: ClienteDB, volver_callback):
        self.page = page
        self.db = db
        self.volver_callback = volver_callback
        self.mostrar_clientes()

    def mostrar_clientes(self, e=None):
        self.page.clean()

        header = ft.Row(
            controls=[
                ft.Text("Gestión de Clientes", size=20, weight="bold"),
                ft.ElevatedButton(text="Alta", on_click=self.formulario_alta),
                ft.ElevatedButton(text="Consulta", on_click=self.cargar_tabla),
                ft.ElevatedButton(text="<-- Volver", on_click=self.volver_al_menu),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )

        self.data_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Apellido")),
                ft.DataColumn(ft.Text("Nombre")),
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
        if not self.db.cursor:
            self.page.add(ft.Text("No hay conexión a la DB"))
            return

        try:
            datos = self.db.listar()
        except Exception as ex:
            self.page.add(ft.Text(f"Error al cargar datos: {ex}"))
            return

        self.data_table.rows.clear()

        for cliente in datos:
            eliminar_btn = ft.IconButton(
                icon=ft.Icons.DELETE,
                tooltip="Eliminar",
                on_click=lambda e, c=cliente: self.eliminar_cliente(c)
            )
            modificar_btn = ft.IconButton(
                icon=ft.Icons.EDIT,
                tooltip="Modificar",
                on_click=lambda e, c=cliente: self.formulario_modificar(c)
            )

            self.data_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(cliente[0])),
                        ft.DataCell(ft.Text(cliente[1])),
                        ft.DataCell(ft.Text(str(cliente[2]))),
                        ft.DataCell(ft.Text(cliente[3])),
                        ft.DataCell(ft.Text(cliente[4])),
                        ft.DataCell(ft.Text(str(cliente[5]))),
                        ft.DataCell(ft.Row([eliminar_btn, modificar_btn]))
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

        def guardar(ev):
            if not apellido.value or not nombre.value or not dni.value:
                self.page.add(ft.Text("Apellido, Nombre y DNI son obligatorios"))
                return
            try:
                self.db.insertar(apellido.value, nombre.value, dni.value, direccion.value, telefono.value, cod_cliente.value)
                self.mostrar_clientes()
            except Exception as ex:
                self.page.add(ft.Text(f"Error al guardar: {ex}"))
                self.db.connection.rollback()

        self.page.add(
            ft.Column([
                ft.Text("Alta de Cliente", size=20, weight="bold"),
                apellido, nombre, dni, direccion, telefono, cod_cliente,
                ft.Row([
                    ft.ElevatedButton(text="Guardar", on_click=guardar),
                    ft.ElevatedButton(text="Cancelar", on_click=self.mostrar_clientes)
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

        def actualizar(ev):
            try:
                self.db.actualizar(apellido.value, nombre.value, direccion.value, telefono.value, cod_cliente.value, dni.value)
                self.mostrar_clientes()
            except Exception as ex:
                self.page.add(ft.Text(f"Error al actualizar: {ex}"))
                self.db.connection.rollback()

        self.page.add(
            ft.Column([
                ft.Text("Modificar Cliente", size=20, weight="bold"),
                apellido, nombre, dni, direccion, telefono, cod_cliente,
                ft.Row([
                    ft.ElevatedButton(text="Actualizar", on_click=actualizar),
                    ft.ElevatedButton(text="Cancelar", on_click=self.mostrar_clientes)
                ])
            ])
        )

    def eliminar_cliente(self, cliente):
        try:
            self.db.eliminar(cliente[2])
            self.cargar_tabla(None)
        except Exception as ex:
            self.page.add(ft.Text(f"Error al eliminar: {ex}"))
            self.db.connection.rollback()

    def volver_al_menu(self, e):
        self.db.cerrar()
        self.page.clean()
        self.volver_callback()
