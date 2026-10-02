"""Punto de entrada: `python -m detector_fraude` o el .exe."""

import sys


def main() -> int:
    from PySide6.QtWidgets import QApplication

    from detector_fraude import NOMBRE_APP
    from detector_fraude.interfaz.ventana_principal import VentanaPrincipal

    app = QApplication(sys.argv)
    app.setApplicationName(NOMBRE_APP)
    ventana = VentanaPrincipal()
    ventana.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
