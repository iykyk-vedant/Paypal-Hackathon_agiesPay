/* Navigation, responsive table layout and accessible dialog behaviour. */
(() => {
  const routes = {
    overview: ['Transaction overview', 'Monitor payments. Review risk. Stay in control.', 'Overview'],
    disputes: ['Dispute horizon', 'Evidence, review and response deadlines.', 'Disputes'],
    activity: ['Activity log', 'Investigation and payment events from this session.', 'Activity log'],
    simulations: ['Sandbox simulations', 'Payment scenarios for the fraud operations workspace.', 'Simulations'],
    systems: ['System status', 'Connected services and workspace configuration.', 'System status']
  };

  function navigate() {
    const route = location.hash.slice(1) || 'overview';
    const current = routes[route] ? route : 'overview';
    const [title, subtitle, crumb] = routes[current];
    document.getElementById('pageTitle').textContent = title;
    document.getElementById('pageSubtitle').textContent = subtitle;
    document.getElementById('routeBreadcrumb').textContent = crumb;
    document.title = `AegisPay · ${crumb}`;
    document.querySelectorAll('[data-route]').forEach(link => {
      link.classList.toggle('active', link.dataset.route === current);
      if (link.dataset.route === current) link.setAttribute('aria-current', 'page');
      else link.removeAttribute('aria-current');
    });
    const sections = {
      overviewMetrics: current === 'overview',
      monitoringTabs: ['overview', 'disputes'].includes(current),
      gridTableSection: current === 'overview',
      bryntumSchedulerSection: current === 'disputes',
      activitySection: ['overview', 'activity'].includes(current),
      simulationSection: current === 'simulations',
      systemsSection: current === 'systems'
    };
    Object.entries(sections).forEach(([id, visible]) => document.getElementById(id).classList.toggle('hidden', !visible));
    document.getElementById('activitySection').classList.toggle('activity-page', current === 'activity');
    ['viewGridTabBtn', 'viewSchedulerTabBtn'].forEach((id, index) => {
      const active = current === (index ? 'disputes' : 'overview');
      const tab = document.getElementById(id);
      tab.classList.toggle('active', active);
      tab.setAttribute('aria-selected', String(active));
    });
    document.getElementById('workspaceSidebar').classList.remove('mobile-open');
    document.getElementById('mobileMenuBtn').setAttribute('aria-expanded', 'false');
    if (current === 'disputes') requestAnimationFrame(() => {
      const scheduler = window.bryntumScheduler;
      if (!scheduler) return;
      scheduler.columns.getAt(0).width = Math.min(205, Math.max(110, document.getElementById('bryntumSchedulerContainer').clientWidth * 0.3));
      scheduler.refresh();
    });
    if (current === 'overview') requestAnimationFrame(fitWorkspaceGrid);
  }

  function fitWorkspaceGrid() {
    if (!gridApi) return;
    const width = document.getElementById('transactionsGrid').clientWidth;
    if (!width) return;
    gridApi.setColumnsVisible(['timestamp'], width >= 1050);
    gridApi.setColumnsVisible(['category'], width >= 1150);
    gridApi.setColumnsVisible(['orderId'], width >= 650);
    gridApi.setColumnsVisible(['status'], width >= 480);
    gridApi.sizeColumnsToFit();
  }

  window.updateWorkspaceCounts = function () {
    if (!gridApi) return;
    const counts = {all:0,critical:0,review:0,safe:0};
    gridApi.forEachNode(node => {
      if (!node.data) return;
      counts.all++;
      counts[node.data.riskScore >= 7 ? 'critical' : node.data.riskScore >= 4 ? 'review' : 'safe']++;
    });
    document.querySelectorAll('[data-risk-count]').forEach(el => { el.textContent = counts[el.dataset.riskCount]; });
    document.getElementById('transactionTabCount').textContent = counts.all;
    const shown = gridApi.getDisplayedRowCount();
    document.getElementById('visibleTransactionCount').textContent = shown === counts.all
      ? `${shown} transaction${shown === 1 ? '' : 's'}` : `${shown} of ${counts.all} transactions`;
    requestAnimationFrame(() => {
      if (gridApi.getDisplayedRowCount() === 0) gridApi.showNoRowsOverlay();
      else gridApi.hideOverlay();
    });
  };

  function setupDialogs() {
    let previousFocus;
    const overlays = [...document.querySelectorAll('.case-file-overlay')];
    const focusable = element => [...element.querySelectorAll('button:not([disabled]),a[href],input,select,textarea,[tabindex="0"]')].filter(el => el.offsetParent !== null);
    overlays.forEach(overlay => {
      overlay.addEventListener('click', event => { if (event.target === overlay) overlay.classList.add('hidden'); });
      new MutationObserver(() => {
        const open = !overlay.classList.contains('hidden');
        document.body.style.overflow = overlays.some(el => !el.classList.contains('hidden')) ? 'hidden' : '';
        if (open) {
          previousFocus = document.activeElement;
          requestAnimationFrame(() => focusable(overlay)[0]?.focus());
        } else if (previousFocus?.isConnected) previousFocus.focus();
      }).observe(overlay, {attributes:true,attributeFilter:['class']});
    });
    document.addEventListener('keydown', event => {
      const open = overlays.find(el => !el.classList.contains('hidden'));
      if (!open) return;
      if (event.key === 'Escape') { event.preventDefault(); open.classList.add('hidden'); }
      if (event.key === 'Tab') {
        const elements = focusable(open);
        const first = elements[0], last = elements.at(-1);
        if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last?.focus(); }
        if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first?.focus(); }
      }
    });
  }

  let testSequence = 0;
  function identifyElements(root) {
    const selectors = 'button,a,input,select,textarea,[id],[role="alert"],[role="status"],.ag-cell,.ag-header-cell,.log-entry,.factor-pill,.elastic-ind-pill,.b-sch-event';
    const nodes = [...root.querySelectorAll(selectors)];
    if (root.matches?.(selectors)) nodes.push(root);
    nodes.forEach(el => {
      if (el.dataset.testid) return;
      const id = el.id?.replace(/([a-z0-9])([A-Z])/g, '$1-$2').toLowerCase();
      el.dataset.testid = id || `workspace-${el.tagName.toLowerCase()}-${++testSequence}`;
    });
  }

  document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('viewGridTabBtn').addEventListener('click', () => { location.hash = 'overview'; navigate(); });
    document.getElementById('viewSchedulerTabBtn').addEventListener('click', () => { location.hash = 'disputes'; navigate(); });
    document.getElementById('mobileMenuBtn').addEventListener('click', () => {
      const open = document.getElementById('workspaceSidebar').classList.toggle('mobile-open');
      document.getElementById('mobileMenuBtn').setAttribute('aria-expanded', String(open));
    });
    document.addEventListener('click', event => {
      if (!event.target.closest('.sidebar, #mobileMenuBtn')) {
        document.getElementById('workspaceSidebar').classList.remove('mobile-open');
        document.getElementById('mobileMenuBtn').setAttribute('aria-expanded', 'false');
      }
    });
    window.addEventListener('hashchange', navigate);
    new ResizeObserver(fitWorkspaceGrid).observe(document.getElementById('transactionsGrid'));
    setupDialogs();
    identifyElements(document.body);
    new MutationObserver(mutations => mutations.forEach(mutation => mutation.addedNodes.forEach(node => {
      if (node.nodeType === Node.ELEMENT_NODE) identifyElements(node);
    }))).observe(document.body, {childList:true,subtree:true});
    window.updateWorkspaceCounts();
    navigate();
  });
})();