import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

CSV_EJEMPLO = (
    "tipo;numero;ano;mes;dia;misstate;c1105;c1110;c2205;c2205; c4220\n"
    "A1;1;2024;1;5;0;100,5;-100,5;0;0;0\n"
    "A1;2;2024;1;6;0;0;50;-20;-30;0\n"
    "B2;3;2023;2;7;2;10;0;0;0;-5\n"
)


@pytest.fixture
def csv_ejemplo(tmp_path):
    ruta = tmp_path / "comprobantes.csv"
    ruta.write_text(CSV_EJEMPLO, encoding="utf-8")
    return ruta


@pytest.fixture(scope="session")
def app_qt():
    from PySide6.QtWidgets import QApplication

    return QApplication.instance() or QApplication([])
