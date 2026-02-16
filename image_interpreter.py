import base64
import json
import re
import logging
from groq import Groq
from config import GROQ_API_TOKEN, ALIAS_VALIDO

logger = logging.getLogger("BristolBOT")

class InterpreteImagen:
    def __init__(self):
        self.client = Groq(api_key=GROQ_API_TOKEN)

    def _imagen_base64(self, img_bytes):
        return base64.b64encode(img_bytes).decode("utf-8")

    def analizar_comprobante(self, img_bytes):
        img64 = self._imagen_base64(img_bytes)

        prompt = f"""
Eres un sistema experto en comprobantes de transferencia ARGENTINOS.

Analiza la imagen y responde SOLO en JSON.

Si NO es un comprobante:
{{"es_comprobante": false}}

Si es comprobante, extrae:
- nombre_pagador
- fecha
- monto
- medio_pago
- alias
- alias_valido (true solo si es "{ALIAS_VALIDO}")
"""

        try:
            response = self.client.chat.completions.create(
                model="meta-llama/llama-4-scout-17b-16e-instruct",
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url",
                         "image_url": {"url": f"data:image/jpeg;base64,{img64}"}}
                    ]
                }],
                temperature=0.2,
                max_tokens=800
            )

            raw = response.choices[0].message.content

            # Extraer JSON de la respuesta (puede venir envuelto en ```json ... ```)
            json_match = re.search(r"\{.*\}", raw, re.DOTALL)
            if not json_match:
                logger.warning(f"LLM no devolvió JSON válido: {raw[:200]}")
                return {"es_comprobante": False, "error": "Respuesta no válida del análisis"}

            parsed = json.loads(json_match.group())
            return parsed

        except json.JSONDecodeError as e:
            logger.error(f"Error parseando JSON del LLM: {e}")
            return {"es_comprobante": False, "error": "JSON inválido"}
        except Exception as e:
            logger.error(f"Error en análisis de comprobante: {e}", exc_info=True)
            return {"es_comprobante": False, "error": str(e)}

