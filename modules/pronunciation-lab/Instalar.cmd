@echo off
setlocal
cd /d "%~dp0"
set "LAB_PYTHON_CHECK=import platform, struct, sys, tkinter; sys.exit(not (sys.version_info[:2] == (3, 12) and struct.calcsize('P') == 8 and platform.machine().upper() in ('AMD64', 'X86_64')))"
set "LAB_BUNDLED_PYTHON=%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"

if exist ".venv\Scripts\python.exe" if exist ".venv\Scripts\pythonw.exe" (
    ".venv\Scripts\python.exe" -c "%LAB_PYTHON_CHECK%" >nul 2>&1 && goto install
    echo El entorno .venv existente no es utilizable. Renombrelo antes de volver a instalar.
    goto failed
)

if defined EOI_LAB_PYTHON goto configured
py -3.12 -c "%LAB_PYTHON_CHECK%" >nul 2>&1 && goto launcher
python -c "%LAB_PYTHON_CHECK%" >nul 2>&1 && goto onpath
if exist "%LAB_BUNDLED_PYTHON%" (
    "%LAB_BUNDLED_PYTHON%" -c "%LAB_PYTHON_CHECK%" >nul 2>&1 && goto bundled
)
echo Se necesita Python 3.12 x64 con Tcl/Tk. Consulta README.md.
goto failed

:configured
"%EOI_LAB_PYTHON%" -c "%LAB_PYTHON_CHECK%" || goto failed
"%EOI_LAB_PYTHON%" -m venv .venv || goto failed
goto install

:launcher
py -3.12 -m venv .venv || goto failed
goto install

:onpath
python -m venv .venv || goto failed
goto install

:bundled
"%LAB_BUNDLED_PYTHON%" -m venv .venv || goto failed

:install
".venv\Scripts\python.exe" -m pip --isolated install --index-url https://pypi.org/simple --only-binary=:all: --disable-pip-version-check -r requirements.txt -r requirements-phonetics.txt || goto failed
".venv\Scripts\python.exe" -m pip check || goto failed
".venv\Scripts\python.exe" -c "import av, numpy, parselmouth, sounddevice, tkinter, onnxruntime, pronunciada; root = tkinter.Tk(); root.withdraw(); root.destroy()" || goto failed
".venv\Scripts\python.exe" src\phonetic_model.py || goto failed
call :install_kokoro || echo La referencia britanica Kokoro no esta disponible. El laboratorio base puede abrirse.
echo Instalacion completa. Para iniciar el laboratorio abre Abrir.cmd.
if /i not "%~1"=="--no-pause" pause
exit /b 0

:install_kokoro
".venv\Scripts\python.exe" -m pip --isolated install --index-url https://pypi.org/simple --only-binary=:all: --require-hashes --no-deps --disable-pip-version-check -r requirements-kokoro.txt || exit /b 1
".venv\Scripts\python.exe" src\kokoro_model.py
exit /b %ERRORLEVEL%

:failed
echo No se completo la instalacion. Revisa el mensaje anterior.
if /i not "%~1"=="--no-pause" pause
exit /b 1
