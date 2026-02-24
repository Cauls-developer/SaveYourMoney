const { contextBridge } = require('electron');

const API_URL = 'http://localhost:5000';

async function handleResponse(response) {
  if (!response.ok) {
    const payload = await response.json().catch(() => ({}));
    const message = payload.error || 'Erro inesperado.';
    throw new Error(message);
  }
  return response.json();
}

async function apiJson(path, options = {}) {
  const res = await fetch(`${API_URL}${path}`, options);
  return handleResponse(res);
}

contextBridge.exposeInMainWorld('api', {
  listCategories: async () => apiJson('/categorias'),
  createCategory: async (data) => apiJson('/categorias', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  }),
  updateCategory: async (id, data) => apiJson(`/categorias/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  }),
  deleteCategory: async (id) => apiJson(`/categorias/${id}`, { method: 'DELETE' }),

  listExpenses: async (month, year, recurringFilter) => {
    const params = new URLSearchParams();
    if (month) params.set('mes', month);
    if (year) params.set('ano', year);
    if (recurringFilter) params.set('recorrente', recurringFilter);
    return apiJson(`/gastos?${params.toString()}`);
  },
  createExpense: async (data) => apiJson('/gastos', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  }),
  updateExpense: async (id, data) => apiJson(`/gastos/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  }),
  deleteExpense: async (id, scope = 'this') => apiJson(`/gastos/${id}`, {
    method: 'DELETE',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ scope }),
  }),

  listIncomes: async (month, year) => {
    const params = new URLSearchParams();
    if (month) params.set('mes', month);
    if (year) params.set('ano', year);
    return apiJson(`/entradas?${params.toString()}`);
  },
  createIncome: async (data) => apiJson('/entradas', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  }),
  updateIncome: async (id, data) => apiJson(`/entradas/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  }),
  deleteIncome: async (id) => apiJson(`/entradas/${id}`, { method: 'DELETE' }),

  listCards: async () => apiJson('/cartoes'),
  createCard: async (data) => apiJson('/cartoes', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  }),
  updateCard: async (id, data) => apiJson(`/cartoes/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  }),
  deleteCard: async (id) => apiJson(`/cartoes/${id}`, { method: 'DELETE' }),

  listInstallments: async (cardId, month, year) => {
    const params = new URLSearchParams();
    if (cardId) params.set('card_id', cardId);
    if (month) params.set('mes', month);
    if (year) params.set('ano', year);
    return apiJson(`/parcelas?${params.toString()}`);
  },
  getInvoice: async (cardId, month, year) => {
    const params = new URLSearchParams();
    params.set('card_id', cardId);
    params.set('mes', month);
    params.set('ano', year);
    return apiJson(`/faturas?${params.toString()}`);
  },

  listRecurrences: async () => apiJson('/recorrencias'),
  createRecurrence: async (data) => apiJson('/recorrencias', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  }),
  updateRecurrence: async (id, data) => apiJson(`/recorrencias/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  }),
  deleteRecurrence: async (id) => apiJson(`/recorrencias/${id}`, { method: 'DELETE' }),
  applyRecurrence: async (id) => apiJson('/recorrencias/aplicar', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ id }),
  }),

  listGoals: async (month, year) => {
    const params = new URLSearchParams();
    if (month) params.set('mes', month);
    if (year) params.set('ano', year);
    return apiJson(`/metas?${params.toString()}`);
  },
  createGoal: async (data) => apiJson('/metas', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  }),
  updateGoal: async (id, data) => apiJson(`/metas/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  }),
  deleteGoal: async (id) => apiJson(`/metas/${id}`, { method: 'DELETE' }),

  getMonthlyReport: async (month, year) => {
    const params = new URLSearchParams();
    params.set('mes', month);
    params.set('ano', year);
    return apiJson(`/relatorios/mes?${params.toString()}`);
  },

  exportBackup: async () => apiJson('/backup/exportar'),
  restoreBackup: async (data) => apiJson('/backup/restaurar', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  }),

  financialCalculator: async (data) => apiJson('/calculadora', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  }),
});
