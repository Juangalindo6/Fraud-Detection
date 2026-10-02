"""Script que PyInstaller convierte en DetectorFraude.exe."""

import sys

from detector_fraude.__main__ import main

if __name__ == "__main__":
    sys.exit(main())
