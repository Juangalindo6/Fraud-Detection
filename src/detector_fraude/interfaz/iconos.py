"""Íconos de línea dibujados con SVG, para que no dependan de archivos externos."""

from __future__ import annotations

from PySide6.QtCore import QByteArray, QRectF, Qt
from PySide6.QtGui import QIcon, QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer

_TRAZOS = {
    "inicio": '<path d="M3 10.5 12 3l9 7.5"/><path d="M5 9.5V20h14V9.5"/><path d="M10 20v-6h4v6"/>',
    "datos": '<rect x="3" y="4" width="18" height="16" rx="2"/><path d="M3 9h18M3 14h18M9 4v16"/>',
    "analisis": '<circle cx="11" cy="11" r="7"/><path d="m20 20-4-4"/><path d="M8 11h6M11 8v6"/>',
    "subir": '<path d="M12 16V4"/><path d="m7 9 5-5 5 5"/><path d="M4 16v3a1 1 0 0 0 1 1h14a1 1 0 0 0 1-1v-3"/>',
    "archivo": '<path d="M14 3H6a1 1 0 0 0-1 1v16a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1V8z"/><path d="M14 3v5h5"/>',
    "exportar": '<path d="M12 4v12"/><path d="m7 11 5 5 5-5"/><path d="M4 20h16"/>',
    "luna": '<path d="M20 14.5A8 8 0 0 1 9.5 4a8 8 0 1 0 10.5 10.5z"/>',
    "sol": '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/>',
    "escudo": '<path d="M12 3 4 6v6c0 4.5 3.4 8.3 8 9 4.6-.7 8-4.5 8-9V6z"/><path d="m9 12 2 2 4-4"/>',
    "buscar": '<circle cx="11" cy="11" r="7"/><path d="m20 20-4-4"/>',
    "rayo": '<path d="M13 2 4 14h7l-1 8 9-12h-7z"/>',
}


def icono(nombre: str, color: str, tamano: int = 20) -> QIcon:
    return QIcon(pixmap(nombre, color, tamano))


def pixmap(nombre: str, color: str, tamano: int = 20) -> QPixmap:
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" '
        f'stroke="{color}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">'
        f"{_TRAZOS[nombre]}</svg>"
    )
    escala = 2  # nitidez en pantallas de alta resolución
    imagen = QPixmap(tamano * escala, tamano * escala)
    imagen.fill(Qt.transparent)
    pintor = QPainter(imagen)
    QSvgRenderer(QByteArray(svg.encode())).render(pintor, QRectF(0, 0, tamano * escala, tamano * escala))
    pintor.end()
    imagen.setDevicePixelRatio(escala)
    return imagen
