import flet as ft
import mysql.connector

#Conexion DB y CRUD
class RepuestoDB:
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
        except mysql.connector.Error as err:
            print(f"Error al conectar DB: {err}")
            self.connection = None
            self.cursor = None

    def obtener_todos(self):
        self.cursor.execute("SELECT cod_repuesto, descripcion, pcio_unit FROM repuestos ORDER BY cod_repuesto")
        return self.cursor.fetchall()

    def insertar(self, cod, desc, precio):
        self.cursor.execute(
            "INSERT INTO repuestos (cod_repuesto, descripcion, pcio_unit) VALUES (%s,%s,%s)",
            (cod, desc, precio)
        )
        self.connection.commit()

    def actualizar(self, cod, desc, precio):
        self.cursor.execute(
            "UPDATE repuestos SET descripcion=%s, pcio_unit=%s WHERE cod_repuesto=%s",
            (desc, precio, cod)
        )
        self.connection.commit()

    def eliminar(self, cod):
        self.cursor.execute("DELETE FROM repuestos WHERE cod_repuesto=%s", (cod,))
        self.connection.commit()

    def cerrar(self):
        if self.cursor:
            self.cursor.close()
        if self.connection and self.connection.is_connected():
            self.connection.close()


# ---------------------- Interfaz Flet ----------------------
class FuncRepuesto(RepuestoDB):
    def __init__(self, page: ft.Page, main_menu_callback):
        super().__init__()  # Uso de POO
        self.page = page
        self.main_menu_callback = main_menu_callback
        self.mostrar_repuestos()

    def mostrar_repuestos(self):
        self.page.clean()
        header = ft.Row(
            controls=[
                ft.Text("Gestión de Repuestos", size=20, weight="bold"),
                ft.ElevatedButton(text="Alta", on_click=self.formulario_alta),
                ft.ElevatedButton(text="Consulta", on_click=self.cargar_tabla),
                ft.ElevatedButton(text="<-- Volver", on_click=self.volver_al_menu),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER
        )

        self.data_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Código Repuesto")),
                ft.DataColumn(ft.Text("Descripción")),
                ft.DataColumn(ft.Text("Precio Unitario")),
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
            datos = self.obtener_todos()
        except Exception as ex:
            self.page.add(ft.Text(f"Error al cargar datos: {ex}"))
            return

        self.data_table.rows.clear()

        def crear_eliminar(repuesto):
            return lambda e: self.eliminar_repuesto(repuesto)

        def crear_modificar(repuesto):
            return lambda e: self.formulario_modificar(repuesto)

        for repuesto in datos:
            eliminar_btn = ft.IconButton(icon=ft.Icons.DELETE, tooltip="Eliminar",
                                        on_click=crear_eliminar(repuesto))
            actualizar_btn = ft.IconButton(icon=ft.Icons.EDIT, tooltip="Modificar",
                                        on_click=crear_modificar(repuesto))

            self.data_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(repuesto[0])),
                        ft.DataCell(ft.Text(repuesto[1])),
                        ft.DataCell(ft.Text(str(repuesto[2]))),
                        ft.DataCell(ft.Row([eliminar_btn, actualizar_btn]))
                    ]
                )
            )
        self.page.update()

    def formulario_alta(self, e):
        self.page.clean()
        cod_repuesto = ft.TextField(label="Código Repuesto")
        descripcion = ft.TextField(label="Descripción")
        precio = ft.TextField(label="Precio Unitario")

        def guardar_datos(ev):
            try:
                self.insertar(cod_repuesto.value, descripcion.value, precio.value)
                self.mostrar_repuestos()
            except Exception as ex:
                self.page.add(ft.Text(f"Error al guardar: {ex}"))

        self.page.add(
            ft.Column([
                ft.Text("Alta de Repuesto", size=20, weight="bold"),
                cod_repuesto, descripcion, precio,
                ft.Row([
                    ft.ElevatedButton(text="Guardar", on_click=guardar_datos),
                    ft.ElevatedButton(text="Cancelar", on_click=lambda e: self.mostrar_repuestos())
                ])
            ])
        )

    def formulario_modificar(self, repuesto):
        self.page.clean()
        cod_repuesto = ft.TextField(label="Código Repuesto", value=repuesto[0], disabled=True)
        descripcion = ft.TextField(label="Descripción", value=repuesto[1])
        precio = ft.TextField(label="Precio Unitario", value=str(repuesto[2]))

        def actualizar_datos(ev):
            try:
                self.actualizar(cod_repuesto.value, descripcion.value, precio.value)
                self.mostrar_repuestos()
            except Exception as ex:
                self.page.add(ft.Text(f"Error al actualizar: {ex}"))

        self.page.add(
            ft.Column([
                ft.Text("Modificar Repuesto", size=20, weight="bold"),
                cod_repuesto, descripcion, precio,
                ft.Row([
                    ft.ElevatedButton(text="Actualizar", on_click=actualizar_datos),
                    ft.ElevatedButton(text="Cancelar", on_click=lambda e: self.mostrar_repuestos())
                ])
            ])
        )

    def eliminar_repuesto(self, repuesto):
        cod_repuesto = repuesto[0]
        try:
            self.eliminar(cod_repuesto)
            self.cargar_tabla(None)
        except Exception as ex:
            self.page.add(ft.Text(f"Error al eliminar: {ex}"))

    def volver_al_menu(self, e):
        self.page.clean()
        self.main_menu_callback()
