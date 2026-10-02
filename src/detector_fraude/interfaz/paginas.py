"""Las tres pantallas de la app: Inicio, Datos y Análisis."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QColor, QIcon
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLineEdit,
    QProgressBar,
    QPushButton,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from detector_fraude.interfaz import iconos
from detector_fraude.interfaz.componentes import (
    Aviso,
    Paso,
    Tarjeta,
    TarjetaDato,
    ZonaArrastre,
    etiqueta,
)
from detector_fraude.interfaz.modelo_tabla import DelegadoRiesgo, ModeloTabla
from detector_fraude.interfaz.tema import Paleta

MAX_FILAS_VISTA = 5000  # la tabla en pantalla no carga millones de filas
COLUMNAS_BUSQUEDA = ["tipo", "numero", "ano", "mes", "dia", "tipo_probable", "motivo"]


def boton(texto: str, primario: bool = False) -> QPushButton:
    b = QPushButton(texto)
    b.setCursor(Qt.PointingHandCursor)
    if primario:
        b.setObjectName("Primario")
    return b


class Pagina(QWidget):
    def __init__(self, titulo: str, subtitulo: str, parent=None):
        super().__init__(parent)
        self.setObjectName("Pagina")
        self.capa = QVBoxLayout(self)
        self.capa.setContentsMargins(36, 32, 36, 28)
        self.capa.setSpacing(18)
        self.cabecera = QHBoxLayout()
        textos = QVBoxLayout()
        textos.setSpacing(4)
        self.titulo = etiqueta(titulo, "Titulo")
        self.subtitulo = etiqueta(subtitulo, "Subtitulo", ajustar=True)
        textos.addWidget(self.titulo)
        textos.addWidget(self.subtitulo)
        self.cabecera.addLayout(textos, stretch=1)
        self.capa.addLayout(self.cabecera)

    def aplicar_paleta(self, paleta: Paleta) -> None:
        """Las páginas que tienen íconos o colores propios la redefinen."""


class TablaConBusqueda(QWidget):
    """Buscador + tabla + contador de filas, sobre un DataFrame que puede ser enorme."""

    def __init__(self, texto_busqueda: str, parent=None):
        super().__init__(parent)
        self.completa = pd.DataFrame()
        self.buscador = QLineEdit()
        self.buscador.setPlaceholderText(texto_busqueda)
        self.buscador.setClearButtonEnabled(True)
        self.modelo = ModeloTabla()
        self.vista = QTableView()
        self.vista.setModel(self.modelo)
        self.vista.setAlternatingRowColors(True)
        self.vista.setShowGrid(False)
        self.vista.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.vista.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.vista.verticalHeader().setVisible(False)
        self.vista.verticalHeader().setDefaultSectionSize(36)
        self.vista.horizontalHeader().setHighlightSections(False)
        self.vista.horizontalHeader().setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.contador = etiqueta("", "TextoSuave")
        self._accion_lupa = None

        self._espera = QTimer(self, singleShot=True, interval=250)
        self._espera.timeout.connect(self._filtrar)
        self.buscador.textChanged.connect(lambda _: self._espera.start())

        capa = QVBoxLayout(self)
        capa.setContentsMargins(0, 0, 0, 0)
        capa.setSpacing(10)
        capa.addWidget(self.buscador)
        capa.addWidget(self.vista, stretch=1)
        capa.addWidget(self.contador)

    def aplicar_paleta(self, paleta: Paleta) -> None:
        if self._accion_lupa is None:
            self._accion_lupa = self.buscador.addAction(QIcon(), QLineEdit.LeadingPosition)
        self._accion_lupa.setIcon(iconos.icono("buscar", paleta.texto_suave, 16))
        self.modelo.color_suave = QColor(paleta.borde if paleta.fondo.startswith("#F") else paleta.texto_suave)
        self.vista.viewport().update()

    def mostrar(self, tabla: pd.DataFrame) -> None:
        self.completa = tabla
        self.buscador.blockSignals(True)
        self.buscador.clear()
        self.buscador.blockSignals(False)
        self._filtrar()

    def _filtrar(self) -> None:
        texto = self.buscador.text().strip().lower()
        tabla = self.completa
        if texto and not tabla.empty:
            columnas = [c for c in COLUMNAS_BUSQUEDA if c in tabla.columns]
            coincide = pd.Series(False, index=tabla.index)
            for c in columnas:
                coincide |= tabla[c].astype(str).str.lower().str.contains(texto, regex=False)
            tabla = tabla[coincide]
        self.modelo.cambiar_tabla(tabla.head(MAX_FILAS_VISTA))
        self.vista.horizontalHeader().resizeSections(QHeaderView.ResizeToContents)
        total = len(self.completa)
        visibles = min(len(tabla), MAX_FILAS_VISTA)
        if texto:
            self.contador.setText(f"{len(tabla):,} coincidencias · mostrando {visibles:,}".replace(",", "."))
        else:
            self.contador.setText(f"Mostrando {visibles:,} de {total:,} filas".replace(",", "."))


class PaginaInicio(Pagina):
    archivo_elegido = Signal(Path)
    pedir_dialogo = Signal()

    def __init__(self, paleta: Paleta, parent=None):
        super().__init__(
            "Bienvenido",
            "Revisa los comprobantes contables de la empresa y encuentra los que merecen una mirada más de cerca.",
            parent,
        )
        self.zona = ZonaArrastre(paleta.primario)
        self.zona.archivo_elegido.connect(self.archivo_elegido)
        self.zona.pedir_dialogo.connect(self.pedir_dialogo)

        self.progreso = QProgressBar()
        self.progreso.setRange(0, 0)
        self.progreso.setTextVisible(False)
        self.progreso.hide()
        self.estado = etiqueta("", "TextoSuave")
        self.estado.hide()
        self.error = Aviso("", "error")
        self.error.hide()

        izquierda = QVBoxLayout()
        izquierda.setSpacing(10)
        izquierda.addWidget(self.zona, stretch=1)
        izquierda.addWidget(self.progreso)
        izquierda.addWidget(self.estado)
        izquierda.addWidget(self.error)

        guia = Tarjeta()
        guia.cuerpo.setSpacing(16)
        guia.cuerpo.addWidget(etiqueta("Cómo funciona", "TituloTarjeta"))
        guia.cuerpo.addWidget(Paso(1, "Carga", "Elige el CSV exportado de SysCafe (vista por tipo de comprobante)."))
        guia.cuerpo.addWidget(Paso(2, "Revisa", "Mira el resumen, los avisos de calidad y la tabla de comprobantes."))
        guia.cuerpo.addWidget(Paso(3, "Analiza", "Calcula el riesgo de cada comprobante y exporta el resultado."))
        guia.cuerpo.addStretch()
        guia.setMinimumWidth(300)

        fila = QHBoxLayout()
        fila.setSpacing(18)
        fila.addLayout(izquierda, stretch=3)
        fila.addWidget(guia, stretch=2)
        self.capa.addLayout(fila, stretch=1)

        self.recientes = Tarjeta(espacio=4)
        self.recientes.cuerpo.addWidget(etiqueta("Archivos recientes", "TituloTarjeta"))
        self.lista_recientes = QVBoxLayout()
        self.lista_recientes.setSpacing(0)
        self.recientes.cuerpo.addLayout(self.lista_recientes)
        self.capa.addWidget(self.recientes)
        self._paleta = paleta

    def aplicar_paleta(self, paleta: Paleta) -> None:
        self._paleta = paleta
        self.zona.cambiar_color(paleta.primario)
        for i in range(self.lista_recientes.count()):
            b = self.lista_recientes.itemAt(i).widget()
            b.setIcon(iconos.icono("archivo", paleta.texto_suave, 16))

    def mostrar_recientes(self, rutas: list[str]) -> None:
        while self.lista_recientes.count():
            self.lista_recientes.takeAt(0).widget().deleteLater()
        existentes = [r for r in rutas if Path(r).exists()]
        self.recientes.setVisible(bool(existentes))
        for r in existentes:
            b = QPushButton(f"  {Path(r).name}   ·   {Path(r).parent}")
            b.setObjectName("Enlace")
            b.setCursor(Qt.PointingHandCursor)
            b.setIcon(iconos.icono("archivo", self._paleta.texto_suave, 16))
            b.clicked.connect(lambda _=False, ruta=r: self.archivo_elegido.emit(Path(ruta)))
            self.lista_recientes.addWidget(b)

    def cargando(self, nombre: str | None) -> None:
        activo = nombre is not None
        self.progreso.setVisible(activo)
        self.estado.setVisible(activo)
        self.zona.setEnabled(not activo)
        if activo:
            self.error.hide()
            self.estado.setText(f"Leyendo {nombre}… los archivos grandes pueden tardar unos segundos.")

    def mostrar_error(self, texto: str) -> None:
        self.error.setText(texto)
        self.error.show()


class PaginaDatos(Pagina):
    pedir_cambio = Signal()
    ir_a_analisis = Signal()

    def __init__(self, parent=None):
        super().__init__("Datos cargados", "", parent)
        self.boton_cambiar = boton("Cambiar archivo")
        self.boton_continuar = boton("Continuar al análisis  →", primario=True)
        self.boton_cambiar.clicked.connect(self.pedir_cambio)
        self.boton_continuar.clicked.connect(self.ir_a_analisis)
        self.cabecera.addWidget(self.boton_cambiar, alignment=Qt.AlignTop)
        self.cabecera.addWidget(self.boton_continuar, alignment=Qt.AlignTop)

        self.datos = {
            "comprobantes": TarjetaDato("Comprobantes"),
            "cuentas": TarjetaDato("Cuentas contables"),
            "anos": TarjetaDato("Años"),
            "descuadrados": TarjetaDato("Descuadrados"),
        }
        rejilla = QGridLayout()
        rejilla.setSpacing(14)
        for i, tarjeta in enumerate(self.datos.values()):
            rejilla.addWidget(tarjeta, 0, i)
        self.capa.addLayout(rejilla)

        self.caja_avisos = QVBoxLayout()
        self.caja_avisos.setSpacing(6)
        self.capa.addLayout(self.caja_avisos)

        self.tabla = TablaConBusqueda("Buscar por tipo, número, año o mes del comprobante…")
        self.capa.addWidget(self.tabla, stretch=1)

    def aplicar_paleta(self, paleta: Paleta) -> None:
        self.tabla.aplicar_paleta(paleta)

    def mostrar(self, comprobantes) -> None:
        r = comprobantes.resumen()
        self.titulo.setText(comprobantes.archivo.name)
        self.subtitulo.setText(str(comprobantes.archivo.parent))
        self.datos["comprobantes"].mostrar(r["Comprobantes"])
        self.datos["cuentas"].mostrar(r["Cuentas"])
        self.datos["anos"].mostrar(r["Años"])
        self.datos["descuadrados"].mostrar(comprobantes.descuadrados)

        while self.caja_avisos.count():
            self.caja_avisos.takeAt(0).widget().deleteLater()
        if comprobantes.avisos:
            for texto in comprobantes.avisos:
                self.caja_avisos.addWidget(Aviso(texto, "alerta"))
        else:
            self.caja_avisos.addWidget(Aviso("El archivo se leyó sin problemas de formato.", "exito"))
        if comprobantes.tiene_etiqueta:
            self.caja_avisos.addWidget(
                Aviso("Este archivo trae la columna misstate (etiqueta de fraude): sirve para practicar y evaluar.", "info")
            )
        self.tabla.mostrar(comprobantes.tabla)


class PaginaAnalisis(Pagina):
    analizar = Signal()
    exportar = Signal()

    def __init__(self, nombres_detectores: list[str], paleta: Paleta, parent=None):
        super().__init__(
            "Análisis de riesgo",
            "Elige un modelo y calcula el riesgo de fraude de cada comprobante. Todo se procesa en este equipo.",
            parent,
        )
        self.boton_exportar = boton("Exportar resultado")
        self.boton_exportar.setEnabled(False)
        self.boton_exportar.clicked.connect(self.exportar)
        self.cabecera.addWidget(self.boton_exportar, alignment=Qt.AlignTop)

        control = Tarjeta()
        fila = QHBoxLayout()
        fila.setSpacing(12)
        textos = QVBoxLayout()
        textos.setSpacing(2)
        textos.addWidget(etiqueta("Modelo de detección", "TituloTarjeta"))
        self.descripcion = etiqueta(
            "Todavía no hay modelos conectados. El análisis marcará cada comprobante como pendiente.",
            "TextoSuave",
            ajustar=True,
        )
        textos.addWidget(self.descripcion)
        self.selector = QComboBox()
        self.selector.addItems(nombres_detectores)
        self.selector.setMinimumWidth(240)
        self.boton_analizar = boton("Analizar", primario=True)
        self.boton_analizar.setEnabled(False)
        self.boton_analizar.clicked.connect(self.analizar)
        fila.addLayout(textos, stretch=1)
        fila.addWidget(self.selector)
        fila.addWidget(self.boton_analizar)
        control.cuerpo.addLayout(fila)
        self.capa.addWidget(control)

        self.vacio = Tarjeta(margen=40)
        self.icono_vacio = etiqueta("")
        self.icono_vacio.setAlignment(Qt.AlignCenter)
        titulo_vacio = etiqueta("Aún no has analizado este archivo", "TituloTarjeta")
        titulo_vacio.setAlignment(Qt.AlignCenter)
        detalle_vacio = etiqueta(
            "Pulsa «Analizar». Cuando conectemos los modelos, aquí verás el riesgo de cada "
            "comprobante, el tipo de fraude probable y el motivo.",
            "TextoSuave",
            ajustar=True,
        )
        detalle_vacio.setAlignment(Qt.AlignCenter)
        self.vacio.cuerpo.addStretch()
        self.vacio.cuerpo.addWidget(self.icono_vacio)
        self.vacio.cuerpo.addWidget(titulo_vacio)
        self.vacio.cuerpo.addWidget(detalle_vacio)
        self.vacio.cuerpo.addStretch()
        self.capa.addWidget(self.vacio, stretch=1)

        self.resultados = QWidget()
        capa_res = QVBoxLayout(self.resultados)
        capa_res.setContentsMargins(0, 0, 0, 0)
        capa_res.setSpacing(14)
        self.datos = {
            "analizados": TarjetaDato("Analizados"),
            "alto": TarjetaDato("Riesgo alto"),
            "medio": TarjetaDato("Riesgo medio"),
            "pendientes": TarjetaDato("Sin calificar"),
        }
        rejilla = QGridLayout()
        rejilla.setSpacing(14)
        for i, tarjeta in enumerate(self.datos.values()):
            rejilla.addWidget(tarjeta, 0, i)
        capa_res.addLayout(rejilla)
        self.tabla = TablaConBusqueda("Buscar por tipo, número, tipo de fraude o motivo…")
        capa_res.addWidget(self.tabla, stretch=1)
        self.resultados.hide()
        self.capa.addWidget(self.resultados, stretch=1)

        self.delegado = DelegadoRiesgo(paleta, self)
        self.aplicar_paleta(paleta)

    def aplicar_paleta(self, paleta: Paleta) -> None:
        self.icono_vacio.setPixmap(iconos.pixmap("analisis", paleta.texto_suave, 48))
        self.delegado.paleta = paleta
        self.tabla.aplicar_paleta(paleta)
        self.tabla.vista.viewport().update()

    def reiniciar(self) -> None:
        self.vacio.show()
        self.resultados.hide()
        self.boton_exportar.setEnabled(False)
        self.boton_analizar.setEnabled(True)

    def mostrar(self, resultado: pd.DataFrame) -> None:
        riesgo = pd.to_numeric(resultado["riesgo"], errors="coerce")
        self.datos["analizados"].mostrar(len(resultado))
        self.datos["alto"].mostrar(int((riesgo >= 0.7).sum()))
        self.datos["medio"].mostrar(int(((riesgo >= 0.4) & (riesgo < 0.7)).sum()))
        self.datos["pendientes"].mostrar(int(riesgo.isna().sum()))
        self.tabla.mostrar(resultado)
        columna = list(resultado.columns).index("riesgo")
        self.tabla.vista.setItemDelegateForColumn(columna, self.delegado)
        self.tabla.vista.setColumnWidth(columna, 140)
        self.vacio.hide()
        self.resultados.show()
        self.boton_exportar.setEnabled(True)
