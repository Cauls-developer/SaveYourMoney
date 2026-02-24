# Backlog de Melhorias - SaveYourMoney

Este documento consolida melhorias tecnicas e de produto para o projeto inteiro (backend, frontend, build e operacao), indo alem do modulo de metas.

## Prioridade P0 (alto impacto / risco)

- Seguranca no frontend (XSS): remover montagem de UI com `innerHTML` para dados vindos da API e migrar para `textContent`/DOM seguro.
- Padronizar atualizacoes parciais no backend: substituir fallback com `or existing` por checagem explicita de chave no payload (`if "campo" in data`).
- Correcao de parsing booleano: evitar `bool("false") == True` em rotas e backup; aplicar parser explicito para `true/false/1/0/sim/nao`.
- Validacao de integridade no create/update: impedir referencia a `category_id`, `card_id` e `recurrence_id` inexistentes antes de gravar.
- Fluxos compostos com transacao: criar gasto + recorrencia + parcelas em transacao unica (rollback em falha parcial).

## Prioridade P1 (qualidade e manutencao)

- Quebrar `backend/app.py` em blueprints por dominio (`categories`, `expenses`, `goals`, `reports`, etc.).
- Criar camada de schemas/DTOs para request/response (validacao centralizada e mensagens de erro consistentes).
- Handler global de erros HTTP para padronizar retorno JSON.
- Mover filtros de listagem para SQL (hoje varios filtros sao feitos em memoria apos `list()` completa).
- Adicionar indices SQLite para consultas frequentes:
  - `expenses(month, year)`
  - `expenses(category_id, month, year)`
  - `installments(card_id, month, year)`
  - `goals(month, year, category_id)`
  - `recurrences(kind, start_year, start_month)`
- Melhorar arredondamento de parcelas: ajustar centavos residuais na ultima parcela para manter soma exata.
- Definir padrao de logs (nivel, formato, rotacao, limite de tamanho).

## Prioridade P2 (testes e confiabilidade)

- Criar dependencias de desenvolvimento separadas (`requirements-dev.txt`) com `pytest`, `ruff`, `black`, `mypy` (opcional).
- Cobertura de testes para API:
  - CRUD completo de todas as entidades
  - validacoes de payload invalido
  - erros 404/409
  - restauracao de backup invalido
- Testes de regressao para campos opcionais/`null` (especialmente updates).
- Testes E2E basicos do Electron (abrir tela, criar/editar/excluir registros).
- Pipeline de CI (GitHub Actions ou similar) com lint + testes.

## Prioridade P3 (UX e produto)

- Padronizar feedback visual: trocar `alert()` por toast/snackbar em todas as telas.
- Estados de carregamento e vazio em todas as listas (com mensagem consistente).
- Filtros de periodo (mes/ano) para metas, com progresso do mesmo periodo filtrado.
- Confirmacao de acoes destrutivas com mensagem mais clara (o que sera apagado).
- Acessibilidade:
  - foco inicial em modal
  - fechar modal com `Esc`
  - navegacao por teclado
  - `aria-label` em botoes iconicos
- Melhorar exibicao de categoria vinculada (sempre nome, evitar `Categoria #id`).
- Validacao de formulario no cliente antes do submit (limites, tipos, obrigatorios).

## Build, distribuicao e operacao

- Fixar versoes minimas de runtime (Python/Node) e validar no startup.
- Adicionar assinatura de instalador Windows.
- Publicar checklist de release (versionamento, changelog, smoke test, upload de artefatos).
- Telemetria local opcional (opt-in) para erros de inicializacao e falhas de update.
- Melhorar estrategia de update:
  - timeout/retry configuravel
  - mensagem de erro amigavel quando feed estiver indisponivel
- Backup:
  - incluir timestamp completo com timezone
  - opcao de compressao
  - opcao de senha/criptografia do arquivo
  - validacao de checksum

## Padroes e governanca tecnica

- Definir convencao de commits (Conventional Commits) no CONTRIBUTING.
- Definir padrao de nomes de campos (pt-BR vs en-US) e manter consistencia na API.
- Documentar contratos da API (OpenAPI simples ou markdown por endpoint).
- Criar "Definition of Done" para evitar regressao:
  - teste automatizado do caso alterado
  - validacao manual minima no frontend
  - log de erro revisado

## Quick wins recomendados (ordem sugerida)

1. Padronizar parser booleano e update parcial por presenca de chave.
2. Substituir `alert()` por toast nas paginas principais.
3. Trocar renderizacao dinamica com `innerHTML` por construcao segura de elementos.
4. Adicionar indices SQLite das consultas mais usadas.
5. Criar suite de testes de API para CRUD de metas, gastos e categorias.

## Fases de execucao

### Fase 1 - Hardening imediato (1-2 dias)

- Padronizar update parcial por presenca de chave no backend.
- Corrigir parsing booleano em rotas e backup.
- Trocar `alert()` por toast nas telas com maior uso.
- Remover `innerHTML` em pontos criticos de relatorio/metas.

Status: **executada parcialmente em 24/02/2026**

- [x] Update parcial por presenca de chave em endpoints principais (`PUT`).
- [x] Parsing booleano robusto no backend e backup.
- [x] Troca de `alert` por toast nas telas de metas e relatorios.
- [x] Remocao de `innerHTML` no item de metas de relatorios.
- [ ] Remocao completa de `innerHTML` em todas as paginas.

### Fase 2 - Performance e consistencia (2-4 dias)

- Adicionar indices no SQLite.
- Mover filtros de listagem para SQL.
- Padronizar validacoes de referencia (`category_id`, `card_id`, `recurrence_id`).
- Melhorar arredondamento de parcelas com ajuste da ultima parcela.

Status: **executada em 24/02/2026**

- [x] Indices adicionados para consultas frequentes.
- [x] Filtros principais movidos para SQL (`expenses`, `incomes`, `goals`, `installments`).
- [x] Validacoes de referencia aplicadas em criacao/edicao (categoria/cartao).
- [x] Arredondamento de parcelas com ajuste de centavos na ultima parcela.

### Fase 3 - Qualidade e testes (3-5 dias)

- Criar `requirements-dev.txt` com ferramentas de qualidade.
- Cobrir CRUD e validacoes de API com testes.
- Criar base de CI para lint e testes.
- Adicionar testes de regressao para updates com `null` e booleanos.

### Fase 4 - Arquitetura e DX (5+ dias)

- Quebrar `backend/app.py` em blueprints.
- Adotar schemas/DTOs para validacao unificada.
- Centralizar tratamento de erros HTTP.
- Publicar documentacao de contrato da API.
