import pytest

from detector_fraude.nucleo.datos import ErrorDeFormato, leer_comprobantes


def test_lee_formato_syscafe(csv_ejemplo):
    c = leer_comprobantes(csv_ejemplo)
    assert len(c.tabla) == 3
    assert c.tabla.loc[0, "c1105"] == pytest.approx(100.5)
    assert c.tiene_etiqueta


def test_une_columnas_repetidas_y_limpia_espacios(csv_ejemplo):
    c = leer_comprobantes(csv_ejemplo)
    assert c.columnas_cuenta == ["c1105", "c1110", "c2205", "c4220"]
    assert c.tabla.loc[1, "c2205"] == pytest.approx(-50)
    assert any("repetidas" in a for a in c.avisos)


def test_avisa_comprobantes_descuadrados(csv_ejemplo):
    c = leer_comprobantes(csv_ejemplo)
    assert any("1 comprobantes no cuadran" in a for a in c.avisos)


def test_resumen(csv_ejemplo):
    r = leer_comprobantes(csv_ejemplo).resumen()
    assert r["Comprobantes"] == 3
    assert r["Años"] == "2023, 2024"


def test_rango_de_anos():
    from detector_fraude.nucleo.datos import _rango_anos

    assert _rango_anos([2020, 2021, 2022, 2023, 2024]) == "2020–2024"
    assert _rango_anos([2020, 2024]) == "2020, 2024"


def test_rechaza_archivo_sin_formato(tmp_path):
    ruta = tmp_path / "otro.csv"
    ruta.write_text("a,b\n1,2\n", encoding="utf-8")
    with pytest.raises(ErrorDeFormato):
        leer_comprobantes(ruta)
