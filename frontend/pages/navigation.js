(() => {
  const navLinks = [
    { href: 'dashboard.html', label: 'Dashboard', icon: '\u{1F3E0}' },
    { href: 'incomes.html', label: 'Entradas', icon: '\u{1F4B0}' },
    { href: 'expenses.html', label: 'Gastos', icon: '\u{1F4B8}' },
    { href: 'goals.html', label: 'Metas', icon: '\u{1F3AF}' },
    { href: 'banks.html', label: 'Bancos', icon: '\u{1F3E6}' },
    { href: 'reports.html', label: 'Relatorios', icon: '\u{1F4CA}' },
    { href: 'settings.html', label: 'Configuracoes', icon: '\u2699' },
  ];

  const currentPage = window.location.pathname.split('/').pop() || 'dashboard.html';
  const appRoot = document.querySelector('.app');
  if (!appRoot) return;

  const topbar = document.createElement('header');
  topbar.className = 'global-topbar';
  topbar.innerHTML = `
    <button id="app-menu-toggle" class="topbar-toggle" type="button" aria-label="Abrir menu lateral" aria-expanded="false" aria-controls="app-nav">
      <span></span><span></span><span></span>
    </button>
    <a class="topbar-brand" href="dashboard.html" aria-label="Save Your Money">
      <img src="../assets/logo.png" alt="" class="topbar-logo-image" />
      <span class="topbar-title">Save Your Money</span>
    </a>
  `;
  document.body.prepend(topbar);

  const navMarkup = `
    <nav id="app-nav" class="app-nav">
      ${navLinks.map((link) => `
        <a href="${link.href}" data-icon="${link.icon}" class="${currentPage === link.href ? 'active' : ''}">${link.label}</a>
      `).join('')}
    </nav>
  `;

  let navbar = document.querySelector('.navbar');
  if (navbar) {
    navbar.innerHTML = navMarkup;
  } else {
    navbar = document.createElement('aside');
    navbar.className = 'navbar';
    navbar.innerHTML = navMarkup;
    const appHeader = appRoot.querySelector('.app-header');
    if (appHeader) {
      appHeader.appendChild(navbar);
    } else {
      appRoot.prepend(navbar);
    }
  }

  let navOverlay = document.getElementById('app-nav-overlay');
  if (!navOverlay) {
    navOverlay = document.createElement('div');
    navOverlay.id = 'app-nav-overlay';
    navOverlay.className = 'nav-overlay';
    document.body.appendChild(navOverlay);
  }

  const menuToggle = document.getElementById('app-menu-toggle');
  const mediaQuery = window.matchMedia('(max-width: 1024px)');
  const syncToggleState = () => {
    if (!menuToggle) return;
    const isMobile = mediaQuery.matches;
    const isExpanded = isMobile
      ? document.body.classList.contains('nav-open')
      : !document.body.classList.contains('nav-collapsed');
    menuToggle.setAttribute('aria-expanded', String(isExpanded));
    menuToggle.setAttribute('aria-label', isExpanded ? 'Fechar menu lateral' : 'Abrir menu lateral');
  };

  if (menuToggle) {
    menuToggle.addEventListener('click', () => {
      if (mediaQuery.matches) {
        document.body.classList.toggle('nav-open');
      } else {
        document.body.classList.toggle('nav-collapsed');
      }
      syncToggleState();
    });
  }

  navOverlay.addEventListener('click', () => {
    document.body.classList.remove('nav-open');
    syncToggleState();
  });

  const resetOnResize = () => {
    if (!mediaQuery.matches) {
      document.body.classList.remove('nav-open');
    }
    syncToggleState();
  };
  mediaQuery.addEventListener('change', resetOnResize);
  resetOnResize();
})();
