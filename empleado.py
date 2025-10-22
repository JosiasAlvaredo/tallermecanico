import flet as ft
import mysql.connector
from conexion import ConexionGlobal


#Conexion DB y CRUD
class EmpleadoDB(ConexionGlobal):
    def __init__(self):
        super().__init__()

    def obtener_todos(self):
        self.cursor.execute("""
            SELECT p.apellido, p.nombre, p.dni, e.legajo
            FROM empleado e
            INNER JOIN persona p ON e.dni = p.dni
            ORDER BY p.apellido
        """)
        return self.cursor.fetchall()

    def insertar(self, legajo, dni):
        self.cursor.execute("INSERT INTO empleado (legajo, dni) VALUES (%s, %s)", (legajo, dni))
        self.connection.commit()

    def actualizar(self, legajo, dni):
        self.cursor.execute("UPDATE empleado SET legajo=%s WHERE dni=%s", (legajo, dni))
        self.connection.commit()

    def eliminar(self, legajo):
        self.cursor.execute("DELETE FROM empleado WHERE legajo=%s", (legajo,))
        self.connection.commit()

    def cerrar(self):
        if self.cursor:
            self.cursor.close()
        if self.connection and self.connection.is_connected():
            self.connection.close()

#UI
class FuncEmpleado(EmpleadoDB):
    def __init__(self, page: ft.Page, main_menu_callback):
        super().__init__()  
        self.page = page
        self.main_menu_callback = main_menu_callback
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
            datos = self.obtener_todos()
        except Exception as ex:
            self.page.add(ft.Text(f"Error al cargar empleados: {ex}"))
            return

        self.data_table.rows.clear()

        def crear_eliminar(fila):
            return lambda e: self.eliminar_empleado(fila[3])

        def crear_modificar(fila):
            return lambda e: self.formulario_modificar(fila)

        for fila in datos:
            eliminar_btn = ft.IconButton(icon=ft.Icons.DELETE, tooltip="Eliminar",
                                        on_click=crear_eliminar(fila))
            modificar_btn = ft.IconButton(icon=ft.Icons.EDIT, tooltip="Modificar",
                                        on_click=crear_modificar(fila))
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
                self.insertar(legajo.value, dni.value)
                self.mostrar_empleados()
            except Exception as ex:
                mensaje.controls.append(ft.Text(f"Error al guardar empleado: {ex}"))
                self.page.update()

        self.page.add(
            ft.Column([
                ft.Text("Alta Empleado", size=20, weight="bold"),
                legajo, dni, mensaje,
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
                self.actualizar(legajo.value, dni.value)
                self.cargar_tabla(None)
            except Exception as ex:
                self.page.add(ft.Text(f"Error al actualizar empleado: {ex}"))

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
            self.eliminar(legajo)
            self.cargar_tabla(None)
        except Exception as ex:
            self.page.add(ft.Text(f"Error al eliminar empleado: {ex}"))

    def volver_al_menu(self, e):
        self.page.clean()
        self.main_menu_callback()
