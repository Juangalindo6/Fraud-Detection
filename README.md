# Detector de Fraude Contable (app de escritorio)

App de escritorio para Windows, **100 % local**, que carga los comprobantes contables
(CSV con el formato de infxComprobantes de SysCafe), los muestra y, más adelante,
los analizará con modelos de machine learning para priorizar posibles fraudes.

Proyecto de grado, UCC 2025.

> **Importante:** este repositorio es público. **Nunca** se suben datos (CSV, Excel)
> ni modelos entrenados. El `.gitignore` ya los bloquea.

## Estado actual (fase 1: solo la app)

Interfaz con menú lateral, tema claro y oscuro, y tres pantallas:

- **Inicio:** arrastrar o elegir el CSV de comprobantes (`;` y coma decimal), con guía de 3 pasos
  y archivos recientes. Los archivos grandes se leen en segundo plano.
- **Datos:** tarjetas de resumen (comprobantes, cuentas, años, descuadrados), avisos de calidad
  y tabla con buscador.
- **Análisis:** elegir el modelo, analizar, ver el riesgo como etiquetas de color y exportar a CSV.
  Por ahora solo existe el detector vacío ("Sin modelo"); los modelos se conectarán después en
  `src/detector_fraude/nucleo/detector.py`.

Para regenerar las capturas con datos inventados: `python herramientas/capturas.py capturas`.

## Descargar el .exe

Cada cambio compila el ejecutable en GitHub Actions (runner de Windows) y lo publica en **Releases**:

1. Abre la sección **Releases** del repositorio (columna derecha) y entra a la más reciente.
2. Descarga `DetectorFraude.exe` (no hace falta iniciar sesión).
3. Haz doble clic. No necesita instalar Python ni tener internet.

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
  interfaz/              ventana, pantallas, tema y componentes (PySide6)
herramientas/            capturas de pantalla con datos inventados
empaquetado/             script para PyInstaller y compilación local
tests/                   pruebas automáticas
.github/workflows/       pruebas y compilación del .exe en Windows
```
