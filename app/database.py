import mysql.connector
import os

def crear_ddbb():
    conexion = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
        database=os.getenv("DB_NAME")
    # host="localhost",
        # user="root",
        # password="12345"  
    )
    cursor = conexion.cursor()
    """
    Crear base localmenmte
        # Crear base de datos si no existe
        cursor.execute("CREATE DATABASE IF NOT EXISTS RinconDelSabor")
        print("Base de datos 'restaurante' verificada o creada correctamente.")

        # Seleccionar la base
        cursor.execute("USE RinconDelSabor;")
    """
    # Crear tabla reservas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reservas (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nombre VARCHAR(100) NOT NULL,
            telefono VARCHAR(20) NOT NULL,
            px INTEGER NOT NULL,
            fecha DATE NOT NULL,
            hora TIME NOT NULL,
            creado_en DATETIME DEFAULT CURRENT_TIMESTAMP,
            necesita_sibo TINYINT(1) DEFAULT 0,
            token VARCHAR(255) NULL,
            token_expires_at DATETIME NULL
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ingredientes (
            idIngrediente INT AUTO_INCREMENT PRIMARY KEY,
            nombre VARCHAR(100) NOT NULL,
            apto_sibo ENUM('Si', 'No', 'Moderado') NOT NULL
        );
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS recetas (
            idReceta INT AUTO_INCREMENT PRIMARY KEY,
            nombre VARCHAR(150) NOT NULL
        );
    """)    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS receta_ingrediente (
        idReceta INT,
        idIngrediente INT,
        FOREIGN KEY (idReceta) REFERENCES recetas(idReceta),
        FOREIGN KEY (idIngrediente) REFERENCES ingredientes(idIngrediente)
        ); 
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ordenes (
        idOrden INT AUTO_INCREMENT PRIMARY KEY,
        mesa INT NOT NULL,
        pedido TEXT NOT NULL,
        fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        estado ENUM('Pendiente', 'En preparación', 'Servido') DEFAULT 'Pendiente'
        );
    """)
    print("Tablas creadas correctamente.")
    # Confirmar y cerrar conexión
    conexion.commit()
    cursor.close()
    conexion.close()

if __name__ == "__main__":
    crear_ddbb()
