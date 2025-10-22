import flet as ft
import mysql.connector
from conexion import ConexionGlobal


#Conexion DB y CRUD
class FichaTecnicaDB(ConexionGlobal):
    def __init__(self):
        super().__init__()

    def obtener_todas(self):
        self.cursor.execute("""
            SELECT nro_ficha, cod_cliente, vehiculo, subtotal, mano_obra, total_general
            FROM ficha_tecnica ORDER BY nro_ficha
        """)
        return self.cursor.fetchall()

    def insertar(self, nro, cliente, vehiculo, subtotal, mano_obra, total):
        self.cursor.execute(
            "INSERT INTO ficha_tecnica (nro_ficha, cod_cliente, vehiculo, subtotal, mano_obra, total_general) VALUES (%s,%s,%s,%s,%s,%s)",
            (nro, cliente, vehiculo, subtotal, mano_obra, total)
        )
        self.connection.commit()

    def actualizar(self, nro, cliente, vehiculo, subtotal, mano_obra, total):
        self.cursor.execute(
            "UPDATE ficha_tecnica SET cod_cliente=%s, vehiculo=%s, subtotal=%s, mano_obra=%s, total_general=%s WHERE nro_ficha=%s",
            (cliente, vehiculo, subtotal, mano_obra, total, nro)
        )
        self.connection.commit()

    def eliminar(self, nro):
        self.cursor.execute("DELETE FROM ficha_tecnica WHERE nro_ficha=%s", (nro,))
        self.connection.commit()

#UI
class FuncFichaTecnica(FichaTecnicaDB):
    def __init__(self, page: ft.Page, main_menu_callback):
        super().__init__()
        self.page = page
        self.main_menu_callback = main_menu_callback
        self.mostrar_fichas()

    def mostrar_fichas(self):
        self.page.clean()
        header = ft.Row([
            ft.Text("Gestión de Fichas Técnicas", size=20, weight="bold"),
            ft.ElevatedButton("Alta", on_click=self.alta_ficha),
            ft.ElevatedButton("Consulta", on_click=self.cargar_tabla),
            ft.ElevatedButton("<-- Volver", on_click=self.volver_al_menu)
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

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

        self.page.add(ft.Column([header, self.data_table]))
        self.cargar_tabla(None)

    def cargar_tabla(self, e):
        if not self.cursor:
            self.page.add(ft.Text("No hay conexión a la base de datos"))
            return

        fichas = self.obtener_todas()
        self.data_table.rows.clear()

        def crear_eliminar(f):
            return lambda e: self.eliminar_ficha(f[0])

        def crear_modificar(f):
            return lambda e: self.formulario_modificar(f)

        for f in fichas:
            eliminar_btn = ft.IconButton(icon=ft.Icons.DELETE, tooltip="Eliminar", on_click=crear_eliminar(f))
            modificar_btn = ft.IconButton(icon=ft.Icons.EDIT, tooltip="Modificar", on_click=crear_modificar(f))
            self.data_table.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(str(f[0]))),
                    ft.DataCell(ft.Text(str(f[1]))),
                    ft.DataCell(ft.Text(f[2])),
                    ft.DataCell(ft.Text(str(f[3]))),
                    ft.DataCell(ft.Text(str(f[4]))),
                    ft.DataCell(ft.Text(str(f[5]))),
                    ft.DataCell(ft.Row([eliminar_btn, modificar_btn]))
                ])
            )
        self.page.update()

    def alta_ficha(self, e):
        self.page.clean()
        nro = ft.TextField(label="Nro Ficha")
        cliente = ft.TextField(label="Código Cliente")
        vehiculo = ft.TextField(label="Vehículo")
        subtotal = ft.TextField(label="Subtotal")
        mano_obra = ft.TextField(label="Mano de Obra")
        total = ft.TextField(label="Total General")

        def guardar(ev):
            self.insertar(nro.value, cliente.value, vehiculo.value, subtotal.value, mano_obra.value, total.value)
            self.mostrar_fichas()

        btns = ft.Row([
            ft.ElevatedButton("Guardar", on_click=guardar),
            ft.ElevatedButton("Cancelar", on_click=lambda e: self.mostrar_fichas())
        ], spacing=10)

        self.page.add(ft.Column([ft.Text("Alta de Ficha Técnica", size=20, weight="bold"), nro, cliente, vehiculo, subtotal, mano_obra, total, btns]))
        self.page.update()

    def formulario_modificar(self, f):
        self.page.clean()
        nro = ft.TextField(label="Nro Ficha", value=str(f[0]), disabled=True)
        cliente = ft.TextField(label="Código Cliente", value=str(f[1]))
        vehiculo = ft.TextField(label="Vehículo", value=f[2])
        subtotal = ft.TextField(label="Subtotal", value=str(f[3]))
        mano_obra = ft.TextField(label="Mano de Obra", value=str(f[4]))
        total = ft.TextField(label="Total General", value=str(f[5]))

        def guardar(ev):
            self.actualizar(nro.value, cliente.value, vehiculo.value, subtotal.value, mano_obra.value, total.value)
            self.mostrar_fichas()

        btns = ft.Row([
            ft.ElevatedButton("Guardar Cambios", on_click=guardar),
            ft.ElevatedButton("Cancelar", on_click=lambda e: self.mostrar_fichas())
        ], spacing=10)

        self.page.add(ft.Column([ft.Text("Editar Ficha Técnica", size=20, weight="bold"), nro, cliente, vehiculo, subtotal, mano_obra, total, btns]))
        self.page.update()

    def eliminar_ficha(self, nro):
        self.eliminar(nro)
        self.cargar_tabla(None)

    def volver_al_menu(self, e):
        self.page.clean()
        self.main_menu_callback()
