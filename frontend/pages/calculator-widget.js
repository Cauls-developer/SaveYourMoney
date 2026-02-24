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
  modal.innerHTML = `
    <div class="modal-content calculator-panel calc-standard">
      <div class="modal-header">
        <h3>Calculadora</h3>
        <button class="modal-close" type="button">×</button>
      </div>

      <div class="calc-layout">
        <div class="calc-left">
          <div class="field">
            <label for="calc-operation">Operação</label>
            <select id="calc-operation">
              <option value="soma">Soma</option>
              <option value="subtracao">Subtração</option>
              <option value="multiplicacao">Multiplicação</option>
              <option value="divisao">Divisão</option>
              <option value="juros_simples">Juros simples</option>
              <option value="juros_compostos">Juros compostos</option>
              <option value="parcelamento">Parcelamento</option>
              <option value="desconto">Desconto</option>
              <option value="rendimento_mensal">Rendimento mensal</option>
              <option value="quitacao_divida">Quitação de dívida</option>
            </select>
          </div>

          <div class="calc-screen" id="calc-screen">0</div>

          <div class="calc-targets" id="calc-targets"></div>

          <div class="calc-keypad">
            <button type="button" data-key="7">7</button>
            <button type="button" data-key="8">8</button>
            <button type="button" data-key="9">9</button>
            <button type="button" data-action="del" class="calc-action">DEL</button>

            <button type="button" data-key="4">4</button>
            <button type="button" data-key="5">5</button>
            <button type="button" data-key="6">6</button>
            <button type="button" data-action="clear" class="calc-action">C</button>

            <button type="button" data-key="1">1</button>
            <button type="button" data-key="2">2</button>
            <button type="button" data-key="3">3</button>
            <button type="button" data-key=",">,</button>

            <button type="button" data-key="0" class="calc-zero">0</button>
            <button type="button" data-key=".">.</button>
            <button type="button" data-action="negate">+/-</button>
          </div>

          <div class="modal-actions" style="justify-content: space-between;">
            <button type="button" class="button secondary" id="calc-cancel">Fechar</button>
            <button type="button" class="button" id="calc-submit">Calcular</button>
          </div>
        </div>

        <div class="calc-right">
          <div class="calculator-answer" id="calc-answer">Selecione a operação e use o teclado.</div>
        </div>
      </div>
    </div>
  `;

  const operation = modal.querySelector('#calc-operation');
  const screen = modal.querySelector('#calc-screen');
  const targets = modal.querySelector('#calc-targets');
  const answer = modal.querySelector('#calc-answer');
  const closeButton = modal.querySelector('.modal-close');
  const cancelButton = modal.querySelector('#calc-cancel');
  const submitButton = modal.querySelector('#calc-submit');
  const keypad = modal.querySelector('.calc-keypad');

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

    targets.innerHTML = '';
    fields.forEach((field) => {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = `calc-target${activeField === field ? ' active' : ''}`;
      btn.dataset.field = field;
      btn.innerHTML = `
        <strong>${fieldLabels[field]}</strong>
        <span>${displayValueFor(field)}</span>
      `;
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
