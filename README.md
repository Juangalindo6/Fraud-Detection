# Detector de Fraude Contable (app de escritorio)

App de escritorio para Windows, **100 % local**, que carga los comprobantes contables
(CSV con el formato de infxComprobantes de SysCafe), los muestra y, más adelante,
los analizará con modelos de machine learning para priorizar posibles fraudes.

Proyecto de grado, UCC 2025.

> **Importante:** este repositorio es público. **Nunca** se suben datos (CSV, Excel)
> ni modelos entrenados. El `.gitignore` ya los bloquea.

## Estado actual (fase 1: solo la app)

- Cargar un CSV de comprobantes (`;` como separador y coma decimal).
- Ver un resumen (comprobantes, cuentas, años, si trae etiqueta) y avisos
  (columnas repetidas unidas, comprobantes descuadrados).
- Vista previa de la tabla.
- Botón **Analizar**, por ahora con un detector vacío ("Sin modelo"), y **Exportar** el resultado a CSV.
- Los modelos se conectarán después en `src/detector_fraude/nucleo/detector.py`.

## Descargar el .exe

Cada cambio compila el ejecutable en GitHub Actions (runner de Windows):

1. Abre la pestaña **Actions** del repositorio y entra a la última ejecución en verde.
2. Descarga el artefacto **DetectorFraude-windows** (es un .zip con `DetectorFraude.exe`).
3. Descomprime y haz doble clic. No necesita instalar Python ni tener internet.

Windows puede mostrar el aviso de SmartScreen porque el .exe no está firmado:
"Más información" → "Ejecutar de todas formas".

## Ejecutar desde el código (para desarrollo)

```bat
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements-dev.txt
set PYTHONPATH=src
python -m detector_fraude
pytest
```

Para compilar el .exe en tu propio PC: `empaquetado\compilar_exe.bat`.

## Estructura

```
src/detector_fraude/
  nucleo/datos.py        lectura y validación del CSV
  nucleo/detector.py     punto de extensión para los modelos (hoy vacío)
  interfaz/              ventana principal (PySide6)
empaquetado/             script para PyInstaller y compilación local
tests/                   pruebas automáticas
.github/workflows/       pruebas y compilación del .exe en Windows
```
