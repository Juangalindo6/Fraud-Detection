"""Lectura y validación del CSV de comprobantes (vista "por tipo de comprobante").

Formato esperado (igual a infxComprobantes de SysCafe):
- separador `;` y coma decimal;
- columnas `tipo`, `numero`, `ano`, `mes`, `dia`, una columna `cXXXX` por cuenta
  y, opcionalmente, `misstate` (la etiqueta, solo existe en datos de práctica).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd

COLUMNAS_OBLIGATORIAS = ["tipo", "numero", "ano", "mes", "dia"]
PATRON_CUENTA = re.compile(r"^c\d+$")


class ErrorDeFormato(ValueError):
    """El archivo no tiene el formato de comprobantes esperado."""


@dataclass
class Comprobantes:
    """Tabla de comprobantes ya leída, con un resumen para mostrar en pantalla."""

    tabla: pd.DataFrame
    archivo: Path
    avisos: list[str] = field(default_factory=list)

    @property
    def columnas_cuenta(self) -> list[str]:
        return [c for c in self.tabla.columns if PATRON_CUENTA.match(c)]

    @property
    def tiene_etiqueta(self) -> bool:
        return "misstate" in self.tabla.columns

    def resumen(self) -> dict[str, object]:
        t = self.tabla
        anos = sorted(int(a) for a in t["ano"].dropna().unique())
        return {
            "Archivo": self.archivo.name,
            "Comprobantes": len(t),
            "Cuentas": len(self.columnas_cuenta),
            "Años": ", ".join(str(a) for a in anos) if anos else "-",
            "Trae etiqueta (misstate)": "Sí" if self.tiene_etiqueta else "No",
        }


def _normalizar_columnas(tabla: pd.DataFrame, avisos: list[str]) -> pd.DataFrame:
    """Quita espacios y mayúsculas de los nombres, y une columnas repetidas sumándolas."""
    # pandas renombra las columnas repetidas como "c2205.1"; se les quita el sufijo.
    nombres = [re.sub(r"^(c\d+)\.\d+$", r"\1", str(c).strip().lower()) for c in tabla.columns]
    if len(set(nombres)) != len(nombres):
        repetidas = sorted({n for n in nombres if nombres.count(n) > 1})
        avisos.append(f"Columnas repetidas unidas: {', '.join(repetidas)}")
    tabla.columns = nombres
    if tabla.columns.duplicated().any():
        cuentas = [c for c in dict.fromkeys(nombres) if PATRON_CUENTA.match(c)]
        resto = [c for c in dict.fromkeys(nombres) if not PATRON_CUENTA.match(c)]
        unidas = {c: tabla.loc[:, tabla.columns == c].sum(axis=1) for c in cuentas}
        fijas = {c: tabla.loc[:, tabla.columns == c].iloc[:, 0] for c in resto}
        tabla = pd.DataFrame({**fijas, **unidas})[list(dict.fromkeys(nombres))]
    return tabla


def leer_comprobantes(ruta: str | Path) -> Comprobantes:
    """Lee un CSV de comprobantes y verifica que tenga el formato esperado."""
    ruta = Path(ruta)
    if not ruta.exists():
        raise ErrorDeFormato(f"No existe el archivo: {ruta}")

    try:
        tabla = pd.read_csv(ruta, sep=";", decimal=",", encoding="utf-8-sig", low_memory=False)
    except UnicodeDecodeError:
        tabla = pd.read_csv(ruta, sep=";", decimal=",", encoding="latin-1", low_memory=False)

    avisos: list[str] = []
    tabla = _normalizar_columnas(tabla, avisos)

    faltan = [c for c in COLUMNAS_OBLIGATORIAS if c not in tabla.columns]
    if faltan:
        raise ErrorDeFormato(
            "El archivo no parece un CSV de comprobantes. Faltan las columnas: "
            + ", ".join(faltan)
            + ". Revisa que use ';' como separador."
        )

    cuentas = [c for c in tabla.columns if PATRON_CUENTA.match(c)]
    if not cuentas:
        raise ErrorDeFormato("El archivo no tiene columnas de cuentas (cXXXX).")

    for c in cuentas:
        if not pd.api.types.is_numeric_dtype(tabla[c]):
            tabla[c] = pd.to_numeric(tabla[c], errors="coerce")
            avisos.append(f"La cuenta {c} tenía valores no numéricos; se dejaron vacíos.")
    tabla[cuentas] = tabla[cuentas].fillna(0.0)

    descuadrados = int((tabla[cuentas].sum(axis=1).abs() > 0.01).sum())
    if descuadrados:
        avisos.append(f"{descuadrados} comprobantes no cuadran (débitos ≠ créditos).")

    return Comprobantes(tabla=tabla, archivo=ruta, avisos=avisos)
