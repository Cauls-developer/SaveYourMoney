@echo off
setlocal EnableExtensions EnableDelayedExpansion

set "ROOT=%~dp0"
cd /d "%ROOT%"

set "PYTHON_CMD=python"
set "VENV_PATH=backend\.venv"
set "BUILD_LOG=%ROOT%backend\build-backend.log"

echo Iniciando build do backend... > "%BUILD_LOG%"

if not exist "%VENV_PATH%\Scripts\python.exe" (
  echo Criando venv do backend...
  %PYTHON_CMD% -m venv "%VENV_PATH%" || goto :error
)

set "PYTHON_CMD=%VENV_PATH%\Scripts\python.exe"

echo Instalando dependencias do backend...
call "%PYTHON_CMD%" -m pip install -r "backend\requirements.txt" >> "%BUILD_LOG%" 2>&1 || goto :error
call "%PYTHON_CMD%" -m pip install pyinstaller >> "%BUILD_LOG%" 2>&1 || goto :error

echo Empacotando backend com PyInstaller...
call "%PYTHON_CMD%" -m PyInstaller ^
  --clean ^
  --noconfirm ^
  --onefile ^
  --name "SaveYourMoney-Backend" ^
  --distpath "%ROOT%backend\dist" ^
  --workpath "%ROOT%backend\build" ^
  --specpath "%ROOT%backend\build" ^
  --add-data "%ROOT%backend\openapi.yaml;backend" ^
  "%ROOT%backend\run_backend.py" >> "%BUILD_LOG%" 2>&1 || goto :error

if not exist "%ROOT%backend\dist\SaveYourMoney-Backend.exe" (
  echo Falha: binario do backend nao encontrado.
  goto :error
)

echo Copiando binario para backend\SaveYourMoney-Backend.exe...
copy /Y "%ROOT%backend\dist\SaveYourMoney-Backend.exe" "%ROOT%backend\SaveYourMoney-Backend.exe" >nul || goto :error

echo Backend empacotado com sucesso.
exit /b 0

:error
echo.
echo Falha ao empacotar o backend.
echo Verifique o log: %BUILD_LOG%
type "%BUILD_LOG%"
exit /b 1
