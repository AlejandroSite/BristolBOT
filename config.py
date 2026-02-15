import os
from dotenv import load_dotenv

load_dotenv()

# === WhatsApp / Meta ===
ACCESS_TOKEN = os.getenv("WHATSAPP_TOKEN")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")

# === IA ===
GROQ_API_TOKEN = os.getenv("GROQ_API_TOKEN")

# === Google Sheets ===
# Definimos los nombres exactamente como los pide el resto del programa
EXCEL_NAME = os.getenv("EXCEL_NAME", "pagos_bristol")
GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "credentials.json")
#GOOGLE_DRIVE_FOLDER_ID = os.getenv("GOOGLE_DRIVE_FOLDER_ID")

# === Negocio ===
ALIAS_VALIDO = os.getenv("ALIAS_VALIDO", "bristol.pame.mp")
CUOTA_VENCE_DIA = 10
RECARGO_PORCENTAJE = 0.1