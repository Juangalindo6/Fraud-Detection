"""Punto de extensión para los modelos de detección.

Por ahora la app NO trae modelos. Cuando se agreguen, cada modelo será una clase
que cumpla la interfaz `Detector` y se registrará en `DETECTORES`.
"""

from __future__ import annotations

from typing import Protocol

import pandas as pd

from detector_fraude.nucleo.datos import Comprobantes

# Columnas que todo detector debe devolver, una fila por comprobante.
COLUMNAS_RESULTADO = ["riesgo", "tipo_probable", "motivo"]


class Detector(Protocol):
    nombre: str

    def analizar(self, comprobantes: Comprobantes) -> pd.DataFrame:
        """Devuelve un DataFrame con COLUMNAS_RESULTADO y el mismo índice de la tabla."""
        ...


class SinModelo:
    """Detector vacío: deja el flujo de la app listo mientras no hay modelos."""

    nombre = "Sin modelo (pendiente)"

    def analizar(self, comprobantes: Comprobantes) -> pd.DataFrame:
        return pd.DataFrame(
            {"riesgo": pd.NA, "tipo_probable": "", "motivo": "Aún no hay un modelo cargado"},
            index=comprobantes.tabla.index,
        )


DETECTORES: list[Detector] = [SinModelo()]
