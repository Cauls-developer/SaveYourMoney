@echo off
setlocal EnableExtensions EnableDelayedExpansion

set "ROOT=%~dp0"
cd /d "%ROOT%"

set "PYTHON_CMD=python"
set "NPM_CMD=npm.cmd"
set "NPX_CMD=npx.cmd"
set "PYTHON_VERSION=3.12.8"
set "PYTHON_URL=https://www.python.org/ftp/python/%PYTHON_VERSION%/python-%PYTHON_VERSION%-amd64.exe"
set "NODE_VERSION=20.19.6"
set "NODE_ZIP_URL=https://nodejs.org/dist/v%NODE_VERSION%/node-v%NODE_VERSION%-win-x64.zip"
set "DOWNLOADS_DIR=%ROOT%.installer-cache"
set "NODE_LOCAL_DIR=%LocalAppData%\Programs\nodejs"
set "BUILD_LOG=%DOWNLOADS_DIR%\electron-builder.log"

if not exist "%DOWNLOADS_DIR%" mkdir "%DOWNLOADS_DIR%" >nul 2>&1

where python >nul 2>&1
if errorlevel 1 (
  echo Python nao encontrado. Instalando automaticamente...
  where winget >nul 2>&1
  if errorlevel 1 (
    echo winget indisponivel. Usando fallback de download direto do Python...
    set "PYTHON_INSTALLER=%DOWNLOADS_DIR%\python-%PYTHON_VERSION%-amd64.exe"
    powershell -NoProfile -ExecutionPolicy Bypass -Command "Invoke-WebRequest -Uri '%PYTHON_URL%' -OutFile '%PYTHON_INSTALLER%' -UseBasicParsing" || goto :error
    "%PYTHON_INSTALLER%" /quiet InstallAllUsers=0 PrependPath=1 Include_pip=1 Include_launcher=1 || goto :error
    set "PATH=%PATH%;%LocalAppData%\Programs\Python\Python312;%LocalAppData%\Programs\Python\Python312\Scripts;%LocalAppData%\Microsoft\WindowsApps"
    goto :python_check
  )
  winget install --id Python.Python.3.12 --exact --scope user --silent --accept-package-agreements --accept-source-agreements || goto :error
  set "PATH=%PATH%;%LocalAppData%\Microsoft\WindowsApps"
  for /f "delims=" %%D in ('dir /b /ad "%LocalAppData%\Programs\Python\Python3*" 2^>nul') do (
    set "PATH=!PATH!;%LocalAppData%\Programs\Python\%%D;%LocalAppData%\Programs\Python\%%D\Scripts"
  )
)

:python_check
where python >nul 2>&1
if errorlevel 1 (
  for /f "delims=" %%D in ('dir /b /ad /o:-n "%LocalAppData%\Programs\Python\Python3*" 2^>nul') do (
    if exist "%LocalAppData%\Programs\Python\%%D\python.exe" (
      set "PYTHON_CMD=%LocalAppData%\Programs\Python\%%D\python.exe"
      goto :python_ready
    )
  )
  if exist "%LocalAppData%\Programs\Python\Python312\python.exe" (
    set "PYTHON_CMD=%LocalAppData%\Programs\Python\Python312\python.exe"
    goto :python_ready
  )
  echo Falha ao localizar python apos instalacao.
  goto :error
)

:python_ready
echo Python pronto: %PYTHON_CMD%

where npm >nul 2>&1
if errorlevel 1 (
  echo Node.js/npm nao encontrados. Instalando automaticamente...
  where winget >nul 2>&1
  if errorlevel 1 (
    echo winget indisponivel. Usando fallback de pacote zip do Node.js...
    set "NODE_ZIP=%DOWNLOADS_DIR%\node-v%NODE_VERSION%-win-x64.zip"
    if exist "%NODE_LOCAL_DIR%" rmdir /s /q "%NODE_LOCAL_DIR%"
    mkdir "%NODE_LOCAL_DIR%" >nul 2>&1 || goto :error
    powershell -NoProfile -ExecutionPolicy Bypass -Command "Invoke-WebRequest -Uri '%NODE_ZIP_URL%' -OutFile '%NODE_ZIP%' -UseBasicParsing" || goto :error
    powershell -NoProfile -ExecutionPolicy Bypass -Command "Expand-Archive -Path '%NODE_ZIP%' -DestinationPath '%DOWNLOADS_DIR%' -Force" || goto :error
    if not exist "%DOWNLOADS_DIR%\node-v%NODE_VERSION%-win-x64\node.exe" (
      echo Falha ao extrair Node.js.
      goto :error
    )
    xcopy /E /I /Y "%DOWNLOADS_DIR%\node-v%NODE_VERSION%-win-x64\*" "%NODE_LOCAL_DIR%\" >nul || goto :error
    set "PATH=%PATH%;%NODE_LOCAL_DIR%;%NODE_LOCAL_DIR%\node_modules\npm\bin;%LocalAppData%\Microsoft\WindowsApps"
    goto :node_check
  )

  winget install --id OpenJS.NodeJS.LTS --exact --scope user --silent --accept-package-agreements --accept-source-agreements || goto :error

  set "PATH=%PATH%;%LocalAppData%\Microsoft\WindowsApps;%LocalAppData%\Programs\nodejs"
)

