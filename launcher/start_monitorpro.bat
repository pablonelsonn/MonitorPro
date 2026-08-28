@echo off
REM Duplo-clique aqui sobe o servidor (se preciso) e abre o Dashboard.
REM Ajuste o caminho da venv abaixo se o nome/local for diferente.

cd /d "%~dp0.."

if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
) else if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

python launcher\start_monitorpro.py
pause
