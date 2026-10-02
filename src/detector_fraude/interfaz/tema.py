"""Colores y hoja de estilos (QSS) de la app, en tema claro y oscuro."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Paleta:
    fondo: str
    lateral: str
    superficie: str
    superficie_alta: str
    borde: str
    texto: str
    texto_suave: str
    primario: str
    primario_hover: str
    primario_texto: str
    peligro: str
    peligro_fondo: str
    alerta: str
    alerta_fondo: str
    exito: str
    exito_fondo: str


CLARO = Paleta(
    fondo="#F4F6FA",
    lateral="#FFFFFF",
    superficie="#FFFFFF",
    superficie_alta="#EEF1F7",
    borde="#E2E6EE",
    texto="#151A2D",
    texto_suave="#5F6982",
    primario="#4F46E5",
    primario_hover="#4338CA",
    primario_texto="#FFFFFF",
    peligro="#DC2626",
    peligro_fondo="#FDECEC",
    alerta="#B45309",
    alerta_fondo="#FEF3E2",
    exito="#15803D",
    exito_fondo="#E7F6EC",
)

OSCURO = Paleta(
    fondo="#0F1220",
    lateral="#151929",
    superficie="#1A1F33",
    superficie_alta="#232A42",
    borde="#2A3150",
    texto="#E8EBF5",
    texto_suave="#9AA3BD",
    primario="#818CF8",
    primario_hover="#A5B4FC",
    primario_texto="#0F1220",
    peligro="#F87171",
    peligro_fondo="#3A1D24",
    alerta="#FBBF24",
    alerta_fondo="#3A2E17",
    exito="#4ADE80",
    exito_fondo="#16331F",
)

FUENTE = '"Segoe UI Variable Text", "Segoe UI", "Inter", "Helvetica Neue", Arial, sans-serif'


def hoja_de_estilos(p: Paleta) -> str:
    return f"""
    * {{
        font-family: {FUENTE};
        font-size: 10pt;
        color: {p.texto};
        outline: none;
    }}
    QMainWindow, #Contenido {{ background: {p.fondo}; }}
    QToolTip {{
        background: {p.superficie_alta}; color: {p.texto};
        border: 1px solid {p.borde}; padding: 6px 8px; border-radius: 6px;
    }}

    /* --- menú lateral --- */
    #Lateral {{ background: {p.lateral}; border-right: 1px solid {p.borde}; }}
    #Marca {{ font-size: 13pt; font-weight: 700; }}
    #MarcaSub {{ color: {p.texto_suave}; font-size: 9pt; }}
    #BotonNav {{
        text-align: left; padding: 10px 14px; border: none; border-radius: 10px;
        background: transparent; color: {p.texto_suave}; font-weight: 600;
    }}
    #BotonNav:hover {{ background: {p.superficie_alta}; color: {p.texto}; }}
    #BotonNav:checked {{ background: {p.primario}; color: {p.primario_texto}; }}
    #BotonNav:disabled {{ color: {p.texto_suave}; background: transparent; }}
    #InsigniaLocal {{
        background: {p.exito_fondo}; color: {p.exito}; border-radius: 10px;
        padding: 8px 10px; font-size: 9pt; font-weight: 600;
    }}
    #Version {{ color: {p.texto_suave}; font-size: 8.5pt; }}

    /* --- títulos y textos --- */
    #Titulo {{ font-size: 20pt; font-weight: 700; }}
    #Subtitulo {{ color: {p.texto_suave}; font-size: 10.5pt; }}
    #TituloTarjeta {{ font-size: 11.5pt; font-weight: 700; }}
    #TextoSuave {{ color: {p.texto_suave}; }}

    /* --- tarjetas --- */
    #Tarjeta {{
        background: {p.superficie}; border: 1px solid {p.borde}; border-radius: 14px;
    }}
    #DatoValor {{ font-size: 20pt; font-weight: 700; }}
    #DatoNombre {{ color: {p.texto_suave}; font-size: 9pt; font-weight: 600; }}
    #NumeroPaso {{
        background: {p.superficie_alta}; color: {p.primario}; border-radius: 15px;
        font-weight: 700; min-width: 30px; max-width: 30px; min-height: 30px; max-height: 30px;
    }}

    /* --- zona para arrastrar el archivo --- */
    #ZonaArrastre {{
        background: {p.superficie}; border: 2px dashed {p.borde}; border-radius: 18px;
    }}
    #ZonaArrastre[activa="true"] {{ border-color: {p.primario}; background: {p.superficie_alta}; }}
    #ZonaTitulo {{ font-size: 13pt; font-weight: 700; }}

    /* --- avisos --- */
    #Aviso {{ border-radius: 10px; padding: 9px 12px; }}
    #Aviso[nivel="alerta"] {{ background: {p.alerta_fondo}; color: {p.alerta}; }}
    #Aviso[nivel="info"] {{ background: {p.superficie_alta}; color: {p.texto_suave}; }}
    #Aviso[nivel="exito"] {{ background: {p.exito_fondo}; color: {p.exito}; }}
    #Aviso[nivel="error"] {{ background: {p.peligro_fondo}; color: {p.peligro}; }}

    /* --- botones --- */
    QPushButton {{
        background: {p.superficie}; border: 1px solid {p.borde}; border-radius: 10px;
        padding: 9px 16px; font-weight: 600;
    }}
    QPushButton:hover {{ background: {p.superficie_alta}; }}
    QPushButton:disabled {{ color: {p.texto_suave}; background: {p.superficie_alta}; }}
    QPushButton#Primario {{
        background: {p.primario}; color: {p.primario_texto}; border: none;
    }}
    QPushButton#Primario:hover {{ background: {p.primario_hover}; }}
    QPushButton#Primario:disabled {{ background: {p.borde}; color: {p.texto_suave}; }}
    QPushButton#Enlace {{
        background: transparent; border: none; color: {p.primario}; padding: 4px 6px; text-align: left;
    }}
    QPushButton#Enlace:hover {{ text-decoration: underline; }}

    /* --- campos --- */
    QLineEdit, QComboBox {{
        background: {p.superficie}; border: 1px solid {p.borde}; border-radius: 10px;
        padding: 8px 12px; selection-background-color: {p.primario};
    }}
    QLineEdit:focus, QComboBox:focus {{ border: 1px solid {p.primario}; }}
    QComboBox::drop-down {{ border: none; width: 26px; }}
    QComboBox QAbstractItemView {{
        background: {p.superficie}; border: 1px solid {p.borde}; border-radius: 8px;
        selection-background-color: {p.superficie_alta}; selection-color: {p.texto}; padding: 4px;
    }}
    QProgressBar {{
        background: {p.superficie_alta}; border: none; border-radius: 3px; max-height: 6px;
    }}
    QProgressBar::chunk {{ background: {p.primario}; border-radius: 3px; }}

    /* --- tabla --- */
    QTableView {{
        background: {p.superficie}; alternate-background-color: {p.fondo};
        border: 1px solid {p.borde}; border-radius: 12px; gridline-color: transparent;
        selection-background-color: {p.superficie_alta}; selection-color: {p.texto};
    }}
    QTableView::item {{ padding: 4px 8px; border: none; }}
    QHeaderView::section {{
        background: {p.superficie}; color: {p.texto_suave}; border: none;
        border-bottom: 1px solid {p.borde}; padding: 8px; font-weight: 600; font-size: 9pt;
    }}
    QTableCornerButton::section {{ background: {p.superficie}; border: none; }}

    /* --- barras de desplazamiento --- */
    QScrollBar:vertical {{ background: transparent; width: 10px; margin: 4px; }}
    QScrollBar:horizontal {{ background: transparent; height: 10px; margin: 4px; }}
    QScrollBar::handle {{ background: {p.borde}; border-radius: 4px; min-height: 30px; min-width: 30px; }}
    QScrollBar::handle:hover {{ background: {p.texto_suave}; }}
    QScrollBar::add-line, QScrollBar::sub-line {{ width: 0; height: 0; }}
    QScrollBar::add-page, QScrollBar::sub-page {{ background: transparent; }}
    QScrollArea {{ background: transparent; border: none; }}
    #Pagina {{ background: transparent; }}
    """
