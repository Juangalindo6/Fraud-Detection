import pandas as pd

from detector_fraude.interfaz.ventana_principal import VentanaPrincipal


def test_flujo_cargar_analizar_exportar(app_qt, csv_ejemplo, tmp_path):
    v = VentanaPrincipal()
    assert not v.boton_analizar.isEnabled()

    assert v.cargar(csv_ejemplo)
    assert v.boton_analizar.isEnabled()
    assert v.modelo_tabla.rowCount() == 3

    v.analizar()
    assert v.boton_exportar.isEnabled()
    assert list(v.resultado.columns[:3]) == ["riesgo", "tipo_probable", "motivo"]

    salida = tmp_path / "resultado.csv"
    v.exportar(salida)
    assert len(pd.read_csv(salida, sep=";", decimal=",")) == 3


def test_archivo_invalido_no_rompe_la_app(app_qt, tmp_path, monkeypatch):
    from PySide6.QtWidgets import QMessageBox

    avisos = []
    monkeypatch.setattr(QMessageBox, "warning", lambda *a: avisos.append(a))
    ruta = tmp_path / "malo.csv"
    ruta.write_text("x;y\n1;2\n", encoding="utf-8")

    v = VentanaPrincipal()
    assert not v.cargar(ruta)
    assert avisos and not v.boton_analizar.isEnabled()
