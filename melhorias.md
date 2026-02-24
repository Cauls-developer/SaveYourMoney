# 📘 Especificação de Funcionalidades — App Financeiro (Offline)

Este documento consolida as implementações discutidas para o aplicativo financeiro, com foco em **padronização de UI**, **gestão de dados**, **calculadora de auxílio** e **backup/restauração**.

---

# 1) 🧾 Gestão de Dados: Editar / Alterar / Excluir (CRUD)

## 🎯 Objetivo

Permitir que o usuário possa **editar, alterar ou excluir** registros de forma consistente e segura.

## ✅ Itens cobertos

* Cartões
* Gastos
* Receitas
* Categorias (se aplicável)
* Itens recorrentes (quando aplicável)

## 📐 Padronização de Tela (Obrigatória)

A UI de edição deve seguir um **template único** para todas as entidades.

### Estrutura padrão

* Título: `Editar <Entidade>`
* Campos pré-preenchidos com dados atuais
* Ações fixas:

  * ✅ **Salvar alterações** (primária)
  * ❌ **Cancelar**
  * 🗑 **Excluir** (secundária, destaque visual)

### Regras de UX

* Exibir confirmação antes de excluir:

  > "Tem certeza que deseja excluir este item?"
* Mostrar feedback após salvar/excluir (Snackbar/Toast/Alert)
* Manter identidade visual do app (cor principal: **amber**)

### Regras de integridade

* Ao excluir cartão: definir comportamento para gastos vinculados (ex: bloquear exclusão se houver vínculo, ou solicitar remapeamento)
* Ao editar categoria: refletir nos itens associados

---

# 2) 🧮 Calculadora de Auxílio Financeiro (Estilo Assistente)

## 🎯 Objetivo

Adicionar uma calculadora de apoio ao usuário, com aparência de mini-assistente ("chat"), mas funcionalmente uma calculadora financeira.

## 📍 Acesso

* Ícone flutuante (FAB) no canto inferior direito em telas principais
* Ícone sugerido: 🧮 (ou 💬 com símbolo de cálculo)

## 🧠 Conceito de Interface

* Aparência semelhante a chatbot, porém:

  * sem IA
  * sem respostas inteligentes
  * apenas **inputs** e **outputs** de cálculos

## 📌 Seções da Calculadora

### 2.1 Operações básicas

* Soma
* Subtração
* Multiplicação
* Divisão

### 2.2 Funções financeiras

Incluir área específica para cálculos financeiros:

* Juros simples
* Juros compostos
* Simulação de parcelamento
* Cálculo de desconto
* Cálculo de rendimento mensal
* Simulação de quitação de dívida

### Exemplo de uso (modo assistente)

* "Quanto vou pagar em 12 parcelas com juros de 2% ao mês?"

### Campos recomendados (modo formulário)

* Valor inicial
* Taxa de juros
* Tempo (meses)
* Tipo de juros
* Botão: **Calcular**

---

# 3) 🔁 Recorrência dentro da Aba de Gastos

## 🎯 Objetivo

Permitir que o usuário marque um gasto como recorrente no momento do cadastro, sem precisar de uma aba separada.

## 📍 Local

A própria tela de criação/edição de gasto.

## ✅ UI sugerida

Na tela de gasto:

* Valor
* Categoria
* Data
* Forma de pagamento
* Toggle: **Gasto recorrente**

Ao ativar **Gasto recorrente**, exibir:

* Frequência: Semanal | Mensal | Anual
* Dia fixo (opcional)
* Data final (opcional) ou “Sem data final”

## 📊 Comportamento esperado

* O gasto recorrente deve ser replicado automaticamente conforme frequência
* Ao editar, permitir:

  * Editar apenas esta ocorrência
  * Editar todas as futuras
  * Cancelar recorrência

## 🏷 Identificação visual

* Indicar recorrência na lista de gastos com ícone **🔁**
* Permitir filtro: `Todos | Recorrentes | Não recorrentes`

---

# 4) 📦 Backup e Restauração

## 🎯 Objetivo

Permitir que o usuário exporte e restaure um backup completo do aplicativo financeiro, garantindo segurança e continuidade dos dados.

## 📂 Localização no App

Menu sugerido:

```
Configurações → Backup e Restauração
```

Opções disponíveis:

* 📤 Exportar Backup
* 📥 Restaurar Backup

---

## 4.1 📤 Exportar Backup

### Requisitos

* Exportar dados em arquivo `.json`
* O arquivo deve conter:

  * versão do backup
  * data/hora de exportação
  * todas as coleções necessárias

### UX

* Botão: **Exportar Backup**
* Exibir sucesso com opção de:

  * compartilhar arquivo
  * salvar em pasta escolhida

---

## 4.2 📥 Restaurar Backup

### Fluxo

1. Usuário seleciona **Restaurar Backup**
2. Abrir seletor de arquivo (apenas `.json`)
3. Validar arquivo antes de importar
4. Exigir confirmação:

> "Restaurar um backup substituirá todos os dados atuais do aplicativo. Deseja continuar?"

Botões:

* ❌ Cancelar
* ✅ Confirmar

### Comportamento ao restaurar

#### MVP (recomendado)

* Substituir completamente os dados atuais

#### Evolução futura

* Mesclar dados existentes
* Resolver conflitos

---

## 4.3 📁 Estrutura do Arquivo de Backup (Sugestão)

```json
{
  "version": "1.0",
  "exportedAt": "2026-02-23",
  "cards": [],
  "expenses": [],
  "recurringExpenses": [],
  "income": [],
  "categories": [],
  "settings": {}
}
```

---

## 4.4 ⚠ Tratamento de Erros

Cenários:

* Arquivo inválido → erro amigável
* Versão incompatível → orientar atualização
* Falha na importação → **não alterar** dados atuais

Mensagem exemplo:

> "Não foi possível restaurar o backup. Verifique se o arquivo é válido."

#

---

# 6) ✅ Checklist para Backlog

## CRUD e Padronização

*

## Calculadora

*

## Recorrência

*

## Backup

*

---

# 🔥 Evoluções Futuras

* Backup automático local
* Backup criptografado
* Backup na nuvem
* Histórico de backups
* Restauração parcial (ex: somente gastos)
