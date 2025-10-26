from flask import Flask, request, render_template, send_file, abort, jsonify
import mysql.connector
from mysql.connector import pooling, Error
import qrcode
import io
import base64
from datetime import datetime, timedelta
import os
import logging
import secrets
from PIL import Image, ImageDraw, ImageFont
import uuid
# --------
# from database import 
from models import conectar_ddbb, crear_reserva, leer_reservas, leer_reserva
from SiBoti import SiBoti

app = Flask(__name__)
bot = SiBoti()  # cargamos el modelo una vez
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', secrets.token_hex(16))

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def generate_secure_token():
    """Genera un token seguro único"""
    return str(uuid.uuid4())

def create_reservation_token(reserva_id):
    """Crea y guarda un token para una reserva"""
    conn = None
    try:
        conn = conectar_ddbb()
        if not conn:
            return None
            
        cursor = conn.cursor()
        token = generate_secure_token()
        expires_at = datetime.now() + timedelta(days=7)
        
        cursor.execute(
            "UPDATE reservas SET token = %s, token_expires_at = %s WHERE id = %s",
            (token, expires_at, reserva_id)
        )
        conn.commit()
        cursor.close()
        
        return token
    except Error as e:
        logger.error(f"Error creando token: {e}")
        return None
    finally:
        if conn:
            conn.close()

def validate_token(token):
    """Valida un token y retorna los datos de la reserva"""
    conn = None
    try:
        conn = conectar_ddbb()
        if not conn:
            return None
            
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """SELECT id, nombre, telefono, fecha, hora, necesita_sibo, token_expires_at 
               FROM reservas WHERE token = %s""",
            (token,)
        )
        reserva = cursor.fetchone()
        cursor.close()
        
        if not reserva:
            return None
            
        # Verificar expiración
        if reserva['token_expires_at'] < datetime.now():
            return None
            
        return reserva
    except Error as e:
        logger.error(f"Error validando token: {e}")
        return None
    finally:
        if conn:
            conn.close()

def generate_printable_qr(reserva_id, token):
    try:
        """Genera QR imprimible con información de la reserva"""
        reserva = leer_reserva(reserva_id)
        if not reserva:
            return None
            
        # URL para escanear
        base_url = os.getenv('BASE_URL', 'http://localhost:5000')
        scan_url = f"{base_url}/scan/{token}"
        
        # Crear QR
        qr = qrcode.QRCode(version=1, box_size=8, border=4)
        qr.add_data(scan_url)
        qr.make(fit=True)
        
        # Crear imagen con información
        img_width, img_height = 400, 600
        img = Image.new('RGB', (img_width, img_height), 'white')
        draw = ImageDraw.Draw(img)
        
        # Título
        draw.text((20, 20), "El Rincón del Sabor", fill='black')
        draw.text((20, 50), f"Reserva #{reserva_id}", fill='black')
        
        # Información de la reserva
        y_pos = 100
        draw.text((20, y_pos), f"Cliente: {reserva['nombre']}", fill='black')
        draw.text((20, y_pos + 30), f"Fecha: {reserva['fecha']}", fill='black')
        draw.text((20, y_pos + 60), f"Hora: {reserva['hora']}", fill='black')
        
        if reserva['necesita_sibo'] == 1:
            draw.text((20, y_pos + 90), "MENÚ SIBO ESPECIAL", fill='red')
        
            # Agregar QR
            qr_img = qr.make_image(fill_color="black", back_color="white")
            qr_img = qr_img.resize((200, 200))
            img.paste(qr_img, (100, 200))
            
            draw.text((20, 420), "Escanea para chatear con SiBoti", fill='black')
            
            # Convertir a bytes
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            buffer.seek(0)
            
            return buffer
            
    except Exception as e:
        logger.error(f"Error generando QR imprimible: {e}")
        return None

