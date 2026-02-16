import os
from dotenv import load_dotenv

load_dotenv()

# === WhatsApp / Meta ===
ACCESS_TOKEN = os.getenv("WHATSAPP_TOKEN")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
APP_SECRET = os.getenv("APP_SECRET")  # Para verificar firma del webhook

# === IA ===
GROQ_API_TOKEN = os.getenv("GROQ_API_TOKEN")

# === Google Sheets ===
EXCEL_NAME = os.getenv("EXCEL_NAME", "pagos_bristol")
GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "credentials.json")

# === Negocio ===
ALIAS_VALIDO = os.getenv("ALIAS_VALIDO", "bristol.pame.mp")
CUOTA_VENCE_DIA = 10
RECARGO_PORCENTAJE = 0.1

# === Validación de variables críticas al inicio ===
_REQUIRED = {
    "WHATSAPP_TOKEN": ACCESS_TOKEN,
    "VERIFY_TOKEN": VERIFY_TOKEN,
    "PHONE_NUMBER_ID": PHONE_NUMBER_ID,
    "APP_SECRET": APP_SECRET,
}

_missing = [name for name, val in _REQUIRED.items() if not val]
if _missing:
    raise RuntimeError(
        f"❌ Faltan variables de entorno obligatorias: {', '.join(_missing)}. "
        "Revisá tu archivo .env"
    )