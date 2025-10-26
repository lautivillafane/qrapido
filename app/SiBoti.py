# SiBoti.py
import mysql.connector
from collections import Counter
from difflib import get_close_matches
import unicodedata, re, random
import os
class SiBoti:
    def __init__(self, db_config=None):
        cfg = db_config or {
            "host":os.getenv("DB_HOST"),
            "user":os.getenv("DB_USER"),
            "password":os.getenv("DB_PASS"),
            "database":os.getenv("DB_NAME")
            # "host": "localhost",
            # "user": "root",
            # "password": "12345",
            # "database": "RinconDelSabor"
        }
        self.conn = mysql.connector.connect(**cfg)
        self.cursor = self.conn.cursor(dictionary=True)

        # Memoria por "mesa" (session): guarda preferencias y última lista mostrada
        self.sessions = {}


    def limpiar_texto(self, texto):
        if not texto:
            return ""
        texto = texto.lower().strip()
        texto = unicodedata.normalize('NFD', texto).encode('ascii', 'ignore').decode('utf-8')
        texto = re.sub(r'[^a-z0-9\s]', ' ', texto)
        texto = re.sub(r'\bpara\b', ' ', texto)
        texto = re.sub(r'\s+', ' ', texto).strip()
        if len(texto) > 1 and texto.endswith('s'):
            texto = texto[:-1]
        return texto

    def detectar_intencion(self, mensaje):
        txt = self.limpiar_texto(mensaje)

        saludos = ["hola", "holaa", "holaaa", "buen", "buenas", "hey", "saludo"]
        personales = ["edad", "nombre", "quien", "estas", "como estas", "como va"]
        fuera_tema = ["precio", "horario", "hora", "direccion", "telefono", "reserv", "reserva"]

        # saludos / personales / fuera de tema
        if any(p in txt for p in saludos):
            return "saludo"
        if any(p in txt for p in personales):
            return "personal"
        if any(p in txt for p in fuera_tema):
            return "fuera_tema"

        # --- MENÚ SIBO ---
        # "recetas moderadas", "platos moderados", "sibo moderado"
        if any(k in txt for k in ["moderado", "moderada", "moderados", "moderadas"]):
            if "sibo" in txt or "receta" in txt or "plato" in txt or "opcion" in txt:
                return "mostrar_sibo_moderado"

        # "no apto"
        if any(k in txt for k in ["no recomendado", "no recomendados", "no apto", "evitar", "prohibido"]):
            return "mostrar_no_recomendado"

        # "ver opciones sibo", "menu sibo", "opciones sibo"
        if "sibo" in txt:
            if any(k in txt for k in ["ver", "mostrar", "opcion", "opciones", "menu", "listar", "apto", "aptas"]):
                return "mostrar_sibo_apto"
            return "mostrar_sibo_apto"

        # sugerir cambios
        if any(k in txt for k in ["sugerir", "sugerencia", "cambio", "reemplazar", "sin"]):
            return "sugerir_cambio"

        # crear orden
        if any(k in txt for k in ["quiero", "pedir", "ordenar", "traeme", "trae", "me gustaria", "me gustaría"]):
            return "crear_orden"

        # gusto
        if "no me gusta" in txt or "no me gustan" in txt or "no me agrada" in txt:
            return "gusto"
        if "quiero algo con" in txt or "me gustaria con" in txt or "quiero con" in txt:
            return "gusto"

        return "buscar_receta"

    def obtener_recetas_completas(self):
        q = """
        SELECT r.idReceta, r.nombre AS receta, i.nombre AS ingrediente, i.apto_sibo
        FROM recetas r
        JOIN receta_ingrediente ri ON r.idReceta = ri.idReceta
        JOIN ingredientes i ON ri.idIngrediente = i.idIngrediente;
        """
        self.cursor.execute(q)
        return self.cursor.fetchall()

    def analizar_recetas(self):
        filas = self.obtener_recetas_completas()
        recetas = {}
        for f in filas:
            recetas.setdefault(f["receta"], []).append(f["apto_sibo"])
        clasif = {}
        for receta, vals in recetas.items():
            c = Counter(vals)
            si = c.get("Si", 0)
            no = c.get("No", 0)
            moderado = c.get("Moderado", 0)
            total = sum(c.values())
            # reglas: si todos Si -> Apto, si mayoría No -> No, else Moderado
            if si == total:
                clasif[receta] = "Apto"
            elif no > si:
                clasif[receta] = "No"
            else:
                clasif[receta] = "Moderado"
        return clasif



    def recomendar_apto_sibo(self, mesa=None):
        clasif = self.analizar_recetas()
        recetas = [r for r, e in clasif.items() if e == "Apto"]
        recetas = self._filtrar_por_gustos(recetas, mesa)
        if mesa:
            self._set_ultima_lista(mesa, "apto")
        return recetas

    def recomendar_moderado(self, mesa=None):
        clasif = self.analizar_recetas()
        recetas = [r for r, e in clasif.items() if e == "Moderado"]
        recetas = self._filtrar_por_gustos(recetas, mesa)
        if mesa:
            self._set_ultima_lista(mesa, "moderado")
        return recetas

    def recomendar_no_apto(self, mesa=None):
        clasif = self.analizar_recetas()
        recetas = [r for r, e in clasif.items() if e == "No"]
        recetas = self._filtrar_por_gustos(recetas, mesa)
        if mesa:
            self._set_ultima_lista(mesa, "no")
        return recetas


    def _filtrar_por_gustos(self, recetas, mesa):
        if not mesa:
            return recetas
        s = str(mesa)
        sess = self.sessions.get(s)
        if not sess:
            return recetas
        rechazos = sess["gustos"].get("rechazos", [])
        if not rechazos:
            return recetas
        filtradas = []
        for r in recetas:
            rlow = r.lower()
            if any(rech.lower() in rlow for rech in rechazos):
                continue
            filtradas.append(r)
        return filtradas


    def _ensure_session(self, mesa):
        s = str(mesa)
        if s not in self.sessions:
            self.sessions[s] = {"ultima_lista": None, "gustos": {"preferencias": [], "rechazos": []}}
        return self.sessions[s]

    def _set_ultima_lista(self, mesa, tipo):
        sess = self._ensure_session(mesa)
        sess["ultima_lista"] = tipo


    def sugerir_cambio(self, nombre_parcial):
        nombre_parcial = self.limpiar_texto(nombre_parcial)
        # obtener lista de recetas
        self.cursor.execute("SELECT nombre FROM recetas;")
        todas_rows = [r["nombre"] for r in self.cursor.fetchall()]
        todas_limpias = [self.limpiar_texto(r) for r in todas_rows]
        # buscar coincidencias aproximadas
        matches = get_close_matches(nombre_parcial, todas_limpias, n=5, cutoff=0.55)
        if not matches:
            return f"No encontré ninguna receta similar a '{nombre_parcial}'. ¿Querés que te muestre opciones parecidas?"

        resultados = []
        for m in matches:
            # recuperar nombre real a la primera coincidencia
            idx = todas_limpias.index(m)
            receta_real = todas_rows[idx]
            # obtener ingredientes y aptitud
            q = """
            SELECT i.nombre AS ingrediente, i.apto_sibo
            FROM recetas r
            JOIN receta_ingrediente ri ON r.idReceta = ri.idReceta
            JOIN ingredientes i ON ri.idIngrediente = i.idIngrediente
            WHERE r.nombre = %s;
            """
            self.cursor.execute(q, (receta_real,))
            filas = self.cursor.fetchall()
            no_aptos = [f["ingrediente"] for f in filas if f["apto_sibo"] == "No"]
            if no_aptos:
                resultados.append(f"Podés pedir '{receta_real}' sin {', '.join(no_aptos)} para hacerlo apto SIBO.")
            else:
                resultados.append(f"Genial! '{receta_real}' ya es apto SIBO.")
        return "\n".join(resultados)


    def buscar_por_ingrediente(self, palabra):
        palabra = self.limpiar_texto(palabra)
        # lista de ingredientes
        self.cursor.execute("SELECT nombre FROM ingredientes;")
        ingredientes = [r["nombre"] for r in self.cursor.fetchall()]
        ingredientes_limpias = [self.limpiar_texto(i) for i in ingredientes]
        match = get_close_matches(palabra, ingredientes_limpias, n=1, cutoff=0.5)
        if not match:
            # sugerir alternativas
            suger = ", ".join(["pollo", "pescado", "tofu"])
            return f"No encontré el ingrediente '{palabra}'. ¿Quizás quisiste decir {suger}? 😊"
        ing_limpio = match[0]
        idx = ingredientes_limpias.index(ing_limpio)
        ing_real = ingredientes[idx]
        # buscar recetas que contengan ese ingrediente
        q = """
        SELECT DISTINCT r.nombre AS receta
        FROM recetas r
        JOIN receta_ingrediente ri ON r.idReceta = ri.idReceta
        JOIN ingredientes i ON ri.idIngrediente = i.idIngrediente
        WHERE LOWER(i.nombre) LIKE %s;
        """
        self.cursor.execute(q, (f"%{ing_real.lower()}%",))
        recetas = [r["receta"] for r in self.cursor.fetchall()]
        if recetas:
            return f"Platos que contienen '{ing_real}':\n" + "\n".join([f"- {r}" for r in recetas])
        return f"No tengo platos que usen '{ing_real}' en este momento."


    def actualizar_gustos(self, mensaje, mesa):
        msg = self.limpiar_texto(mensaje)
        sess = self._ensure_session(mesa)
        # "no me gusta "
        m = re.search(r'no me gusta (.+)', msg)
        if m:
            ing = m.group(1).strip()
            if ing:
                sess["gustos"]["rechazos"].append(ing)
                return f"Entendido! No te sugeriré platos con {ing}."
        # "quiero algo con "
        m2 = re.search(r'quiero (?:algo )?con (.+)', msg)
        if m2:
            pref = m2.group(1).strip()
            if pref:
                sess["gustos"]["preferencias"].append(pref)
                # devolver lista corta con ese ingrediente
                listado = self.buscar_por_ingrediente(pref)
                return f"Perfecto! Te muestro opciones con {pref}:\n{listado}"
        # "no me gustan las opciones"
        if "no me gusta las opciones" in msg or "no me gustaron" in msg or "no me gustan las opciones" in msg:
            ultima = sess.get("ultima_lista")
            if ultima == "apto":
                subs = self.recomendar_moderado(mesa)
                if subs:
                    return "Veo que no te convencieron las opciones aptas. Quizá te interesen estas moderadas:\n" + "\n".join(subs)
                return "No tengo moderadas para sugerir ahora. ¿Querés que contacte a un mozo?"
            elif ultima == "moderado":
                return "Parece que ninguna opción te convence, ¿Querés que contacte a un mozo para ayudarte?"
        return None


    def crear_orden_desde_texto(self, mensaje, mesa):
        # intento de encontrar una receta que coincida
        text = self.limpiar_texto(mensaje)
        # obtener lista de recetas y limpiarlas
        self.cursor.execute("SELECT nombre FROM recetas;")
        todas = [r["nombre"] for r in self.cursor.fetchall()]
        todas_limpias = [self.limpiar_texto(r) for r in todas]
        match = get_close_matches(text, todas_limpias, n=1, cutoff=0.5)
        if not match:
            busc = self.buscar_por_ingrediente(text)
            return f"No encontré exactamente ese plato. {busc}"

        # recuperar receta
        idx = todas_limpias.index(match[0])
        receta_real = todas[idx]

        # conocer clasificación
        clasif = self.analizar_recetas()
        estado = clasif.get(receta_real, "Desconocido")
        if estado == "No":
            return f"'{receta_real}' no es recomendable para SIBO."
        elif estado == "Moderado":
            # podemos preguntar si quiere adaptarlo
            return f"'{receta_real}' tiene ingredientes moderados. ¿Querés que lo adapte (quitar ingredientes) o envío la orden así?"
        else:
            # guardar orden
            self.guardar_orden(mesa, receta_real)
            return f"Pedido registrado: '{receta_real}' para la mesa {mesa}. ¡Ya lo envié a la cocina! 👨‍🍳"

    def guardar_orden(self, mesa, receta):
        q = "INSERT INTO ordenes (mesa, pedido, estado) VALUES (%s, %s, %s);"
        try:
            self.cursor.execute(q, (mesa, receta, "Pendiente"))
            self.conn.commit()
        except Exception as e:
            print(f"[SiBoti] Error guardando orden: {e}")
            self.conn.rollback()



    def predecir(self, mensaje, mesa=None):
        """
        Mensaje: texto del usuario
        mesa: opcional (número o identificador). Si se pasa, usamos/guardamos contexto en sessions.
        """
        if mesa is not None:
            self._ensure_session(mesa)

        intent = self.detectar_intencion(mensaje)
        # Detectar respuestas  de si / no
        texto = self.limpiar_texto(mensaje)
        if texto in ["si", "sí", "dale", "ok", "bueno", "claro"]:
            sess = self._ensure_session(mesa)
            ultima = sess.get("ultima_pregunta")

            if ultima == "mostrar_apto_sibo_pregunta":
                lista = self.recomendar_apto_sibo(mesa)
                if lista:
                    sess["ultima_pregunta"] = None
                    return "Recetas aptas SIBO:\n" + "\n".join([f"✅ {r}" for r in lista])
                else:
                    return "Por ahora no tengo platos 100% aptos registrados"
                
            if ultima == "mostrar_moderado_pregunta":
                lista = self.recomendar_moderado(mesa)
                sess["ultima_pregunta"] = None
                if lista:
                    return "Recetas moderadas (se pueden adaptar):\n" + "\n".join([f"⚠️ {r}" for r in lista])
                else:
                    return "No tengo platos moderados en este momento."
                
            if ultima == "confirmar_orden":
                sess["ultima_pregunta"] = None
                return "Perfecto, envío el pedido a la cocina."
            
            return random.choice([
                "Genial!, ¿querés que te muestre el menú apto SIBO?",
                "Perfecto!, te muestro opciones aptas o moderadas?"
            ])

        elif texto in ["no", "nono","nop", "nah", "no gracias"]:
            sess = self._ensure_session(mesa)
            ultima = sess.get("ultima_pregunta")

            if ultima == "mostrar_apto_sibo_pregunta":
                sess["ultima_pregunta"] = None
                return "Ok, no te muestro el menú por ahora. ¿Querés que te recomiende algo según tus gustos?"
            if ultima == "mostrar_moderado_pregunta":
                sess["ultima_pregunta"] = None
                return "Perfecto!. Si querés, puedo sugerirte algo personalizado según tus gustos."

            if ultima == "confirmar_orden":
                sess["ultima_pregunta"] = None
                return "Pedido cancelado. Si querés cambiar de plato, decime cuál."
            return "Sin problema. Cuando quieras, pedime opciones o sugerencias."


        if intent == "gusto":
            resp = self.actualizar_gustos(mensaje, mesa)
            if resp:
                return resp


        if intent == "saludo":
            sess = self._ensure_session(mesa)
            sess["ultima_pregunta"] = "mostrar_apto_sibo_pregunta"
            return "¡Hola! Soy SiBoti, tu asistente SIBO. ¿Querés que te muestre platos aptos para SIBO?"


        if intent == "personal":
            return random.choice([
                "Jaja, soy una IA creada para ayudar con el menú SIBO",
                "Soy SiBoti 🤖, el asistente gastronómico del restaurante."
            ])

        if intent == "fuera_tema":
            return "Mi especialidad es ayudarte con el menú SIBO y las recetas del restaurante. Si querés, puedo mostrarte opciones aptas o moderadas."

        if intent == "mostrar_sibo_apto":
            lista = self.recomendar_apto_sibo(mesa)
            if not lista:
                return "Por ahora no tengo platos 100% aptos registrados"
            sess = self._ensure_session(mesa)
            sess["ultima_pregunta"] = "mostrar_moderado_pregunta"
            return "Recetas aptas SIBO:\n" + "\n".join([f"✅ {r}" for r in lista]) + "\n\n¿Querés que te muestre también las opciones moderadas?"


        if intent == "mostrar_sibo_moderado":
            lista = self.recomendar_moderado(mesa)
            if not lista:
                return "No encontré platos moderados en este momento."
            return "⚠️ Recetas moderadas (se pueden adaptar):\n" + "\n".join([f"⚠️ {r}" for r in lista])

        if intent == "mostrar_no_recomendado":
            lista = self.recomendar_no_apto(mesa)
            if not lista:
                return "No hay platos clasificados como no recomendables."
            return "🚫 Platos no recomendados para SIBO:\n" + "\n".join([f"🚫 {r}" for r in lista])

        if intent == "sugerir_cambio":
            nombre = re.sub(r'(sugerir|sugerencia|cambio|reemplazar|sin|para)', '', mensaje, flags=re.I).strip()
            if not nombre:
                return "¿Podés decirme el nombre del plato para sugerir un cambio?"
            return self.sugerir_cambio(nombre)

        if intent == "crear_orden":
            if mesa is None:
                return "¿En qué mesa estás? Indicalo para registrar el pedido (ej: 'mesa 3')."
            return self.crear_orden_desde_texto(mensaje, mesa)

        # buscar por ingrediente o receta
        # primero probamos buscar por ingrediente
        busc_ing = self.buscar_por_ingrediente(mensaje)
        # si la respuesta contiene "Platos que contienen", devolvemos eso
        if busc_ing and busc_ing.startswith("Platos"):
            return busc_ing

        # si no, intentamos sugerir cambio si parece una receta
        suger = self.sugerir_cambio(mensaje)
        # si suger devolvió "No encontré", entonces retorna
        if "No encontré ninguna receta similar" not in suger:
            return suger

        # fallback final
        return random.choice([
            "No estoy seguro de haber entendido ¿Querés que te muestre platos aptos para SIBO?",
            "Perdón, ¿podés repetirme eso? Puedo recomendarte platos aptos SIBO si querés 🍽️",
            "Interesante! pero creo que eso se escapa de mi menú. ¿Querés que te muestre opciones sin ajo o sin cebolla?"
        ])
