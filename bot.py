import re
import time
import logging
from image_interpreter import InterpreteImagen
from excel_manager_sheets import ExcelManager
from datetime import datetime

logger = logging.getLogger("BristolBOT")

# --- Límites de seguridad ---
MAX_NOMBRE_LENGTH = 100
MAX_USUARIOS_EN_MEMORIA = 500
TTL_USUARIO_SEGUNDOS = 1800  # 30 minutos
FORMULA_CHARS = re.compile(r"^[=+\-@]")


class BristolBot:
    def __init__(self):
        self.img = InterpreteImagen()
        self.excel = ExcelManager()
        self.usuarios = {}  # {user_id: {"alumno": str, "timestamp": float}}

    # --- Limpieza de entradas expiradas ---
    def _limpiar_expirados(self):
        ahora = time.time()
        expirados = [
            uid for uid, data in self.usuarios.items()
            if ahora - data.get("timestamp", 0) > TTL_USUARIO_SEGUNDOS
        ]
        for uid in expirados:
            del self.usuarios[uid]

    # --- Sanitización de texto ---
    @staticmethod
    def _sanitizar_texto(texto: str) -> str | None:
        """Devuelve el texto limpio o None si es peligroso."""
        texto = texto.strip()

        if len(texto) > MAX_NOMBRE_LENGTH:
            return None

        # Bloquear fórmulas de spreadsheet
        if FORMULA_CHARS.match(texto):
            return None

        # Quitar caracteres de control (excepto espacios normales)
        texto = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", texto)

        return texto if texto else None

    def bienvenida(self):
        return (
            "👋 Hola, soy *BristolBot*, asistente del *Bristol English Institute*.\n\n"
            "📌 Para registrar un pago:\n"
            "1️⃣ Escribí el *nombre del alumno*\n"
            "2️⃣ Enviá la *foto del comprobante*\n\n"
            "📚 Escribí *info* para información del instituto."
        )

    def recibir_texto(self, user_id, texto):
        texto = texto.strip()

        if texto.lower() in ["info", "información"]:
            return (
                "📚 *Bristol English Institute*\n"
                "📍 Salta 2595\n"
                "🕘 9 a 12 / 14 a 21\n"
                "👩‍🏫 Pamela Cetta"
            )

        # Sanitizar entrada
        nombre_limpio = self._sanitizar_texto(texto)
        if nombre_limpio is None:
            return (
                "⚠️ El nombre ingresado no es válido.\n"
                "Por favor, escribí solo el *nombre del alumno* (máximo 100 caracteres)."
            )

        # Limpiar usuarios expirados antes de agregar más
        self._limpiar_expirados()

        # Verificar límite de memoria
        if len(self.usuarios) >= MAX_USUARIOS_EN_MEMORIA and user_id not in self.usuarios:
            logger.warning("⚠️ Límite de usuarios en memoria alcanzado")
            return "⚠️ El sistema está ocupado. Por favor, reintentá en unos minutos."

        self.usuarios[user_id] = {
            "alumno": nombre_limpio,
            "timestamp": time.time(),
        }

        return (
            f"✅ Nombre registrado: *{nombre_limpio}*\n"
            "📸 Ahora enviá la foto del comprobante para finalizar el registro."
        )

    def recibir_imagen(self, user_id, img_id):
        # Si mandan foto sin decir el nombre antes
        if user_id not in self.usuarios:
            return "⚠️ Por favor, primero decime el *nombre del alumno* y luego enviá la foto."

        data_usuario = self.usuarios[user_id]

        # Verificar si expiró
        if time.time() - data_usuario.get("timestamp", 0) > TTL_USUARIO_SEGUNDOS:
            del self.usuarios[user_id]
            return "⏰ Tu sesión expiró. Por favor, volvé a escribir el *nombre del alumno*."

        alumno = data_usuario["alumno"]

        # Preparamos los datos para el Excel
        registro = {
            "pagador": "Verificar en foto",
            "alumno": alumno,
            "monto_base": 0,
            "medio": "Transferencia",
            "fecha_comprobante": datetime.now().strftime("%d/%m/%Y"),
            "alias_ok": "Pendiente",
            "telefono": user_id,
            "observaciones": "Registrado por BristolBot"
        }

        try:
            self.excel.registrar_pago(registro)

            # Limpiamos la memoria para este usuario
            del self.usuarios[user_id]

            return (
                "✅ *¡Comprobante recibido con éxito!*\n\n"
                f"👤 Alumno: {alumno}\n"
                "⏳ Lo validaremos a la brevedad. ¡Muchas gracias!"
            )
        except Exception as e:
            logger.error(f"Error al guardar en Excel: {e}", exc_info=True)
            return "❌ Tuve un problema al guardar los datos. Por favor, reintentá en unos momentos."
