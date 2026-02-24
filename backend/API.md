# API - SaveYourMoney (Backend)

Base URL: `http://127.0.0.1:5000`

Formato de erro (todas as rotas):

```json
{ "error": "Mensagem" }
```

## Saúde

`GET /health`

Resposta `200`:

```json
{ "status": "ok" }
```

## Calculadora

`POST /calculadora`

Payload base:

```json
{ "operation": "soma" }
```

Operações e campos:

1. `soma`, `subtracao`, `multiplicacao`, `divisao`
2. Campos: `a`, `b` (números)

```json
{ "operation": "soma", "a": 10, "b": 5 }
```

3. `juros_simples`, `juros_compostos`, `parcelamento`
4. Campos: `principal`, `rate`, `months`

```json
{ "operation": "juros_simples", "principal": 1000, "rate": 1.5, "months": 12 }
```

5. `desconto`
6. Campos: `principal`, `rate`

```json
{ "operation": "desconto", "principal": 500, "rate": 10 }
```

7. `rendimento_mensal`
8. Campos: `principal`, `rate`

9. `quitacao_divida`
10. Campos: `principal`, `rate`, `payment`

Resposta `200`:

```json
{ "operation": "soma", "result": 15 }
```

## Backup

`GET /backup/exportar`

Resposta `200`:

```json
{
  "cards": [],
  "categories": [],
  "expenses": [],
  "goals": [],
  "incomes": [],
  "installments": [],
  "recurrences": []
}
```

`POST /backup/restaurar`

Payload: o mesmo formato retornado em `GET /backup/exportar`.

Resposta `200`:

```json
{ "message": "Backup restaurado com sucesso.", "imported": { "cards": 0 } }
```

`POST /backup`

Cria um arquivo `.db` na pasta de backup.

Resposta `201`:

```json
{ "backup": "saveyourmoney_20260224_120000.db", "path": "D:\\...\\backups\\saveyourmoney_20260224_120000.db" }
```

## Categorias

`GET /categorias`

`POST /categorias`

```json
{ "name": "Alimentação", "description": "Mercado" }
```

`PUT /categorias/{id}`

```json
{ "name": "Alimentação", "description": "Supermercado" }
```

`DELETE /categorias/{id}`

## Gastos

`GET /gastos`

Query:

1. `mes` (int)
2. `ano` (int)
3. `recorrente` (`todos` | `sim` | `nao`)

`POST /gastos`

```json
{
  "name": "Mercado",
  "value": 120.5,
  "month": 2,
  "year": 2026,
  "category_id": 1,
  "payment_method": "debit",
  "notes": "Compra do mês",
  "installments": { "card_id": 10, "total": 3 }
}
```

Campos de recorrência no `POST /gastos`:

```json
{
  "recurring": {
    "enabled": true,
    "frequency": "mensal",
    "interval_months": 1,
    "occurrences": 12,
    "end_month": 12,
    "end_year": 2026
  }
}
```

`PUT /gastos/{id}`

```json
{
  "name": "Mercado",
  "value": 150,
  "month": 2,
  "year": 2026,
  "category_id": 1,
  "payment_method": "credit",
  "notes": "Atualizado",
  "scope": "future"
}
```

`DELETE /gastos/{id}`

Payload opcional:

```json
{ "scope": "future" }
```

## Entradas

`GET /entradas`

Query:

1. `mes` (int)
2. `ano` (int)

`POST /entradas`

```json
{
  "name": "Salário",
  "value": 5000,
  "month": 2,
  "year": 2026,
  "confirmed": true,
  "notes": "CLT"
}
```

`PUT /entradas/{id}`

`DELETE /entradas/{id}`

## Cartões

`GET /cartoes`

`POST /cartoes`

```json
{
  "name": "Nubank",
  "limit": 3000,
  "bank": "Nubank",
  "brand": "Mastercard",
  "closing_day": 5,
  "due_day": 12
}
```

`PUT /cartoes/{id}`

`DELETE /cartoes/{id}`

## Parcelas e Faturas

`GET /parcelas`

Query:

1. `cartao_id` ou `card_id`
2. `mes` (int)
3. `ano` (int)

`GET /faturas`

Query:

1. `cartao_id` ou `card_id`
2. `mes` (int)
3. `ano` (int)

Resposta `200`:

```json
{ "total": 123.45, "parcelas": [] }
```

## Recorrências

`GET /recorrencias`

`POST /recorrencias`

```json
{
  "kind": "expense",
  "name": "Assinatura",
  "value": 39.9,
  "start_month": 2,
  "start_year": 2026,
  "interval_months": 1,
  "occurrences": 6,
  "category_id": 1,
  "payment_method": "debit",
  "notes": "Streaming"
}
```

`PUT /recorrencias/{id}`

`DELETE /recorrencias/{id}`

`POST /recorrencias/aplicar`

```json
{ "id": 10 }
```

Resposta `200`:

```json
{ "expenses": [], "incomes": [] }
```

## Metas

`GET /metas`

Query:

1. `mes` (int)
2. `ano` (int)

`POST /metas`

```json
{
  "name": "Gastos do mês",
  "limit_value": 2000,
  "month": 2,
  "year": 2026,
  "category_id": 1
}
```

`PUT /metas/{id}`

`DELETE /metas/{id}`

## Relatórios

`GET /relatorios/mes`

Query:

1. `mes` (int)
2. `ano` (int)

`GET /relatorios/mes/csv`

`GET /relatorios/mes/pdf`

## Observações

1. Campos booleanos aceitam `true/false`, `1/0`, `sim/nao`, `yes/no`.
2. Campos opcionais podem ser omitidos ou enviados como `null`.
