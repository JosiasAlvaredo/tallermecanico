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

class funcEmpleado:
    def __init__(self, page: ft.Page, main_menu_callback):
        self.page = page
        self.main_menu_callback = main_menu_callback
        self.connection = connect_to_db()
        self.cursor = self.connection.cursor() if self.connection else None
        self.mostrar_empleados()

    def mostrar_empleados(self):
        self.page.clean()
        header = ft.Row([
            ft.Text("Gestión de Empleados", size=20, weight="bold"),
            ft.ElevatedButton(text="Alta", on_click=self.formulario_alta),
            ft.ElevatedButton(text="Consulta", on_click=self.cargar_tabla),
            ft.ElevatedButton(text="<-- Volver", on_click=self.volver_al_menu),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        self.data_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Apellido")),
                ft.DataColumn(ft.Text("Nombre")),
                ft.DataColumn(ft.Text("DNI")),
                ft.DataColumn(ft.Text("Legajo")),
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
                SELECT p.apellido, p.nombre, p.dni, e.legajo
                FROM empleado e
                INNER JOIN persona p ON e.dni = p.dni
                ORDER BY p.apellido
            """)
            datos = self.cursor.fetchall()
        except Exception as ex:
            self.page.add(ft.Text(f"Error al cargar empleados: {ex}"))
            return

        self.data_table.rows.clear()

        for fila in datos:
            eliminar_btn = ft.IconButton(icon=ft.Icons.DELETE, tooltip="Eliminar",
                                        on_click=lambda e, l=fila[3]: self.eliminar_empleado(l))
            modificar_btn = ft.IconButton(icon=ft.Icons.EDIT, tooltip="Modificar",
                                        on_click=lambda e, f=fila: self.formulario_modificar(f))
            self.data_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(fila[0])),
                        ft.DataCell(ft.Text(fila[1])),
                        ft.DataCell(ft.Text(fila[2])),
                        ft.DataCell(ft.Text(str(fila[3]))),
                        ft.DataCell(ft.Row([eliminar_btn, modificar_btn]))
                    ]
                )
            )
        self.page.update()

    def formulario_alta(self, e):
        self.page.clean()
        legajo = ft.TextField(label="Legajo")
        dni = ft.TextField(label="DNI (Debe existir en Personas)")

        mensaje = ft.Column([])

        def guardar(ev):
            mensaje.controls.clear()
            if not legajo.value or not dni.value:
                mensaje.controls.append(ft.Text("Todos los campos son obligatorios"))
                self.page.update()
                return
            try:
                self.cursor.execute("SELECT dni FROM persona WHERE dni=%s", (dni.value,))
                if not self.cursor.fetchone():
                    mensaje.controls.append(ft.Text("Error: DNI no existe en Personas. Cree la persona primero."))
                    self.page.update()
                    return
                self.cursor.execute("INSERT INTO empleado (legajo, dni) VALUES (%s, %s)", (legajo.value, dni.value))
                self.connection.commit()
                self.mostrar_empleados()
            except Exception as ex:
                mensaje.controls.append(ft.Text(f"Error al guardar empleado: {ex}"))
                self.connection.rollback()
                self.page.update()

        self.page.add(
            ft.Column([
                ft.Text("Alta Empleado", size=20, weight="bold"),
                legajo, dni,
                mensaje,
                ft.Row([
                    ft.ElevatedButton(text="Guardar", on_click=guardar),
                    ft.ElevatedButton(text="Cancelar", on_click=lambda e: self.mostrar_empleados())
                ])
            ], spacing=10)
        )

    def formulario_modificar(self, fila):
        self.page.clean()
        apellido = ft.TextField(label="Apellido", value=fila[0])
        nombre = ft.TextField(label="Nombre", value=fila[1])
        dni = ft.TextField(label="DNI", value=fila[2], disabled=True)
        legajo = ft.TextField(label="Legajo", value=str(fila[3]))

        def actualizar(ev):
            try:
                self.cursor.execute("UPDATE empleado SET legajo=%s WHERE dni=%s", (legajo.value, dni.value))
                self.connection.commit()
                self.cargar_tabla(None)
            except Exception as ex:
                self.page.add(ft.Text(f"Error al actualizar empleado: {ex}"))
                self.connection.rollback()

        self.page.add(
            ft.Column([
                ft.Text("Modificar Empleado", size=20, weight="bold"),
                apellido, nombre, dni, legajo,
                ft.Row([
                    ft.ElevatedButton(text="Actualizar", on_click=actualizar),
                    ft.ElevatedButton(text="Cancelar", on_click=lambda e: self.mostrar_empleados())
                ])
            ], spacing=10)
        )

    def eliminar_empleado(self, legajo):
        try:
            self.cursor.execute("DELETE FROM empleado WHERE legajo=%s", (legajo,))
            self.connection.commit()
            self.cargar_tabla(None)
        except Exception as ex:
            self.page.add(ft.Text(f"Error al eliminar empleado: {ex}"))
            self.connection.rollback()

    def volver_al_menu(self, e):
        self.page.clean()
        self.main_menu_callback(self.page)
