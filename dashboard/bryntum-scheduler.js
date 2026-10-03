/**
 * AegisPay Enterprise Dispute Horizon & Response Scheduling Engine
 * Autonomous PayPal Dispute Triage & Response Deadline Horizon
 */

import { Scheduler } from './bryntum/scheduler.module.js';

let bryntumSchedulerInstance = null;

// Initial Dispute & Mitigation Pipeline Events (October 2026)
const INITIAL_RESOURCES = [
  { id: 'ai-gemini', name: 'Investigation agent', role: 'Risk evaluation' },
  { id: 'actuator', name: 'Payment response', role: 'PayPal Payments v2' },
  { id: 'analyst-marcus', name: 'Marcus', role: 'Fraud analyst' },
  { id: 'analyst-elena', name: 'Elena', role: 'Dispute lead' }
];

const INITIAL_EVENTS = [
  {
    id: 'disp-01',
    resourceId: 'actuator',
    name: 'Void authorization · PP-2026-9815',
    startDate: '2026-10-02 08:30',
    endDate: '2026-10-02 14:00',
    eventColor: 'red',
    iconCls: 'fa-solid fa-bolt'
  },
  {
    id: 'disp-02',
    resourceId: 'actuator',
    name: 'Refund capture · PP-2026-9812',
    startDate: '2026-10-02 11:00',
    endDate: '2026-10-02 18:00',
    eventColor: 'red',
    iconCls: 'fa-solid fa-shield-virus'
  },
  {
    id: 'disp-03',
    resourceId: 'ai-gemini',
    name: 'Evidence ingestion & signal mapping',
    startDate: '2026-10-01 00:00',
    endDate: '2026-10-05 23:59',
    eventColor: 'teal',
    iconCls: 'fa-solid fa-brain'
  },
  {
    id: 'disp-04',
    resourceId: 'analyst-marcus',
    name: 'Order review · PP-2026-9811',
    startDate: '2026-10-03 09:00',
    endDate: '2026-10-04 18:00',
    eventColor: 'orange',
    iconCls: 'fa-solid fa-user-clock'
  },
  {
    id: 'disp-05',
    resourceId: 'analyst-elena',
    name: 'Dispute evidence filing · DISP-9811',
    startDate: '2026-10-03 12:00',
    endDate: '2026-10-12 17:00',
    eventColor: 'blue',
    iconCls: 'fa-solid fa-scale-balanced'
  },
  {
    id: 'disp-06',
    resourceId: 'analyst-marcus',
    name: 'Evidence assembled · Product & browser audit',
    startDate: '2026-10-03 12:00',
    endDate: '2026-10-05 17:00',
    eventColor: 'teal',
    iconCls: 'fa-solid fa-folder-open'
  },
  {
    id: 'disp-07',
    resourceId: 'analyst-elena',
    name: 'Merchant review · Evidence sign-off',
    startDate: '2026-10-05 17:00',
    endDate: '2026-10-08 17:00',
    eventColor: 'orange',
    iconCls: 'fa-solid fa-user-check'
  },
  {
    id: 'disp-08',
    resourceId: 'analyst-elena',
    name: 'Resolution deadline · 10-day response window',
    startDate: '2026-10-08 17:00',
    endDate: '2026-10-13 17:00',
    eventColor: 'red',
    iconCls: 'fa-solid fa-flag-checkered'
  }
];

export function initBryntumScheduler() {
  const container = document.getElementById('bryntumSchedulerContainer');
  if (!container || bryntumSchedulerInstance) return;

  try {
    bryntumSchedulerInstance = new Scheduler({
      appendTo: container,
      startDate: new Date(2026, 9, 1), // Oct 1, 2026
      endDate: new Date(2026, 9, 14),   // Oct 14, 2026
      viewPreset: 'dayAndWeek',
      rowHeight: 68,
      barMargin: 8,
      eventStyle: 'colored',
      fillTicks: true,
      snap: true,
      readOnly: true,

      columns: [
        {
          text: 'Assigned to',
          field: 'name',
          width: 205,
          minWidth: 110,
          htmlEncode: false,
          renderer: ({ record }) => `
            <div style="display:flex; flex-direction:column; gap:2px;">
              <span class="scheduler-resource-name">${record.name}</span>
              <span class="scheduler-resource-role">${record.role || 'Resolution unit'}</span>
            </div>
          `
        }
      ],

      resources: INITIAL_RESOURCES,
      events: INITIAL_EVENTS,

      // Tooltip customization for PayPal fraud files
      features: {
        eventTooltip: {
          template: ({ eventRecord }) => `
            <div class="scheduler-tooltip">
              <strong>${String(eventRecord.name).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}</strong>
              <div><strong>Start:</strong> ${eventRecord.startDate.toLocaleDateString()}</div>
              <div><strong>Deadline / End:</strong> ${eventRecord.endDate.toLocaleDateString()}</div>
            </div>
          `
        }
      }
    });

    window.bryntumScheduler = bryntumSchedulerInstance;
    console.log('[Bryntum] Light dispute timeline initialized.');
  } catch (err) {
    console.error('[Bryntum] Error initializing scheduler:', err);
  }
}

// Function to dynamically add new disputes / mitigations to the Bryntum timeline in real-time
window.addDisputeToBryntumScheduler = function(orderId, amount, riskScore, status, description) {
  if (!bryntumSchedulerInstance) return;

  const now = new Date(2026, 9, 3, 10, 0); // Oct 3, 2026 current time
  const targetResource = riskScore >= 8.5 ? 'actuator' : (riskScore >= 7.0 ? 'analyst-elena' : 'analyst-marcus');
  const color = riskScore >= 8.5 ? 'red' : (riskScore >= 7.0 ? 'orange' : 'blue');
  const actionLabel = riskScore >= 7.0 ? (status.includes('Void') ? 'Auto-Voided' : 'Auto-Refunded') : 'Review Required';

  const newEvent = {
    id: `ev-live-${Date.now()}`,
    resourceId: targetResource,
    name: `${orderId} ($${amount.toFixed(2)}) · ${actionLabel}`,
    startDate: now,
    endDate: new Date(now.getTime() + (riskScore >= 7.0 ? 8 : 72) * 3600 * 1000), // hours
    eventColor: color
  };

  try {
    bryntumSchedulerInstance.eventStore.add(newEvent);
    bryntumSchedulerInstance.scrollEventIntoView(newEvent, { animate: true });
  } catch (e) {
    console.warn('[Bryntum] Could not add live event to store:', e);
  }
};

// Auto-initialize when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initBryntumScheduler);
} else {
  initBryntumScheduler();
}
