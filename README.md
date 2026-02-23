# Save Your Money

Aplicativo desktop para controle de finanças pessoais, com backend em Python (Flask + SQLite) e interface em Electron.

## Visão geral

- Backend local com API HTTP em `http://127.0.0.1:5000`
- Frontend desktop em Electron
- Banco local SQLite (`saveyourmoney.db`)
- Geração de instalador Windows (`.exe`) com `electron-builder`
- Suporte a auto-update via `electron-updater`

## Estrutura do projeto

```text
backend/                 # API, domínio, casos de uso e repositórios SQLite
frontend/                # Aplicação Electron
deploy-installer.bat     # Script de deploy do instalador
DEPLOY-INSTALLER.txt     # Guia rápido do deploy
SaveYourMoney-Installer.exe  # Instalador final para distribuição (raiz)
```

## Pré-requisitos

- Windows (fluxo de instalador atual foi preparado para Windows/NSIS)
- Python 3.10+
- Node.js 18+
- npm

## Setup de desenvolvimento

1. Criar e preparar o ambiente Python:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

2. Instalar dependências do frontend:

```powershell
cd ..\frontend
npm install
```

## Como executar em desenvolvimento

1. Iniciar backend (na raiz do projeto):

```powershell
cd D:\developer\projects\SaveYourMoney
backend\.venv\Scripts\python.exe -m backend.app
```

2. Em outro terminal, iniciar Electron:

```powershell
cd D:\developer\projects\SaveYourMoney\frontend
npm run start
```

## Build do instalador (recomendado)

Use o script da raiz:

```powershell
.\deploy-installer.bat
```

Esse script executa automaticamente:

1. Cria o `backend\.venv` (se não existir) e instala `backend\requirements.txt`
2. Executa `npm install` no `frontend`
3. Gera instalador com `npx electron-builder --win nsis`
4. Copia o instalador mais recente de `frontend\dist\SaveYourMoney Setup *.exe` para:
   `SaveYourMoney-Installer.exe` (na raiz)

Arquivo final para distribuição:

- `SaveYourMoney-Installer.exe`

Referência rápida:

- `DEPLOY-INSTALLER.txt`

## Build manual (alternativa)

```powershell
cd frontend
npm install
npm run build:win
```

Artefatos de build ficam em `frontend\dist\`.

## Execução no app instalado

- O Electron inicia o backend automaticamente em segundo plano.
- Dados e backups são gravados na pasta de usuário (`AppData`), não em `Program Files`.
- Logs do backend ficam em `AppData\...\logs\backend.log`.

## Auto-update (Windows)

O app usa `electron-updater` com provider `generic`.

1. Configure `frontend\update-config.json` com a URL pública dos artefatos.
2. A cada release:
   - Atualize `version` em `frontend\package.json`
   - Rode o build
   - Publique **todos** os arquivos de `frontend\dist\` na URL configurada

## Testes (backend)

Os testes ficam em `backend\tests\`. Se quiser executar:

```powershell
cd backend
python -m pytest
```

Se `pytest` não estiver instalado no ambiente, instale com:

```powershell
python -m pip install pytest
```

## Troubleshooting rápido

- Erro no build do instalador:
  - Verifique se Node/npm estão instalados e acessíveis no terminal.
- Backend não sobe no app instalado:
  - Verifique o log em `AppData\...\logs\backend.log`.
- `SaveYourMoney-Installer.exe` não atualizou:
  - Confirme se `frontend\dist\SaveYourMoney Setup *.exe` foi gerado com sucesso.
