@echo off
setlocal

set "ROOT=%~dp0"
cd /d "%ROOT%"

echo [1/4] Preparando backend...
if not exist "backend\.venv\Scripts\python.exe" (
  python -m venv backend\.venv || goto :error
)
call "backend\.venv\Scripts\python.exe" -m pip install -r "backend\requirements.txt" || goto :error

echo [2/4] Preparando frontend...
cd /d "%ROOT%frontend"
call npm.cmd install || goto :error

echo [3/4] Gerando instalador...
call npx.cmd electron-builder --win nsis || goto :error

echo [4/4] Copiando instalador para a raiz...
for /f "delims=" %%F in ('dir /b /o:-d "dist\SaveYourMoney Setup *.exe"') do (
  copy /Y "dist\%%F" "%ROOT%SaveYourMoney-Installer.exe" >nul
  goto :done
)

echo Nenhum instalador .exe encontrado em frontend\dist.
goto :error

:done
echo.
echo Instalador pronto:
echo %ROOT%SaveYourMoney-Installer.exe
exit /b 0

:error
echo.
echo Falha no deploy do instalador.
exit /b 1
