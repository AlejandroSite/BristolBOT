import logging
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from config import EXCEL_NAME, GOOGLE_APPLICATION_CREDENTIALS
from cuotas_manager import estado_cuota

logger = logging.getLogger("BristolBOT")

COLUMNAS = [
    "Fecha carga", "Pagador", "Alumno", "Monto base",
    "Recargo %", "Monto final", "Estado cuota",
    "Medio de pago", "Fecha comprobante",
    "Alias verificado", "Telefono", "Observaciones"
]

class ExcelManager:
    def __init__(self):
        # Configuración de credenciales (google-auth moderno)
        scopes = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]

        try:
            creds = Credentials.from_service_account_file(
                GOOGLE_APPLICATION_CREDENTIALS, scopes=scopes
            )
            self.client = gspread.authorize(creds)
            
            # SOLO ABRIR: No se toca la estructura de creación para evitar el error 403
            self.spreadsheet = self.client.open(EXCEL_NAME)
            print(f"✅ Conexión exitosa al Excel existente: {EXCEL_NAME}")
                
        except gspread.SpreadsheetNotFound:
            print(f"❌ ERROR: No se encuentra el archivo '{EXCEL_NAME}' en Google Drive.")
            raise Exception("Asegurate de que el nombre coincida y el mail del bot sea Editor.")
        except Exception as e:
            print(f"❌ Error crítico de conexión: {e}")
            raise e

    def _obtener_o_crear_hoja_mes(self):
        nombre = datetime.now().strftime("%Y-%m")
        try:
            return self.spreadsheet.worksheet(nombre)
        except gspread.WorksheetNotFound:
            # Si el mes no existe, lo crea dentro de tu Excel
            sheet = self.spreadsheet.add_worksheet(
                title=nombre, rows="1000", cols=len(COLUMNAS)
            )
            sheet.append_row(COLUMNAS)
            return sheet

    def registrar_pago(self, data):
        try:
            sheet = self._obtener_o_crear_hoja_mes()
            hoy = datetime.now()
            cuota = estado_cuota(hoy)

            monto_base = float(data.get("monto_base", 0))
            monto_final = monto_base * cuota["factor"]

            fila = [
                hoy.strftime("%d/%m/%Y %H:%M"),
                data.get("pagador", ""),
                data.get("alumno", ""),
                monto_base,
                f"{int(cuota['recargo'] * 100)}%",
                monto_final,
                cuota["estado"],
                data.get("medio", ""),
                data.get("fecha_comprobante", ""),
                data.get("alias_ok", ""),
                data.get("telefono", ""),
                data.get("observaciones", "")
            ]

            sheet.append_row(fila)
            return True
        except Exception as e:
            print(f"❌ Error al registrar fila: {e}")
            return False

    def obtener_datos_mes(self):
        try:
            return self._obtener_o_crear_hoja_mes().get_all_records()
        except Exception as e:
            logger.error(f"Error al obtener datos del mes: {e}", exc_info=True)
            return []