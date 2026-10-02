"""Adaptador para mostrar un DataFrame de pandas en una QTableView."""

from __future__ import annotations

import pandas as pd
from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt


class ModeloTabla(QAbstractTableModel):
    def __init__(self, tabla: pd.DataFrame | None = None, parent=None):
        super().__init__(parent)
        self._tabla = tabla if tabla is not None else pd.DataFrame()

    def cambiar_tabla(self, tabla: pd.DataFrame) -> None:
        self.beginResetModel()
        self._tabla = tabla
        self.endResetModel()

    def rowCount(self, parent=QModelIndex()) -> int:
        return 0 if parent.isValid() else len(self._tabla)

    def columnCount(self, parent=QModelIndex()) -> int:
        return 0 if parent.isValid() else len(self._tabla.columns)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or role != Qt.DisplayRole:
            return None
        valor = self._tabla.iat[index.row(), index.column()]
        if pd.isna(valor):
            return ""
        if isinstance(valor, float):
            return f"{valor:,.2f}"
        return str(valor)

    def headerData(self, seccion, orientacion, role=Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return None
        if orientacion == Qt.Horizontal:
            return str(self._tabla.columns[seccion])
        return str(seccion + 1)
