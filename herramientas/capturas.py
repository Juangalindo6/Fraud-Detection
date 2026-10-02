"""Genera capturas de las pantallas con datos inventados (sin datos reales).

Uso:  QT_QPA_PLATFORM=offscreen python herramientas/capturas.py carpeta_salida
"""

from __future__ import annotations

import random
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from PySide6.QtCore import QSettings  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402

from detector_fraude.interfaz.ventana_principal import VentanaPrincipal  # noqa: E402

CUENTAS = ["c1105", "c1110", "c1305", "c1435", "c2205", "c2365", "c2408", "c4135", "c5105", "c6135"]
TIPOS = ["FV1", "RC1", "CE1", "NC1", "C18", "R13"]


def csv_inventado(ruta: Path, filas: int = 2400) -> None:
    azar = random.Random(7)
    lineas = ["tipo;numero;ano;mes;dia;" + ";".join(CUENTAS)]
    for i in range(filas):
        valores = [0.0] * len(CUENTAS)
        monto = round(azar.lognormvariate(13, 1.2), 2)
        a, b = azar.sample(range(len(CUENTAS)), 2)
        valores[a], valores[b] = monto, -monto
        if i % 97 == 0:
            valores[b] += 0.5  # algunos descuadrados para que aparezca el aviso
        fecha = (azar.choice([2022, 2023, 2024]), azar.randint(1, 12), azar.randint(1, 28))
        celdas = ";".join(f"{v:.2f}".replace(".", ",") if v else "0" for v in valores)
        lineas.append(f"{azar.choice(TIPOS)};{i + 1};{fecha[0]};{fecha[1]};{fecha[2]};{celdas}")
    ruta.write_text("\n".join(lineas), encoding="utf-8")


def main(salida: Path) -> None:
    salida.mkdir(parents=True, exist_ok=True)
    app = QApplication.instance() or QApplication([])
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        csv = tmp / "comprobantes_2024.csv"
        csv_inventado(csv)
        for oscuro in (False, True):
            ajustes = QSettings(str(tmp / f"ajustes{oscuro}.ini"), QSettings.IniFormat)
            ajustes.setValue("tema_oscuro", oscuro)
            ajustes.setValue("recientes", [str(csv)])
            v = VentanaPrincipal(ajustes)
            v.resize(1280, 800)
            v.show()
            sufijo = "_oscuro" if oscuro else ""

            def guardar(nombre: str) -> None:
                app.processEvents()
                v.grab().save(str(salida / f"{nombre}{sufijo}.png"))

            guardar("1_inicio")
            v.cargar(csv)
            guardar("2_datos")
            v.ir_a(v.ANALISIS)
            guardar("3_analisis_vacio")
            v.analizar()
            guardar("4_analisis_resultado")
            v.close()


if __name__ == "__main__":
    main(Path(sys.argv[1] if len(sys.argv) > 1 else "capturas"))
