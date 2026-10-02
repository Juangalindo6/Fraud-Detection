"""Ventana principal: menú lateral y las pantallas Inicio, Datos y Análisis."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from PySide6.QtCore import QObject, QRunnable, QSettings, Qt, QThreadPool, Signal
from PySide6.QtWidgets import (
    QApplication,
    QButtonGroup,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from detector_fraude import NOMBRE_APP, __version__
from detector_fraude.interfaz import iconos
from detector_fraude.interfaz.componentes import BotonNav, etiqueta
from detector_fraude.interfaz.paginas import PaginaAnalisis, PaginaDatos, PaginaInicio
from detector_fraude.interfaz.tema import CLARO, OSCURO, Paleta, hoja_de_estilos
from detector_fraude.nucleo.datos import Comprobantes, ErrorDeFormato, leer_comprobantes
from detector_fraude.nucleo.detector import DETECTORES

MAX_RECIENTES = 5
ERRORES_LECTURA = (ErrorDeFormato, OSError, pd.errors.ParserError, UnicodeDecodeError, ValueError)


class _Senales(QObject):
    listo = Signal(object)
    fallo = Signal(str)


class _TareaLectura(QRunnable):
    """Lee el CSV en segundo plano para que la ventana no se congele."""

    def __init__(self, ruta: Path):
        super().__init__()
        self.ruta = ruta
        self.senales = _Senales()

    def run(self):
        try:
            self.senales.listo.emit(leer_comprobantes(self.ruta))
        except ERRORES_LECTURA as error:
            self.senales.fallo.emit(str(error))


class VentanaPrincipal(QMainWindow):
    INICIO, DATOS, ANALISIS = range(3)

    def __init__(self, ajustes: QSettings | None = None):
        super().__init__()
        self.setWindowTitle(NOMBRE_APP)
        self.resize(1240, 780)
        self.setMinimumSize(980, 640)
        self.ajustes = ajustes if ajustes is not None else QSettings("UCC", "DetectorFraude")
        self.oscuro = self.ajustes.value("tema_oscuro", False, type=bool)
        self.comprobantes: Comprobantes | None = None
        self.resultado: pd.DataFrame | None = None
        self._tarea: _TareaLectura | None = None

        paleta = self.paleta
        self.inicio = PaginaInicio(paleta)
        self.datos = PaginaDatos()
        self.analisis = PaginaAnalisis([d.nombre for d in DETECTORES], paleta)
        self.paginas = QStackedWidget()
        self.paginas.setObjectName("Contenido")
        for pagina in (self.inicio, self.datos, self.analisis):
            self.paginas.addWidget(pagina)

        raiz = QWidget()
        capa = QHBoxLayout(raiz)
        capa.setContentsMargins(0, 0, 0, 0)
        capa.setSpacing(0)
        capa.addWidget(self._crear_lateral())
        capa.addWidget(self.paginas, stretch=1)
        self.setCentralWidget(raiz)

        self.inicio.pedir_dialogo.connect(self.elegir_archivo)
        self.inicio.archivo_elegido.connect(self.cargar_en_segundo_plano)
        self.datos.pedir_cambio.connect(self.elegir_archivo)
        self.datos.ir_a_analisis.connect(lambda: self.ir_a(self.ANALISIS))
        self.analisis.analizar.connect(self.analizar)
        self.analisis.exportar.connect(self.elegir_destino_exportar)

        self.inicio.mostrar_recientes(self._recientes())
        self.aplicar_tema()
        self.ir_a(self.INICIO)

    # --- atajos que usan las pruebas y el resto de la app ---------------------

    @property
    def paleta(self) -> Paleta:
        return OSCURO if self.oscuro else CLARO

    @property
    def boton_analizar(self) -> QPushButton:
        return self.analisis.boton_analizar

    @property
    def boton_exportar(self) -> QPushButton:
        return self.analisis.boton_exportar

    # --- menú lateral ----------------------------------------------------------

    def _crear_lateral(self) -> QFrame:
        lateral = QFrame()
        lateral.setObjectName("Lateral")
        lateral.setFixedWidth(232)
        capa = QVBoxLayout(lateral)
        capa.setContentsMargins(16, 22, 16, 18)
        capa.setSpacing(6)

        marca = QHBoxLayout()
        marca.setSpacing(10)
        self.logo = etiqueta("")
        marca.addWidget(self.logo)
        textos = QVBoxLayout()
        textos.setSpacing(0)
        textos.addWidget(etiqueta("Detector", "Marca"))
        textos.addWidget(etiqueta("de fraude contable", "MarcaSub"))
        marca.addLayout(textos, stretch=1)
        capa.addLayout(marca)
        capa.addSpacing(22)

        self.nav = [
            BotonNav("Inicio", "inicio"),
            BotonNav("Datos", "datos"),
            BotonNav("Análisis", "analisis"),
        ]
        self.grupo_nav = QButtonGroup(self)
        self.grupo_nav.setExclusive(True)
        for i, b in enumerate(self.nav):
            self.grupo_nav.addButton(b, i)
            capa.addWidget(b)
        self.grupo_nav.idClicked.connect(self.ir_a)
        for b in self.nav[1:]:
            b.setEnabled(False)
            b.setToolTip("Primero carga un archivo en Inicio")
        capa.addStretch()

        self.boton_tema = QPushButton()
        self.boton_tema.setObjectName("BotonNav")
        self.boton_tema.setCursor(Qt.PointingHandCursor)
        self.boton_tema.clicked.connect(self.cambiar_tema)
        capa.addWidget(self.boton_tema)
        capa.addSpacing(8)
        self.insignia = etiqueta("100 % local · tus datos no salen de este equipo", "InsigniaLocal", ajustar=True)
        capa.addWidget(self.insignia)
        capa.addSpacing(6)
        capa.addWidget(etiqueta(f"Versión {__version__} · UCC", "Version"))
        return lateral

    # --- navegación y tema -----------------------------------------------------

    def ir_a(self, indice: int) -> None:
        self.paginas.setCurrentIndex(indice)
        self.nav[indice].setChecked(True)
        self._colorear_nav()

    def _colorear_nav(self) -> None:
        p = self.paleta
        for b in self.nav:
            b.colorear(p.texto_suave, p.primario_texto)

    def cambiar_tema(self) -> None:
        self.oscuro = not self.oscuro
        self.ajustes.setValue("tema_oscuro", self.oscuro)
        self.aplicar_tema()

    def aplicar_tema(self) -> None:
        p = self.paleta
        self.setStyleSheet(hoja_de_estilos(p))
        self.logo.setPixmap(iconos.pixmap("escudo", p.primario, 34))
        self.boton_tema.setText("  Tema claro" if self.oscuro else "  Tema oscuro")
        self.boton_tema.setIcon(iconos.icono("sol" if self.oscuro else "luna", p.texto_suave, 18))
        for pagina in (self.inicio, self.datos, self.analisis):
            pagina.aplicar_paleta(p)
        self._colorear_nav()

    # --- carga de archivos -----------------------------------------------------

    def elegir_archivo(self) -> None:
        ruta, _ = QFileDialog.getOpenFileName(
            self, "Elegir CSV de comprobantes", self.ajustes.value("ultima_carpeta", ""), "CSV (*.csv *.CSV)"
        )
        if ruta:
            self.cargar_en_segundo_plano(Path(ruta))

    def cargar_en_segundo_plano(self, ruta: Path) -> None:
        if self._tarea is not None:
            return
        self.ir_a(self.INICIO)
        self.inicio.cargando(ruta.name)
        QApplication.setOverrideCursor(Qt.BusyCursor)
        self._tarea = _TareaLectura(ruta)
        self._tarea.senales.listo.connect(self._al_cargar)
        self._tarea.senales.fallo.connect(self._al_fallar)
        QThreadPool.globalInstance().start(self._tarea)

    def cargar(self, ruta: Path) -> bool:
        """Carga sin hilo (la usan las pruebas). Devuelve True si se pudo leer."""
        try:
            comprobantes = leer_comprobantes(ruta)
        except ERRORES_LECTURA as error:
            self._al_fallar(str(error))
            return False
        self._al_cargar(comprobantes)
        return True

    def _terminar_carga(self) -> None:
        if self._tarea is not None:
            self._tarea = None
            QApplication.restoreOverrideCursor()
        self.inicio.cargando(None)

    def _al_fallar(self, mensaje: str) -> None:
        self._terminar_carga()
        self.inicio.mostrar_error(f"No se pudo leer el archivo. {mensaje}")

    def _al_cargar(self, comprobantes: Comprobantes) -> None:
        self._terminar_carga()
        self.comprobantes = comprobantes
        self.resultado = None
        self._recordar(comprobantes.archivo)
        self.datos.mostrar(comprobantes)
        self.analisis.reiniciar()
        for b in self.nav[1:]:
            b.setEnabled(True)
            b.setToolTip("")
        self.ir_a(self.DATOS)

    def _recientes(self) -> list[str]:
        valor = self.ajustes.value("recientes", [])
        return [valor] if isinstance(valor, str) else list(valor or [])

    def _recordar(self, ruta: Path) -> None:
        ruta = str(ruta.resolve())
        recientes = [ruta] + [r for r in self._recientes() if r != ruta]
        self.ajustes.setValue("recientes", recientes[:MAX_RECIENTES])
        self.ajustes.setValue("ultima_carpeta", str(Path(ruta).parent))
        self.inicio.mostrar_recientes(recientes[:MAX_RECIENTES])

    # --- análisis y exportación -----------------------------------------------

    def analizar(self) -> None:
        if self.comprobantes is None:
            return
        detector = DETECTORES[self.analisis.selector.currentIndex()]
        evaluacion = detector.analizar(self.comprobantes)
        self.resultado = pd.concat([evaluacion, self.comprobantes.tabla], axis=1)
        self.analisis.mostrar(self.resultado)

    def elegir_destino_exportar(self) -> None:
        sugerido = "resultado.csv"
        if self.comprobantes is not None:
            sugerido = str(self.comprobantes.archivo.with_name(f"{self.comprobantes.archivo.stem}_resultado.csv"))
        ruta, _ = QFileDialog.getSaveFileName(self, "Guardar resultado", sugerido, "CSV (*.csv)")
        if ruta:
            self.exportar(Path(ruta))

    def exportar(self, ruta: Path) -> None:
        if self.resultado is None:
            return
        self.resultado.to_csv(ruta, sep=";", decimal=",", index=False, encoding="utf-8-sig")
        self.analisis.subtitulo.setText(f"Resultado guardado en {ruta}")
