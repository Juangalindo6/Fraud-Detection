"""Piezas visuales reutilizables: tarjetas, zona de arrastre, avisos y menú lateral."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from detector_fraude.interfaz import iconos

EXTENSIONES_CSV = {".csv"}


def etiqueta(texto: str, nombre_objeto: str = "", ajustar: bool = False) -> QLabel:
    e = QLabel(texto)
    if nombre_objeto:
        e.setObjectName(nombre_objeto)
    e.setWordWrap(ajustar)
    return e


def sombra(widget: QWidget, oscuro: bool = False) -> None:
    efecto = QGraphicsDropShadowEffect(widget)
    efecto.setBlurRadius(24)
    efecto.setOffset(0, 4)
    efecto.setColor(QColor(0, 0, 0, 70 if oscuro else 18))
    widget.setGraphicsEffect(efecto)


class Tarjeta(QFrame):
    def __init__(self, parent=None, margen: int = 20, espacio: int = 12):
        super().__init__(parent)
        self.setObjectName("Tarjeta")
        self.cuerpo = QVBoxLayout(self)
        self.cuerpo.setContentsMargins(margen, margen, margen, margen)
        self.cuerpo.setSpacing(espacio)


class TarjetaDato(Tarjeta):
    """Tarjeta con un número grande y su nombre (por ejemplo, "Comprobantes")."""

    def __init__(self, nombre: str, parent=None):
        super().__init__(parent, margen=18, espacio=4)
        self.nombre = etiqueta(nombre.upper(), "DatoNombre")
        self.valor = etiqueta("—", "DatoValor")
        self.cuerpo.addWidget(self.nombre)
        self.cuerpo.addWidget(self.valor)

    def mostrar(self, valor: object) -> None:
        self.valor.setText(f"{valor:,}".replace(",", ".") if isinstance(valor, int) else str(valor))


class Aviso(QLabel):
    """Franja de color para avisos. nivel: info, alerta, exito o error."""

    def __init__(self, texto: str, nivel: str = "info", parent=None):
        super().__init__(texto, parent)
        self.setObjectName("Aviso")
        self.setProperty("nivel", nivel)
        self.setWordWrap(True)


class ZonaArrastre(QFrame):
    """Área grande donde se suelta o se elige el CSV."""

    archivo_elegido = Signal(Path)
    pedir_dialogo = Signal()

    def __init__(self, color_icono: str, parent=None):
        super().__init__(parent)
        self.setObjectName("ZonaArrastre")
        self.setAcceptDrops(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(240)

        self.icono = QLabel()
        self.icono.setAlignment(Qt.AlignCenter)
        self.cambiar_color(color_icono)
        titulo = etiqueta("Arrastra aquí tu CSV de comprobantes", "ZonaTitulo")
        titulo.setAlignment(Qt.AlignCenter)
        detalle = etiqueta("o haz clic para buscarlo en tu equipo", "TextoSuave")
        detalle.setAlignment(Qt.AlignCenter)
        self.boton = QPushButton("Elegir archivo")
        self.boton.setObjectName("Primario")
        self.boton.setCursor(Qt.PointingHandCursor)
        self.boton.clicked.connect(self.pedir_dialogo)

        capa = QVBoxLayout(self)
        capa.setSpacing(10)
        capa.addStretch()
        capa.addWidget(self.icono)
        capa.addWidget(titulo)
        capa.addWidget(detalle)
        capa.addSpacing(6)
        capa.addWidget(self.boton, alignment=Qt.AlignCenter)
        capa.addStretch()

    def cambiar_color(self, color: str) -> None:
        self.icono.setPixmap(iconos.pixmap("subir", color, 44))

    def _resaltar(self, activa: bool) -> None:
        self.setProperty("activa", "true" if activa else "false")
        self.style().unpolish(self)
        self.style().polish(self)

    def mousePressEvent(self, evento):
        if evento.button() == Qt.LeftButton:
            self.pedir_dialogo.emit()

    def dragEnterEvent(self, evento):
        if self._ruta_csv(evento.mimeData()):
            evento.acceptProposedAction()
            self._resaltar(True)

    def dragLeaveEvent(self, evento):
        self._resaltar(False)

    def dropEvent(self, evento):
        self._resaltar(False)
        ruta = self._ruta_csv(evento.mimeData())
        if ruta:
            self.archivo_elegido.emit(ruta)

    @staticmethod
    def _ruta_csv(datos) -> Path | None:
        for url in datos.urls() if datos.hasUrls() else []:
            ruta = Path(url.toLocalFile())
            if ruta.suffix.lower() in EXTENSIONES_CSV:
                return ruta
        return None


class BotonNav(QPushButton):
    def __init__(self, texto: str, nombre_icono: str, parent=None):
        super().__init__(f"  {texto}", parent)
        self.setObjectName("BotonNav")
        self.nombre_icono = nombre_icono
        self.setCheckable(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setIconSize(QSize(18, 18))

    def colorear(self, normal: str, activo: str) -> None:
        self.setIcon(iconos.icono(self.nombre_icono, activo if self.isChecked() else normal, 18))


class Paso(QWidget):
    """Paso numerado de la guía rápida en Inicio."""

    def __init__(self, numero: int, titulo: str, detalle: str, parent=None):
        super().__init__(parent)
        num = etiqueta(str(numero), "NumeroPaso")
        num.setAlignment(Qt.AlignCenter)
        textos = QVBoxLayout()
        textos.setSpacing(2)
        textos.addWidget(etiqueta(titulo, "TituloTarjeta"))
        textos.addWidget(etiqueta(detalle, "TextoSuave", ajustar=True))
        capa = QHBoxLayout(self)
        capa.setContentsMargins(0, 0, 0, 0)
        capa.setSpacing(12)
        capa.addWidget(num, alignment=Qt.AlignTop)
        capa.addLayout(textos, stretch=1)
