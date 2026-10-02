"""Ventana principal: cargar un CSV, verlo, analizarlo y exportar el resultado."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from detector_fraude import NOMBRE_APP, __version__
from detector_fraude.interfaz.modelo_tabla import ModeloTabla
from detector_fraude.nucleo.datos import Comprobantes, ErrorDeFormato, leer_comprobantes
from detector_fraude.nucleo.detector import DETECTORES

MAX_FILAS_VISTA = 5000  # la vista previa no carga millones de filas en pantalla


class VentanaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{NOMBRE_APP} {__version__}")
        self.resize(1100, 700)
        self.comprobantes: Comprobantes | None = None
        self.resultado: pd.DataFrame | None = None

        self.boton_cargar = QPushButton("Cargar CSV de comprobantes…")
        self.selector_detector = QComboBox()
        for d in DETECTORES:
            self.selector_detector.addItem(d.nombre)
        self.boton_analizar = QPushButton("Analizar")
        self.boton_exportar = QPushButton("Exportar resultado…")
        self.boton_analizar.setEnabled(False)
        self.boton_exportar.setEnabled(False)

        barra = QHBoxLayout()
        barra.addWidget(self.boton_cargar)
        barra.addStretch()
        barra.addWidget(QLabel("Modelo:"))
        barra.addWidget(self.selector_detector)
        barra.addWidget(self.boton_analizar)
        barra.addWidget(self.boton_exportar)

        self.caja_resumen = QGroupBox("Resumen del archivo")
        self.form_resumen = QFormLayout(self.caja_resumen)
        self.etiqueta_avisos = QLabel("Carga un archivo para empezar.")
        self.etiqueta_avisos.setWordWrap(True)

        self.modelo_tabla = ModeloTabla()
        self.vista_tabla = QTableView()
        self.vista_tabla.setModel(self.modelo_tabla)

        cuerpo = QVBoxLayout()
        cuerpo.addLayout(barra)
        cuerpo.addWidget(self.caja_resumen)
        cuerpo.addWidget(self.etiqueta_avisos)
        cuerpo.addWidget(self.vista_tabla, stretch=1)
        central = QWidget()
        central.setLayout(cuerpo)
        self.setCentralWidget(central)
        self.statusBar().showMessage("Todo se procesa en este equipo; nada sale a internet.")

        self.boton_cargar.clicked.connect(self.elegir_archivo)
        self.boton_analizar.clicked.connect(self.analizar)
        self.boton_exportar.clicked.connect(self.elegir_destino_exportar)

    # --- acciones -------------------------------------------------------------

    def elegir_archivo(self) -> None:
        ruta, _ = QFileDialog.getOpenFileName(
            self, "Elegir CSV de comprobantes", "", "CSV (*.csv *.CSV);;Todos (*.*)"
        )
        if ruta:
            self.cargar(Path(ruta))

    def cargar(self, ruta: Path) -> bool:
        try:
            self.comprobantes = leer_comprobantes(ruta)
        except (ErrorDeFormato, OSError, pd.errors.ParserError) as error:
            QMessageBox.warning(self, "No se pudo leer el archivo", str(error))
            return False

        self.resultado = None
        self._mostrar_resumen(self.comprobantes.resumen())
        avisos = self.comprobantes.avisos
        self.etiqueta_avisos.setText("Avisos: " + " · ".join(avisos) if avisos else "Sin avisos.")
        self._mostrar_tabla(self.comprobantes.tabla)
        self.boton_analizar.setEnabled(True)
        self.boton_exportar.setEnabled(False)
        return True

    def analizar(self) -> None:
        if self.comprobantes is None:
            return
        detector = DETECTORES[self.selector_detector.currentIndex()]
        evaluacion = detector.analizar(self.comprobantes)
        self.resultado = pd.concat([evaluacion, self.comprobantes.tabla], axis=1)
        self._mostrar_tabla(self.resultado)
        self.boton_exportar.setEnabled(True)
        self.statusBar().showMessage(f"Análisis hecho con: {detector.nombre}")

    def elegir_destino_exportar(self) -> None:
        ruta, _ = QFileDialog.getSaveFileName(self, "Guardar resultado", "resultado.csv", "CSV (*.csv)")
        if ruta:
            self.exportar(Path(ruta))

    def exportar(self, ruta: Path) -> None:
        if self.resultado is None:
            return
        self.resultado.to_csv(ruta, sep=";", decimal=",", index=False, encoding="utf-8-sig")
        self.statusBar().showMessage(f"Resultado guardado en {ruta}")

    # --- ayudas de pantalla ---------------------------------------------------

    def _mostrar_resumen(self, resumen: dict[str, object]) -> None:
        while self.form_resumen.rowCount():
            self.form_resumen.removeRow(0)
        for clave, valor in resumen.items():
            self.form_resumen.addRow(f"{clave}:", QLabel(str(valor)))

    def _mostrar_tabla(self, tabla: pd.DataFrame) -> None:
        self.modelo_tabla.cambiar_tabla(tabla.head(MAX_FILAS_VISTA))
        if len(tabla) > MAX_FILAS_VISTA:
            self.statusBar().showMessage(
                f"Vista previa: primeras {MAX_FILAS_VISTA:,} de {len(tabla):,} filas."
            )
