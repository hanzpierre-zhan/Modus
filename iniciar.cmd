@echo off
setlocal
cd /d "%~dp0"
if not exist "%~dp0.venv-local\Scripts\python.exe" (
    echo Falta el entorno local .venv-local de Modus.
    exit /b 1
)
"%~dp0.venv-local\Scripts\python.exe" "%~dp0app.py" %*
