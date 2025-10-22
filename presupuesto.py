import flet as ft
import mysql.connector
from conexion import ConexionGlobal


#Conexion DB y CRUD
class PresupuestoDB(ConexionGlobal):
    def __init__(self):
        super().__init__()

    def obtener_todos(self):
        self.cursor.execute("""
            SELECT nro_presupuesto, cod_cliente, descripcion, total_presupuesto, total_gastado
            FROM presupuesto ORDER BY nro_presupuesto
        """)
        return self.cursor.fetchall()

    def insertar(self, cliente, descripcion, total_presupuesto, total_gastado):
        self.cursor.execute(
            "INSERT INTO presupuesto (cod_cliente, descripcion, total_presupuesto, total_gastado) VALUES (%s,%s,%s,%s)",
            (cliente, descripcion, total_presupuesto, total_gastado)
        )
        self.connection.commit()

    def actualizar(self, nro, cliente, descripcion, total_presupuesto, total_gastado):
        self.cursor.execute(
            "UPDATE presupuesto SET cod_cliente=%s, descripcion=%s, total_presupuesto=%s, total_gastado=%s WHERE nro_presupuesto=%s",
            (cliente, descripcion, total_presupuesto, total_gastado, nro)
        )
        self.connection.commit()

    def eliminar(self, nro):
        self.cursor.execute("DELETE FROM presupuesto WHERE nro_presupuesto=%s", (nro,))
        self.connection.commit()

#UI
class FuncPresupuesto(PresupuestoDB):
    def __init__(self, page: ft.Page, main_menu_callback):
        super().__init__()
        self.page = page
        self.main_menu_callback = main_menu_callback
        self.mostrar_presupuesto()

    def mostrar_presupuesto(self):
        self.page.clean()
        header = ft.Row([
            ft.Text("Gestión de Presupuestos", size=20, weight="bold"),
            ft.ElevatedButton("Alta", on_click=self.alta_presupuesto),
            ft.ElevatedButton("Consulta", on_click=self.cargar_tabla),
            ft.ElevatedButton("<-- Volver", on_click=self.volver_al_menu)
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

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

        self.page.add(ft.Column([header, self.data_table]))
        self.cargar_tabla(None)

    def cargar_tabla(self, e):
        if not self.cursor:
            self.page.add(ft.Text("No hay conexión a la base de datos"))
            return

        presupuestos = self.obtener_todos()
        self.data_table.rows.clear()

        def crear_eliminar(p):
            return lambda e: self.eliminar_presupuesto(p[0])

        def crear_modificar(p):
            return lambda e: self.formulario_modificar(p)

        for p in presupuestos:
            eliminar_btn = ft.IconButton(icon=ft.Icons.DELETE, tooltip="Eliminar", on_click=crear_eliminar(p))
            modificar_btn = ft.IconButton(icon=ft.Icons.EDIT, tooltip="Modificar", on_click=crear_modificar(p))
            self.data_table.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(str(p[0]))),
                    ft.DataCell(ft.Text(str(p[1]))),
                    ft.DataCell(ft.Text(p[2] or "")),
                    ft.DataCell(ft.Text(str(p[3]))),
                    ft.DataCell(ft.Text(str(p[4]))),
                    ft.DataCell(ft.Row([eliminar_btn, modificar_btn]))
                ])
            )
        self.page.update()

    def alta_presupuesto(self, e):
        self.page.clean()
        cliente = ft.TextField(label="Código Cliente")
        descripcion = ft.TextField(label="Descripción")
        total_presupuesto = ft.TextField(label="Total Presupuesto")
        total_gastado = ft.TextField(label="Total Gastado")

        def guardar(ev):
            try:
                self.insertar(
                    cliente.value, descripcion.value,
                    float(total_presupuesto.value or 0),
                    float(total_gastado.value or 0))
                self.page.snack_bar = ft.SnackBar(ft.Text("Presupuesto guardado correctamente"))
                self.page.snack_bar.open = True
                self.cargar_tabla(None)
            except Exception as ex:
                self.page.snack_bar = ft.SnackBar(ft.Text(f"Error al guardar: {ex}"))
                self.page.snack_bar.open = True
            self.page.update()

        self.page.add(ft.Column([
            ft.Text("Alta de Presupuesto", size=20, weight="bold"),
            cliente, 
            descripcion, total_presupuesto, total_gastado,
            ft.Row([
                ft.ElevatedButton("Guardar", on_click=guardar),
                ft.ElevatedButton("Cancelar", on_click=lambda e: self.mostrar_presupuesto())],
                spacing=10)]))
        self.page.update()

    def formulario_modificar(self, p):
        self.page.clean()
        nro = ft.TextField(label="Nro Presupuesto", value=str(p[0]), disabled=True)
        cliente = ft.TextField(label="Código Cliente", value=str(p[1]))
        descripcion = ft.TextField(label="Descripción", value=p[2] or "")
        total_presupuesto = ft.TextField(label="Total Presupuesto", value=str(p[3]))
        total_gastado = ft.TextField(label="Total Gastado", value=str(p[4]))

        def guardar_cambios(ev):
            try:
                self.actualizar(
                    nro.value, cliente.value, descripcion.value,
                    float(total_presupuesto.value or 0),
                    float(total_gastado.value or 0))
                self.page.snack_bar = ft.SnackBar(ft.Text("Presupuesto actualizado correctamente"))
                self.page.snack_bar.open = True
                self.cargar_tabla(None)
            except Exception as ex:
                self.page.snack_bar = ft.SnackBar(ft.Text(f"Error al actualizar: {ex}"))
                self.page.snack_bar.open = True
            self.page.update()

        self.page.add(ft.Column([
            ft.Text("Modificar Presupuesto", size=20, weight="bold"),
            nro, cliente, descripcion, total_presupuesto, total_gastado,
            ft.Row([
                ft.ElevatedButton("Guardar Cambios", on_click=guardar_cambios),
                ft.ElevatedButton("Cancelar", on_click=lambda e: self.mostrar_presupuesto())],
                spacing=10)]))
        self.page.update()

    def eliminar_presupuesto(self, nro):
        self.eliminar(nro)
        self.cargar_tabla(None)

    def volver_al_menu(self, e):
        self.page.clean()
        self.main_menu_callback()
