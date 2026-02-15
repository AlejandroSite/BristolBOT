from datetime import datetime

# CONFIGURACIÓN
DIA_VENCIMIENTO = 10
RECARGO = 0.1  # 10% (modificable)


def estado_cuota(fecha: datetime):
    """
    Devuelve el estado de la cuota según la fecha actual
    """

    if fecha.day <= DIA_VENCIMIENTO:
        return {
            "estado": "En término",
            "recargo": 0.0,
            "factor": 1.0
        }
    else:
        return {
            "estado": "Con recargo",
            "recargo": RECARGO,
            "factor": 1 + RECARGO
        }
