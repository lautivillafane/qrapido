#!/usr/bin/env python3
import qrcode
from PIL import Image, ImageDraw, ImageFont
import os

def generar_qr_restaurante():
    """Genera QR imprimible para el restaurante""" 

    # URL del menú SIBO
    base_url = os.getenv('BASE_URL', 'http://localhost:5000')
    menu_url = f"{base_url}/menu-sibo"
    
    print(f"Generando QR para: {menu_url}")
    
    # Crear QR
    qr = qrcode.QRCode(version=1, box_size=8, border=4)
    qr.add_data(menu_url)
    qr.make(fit=True)
    
    # Crear imagen con información
    img_width, img_height = 400, 500
    img = Image.new('RGB', (img_width, img_height), 'white')
    draw = ImageDraw.Draw(img)
    
    # Título del restaurante
    draw.text((20, 20), "El Rincón del Sabor", fill='black')
    draw.text((20, 50), "Menú SIBO Especial", fill='black')
    
    # Instrucciones
    draw.text((20, 90), "1. Escanea este código QR", fill='black')
    draw.text((20, 110), "2. Ve nuestro menú SIBO", fill='black')
    draw.text((20, 130), "3. Chatea con SiBoti", fill='black')
    
    # Agregar QR
    qr_img = qr.make_image(fill_color="black", back_color="white")
    qr_img = qr_img.resize((200, 200))
    img.paste(qr_img, (100, 180))
    
    # Información adicional
    draw.text((20, 400), "Especialistas en dietas SIBO", fill='black')
    draw.text((20, 420), "Av. Corrientes 1234, CABA", fill='black')
    draw.text((20, 440), "Tel: +54 11 5555 5555", fill='black')
    
    # Guardar imagen
    filename = "qr_menu_sibo_restaurante.png"
    img.save(filename)
    
    print(f"[OK] QR generado exitosamente: {filename}")
    print(f"[URL] {menu_url}")
    print("\n[INFO] Puedes imprimir este QR y colocarlo en las mesas del restaurante")
    
    return filename



def generar_qr_mesas():
    BASE_URL = "http://localhost:5000/chat?mesa="

    output_dir = "qrs_mesas"
    os.makedirs(output_dir, exist_ok=True)
    
    for mesa in range(1, 4):  # tres mesas base
        url = f"{BASE_URL}{mesa}"
        img = qrcode.make(url)
        filename = os.path.join(output_dir, f"mesa_{mesa}.png")
        img.save(filename)
        print(f"✅ QR generado para Mesa {mesa}: {filename}")


if __name__ == "__main__":
    generar_qr_restaurante()
    generar_qr_mesas()