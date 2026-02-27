(function () {
  function formatCurrency(value) {
    return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(Number(value || 0));
  }

  function formatNumber(value) {
    return new Intl.NumberFormat('pt-BR', { maximumFractionDigits: 2 }).format(Number(value || 0));
  }

  function parseDecimal(raw) {
    const value = String(raw || '').trim();
    if (!value) return null;
    let normalized = value.replace(/\s/g, '');
    if (normalized.includes(',') && normalized.includes('.')) {
      normalized = normalized.replace(/\./g, '').replace(',', '.');
    } else if (normalized.includes(',')) {
      normalized = normalized.replace(',', '.');
    }
    const parsed = Number.parseFloat(normalized);
    return Number.isNaN(parsed) ? null : parsed;
  }

  const fab = document.createElement('button');
  fab.type = 'button';
  fab.className = 'fab-calculator';
  fab.title = 'Calculadora financeira';
  fab.textContent = '🧮';

  const modal = document.createElement('div');
  modal.className = 'modal';
  const modalContent = document.createElement('div');
  modalContent.className = 'modal-content calculator-panel calc-standard';

  const modalHeader = document.createElement('div');
  modalHeader.className = 'modal-header';
  const headerCopy = document.createElement('div');
  headerCopy.className = 'stack-1';
  const modalTitle = document.createElement('h3');
  modalTitle.textContent = 'Calculadora Financeira';
  const modalSubtitle = document.createElement('small');
  modalSubtitle.className = 'text-secondary';
  modalSubtitle.textContent = 'Use o teclado para preencher os campos da operação.';
  const closeButton = document.createElement('button');
  closeButton.className = 'modal-close';
  closeButton.type = 'button';
  closeButton.textContent = '×';
  headerCopy.appendChild(modalTitle);
  headerCopy.appendChild(modalSubtitle);
  modalHeader.appendChild(headerCopy);
  modalHeader.appendChild(closeButton);

  const layout = document.createElement('div');
  layout.className = 'calc-layout';
  const left = document.createElement('div');
  left.className = 'calc-left';
  const right = document.createElement('div');
  right.className = 'calc-right';

  const operationField = document.createElement('div');
  operationField.className = 'field';
  const operationLabel = document.createElement('label');
  operationLabel.setAttribute('for', 'calc-operation');
  operationLabel.textContent = 'Operação';
  const operationSelect = document.createElement('select');
  operationSelect.id = 'calc-operation';
  const operationOptions = [
    ['soma', 'Soma'],
    ['subtracao', 'Subtração'],
    ['multiplicacao', 'Multiplicação'],
    ['divisao', 'Divisão'],
    ['juros_simples', 'Juros simples'],
    ['juros_compostos', 'Juros compostos'],
    ['parcelamento', 'Parcelamento'],
    ['desconto', 'Desconto'],
    ['rendimento_mensal', 'Rendimento mensal'],
    ['quitacao_divida', 'Quitação de dívida'],
  ];
  operationOptions.forEach(([value, label]) => {
    const option = document.createElement('option');
    option.value = value;
    option.textContent = label;
    operationSelect.appendChild(option);
  });
  operationField.appendChild(operationLabel);
  operationField.appendChild(operationSelect);

  const screen = document.createElement('div');
  screen.className = 'calc-screen';
  screen.id = 'calc-screen';
  screen.textContent = '0';

  const targets = document.createElement('div');
  targets.className = 'calc-targets';
  targets.id = 'calc-targets';

  const keypad = document.createElement('div');
  keypad.className = 'calc-keypad';
  const keypadButtons = [
    ['7', '7'],
    ['8', '8'],
    ['9', '9'],
    ['del', 'DEL', 'calc-action', 'action'],
    ['4', '4'],
    ['5', '5'],
    ['6', '6'],
    ['clear', 'C', 'calc-action', 'action'],
    ['1', '1'],
    ['2', '2'],
    ['3', '3'],
    [',', ','],
    ['0', '0', 'calc-zero'],
    ['.', '.'],
    ['negate', '+/-', null, 'action'],
  ];
  keypadButtons.forEach((definition) => {
    const [value, label, className, kind] = definition;
    const btn = document.createElement('button');
    btn.type = 'button';
    if (className) btn.className = className;
    if (kind === 'action') {
      btn.dataset.action = value;
    } else {
      btn.dataset.key = value;
    }
    btn.textContent = label;
    keypad.appendChild(btn);
  });

  const actions = document.createElement('div');
  actions.className = 'modal-actions';
  actions.style.justifyContent = 'space-between';
  const cancelButton = document.createElement('button');
  cancelButton.type = 'button';
  cancelButton.className = 'button secondary';
  cancelButton.id = 'calc-cancel';
  cancelButton.textContent = 'Fechar';
  const submitButton = document.createElement('button');
  submitButton.type = 'button';
  submitButton.className = 'button';
  submitButton.id = 'calc-submit';
  submitButton.textContent = 'Calcular';
  actions.appendChild(cancelButton);
  actions.appendChild(submitButton);

  left.appendChild(operationField);
  left.appendChild(screen);
  left.appendChild(targets);
  left.appendChild(keypad);
  left.appendChild(actions);

  const answer = document.createElement('div');
  answer.className = 'calculator-answer';
  answer.id = 'calc-answer';
  answer.textContent = 'Selecione uma operação e toque em Calcular.';
  const note = document.createElement('p');
  note.className = 'calc-note';
  note.textContent = 'Dica: alterne os campos clicando nos blocos acima do teclado.';
  right.appendChild(answer);
  right.appendChild(note);

  layout.appendChild(left);
  layout.appendChild(right);
  modalContent.appendChild(modalHeader);
  modalContent.appendChild(layout);
  modal.appendChild(modalContent);

  const operation = operationSelect;

  const values = {
    a: '',
    b: '',
    principal: '',
    rate: '',
    months: '12',
    payment: '',
  };
  let activeField = 'a';

  const operationFields = {
    soma: ['a', 'b'],
    subtracao: ['a', 'b'],
    multiplicacao: ['a', 'b'],
    divisao: ['a', 'b'],
    juros_simples: ['principal', 'rate', 'months'],
    juros_compostos: ['principal', 'rate', 'months'],
    parcelamento: ['principal', 'rate', 'months'],
    desconto: ['principal', 'rate'],
    rendimento_mensal: ['principal', 'rate'],
    quitacao_divida: ['principal', 'rate', 'payment'],
  };

  const fieldLabels = {
    a: 'Valor A',
    b: 'Valor B',
    principal: 'Valor inicial',
    rate: 'Taxa (%)',
    months: 'Meses',
    payment: 'Pagamento mensal',
  };

  function currentFields() {
    return operationFields[operation.value] || ['a', 'b'];
  }

  function normalizeNumberInput(str) {
    return String(str || '').replace('.', ',');
  }

  function displayValueFor(field) {
    const raw = values[field] || '';
    if (!raw) return '0';
    return normalizeNumberInput(raw);
  }

  function renderTargets() {
    const fields = currentFields();
    if (!fields.includes(activeField)) activeField = fields[0];

    targets.replaceChildren();
    fields.forEach((field) => {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = `calc-target${activeField === field ? ' active' : ''}`;
      btn.dataset.field = field;
      const label = document.createElement('strong');
      label.textContent = fieldLabels[field];
      const value = document.createElement('span');
      value.textContent = displayValueFor(field);
      btn.appendChild(label);
      btn.appendChild(value);
      targets.appendChild(btn);
    });

    screen.textContent = displayValueFor(activeField);
  }

  function setActiveField(field) {
    activeField = field;
    renderTargets();
  }

  function appendChar(char) {
    const existing = values[activeField] || '';
    const normalizedChar = char === '.' ? ',' : char;

    if (normalizedChar === ',' && existing.includes(',')) return;

    if (normalizedChar === ',' && !existing) {
      values[activeField] = '0,';
    } else {
      values[activeField] = `${existing}${normalizedChar}`;
    }
    renderTargets();
  }

  function clearActive() {
    values[activeField] = '';
    renderTargets();
  }

  function deleteActive() {
    const existing = values[activeField] || '';
    values[activeField] = existing.slice(0, -1);
    renderTargets();
  }

  function negateActive() {
    const existing = values[activeField] || '';
    if (!existing) return;
    values[activeField] = existing.startsWith('-') ? existing.slice(1) : `-${existing}`;
    renderTargets();
  }

  function readNumber(field, required = true) {
    const parsed = parseDecimal(values[field]);
    if (required && parsed === null) {
      throw new Error(`Informe ${fieldLabels[field]}.`);
    }
    return parsed;
  }

  function buildPayload() {
    const op = operation.value;
    const payload = { operation: op };

    if (['soma', 'subtracao', 'multiplicacao', 'divisao'].includes(op)) {
      payload.a = readNumber('a');
      payload.b = readNumber('b');
      return payload;
    }

    payload.principal = readNumber('principal');
    payload.rate = readNumber('rate', false) || 0;

    if (['juros_simples', 'juros_compostos', 'parcelamento'].includes(op)) {
      payload.months = Math.max(1, Math.trunc(readNumber('months')));
    }

    if (op === 'quitacao_divida') {
      payload.payment = readNumber('payment');
    }

    return payload;
  }

  function showResult(result) {
    if (typeof result === 'number') {
      answer.textContent = `Resultado: ${formatNumber(result)}`;
      return;
    }

    const parts = [];
    Object.entries(result || {}).forEach(([key, value]) => {
      if (typeof value !== 'number') return;
      if (key === 'meses') {
        parts.push(`Meses: ${value}`);
      } else {
        parts.push(`${key.replace(/_/g, ' ')}: ${formatCurrency(value)}`);
      }
    });
    answer.textContent = parts.join(' | ') || 'Sem resultado para exibir.';
  }

  async function runCalculation() {
    answer.textContent = 'Calculando...';
    try {
      const payload = buildPayload();
      const data = await window.api.financialCalculator(payload);
      showResult(data.result);
    } catch (error) {
      answer.textContent = error.message || 'Erro ao calcular.';
    }
  }

  function openModal() {
    modal.classList.add('active');
  }

  function closeModal() {
    modal.classList.remove('active');
  }

  operation.addEventListener('change', renderTargets);

  targets.addEventListener('click', (event) => {
    const target = event.target.closest('[data-field]');
    if (!target) return;
    setActiveField(target.dataset.field);
  });

  keypad.addEventListener('click', (event) => {
    const btn = event.target.closest('button');
    if (!btn) return;
    const key = btn.getAttribute('data-key');
    const action = btn.getAttribute('data-action');
    if (key) appendChar(key);
    if (action === 'clear') clearActive();
    if (action === 'del') deleteActive();
    if (action === 'negate') negateActive();
  });

  submitButton.addEventListener('click', runCalculation);
  closeButton.addEventListener('click', closeModal);
  cancelButton.addEventListener('click', closeModal);

  modal.addEventListener('click', (event) => {
    if (event.target === modal) closeModal();
  });

  fab.addEventListener('click', openModal);

  renderTargets();
  document.body.appendChild(fab);
  document.body.appendChild(modal);
})();
