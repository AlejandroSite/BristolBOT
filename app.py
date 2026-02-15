from fastapi import FastAPI, Request, Response
from config import VERIFY_TOKEN
from scheduler import enviar_mensaje_whatsapp
from bot import BristolBot

app = FastAPI()
bot = BristolBot()

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

    return {"error": "Verificación fallida"}

# ------------------------
# RECEPCIÓN DE MENSAJES
# ------------------------
@app.post("/webhook")
async def receive_message(request: Request):
    data = await request.json()
    print("📩 Webhook recibido:", data)

    try:
        value = data["entry"][0]["changes"][0]["value"]

        if "messages" not in value:
            return {"status": "ignored"}

        message = value["messages"][0]
        from_number = message["from"]

        # TEXTO
        if message["type"] == "text":
            text = message["text"]["body"]
            print(f"📨 Texto de {from_number}: {text}")
            respuesta = bot.recibir_texto(from_number, text)
            enviar_mensaje_whatsapp(from_number, respuesta)

        # IMAGEN
        elif message["type"] == "image":
            img_id = message["image"]["id"]
            print(f"📷 Imagen de {from_number}: {img_id}")
            respuesta = bot.recibir_imagen(from_number, img_id)
            enviar_mensaje_whatsapp(from_number, respuesta)

        return {"status": "ok"}

    except Exception as e:
        print("❌ Error procesando mensaje:", e)
        return {"status": "error"}
