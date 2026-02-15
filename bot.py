from image_interpreter import InterpreteImagen
from excel_manager_sheets import ExcelManager
from datetime import datetime

class BristolBot:
    def __init__(self):
        self.img = InterpreteImagen()
        self.excel = ExcelManager()
        self.usuarios = {}

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

        # Guardamos el nombre en memoria para cuando llegue la foto
        self.usuarios[user_id] = {"alumno": texto}

        return (
            f"✅ Nombre registrado: *{texto}*\n"
            "📸 Ahora enviá la foto del comprobante para finalizar el registro."
        )

    def recibir_imagen(self, user_id, img_id):
        # Si mandan foto sin decir el nombre antes
        if user_id not in self.usuarios:
            return "⚠️ Por favor, primero decime el *nombre del alumno* y luego enviá la foto."

        alumno = self.usuarios[user_id]["alumno"]

        # Preparamos los datos para el Excel
        registro = {
            "pagador": "Verificar en foto", 
            "alumno": alumno,
            "monto_base": 0,
            "medio": "Transferencia",
            "fecha_comprobante": datetime.now().strftime("%d/%m/%Y"),
            "alias_ok": "Pendiente",
            "telefono": user_id, # Guardamos el número de quien escribe
            "observaciones": "Registrado por BristolBot"
        }

        try:
            # Creamos una fila nueva directamente
            self.excel.registrar_pago(registro)
            
            # Limpiamos la memoria para este usuario
            del self.usuarios[user_id]
            
            return (
                "✅ *¡Comprobante recibido con éxito!*\n\n"
                f"👤 Alumno: {alumno}\n"
                "⏳ Lo validaremos a la brevedad. ¡Muchas gracias!"
            )
        except Exception as e:
            print(f"Error al guardar en Excel: {e}")
            return "❌ Tuve un problema al guardar los datos. Por favor, reintentá en unos momentos."