# Rutas de la aplicación
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/reservar", methods=["POST"])
def reservar():
    conn = None
    # Validar y sanitizar datos
    nombre = request.form.get("nombre", "").strip()
    telefono = request.form.get("telefono", "").strip()
    personas = request.form["personas"]
    fecha = request.form.get("fecha", "")
    hora = request.form.get("hora", "")
    necesita_sibo = bool(request.form.get("necesita_sibo"))
    
    # Validaciones
    if not all([nombre, telefono,personas, fecha, hora]):
        return render_template("error.html", 
                                mensaje="Todos los campos son obligatorios"), 400
    
    if len(nombre) > 100 or len(telefono) > 20:
        return render_template("error.html", 
                                mensaje="Datos demasiado largos"), 400
        
    crear_reserva(nombre,telefono,personas,fecha,hora,necesita_sibo)
    
    # Crear token para la reserva
    # token = create_reservation_token(reserva_id)
    
    
    logger.info(f"Reserva creada, SIBO: {necesita_sibo}")
    
    # NO generar QR en la confirmación (requisito)
    return render_template("confirmacion.html", 
                        #  reserva_id=reserva_id,
                        nombre=nombre,
                        personas = personas, 
                        fecha=fecha, 
                        hora=hora, 
                        necesita_sibo=necesita_sibo)


@app.route("/reservas")
def ver_reservas():
    try:
        reservas = leer_reservas()
        return render_template("reservas.html", reservas=reservas)
    except Exception as e:
        return f"Error cargando reservas: {e}", 500

@app.route("/reservas/<int:reserva_id>/qr-impreso")
def qr_impreso(reserva_id):
    """Genera QR imprimible para una reserva"""
    reserva = leer_reserva(reserva_id)
        
    if not reserva:
        abort(404)
        
    token = reserva['token']
    if not token:
        # Crear token si no existe
        token = create_reservation_token(reserva_id)
        if not token:
            abort(500)
    
    # Generar QR imprimible
    qr_buffer = generate_printable_qr(reserva_id, token)
    if not qr_buffer:
        abort(500)
        
    return send_file(
        qr_buffer,
        mimetype='image/png',
        as_attachment=True,
        download_name=f'qr_reserva_{reserva_id}.png'
    )

@app.route("/scan/<token>")
def scan_token(token):
    """Interfaz móvil para chatear con SiBoti"""
    reserva = validate_token(token)
    if not reserva:
        return render_template("error.html", 
                             mensaje="Token inválido o expirado"), 403
    
    return render_template("chat_siboti.html", 
                         reserva=reserva, 
                         token=token)

@app.route("/chat")
def chat_por_mesa():
    """Interfaz de chat abierta desde QR por número de mesa"""
    mesa = request.args.get("mesa")
    if not mesa:
        return render_template("error.html", mensaje="Número de mesa no especificado"), 400
    return render_template("chat.html", mesa=mesa)

@app.route("/chatbot", methods=["POST"])
def chatbot():
    """
    Endpoint del chatbot SIBO conectado a la base de datos.
    Interpreta el mensaje del usuario y devuelve recomendaciones reales.
    """
    data = request.get_json()
    mensaje = data.get("mensaje", "")
    mesa = data.get("mesa", None)

    # Si el mensaje incluye una posible orden
    if mesa and any(p in mensaje.lower() for p in ["quiero", "pedir", "trae", "me gustaría"]):
        respuesta = bot.procesar_pedido(mensaje, mesa)
    else:
        respuesta = bot.predecir(mensaje)
    return jsonify({"respuesta": respuesta})

@app.route("/ordenes", methods=["GET"])
def ver_ordenes():
    bot.cursor.execute("SELECT * FROM ordenes ORDER BY fecha DESC;")
    ordenes = bot.cursor.fetchall()
    return jsonify(ordenes)


@app.errorhandler(404)
def not_found(error):
    return render_template("error.html", mensaje="Página no encontrada"), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template("error.html", mensaje="Error interno del servidor"), 500

if __name__ == "__main__":
    debug_mode = os.getenv('FLASK_ENV') == 'development'
    app.run(debug=debug_mode, host='127.0.0.1', port=5000)