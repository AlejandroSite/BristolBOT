import logging
from datetime import datetime
import requests
from apscheduler.schedulers.background import BackgroundScheduler
from excel_manager_sheets import ExcelManager
from config import ACCESS_TOKEN, PHONE_NUMBER_ID

logger = logging.getLogger("BristolBOT")

excel_manager = ExcelManager()

def enviar_mensaje_whatsapp(telefono: str, mensaje: str):
    url = f"https://graph.facebook.com/v24.0/{PHONE_NUMBER_ID}/messages"

    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }

    data = {
        "messaging_product": "whatsapp",
        "to": telefono,
        "type": "text",
        "text": {"body": mensaje}
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=10)
        if response.status_code == 200:
            logger.info(f"✅ Mensaje enviado a {telefono}")
        else:
            logger.error(f"❌ Error Meta: {response.status_code} - {response.text}")
    except Exception as e:
        logger.error(f"⚠️ Error de conexión: {e}", exc_info=True)

def aviso_pre_vencimiento():
    logger.info("Iniciando envío de avisos preventivos...")
    registros = excel_manager.obtener_datos_mes()

    mensaje_friendly = (
        "Hola! 📢 *Aviso de cuota*\n\n"
        "Recordá que pagando antes del día 10 evitás recargos.\n"
        "✅ Enviá el comprobante por este medio.\n\n"
        "¡Thank you so much! ✨"
    )

    for fila in registros:
        if fila.get("Estado cuota") == "Pendiente":
            telefono = fila.get("Telefono")
            if telefono:
                enviar_mensaje_whatsapp(telefono, mensaje_friendly)

def aviso_post_vencimiento():
    logger.info("Iniciando envío de avisos con recargo...")
    registros = excel_manager.obtener_datos_mes()

    for fila in registros:
        if fila.get("Estado cuota") == "Pendiente":
            alumno = fila.get("Alumno", "estudiante")
            monto = fila.get("Monto final", "la cuota")

            mensaje_recargo = (
                f"⚠️ *Aviso de vencimiento*\n\n"
                f"Hola, el pago de {alumno} está vencido.\n"
                f"Aplica recargo.\n"
                f"Monto: ${monto}\n\n"
                f"Enviá el comprobante cuando pagues."
            )

            telefono = fila.get("Telefono")
            if telefono:
                enviar_mensaje_whatsapp(telefono, mensaje_recargo)

def iniciar_scheduler():
    scheduler = BackgroundScheduler(timezone="America/Argentina/Buenos_Aires")

    scheduler.add_job(aviso_pre_vencimiento, "cron", day=8, hour=9, minute=0)
    scheduler.add_job(aviso_post_vencimiento, "cron", day=12, hour=0, minute=0)

    scheduler.start()
