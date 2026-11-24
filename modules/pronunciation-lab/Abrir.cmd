@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\pythonw.exe" goto setup
".venv\Scripts\python.exe" -c "import sys; sys.path.insert(0, 'src'); import lab_app" >nul 2>&1 || goto setup
start "" ".venv\Scripts\pythonw.exe" "%~dp0src\lab_app.py"
exit /b 0

:setup
echo Ejecuta Instalar.cmd antes de abrir el laboratorio.
pause
exit /b 1
