import flet as ft
import mysql.connector

#Conexion DB
class UsuarioDB:
    def __init__(self):
        try:
            self.connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="root",
                database="taller_mecanico"
            )
            self.cursor = self.connection.cursor(buffered=True)
        except mysql.connector.Error as err:
            print(f"Error al conectar a la DB: {err}")
            self.connection = None
            self.cursor = None

    def verificar_usuario(self, usuario, contrasena):
        self.cursor.execute(
            "SELECT usuario FROM detalle_usuario WHERE usuario=%s AND contrasena=%s",
            (usuario, contrasena)
        )
        return self.cursor.fetchone()

    def cerrar(self):
        if self.cursor:
            self.cursor.close()
        if self.connection and self.connection.is_connected():
            self.connection.close()

#UI
class FuncUsuario(UsuarioDB):
    def __init__(self, page: ft.Page, volver_menu, estado_usuario):
        super().__init__()
        self.page = page
        self.volver_menu = volver_menu
        self.estado_usuario = estado_usuario
        self.form_login()

    def form_login(self):
        self.page.clean()

        if self.estado_usuario["nombre"]:
            self.page.add(
                ft.Column(
                    controls=[
                        ft.Text(f"Sesión iniciada como: {self.estado_usuario['nombre']}", size=22, weight="bold", text_align="center"),
                        ft.ElevatedButton("Cerrar sesión", on_click=self.cerrar_sesion),
                        ft.ElevatedButton("<-- Volver", on_click=lambda e: self.volver_menu())
                    ],
                    alignment="center",
                    horizontal_alignment="center",
                    spacing=15
                )
            )
            return

        # Login
        self.campo_usuario = ft.TextField(label="Usuario", width=280)
        self.campo_pass = ft.TextField(label="Contraseña", password=True, width=280)
        self.mensaje_error = ft.Text("", color="red")
        btn_login = ft.ElevatedButton(text="Acceder", icon=ft.Icons.LOGIN, on_click=self.verificar_login)
        btn_volver = ft.ElevatedButton(text="<-- Volver", on_click=lambda e: self.volver_menu())

        self.page.add(
            ft.Column(
                controls=[
                    ft.Text("Login de Usuario", size=26, weight="bold"),
                    self.campo_usuario,
                    self.campo_pass,
                    self.mensaje_error,
                    ft.Row([btn_login, btn_volver], spacing=15, alignment="center"),
                ],
                alignment="center",
                horizontal_alignment="center",
                spacing=12
            )
        )

    def verificar_login(self, e):
        usuario = self.campo_usuario.value.strip()
        contrasena = self.campo_pass.value.strip()

        if not usuario or not contrasena:
            self.mensaje_error.value = "Complete todos los campos."
            self.page.update()
            return

        try:
            resultado = self.verificar_usuario(usuario, contrasena)
            self.cerrar()

            if resultado:
                self.estado_usuario["nombre"] = resultado[0]
                self.form_login()
            else:
                self.mensaje_error.value = "Usuario o contraseña incorrectos."
                self.page.update()

        except mysql.connector.Error as err:
            self.mensaje_error.value = f"Error con la base de datos: {err}"
            self.page.update()

    def cerrar_sesion(self, e):
        self.estado_usuario["nombre"] = None
        self.form_login()
