import mysql.connector

class ConexionGlobal:
    def __init__(self):
        try:
            self.connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="root",
                database="taller_mecanico"
            )
            self.cursor = self.connection.cursor(buffered=True)
            print("Conexión exitosa")
        except mysql.connector.Error as err:
            print(f"Error al conectar a la DB: {err}")
            self.connection = None
            self.cursor = None

    def cerrar(self):
        if self.cursor:
            self.cursor.close()
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("Conexión cerrada")
