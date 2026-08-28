@echo off
REM ============================================================
REM  build_exe.bat
REM  --------------
REM  Gera o MonitorPro.exe a partir do dashboard/main.py.
REM
REM  Como usar:
REM  1) Extraia o MonitorPro.zip em uma pasta no Windows.
REM  2) Coloque este arquivo (build_exe.bat) dentro dessa pasta,
REM     no mesmo nivel de requirements.txt.
REM  3) De um duplo-clique neste arquivo (ou rode-o pelo Prompt
REM     de Comando).
REM  4) Ao final, o executavel estara em:
REM        dist\MonitorPro.exe
REM     Esse arquivo pode ser copiado para a Area de Trabalho e
REM     aberto com duplo-clique dali pra frente, sem terminal.
REM ============================================================

echo Instalando dependencias...
pip install -r requirements.txt pyinstaller

echo.
echo Gerando o executavel MonitorPro.exe ...
pyinstaller --noconfirm --onefile --windowed ^
    --name "MonitorPro" ^
    --icon NONE ^
    dashboard\main.py

echo.
echo ============================================================
echo  Pronto! O executavel esta em: dist\MonitorPro.exe
echo  Copie esse arquivo para a Area de Trabalho e abra com
echo  duplo-clique. Nao precisa mais de terminal a partir daqui.
echo ============================================================
pause
