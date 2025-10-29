import mysql.connector
from datetime import datetime
from .database import crear_ddbb
import os
def conectar_ddbb():
    crear_ddbb()
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
        database=os.getenv("DB_NAME"),
        charset='utf8mb4',
        use_unicode=True    
        # host="localhost",
        # user="root",
        # password="12345",
        # database="RinconDelSabor"
    )
########################## RESERVAS ##########################
# --- Crear reserva ---
def crear_reserva(nombre, telefono, px, fecha, hora, necesita_sibo, token=None, token_expires_at=None):
    conexion = conectar_ddbb()
    cursor = conexion.cursor()
    query = """
        INSERT INTO reservas (nombre, telefono, px, fecha, hora, creado_en, necesita_sibo, token, token_expires_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
    creado_en = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    valores = (nombre, telefono, px, fecha, hora, creado_en, necesita_sibo, token, token_expires_at)
    cursor.execute(query, valores)
    conexion.commit()
    print("Reserva creada correctamente.")
    cursor.close()
    conexion.close()

def leer_reservas():
    conexion = conectar_ddbb()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT * FROM reservas")
    resultados = cursor.fetchall()
    cursor.close()
    conexion.close()
    if resultados:
        return resultados


def leer_reserva(id_reserva):
    conexion = conectar_ddbb()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT * FROM reservas WHERE id = %s", (id_reserva,))
    resultado = cursor.fetchone()
    cursor.close()
    conexion.close()
    if resultado:
        return resultado
    else: 
        return None


def actualizar_reserva(id_reserva, nombre=None, telefono=None, px = None, fecha=None, hora=None, necesita_sibo=None):
    conexion = conectar_ddbb()
    cursor = conexion.cursor()
    query = "UPDATE reservas SET "
    campos = []
    valores = []

    if nombre:
        campos.append("nombre = %s")
        valores.append(nombre)
    if telefono:
        campos.append("telefono = %s")
        valores.append(telefono)
    if px:
        campos.append("px = %s")
        valores.append(px)
    if fecha:
        campos.append("fecha = %s")
        valores.append(fecha)
    if hora:
        campos.append("hora = %s")
        valores.append(hora)
    if necesita_sibo is not None:
        campos.append("necesita_sibo = %s")
        valores.append(necesita_sibo)

    if not campos:
        print("No se proporcionaron campos para actualizar.")
        return

    query += ", ".join(campos) + " WHERE id = %s"
    valores.append(id_reserva)
    cursor.execute(query, tuple(valores))
    conexion.commit()

    print("Reserva actualizada correctamente.")
    cursor.close()
    conexion.close()

# --- Eliminar reserva ---
def eliminar_reserva(id_reserva):
    conexion = conectar_ddbb()
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM reservas WHERE id = %s", (id_reserva,))
    conexion.commit()
    print("Reserva eliminada correctamente.")
    cursor.close()
    conexion.close()

########################## INGREDIENTES ##########################
# --- Crear reserva ---
def crear_ingrediente(nombre, apto_sibo):
    conexion = conectar_ddbb()
    cursor = conexion.cursor()
    query = """
        INSERT INTO ingredientes (nombre, apto_sibo)
        VALUES (%s, %s)
        """
    valores = (nombre, apto_sibo)
    cursor.execute(query, valores)
    conexion.commit()
    print("Ingrediente creada correctamente.")
    cursor.close()
    conexion.close()

def leer_ingredientes():
    conexion = conectar_ddbb()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT * FROM ingredientes")
    resultados = cursor.fetchall()
    cursor.close()
    conexion.close()
    if resultados:
        return resultados


def leer_ingrediente(id_ingrediente):
    conexion = conectar_ddbb()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT * FROM ingredientes WHERE idIngrediente = %s", (id_ingrediente,))
    resultado = cursor.fetchone()
    cursor.close()
    conexion.close()
    if resultado:
        return resultado
    else: 
        return None


def actualizar_ingrediente(id_ingrediente, nombre=None, apto_sibo=None):
    conexion = conectar_ddbb()
    cursor = conexion.cursor()
    query = "UPDATE ingredientes SET "
    campos = []
    valores = []

    if nombre:
        campos.append("nombre = %s")
        valores.append(nombre)
    if apto_sibo:
        campos.append("apto_sibo = %s")
        valores.append(apto_sibo)
    if not campos:
        print("No se proporcionaron campos para actualizar.")
        return

    query += ", ".join(campos) + " WHERE id = %s"
    valores.append(id_ingrediente)
    cursor.execute(query, tuple(valores))
    conexion.commit()

    print("Reserva actualizada correctamente.")
    cursor.close()
    conexion.close()


def eliminar_ingrediente(id_ingrediente):
    conexion = conectar_ddbb()
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM ingredientes WHERE id = %s", (id_ingrediente,))
    conexion.commit()
    print("ingrediente eliminada correctamente.")
    cursor.close()
    conexion.close()


########################## RECETAS ##########################
def crear_receta(nombre):
    conexion = conectar_ddbb()
    cursor = conexion.cursor()
    query = """
        INSERT INTO recetas (nombre)
        VALUES (%s)
        """

    valores = (nombre)
    cursor.execute(query, valores)
    conexion.commit()
    print("receta creada correctamente.")
    cursor.close()
    conexion.close()

def leer_recetas():
    conexion = conectar_ddbb()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT * FROM recetas")
    resultados = cursor.fetchall()
    cursor.close()
    conexion.close()
    if resultados:
        return resultados


def leer_receta(id_receta):
    conexion = conectar_ddbb()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT * FROM recetas WHERE idReceta = %s", (id_receta,))
    resultado = cursor.fetchone()
    cursor.close()
    conexion.close()
    if resultado:
        return resultado
    else: 
        return None


def actualizar_receta(id_receta, nombre=None):
    conexion = conectar_ddbb()
    cursor = conexion.cursor()
    query = "UPDATE recetas SET "
    campos = []
    valores = []

    if nombre:
        campos.append("nombre = %s")
        valores.append(nombre)
    if not campos:
        print("No se proporcionaron campos para actualizar.")
        return

    query += ", ".join(campos) + " WHERE id = %s"
    valores.append(id_receta)
    cursor.execute(query, tuple(valores))
    conexion.commit()

    print("receta actualizada correctamente.")
    cursor.close()
    conexion.close()

def eliminar_receta(id_receta):
    conexion = conectar_ddbb()
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM recetas WHERE idReceta = %s", (id_receta,))
    conexion.commit()
    print("receta eliminada correctamente.")
    cursor.close()
    conexion.close()


########################## RECETA/INGREDIENTES ##########################

def crear_recetaIngrediente(idReceta,idIngrediente):
    conexion = conectar_ddbb()
    cursor = conexion.cursor()
    query = """
        INSERT INTO receta_ingrediente (idReceta,idIngrediente)
        VALUES (%s, %s)
        """

    valores = (idReceta,idIngrediente)
    cursor.execute(query, valores)
    conexion.commit()
    print("recetaIngrediente creada correctamente.")
    cursor.close()
    conexion.close()

def leer_recetaIngredientes():
    conexion = conectar_ddbb()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT * FROM receta_ingrediente")
    resultados = cursor.fetchall()
    cursor.close()
    conexion.close()
    if resultados:
        return resultados


def leer_recetaIngrediente(id_recetaIngrediente):
    conexion = conectar_ddbb()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT * FROM receta_ingrediente WHERE idRecetaIngrediente = %s", (id_recetaIngrediente,))
    resultado = cursor.fetchone()
    cursor.close()
    conexion.close()
    if resultado:
        return resultado
    else: 
        return None


def actualizar_recetaIngrediente(id_recetaIngrediente, idReceta = None, idIngrediente = None):
    conexion = conectar_ddbb()
    cursor = conexion.cursor()
    query = "UPDATE receta_ingrediente SET "
    campos = []
    valores = []

    if idReceta:
        campos.append("idReceta = %s")
        valores.append(idReceta)
    if idIngrediente:
        campos.append("idIngrediente = %s")
        valores.append(idIngrediente)
    if not campos:
        print("No se proporcionaron campos para actualizar.")
        return

    query += ", ".join(campos) + " WHERE id = %s"
    valores.append(id_recetaIngrediente)
    cursor.execute(query, tuple(valores))
    conexion.commit()

    print("recetaIngrediente actualizada correctamente.")
    cursor.close()
    conexion.close()



def eliminar_recetaIngrediente(id_recetaIngrediente):
    conexion = conectar_ddbb()
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM receta_ingrediente WHERE idRecetaIngrediente = %s", (id_recetaIngrediente,))
    conexion.commit()
    print("recetaIngrediente eliminada correctamente.")
    cursor.close()
    conexion.close()


if __name__ == "__main__":
    crear_ddbb()
    leer_reservas()