:node_check
where npm >nul 2>&1
if errorlevel 1 (
  if exist "%LocalAppData%\Programs\nodejs\npm.cmd" (
    set "NPM_CMD=\"%LocalAppData%\Programs\nodejs\npm.cmd\""
    set "NPX_CMD=\"%LocalAppData%\Programs\nodejs\npx.cmd\""
    goto :node_ready
  )
  if exist "%NODE_LOCAL_DIR%\npm.cmd" (
    set "NPM_CMD=\"%NODE_LOCAL_DIR%\npm.cmd\""
    set "NPX_CMD=\"%NODE_LOCAL_DIR%\npx.cmd\""
    goto :node_ready
  )
  echo Falha ao localizar npm apos instalacao.
  goto :error
)

:node_ready
echo Node/npm prontos.

echo [1/5] Verificando backend (binario)...
set "BACKEND_EXE=%ROOT%backend\SaveYourMoney-Backend.exe"
set "BACKEND_BIN_UPTODATE=0"
if defined FORCE_BACKEND_BUILD (
  echo FORCE_BACKEND_BUILD definido. Ignorando cache do binario.
) else (
  if exist "%BACKEND_EXE%" (
    set "BACKEND_BIN_UPTODATE=1"
  )
)

if defined FORCE_BACKEND_BUILD goto :build_backend
if "%BACKEND_BIN_UPTODATE%"=="1" goto :skip_backend

:build_backend
echo [2/5] Empacotando backend (binario)...
call "build-backend.bat" || goto :error_backend
goto :after_backend

:skip_backend
echo Backend binario atualizado encontrado. Pulando build.

:after_backend

echo [3/5] Preparando frontend...
cd /d "%ROOT%frontend"
call %NPM_CMD% install || goto :error

echo [4/5] Gerando instalador...
call %NPX_CMD% electron-builder --win nsis > "%BUILD_LOG%" 2>&1
if errorlevel 1 (
  type "%BUILD_LOG%"
  findstr /I /C:"spawn EPERM" /C:"app-builder.exe" "%BUILD_LOG%" >nul 2>&1
  if not errorlevel 1 (
    echo.
    echo Diagnostico: o Windows bloqueou a execucao do app-builder.exe ^(spawn EPERM^).
    echo Causas comuns:
    echo 1^) Antivirus/Windows Security bloqueando executaveis em node_modules.
    echo 2^) Controlled Folder Access ativo bloqueando o processo.
    echo 3^) Arquivo baixado marcado como nao confiavel.
    echo.
    echo Como corrigir:
    echo - Adicione excecao para a pasta do projeto:
    echo   %ROOT%frontend\node_modules\app-builder-bin\
    echo - No Windows Security, permita o app-builder.exe em Ransomware Protection.
    echo - Execute uma vez no PowerShell:
    echo   Unblock-File "%ROOT%frontend\node_modules\app-builder-bin\win\x64\app-builder.exe"
    echo - Reexecute o deploy-installer.bat como usuario com permissao local.
  )
  goto :error
)
type "%BUILD_LOG%"

echo [5/5] Copiando instalador para a raiz...
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

:error_backend
echo.
echo Falha ao empacotar o backend.
if exist "%ROOT%backend\build-backend.log" (
  echo Log do backend:
  type "%ROOT%backend\build-backend.log"
)
goto :error

:error
echo.
echo Falha no deploy do instalador.
exit /b 1
