@echo off
REM Compila DetectorFraude.exe en este PC (alternativa local a GitHub Actions).
REM Requisito: Python 3.11 instalado. El .exe queda en la carpeta dist\
cd /d "%~dp0\.."
python -m venv .venv || goto :error
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip || goto :error
pip install -r requirements-dev.txt || goto :error
pyinstaller --noconfirm --onefile --windowed --name DetectorFraude --paths src empaquetado\lanzador.py || goto :error
echo.
echo Listo: dist\DetectorFraude.exe
goto :eof
:error
echo Hubo un error. Revisa los mensajes de arriba.
exit /b 1
