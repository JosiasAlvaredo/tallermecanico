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
        print("Conexión errónea")
        print(ex)
        return None

class funcPresupuesto:
    def __init__(self, page: ft.Page, main_menu_callback):
        self.page = page
        self.main_menu_callback = main_menu_callback
        self.connection = connect_to_db()
        self.cursor = self.connection.cursor(buffered=True) if self.connection else None
        self.mostrar_presupuesto()

    def mostrar_presupuesto(self):
        self.page.clean()
        header = ft.Row(
            controls=[
                ft.Text("Gestión de Presupuestos", size=20, weight="bold"),
                ft.ElevatedButton(text="Alta", on_click=self.alta_presupuesto),
                ft.ElevatedButton(text="Consulta", on_click=self.cargar_tabla),
                ft.ElevatedButton(text="<-- Volver", on_click=self.volver_al_menu),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

        self.data_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Nro Presupuesto")),
                ft.DataColumn(ft.Text("Código Cliente")),
                ft.DataColumn(ft.Text("Descripción")),
                ft.DataColumn(ft.Text("Total Presupuesto")),
                ft.DataColumn(ft.Text("Total Gastado")),
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
                SELECT nro_presupuesto, cod_cliente, descripcion, total_presupuesto, total_gastado
                FROM presupuesto ORDER BY nro_presupuesto
            """)
            datos = self.cursor.fetchall()
        except Exception as ex:
            self.page.snack_bar = ft.SnackBar(ft.Text(f"Error al cargar presupuestos: {ex}"))
            self.page.snack_bar.open = True
            self.page.update()
            return

        self.data_table.rows.clear()

        for p in datos:
            eliminar_btn = ft.IconButton(icon=ft.Icons.DELETE, tooltip="Eliminar",
                                        on_click=lambda e, p=p: self.eliminar_presupuesto(p))
            modificar_btn = ft.IconButton(icon=ft.Icons.EDIT, tooltip="Modificar",
                                        on_click=lambda e, p=p: self.formulario_modificar(p))
            self.data_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(p[0]))),
                        ft.DataCell(ft.Text(str(p[1]))),
                        ft.DataCell(ft.Text(p[2] or "")),
                        ft.DataCell(ft.Text(str(p[3]))),
                        ft.DataCell(ft.Text(str(p[4]))),
                        ft.DataCell(ft.Row([eliminar_btn, modificar_btn]))
                    ]
                )
            )
        self.page.update()

    def alta_presupuesto(self, e):
        self.page.clean()
        self.cod_cliente = ft.TextField(label="Código Cliente")
        self.descripcion = ft.TextField(label="Descripción")
        self.total_presupuesto = ft.TextField(label="Total Presupuesto")
        self.total_gastado = ft.TextField(label="Total Gastado")

        def guardar(ev):
            try:
                self.cursor.execute(
                    "INSERT INTO presupuesto (cod_cliente, descripcion, total_presupuesto, total_gastado) VALUES (%s, %s, %s, %s)",
                    (
                        self.cod_cliente.value,
                        self.descripcion.value,
                        float(self.total_presupuesto.value or 0),
                        float(self.total_gastado.value or 0),
                    )
                )
                self.connection.commit()
                self.page.snack_bar = ft.SnackBar(ft.Text("Presupuesto guardado correctamente"))
                self.page.snack_bar.open = True
                self.cargar_tabla(None)
            except Exception as ex:
                self.page.snack_bar = ft.SnackBar(ft.Text(f"Error al guardar: {ex}"))
                self.page.snack_bar.open = True
            self.page.update()

        self.page.add(
            ft.Column([
                ft.Text("Alta de Presupuesto", size=20, weight="bold"),
                self.cod_cliente,
                self.descripcion,
                self.total_presupuesto,
                self.total_gastado,
                ft.Row([
                    ft.ElevatedButton("Guardar", on_click=guardar),
                    ft.ElevatedButton("Cancelar", on_click=lambda e: self.mostrar_presupuesto())
                ], spacing=10)
            ], spacing=10)
        )
        self.page.update()

    def formulario_modificar(self, p):
        self.page.clean()
        nro_presupuesto = ft.TextField(label="Nro Presupuesto", value=str(p[0]), disabled=True)
        cod_cliente = ft.TextField(label="Código Cliente", value=str(p[1]))
        descripcion = ft.TextField(label="Descripción", value=p[2] or "")
        total_presupuesto = ft.TextField(label="Total Presupuesto", value=str(p[3]))
        total_gastado = ft.TextField(label="Total Gastado", value=str(p[4]))

        def guardar_cambios(ev):
            try:
                self.cursor.execute(
                    "UPDATE presupuesto SET cod_cliente=%s, descripcion=%s, total_presupuesto=%s, total_gastado=%s WHERE nro_presupuesto=%s",
                    (cod_cliente.value, descripcion.value, float(total_presupuesto.value or 0),
                    float(total_gastado.value or 0), nro_presupuesto.value)
                )
                self.connection.commit()
                self.page.snack_bar = ft.SnackBar(ft.Text("Presupuesto actualizado correctamente"))
                self.page.snack_bar.open = True
                self.cargar_tabla(None)
            except Exception as ex:
                self.page.snack_bar = ft.SnackBar(ft.Text(f"Error al actualizar: {ex}"))
                self.page.snack_bar.open = True
            self.page.update()

        self.page.add(
            ft.Column([
                ft.Text("Modificar Presupuesto", size=20, weight="bold"),
                nro_presupuesto, cod_cliente, descripcion, total_presupuesto, total_gastado,
                ft.Row([
                    ft.ElevatedButton("Guardar Cambios", on_click=guardar_cambios),
                    ft.ElevatedButton("Cancelar", on_click=lambda e: self.mostrar_presupuesto())
                ], spacing=10)
            ], spacing=10)
        )
        self.page.update()

    def eliminar_presupuesto(self, p):
        try:
            self.cursor.execute("DELETE FROM presupuesto WHERE nro_presupuesto=%s", (p[0],))
            self.connection.commit()
            self.page.snack_bar = ft.SnackBar(ft.Text("Presupuesto eliminado correctamente"))
            self.page.snack_bar.open = True
            self.cargar_tabla(None)
        except Exception as ex:
            self.page.snack_bar = ft.SnackBar(ft.Text(f"Error al eliminar: {ex}"))
            self.page.snack_bar.open = True
        self.page.update()

    def volver_al_menu(self, e):
        self.page.clean()
        self.main_menu_callback(self.page)
