# Save Your Money

Aplicativo desktop para controle de finanças pessoais. Este repositório contém uma implementação inicial de referência com backend em Python e interface em Electron. O objetivo do MVP é permitir o registro de categorias, gastos e entradas de dinheiro em um banco local SQLite.

## Instalador (Raiz)

- Arquivo para distribuir: `SaveYourMoney-Installer.exe`
- Para gerar um novo apos ajustes no codigo: execute `deploy-installer.bat` na raiz.
- Guia rapido: `DEPLOY-INSTALLER.txt`

## Pré-requisitos

- Python 3.10+
- Node 18+
- npm

## Estrutura de Pastas

```
backend/        # Código Python contendo domínio, serviços, repositórios e casos de uso
frontend/       # Código Electron para a interface de usuário
```

Consulte `implementation_plan.md` para obter o roadmap e detalhes de arquitetura.

## Instalação

1. Backend:
   - `cd backend`
   - `python -m venv .venv`
   - Ative o ambiente virtual
   - `pip install -r requirements.txt`
2. Frontend:
   - `cd frontend`
   - `npm install`

## Execução

1. Inicie o backend:
   - `python -m backend.app`
2. Em outro terminal, inicie o Electron:
   - `npm run start`

## Executável `.exe` (sem terminal para o usuário)

O frontend agora inicia o backend automaticamente em segundo plano. Isso permite distribuir o app como instalador `.exe` para uso por clique duplo.

### Como gerar o instalador no Windows

1. Garanta que o ambiente Python do backend esteja pronto:
   - `cd backend`
   - `python -m venv .venv`
   - `.\.venv\Scripts\pip install -r requirements.txt`
2. Instale dependências de build do frontend:
   - `cd ..\frontend`
   - `npm install`
3. Gere o instalador:
   - `npm run build:win`

O instalador será gerado em `frontend\dist\` (arquivo `.exe`).

### Primeiro uso e próximos usos

- Primeiro uso: o usuário instala e abre o app pelo atalho do Windows.
- Próximos usos: basta abrir o atalho; o backend sobe automaticamente.
- O banco SQLite e backups ficam na pasta de dados do usuário (AppData), evitando problemas de permissão em `Program Files`.

## Atualização automática (auto-update)

O app já está preparado para auto-update no Windows via `electron-updater`.

### Configuração inicial

1. Edite `frontend\update-config.json` e informe a URL pública onde ficarão os arquivos de atualização:
   - exemplo: `https://seudominio.com/saveyourmoney/windows`
2. Gere o instalador:
   - `cd frontend`
   - `npm install`
   - `npm run build:win`

Na pasta `frontend\dist\` serão gerados, entre outros:
- `SaveYourMoney Setup <versao>.exe`
- `latest.yml`
- pacote(s) `.7z`/`.exe` usados no update

### Publicação dos updates

1. Faça upload de **todos** os arquivos gerados em `frontend\dist\` para a URL definida em `update-config.json`.
2. Mantenha os nomes dos arquivos exatamente como gerados.
3. Em cada nova versão:
   - aumente `version` em `frontend\package.json`
   - rode `npm run build:win`
   - publique novamente os novos arquivos na mesma URL

### Comportamento no usuário final

- O app verifica atualização automaticamente ao abrir e periodicamente.
- Se houver nova versão, pergunta se deseja baixar.
- Após baixar, pergunta se deseja reiniciar para instalar.
