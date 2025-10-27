from flask import Flask, jsonify, request
import mysql.connector
import os

app = Flask(__name__)

# Configuración de conexión a Railway
def conectar_db():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
        database=os.getenv("DB_NAME")
    )

# Función para ejecutar un archivo SQL
def ejecutar_sql(archivo_sql):
    conexion = conectar_db()
    cursor = conexion.cursor()

    with open(archivo_sql, "r", encoding="utf-8") as f:
        sql_script = f.read()

    # Divide las sentencias por punto y coma
    sentencias = [s.strip() for s in sql_script.split(";") if s.strip()]

    for sentencia in sentencias:
        try:
            cursor.execute(sentencia)
        except Exception as e:
            print(f"Error en sentencia:\n{sentencia}\n{e}")

    conexion.commit()
    cursor.close()
    conexion.close()

@app.route('/cargar_datos', methods=['POST'])
def cargar_datos():
    try:
        ejecutar_sql("data/rincondelsabor_ingredientes.sql")
        ejecutar_sql("data/rincondelsabor_recetas.sql")
        ejecutar_sql("data/rincondelsabor_receta_ingrediente.sql")
        ejecutar_sql("data/rincondelsabor_reservas.sql")
        ejecutar_sql("data/rincondelsabor_ordenes.sql")

        return jsonify({"mensaje": "Datos cargados correctamente en la base de datos."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
