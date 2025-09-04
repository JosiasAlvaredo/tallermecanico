import flet as ft

class funcUsuario:
    def __init__(self, page: ft.Page, volver_menu):
        self.page = page
        self.volver_menu = volver_menu
        self.form_login()

    def form_login(self):
        self.page.clean()

        self.campo_usuario = ft.TextField(label="Ingrese su usuario", width=280)
        self.campo_pass = ft.TextField(label="Ingrese su contraseña", password=True, width=280)

        btn_login = ft.ElevatedButton(
            text="Acceder",
            icon=ft.Icons.LOGIN,
            on_click=lambda e: self.volver_menu(self.page)  # Lleva al menú
        )
        btn_volver = ft.ElevatedButton(
            text="<-- Volver",
            on_click=lambda e: self.volver_menu(self.page)
        )

        self.page.add(
            ft.Column(
                controls=[
                    ft.Text("Login de Usuario", size=26, weight="bold"),
                    self.campo_usuario,
                    self.campo_pass,
                    ft.Row([btn_login, btn_volver], spacing=15, alignment="center"),
                ],
                alignment="center",
                horizontal_alignment="center",
                spacing=12
            )
        )
