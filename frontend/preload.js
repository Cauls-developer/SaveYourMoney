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

contextBridge.exposeInMainWorld('api', {
  listCategories: async () => {
    const res = await fetch(`${API_URL}/categorias`);
    return handleResponse(res);
  },
  createCategory: async (data) => {
    const res = await fetch(`${API_URL}/categorias`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    return handleResponse(res);
  },
  listExpenses: async (month, year) => {
    const params = new URLSearchParams();
    if (month) params.set('mes', month);
    if (year) params.set('ano', year);
    const res = await fetch(`${API_URL}/gastos?${params.toString()}`);
    return handleResponse(res);
  },
  createExpense: async (data) => {
    const res = await fetch(`${API_URL}/gastos`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    return handleResponse(res);
  },
  listIncomes: async (month, year) => {
    const params = new URLSearchParams();
    if (month) params.set('mes', month);
    if (year) params.set('ano', year);
    const res = await fetch(`${API_URL}/entradas?${params.toString()}`);
    return handleResponse(res);
  },
  createIncome: async (data) => {
    const res = await fetch(`${API_URL}/entradas`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    return handleResponse(res);
  },
  listCards: async () => {
    const res = await fetch(`${API_URL}/cartoes`);
    return handleResponse(res);
  },
  createCard: async (data) => {
    const res = await fetch(`${API_URL}/cartoes`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    return handleResponse(res);
  },
  listInstallments: async (cardId, month, year) => {
    const params = new URLSearchParams();
    if (cardId) params.set('card_id', cardId);
    if (month) params.set('mes', month);
    if (year) params.set('ano', year);
    const res = await fetch(`${API_URL}/parcelas?${params.toString()}`);
    return handleResponse(res);
  },
  getInvoice: async (cardId, month, year) => {
    const params = new URLSearchParams();
    params.set('card_id', cardId);
    params.set('mes', month);
    params.set('ano', year);
    const res = await fetch(`${API_URL}/faturas?${params.toString()}`);
    return handleResponse(res);
  },
  listRecurrences: async () => {
    const res = await fetch(`${API_URL}/recorrencias`);
    return handleResponse(res);
  },
  createRecurrence: async (data) => {
    const res = await fetch(`${API_URL}/recorrencias`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    return handleResponse(res);
  },
  applyRecurrence: async (id) => {
    const res = await fetch(`${API_URL}/recorrencias/aplicar`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ id }),
    });
    return handleResponse(res);
  },
  listGoals: async (month, year) => {
    const params = new URLSearchParams();
    if (month) params.set('mes', month);
    if (year) params.set('ano', year);
    const res = await fetch(`${API_URL}/metas?${params.toString()}`);
    return handleResponse(res);
  },
  createGoal: async (data) => {
    const res = await fetch(`${API_URL}/metas`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    return handleResponse(res);
  },
  getMonthlyReport: async (month, year) => {
    const params = new URLSearchParams();
    params.set('mes', month);
    params.set('ano', year);
    const res = await fetch(`${API_URL}/relatorios/mes?${params.toString()}`);
    return handleResponse(res);
  },
});
