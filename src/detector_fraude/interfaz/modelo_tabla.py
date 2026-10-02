"""Adaptadores para mostrar un DataFrame de pandas en una QTableView."""

from __future__ import annotations

import pandas as pd
from PySide6.QtCore import QAbstractTableModel, QModelIndex, QRectF, Qt
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import QStyledItemDelegate

from detector_fraude.interfaz.tema import Paleta


ENCABEZADOS = {
    "riesgo": "Riesgo",
    "tipo_probable": "Tipo probable",
    "motivo": "Motivo",
    "tipo": "Tipo",
    "numero": "Número",
    "ano": "Año",
    "mes": "Mes",
    "dia": "Día",
    "misstate": "Etiqueta",
}


def formato_numero(valor: float) -> str:
    """Formato colombiano: punto para miles y coma para decimales."""
    texto = f"{valor:,.2f}"
    return texto.replace(",", "_").replace(".", ",").replace("_", ".")


class ModeloTabla(QAbstractTableModel):
    def __init__(self, tabla: pd.DataFrame | None = None, parent=None):
        super().__init__(parent)
        self._tabla = tabla if tabla is not None else pd.DataFrame()
        self.color_suave: QColor | None = None  # color de los ceros, para que no distraigan

    @property
    def tabla(self) -> pd.DataFrame:
        return self._tabla

    def cambiar_tabla(self, tabla: pd.DataFrame) -> None:
        self.beginResetModel()
        self._tabla = tabla
        self.endResetModel()

    def rowCount(self, parent=QModelIndex()) -> int:
        return 0 if parent.isValid() else len(self._tabla)

    def columnCount(self, parent=QModelIndex()) -> int:
        return 0 if parent.isValid() else len(self._tabla.columns)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        valor = self._tabla.iat[index.row(), index.column()]
        if role == Qt.DisplayRole:
            if pd.isna(valor):
                return ""
            if isinstance(valor, float):
                return formato_numero(valor)
            return str(valor)
        if role == Qt.ForegroundRole and self.color_suave is not None and isinstance(valor, float) and valor == 0:
            return self.color_suave
        if role == Qt.TextAlignmentRole and isinstance(valor, (int, float)) and not isinstance(valor, bool):
            return int(Qt.AlignRight | Qt.AlignVCenter)
        if role == Qt.UserRole:
            return valor
        return None

    def headerData(self, seccion, orientacion, role=Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return None
        if orientacion == Qt.Horizontal:
            nombre = str(self._tabla.columns[seccion])
            return ENCABEZADOS.get(nombre, nombre)
        return str(seccion + 1)


class DelegadoRiesgo(QStyledItemDelegate):
    """Pinta el riesgo como una píldora de color: alto, medio o bajo."""

    def __init__(self, paleta: Paleta, parent=None):
        super().__init__(parent)
        self.paleta = paleta

    def paint(self, pintor: QPainter, opcion, index):
        valor = index.data(Qt.UserRole)
        if valor is None or pd.isna(valor):
            texto, color, fondo = "Pendiente", self.paleta.texto_suave, self.paleta.superficie_alta
        elif valor >= 0.7:
            texto, color, fondo = f"Alto · {valor:.0%}", self.paleta.peligro, self.paleta.peligro_fondo
        elif valor >= 0.4:
            texto, color, fondo = f"Medio · {valor:.0%}", self.paleta.alerta, self.paleta.alerta_fondo
        else:
            texto, color, fondo = f"Bajo · {valor:.0%}", self.paleta.exito, self.paleta.exito_fondo

        pintor.save()
        pintor.setRenderHint(QPainter.Antialiasing)
        metricas = opcion.fontMetrics
        ancho = metricas.horizontalAdvance(texto) + 20
        alto = metricas.height() + 6
        r = opcion.rect
        caja = QRectF(r.x() + 8, r.y() + (r.height() - alto) / 2, ancho, alto)
        pintor.setPen(Qt.NoPen)
        pintor.setBrush(QColor(fondo))
        pintor.drawRoundedRect(caja, alto / 2, alto / 2)
        pintor.setPen(QColor(color))
        pintor.drawText(caja, Qt.AlignCenter, texto)
        pintor.restore()
