import pandas as pd
import pytest
from PySide6.QtCore import QSettings

from detector_fraude.interfaz.ventana_principal import VentanaPrincipal


@pytest.fixture
def ventana(app_qt, tmp_path):
    """Ventana con ajustes en un archivo temporal, para no tocar los del usuario."""
    ajustes = QSettings(str(tmp_path / "ajustes.ini"), QSettings.IniFormat)
    return lambda: VentanaPrincipal(ajustes)


def test_flujo_cargar_analizar_exportar(ventana, csv_ejemplo, tmp_path):
    v = ventana()
    assert v.paginas.currentIndex() == v.INICIO
    assert not v.nav[v.DATOS].isEnabled()

    assert v.cargar(csv_ejemplo)
    assert v.paginas.currentIndex() == v.DATOS
    assert v.boton_analizar.isEnabled()
    assert v.datos.tabla.modelo.rowCount() == 3
    assert v.datos.datos["comprobantes"].valor.text() == "3"
    assert v.datos.datos["descuadrados"].valor.text() == "1"

    v.analizar()
    assert v.boton_exportar.isEnabled()
    assert list(v.resultado.columns[:3]) == ["riesgo", "tipo_probable", "motivo"]
    assert v.analisis.datos["pendientes"].valor.text() == "3"

    salida = tmp_path / "resultado.csv"
    v.exportar(salida)
    assert len(pd.read_csv(salida, sep=";", decimal=",")) == 3


def test_buscador_filtra_la_tabla(ventana, csv_ejemplo):
    v = ventana()
    v.cargar(csv_ejemplo)
    v.datos.tabla.buscador.setText("b2")
    v.datos.tabla._filtrar()
    assert v.datos.tabla.modelo.rowCount() == 1


def test_archivo_invalido_muestra_aviso(ventana, tmp_path):
    ruta = tmp_path / "malo.csv"
    ruta.write_text("x;y\n1;2\n", encoding="utf-8")
    v = ventana()
    assert not v.cargar(ruta)
    assert not v.inicio.error.isHidden()
    assert "Faltan las columnas" in v.inicio.error.text()
    assert not v.nav[v.DATOS].isEnabled()


def test_recuerda_archivos_recientes_y_tema(ventana, csv_ejemplo):
    v = ventana()
    v.cargar(csv_ejemplo)
    v.cambiar_tema()
    otra = ventana()
    assert otra.oscuro
    assert otra.inicio.lista_recientes.count() == 1
