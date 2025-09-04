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
            print("Conexión exitosa")
            return connection
    except Exception as ex:
        print("Conexión errónea:", ex)
        return None


class funcFichaTecnica:
    def __init__(self, page: ft.Page, main_menu_callback):
        self.page = page
        self.main_menu_callback = main_menu_callback
        self.connection = connect_to_db()
        self.cursor = self.connection.cursor(buffered=True) if self.connection else None
        self.mostrar_fichas()

    def mostrar_fichas(self):
        self.page.clean()

        header = ft.Row(
            controls=[
                ft.Text("Gestión de Fichas Técnicas", size=20, weight="bold"),
                ft.ElevatedButton(text="Alta", on_click=self.formulario_alta),
                ft.ElevatedButton(text="Consulta", on_click=self.cargar_tabla),
                ft.ElevatedButton(text="<-- Volver", on_click=self.volver_al_menu),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        self.data_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Nro Ficha")),
                ft.DataColumn(ft.Text("Código Cliente")),
                ft.DataColumn(ft.Text("Vehículo")),
                ft.DataColumn(ft.Text("Subtotal")),
                ft.DataColumn(ft.Text("Mano de Obra")),
                ft.DataColumn(ft.Text("Total General")),
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
                SELECT nro_ficha, cod_cliente, vehiculo, subtotal, mano_obra, total_general
                FROM ficha_tecnica
                ORDER BY nro_ficha
            """)
            datos = self.cursor.fetchall()
        except Exception as ex:
            self.page.add(ft.Text(f"Error al cargar datos: {ex}"))
            return

        self.data_table.rows.clear()

        def crear_eliminar(ficha):
            return lambda e: self.eliminar_ficha(ficha)

        def crear_modificar(ficha):
            return lambda e: self.formulario_modificar(ficha)

        for ficha in datos:
            eliminar_btn = ft.IconButton(icon=ft.Icons.DELETE, tooltip="Eliminar",
                                         on_click=crear_eliminar(ficha))
            actualizar_btn = ft.IconButton(icon=ft.Icons.EDIT, tooltip="Modificar",
                                           on_click=crear_modificar(ficha))

            self.data_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(ficha[0]))),
                        ft.DataCell(ft.Text(str(ficha[1]))),
                        ft.DataCell(ft.Text(ficha[2])),
                        ft.DataCell(ft.Text(str(ficha[3]))),
                        ft.DataCell(ft.Text(str(ficha[4]))),
                        ft.DataCell(ft.Text(str(ficha[5]))),
                        ft.DataCell(ft.Row([eliminar_btn, actualizar_btn]))
                    ]
                )
            )
        self.page.update()

    def formulario_alta(self, e):
        self.page.clean()
        nro_ficha = ft.TextField(label="Nro Ficha")
        cod_cliente = ft.TextField(label="Código Cliente")
        vehiculo = ft.TextField(label="Vehículo")
        subtotal = ft.TextField(label="Subtotal")
        mano_obra = ft.TextField(label="Mano de Obra")
        total_general = ft.TextField(label="Total General")

        def guardar_datos(ev):
            try:
                self.cursor.execute(
                    "INSERT INTO ficha_tecnica (nro_ficha, cod_cliente, vehiculo, subtotal, mano_obra, total_general) VALUES (%s,%s,%s,%s,%s,%s)",
                    (nro_ficha.value, cod_cliente.value, vehiculo.value, subtotal.value, mano_obra.value, total_general.value)
                )
                self.connection.commit()
                self.mostrar_fichas()
            except Exception as ex:
                self.page.add(ft.Text(f"Error al guardar: {ex}"))
                self.connection.rollback()

        self.page.add(
            ft.Column([
                ft.Text("Alta de Ficha Técnica", size=20, weight="bold"),
                nro_ficha, cod_cliente, vehiculo, subtotal, mano_obra, total_general,
                ft.Row([
                    ft.ElevatedButton(text="Guardar", on_click=guardar_datos),
                    ft.ElevatedButton(text="Cancelar", on_click=lambda e: self.mostrar_fichas())
                ])
            ])
        )

    def formulario_modificar(self, ficha):
        self.page.clean()
        nro_ficha = ft.TextField(label="Nro Ficha", value=str(ficha[0]), disabled=True)
        cod_cliente = ft.TextField(label="Código Cliente", value=str(ficha[1]))
        vehiculo = ft.TextField(label="Vehículo", value=ficha[2])
        subtotal = ft.TextField(label="Subtotal", value=str(ficha[3]))
        mano_obra = ft.TextField(label="Mano de Obra", value=str(ficha[4]))
        total_general = ft.TextField(label="Total General", value=str(ficha[5]))

        def actualizar_datos(ev):
            try:
                self.cursor.execute(
                    "UPDATE ficha_tecnica SET cod_cliente=%s, vehiculo=%s, subtotal=%s, mano_obra=%s, total_general=%s WHERE nro_ficha=%s",
                    (cod_cliente.value, vehiculo.value, subtotal.value, mano_obra.value, total_general.value, nro_ficha.value)
                )
                self.connection.commit()
                self.mostrar_fichas()
            except Exception as ex:
                self.page.add(ft.Text(f"Error al actualizar: {ex}"))
                self.connection.rollback()

        self.page.add(
            ft.Column([
                ft.Text("Modificar Ficha Técnica", size=20, weight="bold"),
                nro_ficha, cod_cliente, vehiculo, subtotal, mano_obra, total_general,
                ft.Row([
                    ft.ElevatedButton(text="Actualizar", on_click=actualizar_datos),
                    ft.ElevatedButton(text="Cancelar", on_click=lambda e: self.mostrar_fichas())
                ])
            ])
        )

    def eliminar_ficha(self, ficha):
        nro_ficha = ficha[0]
        try:
            self.cursor.execute("DELETE FROM ficha_tecnica WHERE nro_ficha=%s", (nro_ficha,))
            self.connection.commit()
            self.cargar_tabla(None)
        except Exception as ex:
            self.page.add(ft.Text(f"Error al eliminar: {ex}"))
            self.connection.rollback()

    def volver_al_menu(self, e):
        self.page.clean()
        self.main_menu_callback(self.page)