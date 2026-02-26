# Save Your Money

Aplicativo desktop para controle de finanças pessoais, com backend em
Python (Flask + SQLite) e interface desktop em Electron.

------------------------------------------------------------------------

# 🚀 Visão Geral

**Save Your Money** é um aplicativo desktop focado em organização
financeira pessoal.

Arquitetura:

-   Backend local em Python (Flask + SQLite)
-   API HTTP em `http://127.0.0.1:5000`
-   Documentação Swagger em `http://127.0.0.1:5000/docs`
-   Frontend desktop em Electron
-   Banco local SQLite (`saveyourmoney.db`)
-   Instalador Windows gerado com `electron-builder`
-   Auto-update via `electron-updater`

------------------------------------------------------------------------

# 📁 Estrutura do Projeto

    backend/                 API, domínio, casos de uso e repositórios SQLite
    frontend/                Aplicação Electron
    scripts/                 Scripts auxiliares
    deploy-installer.bat     Script principal de build do instalador
    build-backend.bat        Build manual do backend
    SaveYourMoney-Installer.exe  Instalador final (raiz)

------------------------------------------------------------------------

# ⚙️ Pré-requisitos

-   Windows (fluxo de instalador preparado para NSIS)
-   Python 3.10+
-   Node.js 18+

O script `deploy-installer.bat` instala dependências automaticamente via
`winget` quando disponível.

------------------------------------------------------------------------

# 🛠️ Setup de Desenvolvimento

## Backend

``` powershell
cd backend
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Frontend

``` powershell
cd ..\frontend
npm install
```

------------------------------------------------------------------------

# ▶️ Executando em Desenvolvimento

## Iniciar Backend

``` powershell
backend\.venv\Scripts\python.exe -m backend.app
```

## Iniciar Electron

``` powershell
cd frontend
npm run start
```

------------------------------------------------------------------------

# 🏗️ Build do Instalador (Recomendado)

``` powershell
.\deploy-installer.bat
```

O script:

1.  Garante Python e Node instalados
2.  Cria `.venv` se necessário
3.  Empacota backend via PyInstaller
4.  Executa `npm install`
5.  Gera instalador via electron-builder
6.  Copia instalador final para raiz

Artefato final:

    SaveYourMoney-Installer.exe

------------------------------------------------------------------------

# 🧪 Testes (Backend)

``` powershell
cd backend
python -m pytest
```

------------------------------------------------------------------------

# 🔄 Sistema de Execução Automática de Tasks (Codex)

Este projeto possui um ecossistema opcional para automação de tarefas
via Codex.

## Objetivo

Permitir que tarefas sejam descritas em `Tasks.md` e executadas
automaticamente, com registro técnico completo em `progress.md`.

## Arquivos na Raiz

    Tasks.md
    progress.md
    scripts/run_tasks.bat

## Como Funciona

1.  O desenvolvedor escreve tarefas em `Tasks.md` com:
    -   Título
    -   Descrição
    -   Critérios de aceite
    -   Status (TODO \| DONE \| BLOCKED)
2.  Executa:

``` powershell
.\scripts\run_tasks.bat
```

3.  O Codex:
    -   Lê `AGENTS.md`
    -   Processa a primeira task com Status: TODO
    -   Executa mudanças mínimas necessárias
    -   Roda validações (pytest / npm quando aplicável)
    -   Atualiza `Tasks.md`
    -   Registra em `progress.md`
    -   Repete até não haver TODO

## Benefícios

-   Histórico técnico automático
-   Execução disciplinada
-   Redução de decisões repetitivas
-   Padronização de mudanças
-   Economia de tokens (arquivos como fonte de verdade)

------------------------------------------------------------------------

# 🧠 Contribuição via Codex (Modelo Profissional)

Este projeto adota um modelo estruturado de colaboração assistida por
IA.

## Princípios

-   Tasks como fonte oficial de trabalho
-   Uma task por vez
-   Critérios de aceite obrigatórios
-   Registro técnico completo
-   Mudanças pequenas e auditáveis

## Fluxo de Contribuição

1.  Criar ou atualizar `Tasks.md`
2.  Definir critérios de aceite claros
3.  Executar runner
4.  Revisar `progress.md`
5.  Validar testes e commits

Esse modelo garante:

-   Rastreabilidade
-   Transparência técnica
-   Menor risco de regressão
-   Integração harmoniosa entre backend e frontend

------------------------------------------------------------------------

# 🔐 Execução no App Instalado

-   Backend inicia automaticamente
-   Dados armazenados em AppData
-   Logs disponíveis em `AppData\...\logs\backend.log`

------------------------------------------------------------------------

# 🔁 Auto-update (Windows)

1.  Configurar `frontend/update-config.json`
2.  Atualizar `version` em `frontend/package.json`
3.  Gerar build
4.  Publicar arquivos de `frontend/dist/`

------------------------------------------------------------------------

# 📌 Troubleshooting

-   Verificar bloqueio de antivirus no `app-builder.exe`
-   Confirmar geração de `backend\SaveYourMoney-Backend.exe`
-   Rodar com `SAVEYOURMONEY_DEBUG=1` para debug backend

------------------------------------------------------------------------

# 📜 Licença

Uso pessoal e educacional.
