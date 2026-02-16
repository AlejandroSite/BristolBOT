import hmac
import hashlib
import logging
from fastapi import FastAPI, Request, Response
from config import VERIFY_TOKEN, APP_SECRET
from scheduler import enviar_mensaje_whatsapp, iniciar_scheduler
from bot import BristolBot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("BristolBOT")

app = FastAPI()
bot = BristolBot()

# Iniciar el scheduler de avisos automáticos
iniciar_scheduler()

# ------------------------------------------
# VERIFICACIÓN DE FIRMA DEL WEBHOOK (Meta)
# ------------------------------------------
def verificar_firma(body: bytes, signature: str) -> bool:
    """Verifica la firma X-Hub-Signature-256 enviada por Meta."""
    if not signature or not signature.startswith("sha256="):
        return False
    expected = "sha256=" + hmac.new(
        APP_SECRET.encode(), body, hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)

# ------------------------
# VERIFICACIÓN DEL WEBHOOK
# ------------------------
@app.get("/webhook")
async def verify_webhook(request: Request):
    params = request.query_params

    if (
        params.get("hub.mode") == "subscribe"
        and params.get("hub.verify_token") == VERIFY_TOKEN
    ):
        return int(params.get("hub.challenge"))

    return Response(content="Verificación fallida", status_code=403)

# ------------------------
# RECEPCIÓN DE MENSAJES
# ------------------------
@app.post("/webhook")
async def receive_message(request: Request):
    body = await request.body()

    # Verificar firma de Meta
    signature = request.headers.get("X-Hub-Signature-256", "")
    if not verificar_firma(body, signature):
        logger.warning("⚠️ Firma inválida — request rechazado")
        return Response(content="Firma inválida", status_code=403)

    import json
    data = json.loads(body)
    logger.info("📩 Webhook recibido")

    try:
        value = data["entry"][0]["changes"][0]["value"]

        if "messages" not in value:
            return {"status": "ignored"}

        message = value["messages"][0]
        from_number = message["from"]

        # TEXTO
        if message["type"] == "text":
            text = message["text"]["body"]
            logger.info(f"📨 Texto de {from_number}")
            respuesta = bot.recibir_texto(from_number, text)
            enviar_mensaje_whatsapp(from_number, respuesta)

        # IMAGEN
        elif message["type"] == "image":
            img_id = message["image"]["id"]
            logger.info(f"📷 Imagen de {from_number}")
            respuesta = bot.recibir_imagen(from_number, img_id)
            enviar_mensaje_whatsapp(from_number, respuesta)

        return {"status": "ok"}

    except KeyError as e:
        logger.error(f"❌ Campo faltante en payload: {e}", exc_info=True)
        return {"status": "error", "detail": "Payload inválido"}
    except Exception as e:
        logger.error(f"❌ Error procesando mensaje: {e}", exc_info=True)
        return {"status": "error"}

