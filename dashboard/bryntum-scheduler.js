/**
 * AegisPay — Bryntum Scheduler Integration
 * Autonomous PayPal Dispute Triage & Response Deadline Horizon
 * Submitting for "Best Use of Bryntum" Hackathon Prize
 */

import { Scheduler } from './bryntum/scheduler.module.js';

let bryntumSchedulerInstance = null;

// Initial Dispute & Mitigation Pipeline Events (October 2026)
const INITIAL_RESOURCES = [
  { id: 'ai-gemini', name: '🤖 Gemini 2.5 Flash Agent', role: 'Autonomous AI Risk Engine' },
  { id: 'actuator', name: '🛡️ Actuator Mitigation Officer', role: 'PayPal Payments v2 Engine' },
  { id: 'analyst-marcus', name: '👤 Marcus (Fraud Analyst)', role: 'Tier 1 Review' },
  { id: 'analyst-elena', name: '⚖️ Elena (Dispute Lead)', role: 'Chargeback Arbitration' }
];

const INITIAL_EVENTS = [
  {
    id: 'disp-01',
    resourceId: 'actuator',
    name: '⚡ Void Authorization #PP-2026-9815 (Bot Burst $1.28)',
    startDate: '2026-10-02 08:30',
    endDate: '2026-10-02 14:00',
    eventColor: 'purple',
    iconCls: 'fa-solid fa-bolt'
  },
  {
    id: 'disp-02',
    resourceId: 'actuator',
    name: '⚡ Refund Capture #PP-2026-9812 (Account Takeover $4,850)',
    startDate: '2026-10-02 11:00',
    endDate: '2026-10-02 18:00',
    eventColor: 'red',
    iconCls: 'fa-solid fa-shield-virus'
  },
  {
    id: 'disp-03',
    resourceId: 'ai-gemini',
    name: '🧠 Gemini APIMatic Context Ingestion & Signal Mapping',
    startDate: '2026-10-01 00:00',
    endDate: '2026-10-05 23:59',
    eventColor: 'teal',
    iconCls: 'fa-solid fa-brain'
  },
  {
    id: 'disp-04',
    resourceId: 'analyst-marcus',
    name: '🔍 Manual Order Review #PP-2026-9811 ($1,499 Electronics)',
    startDate: '2026-10-03 09:00',
    endDate: '2026-10-04 18:00',
    eventColor: 'orange',
    iconCls: 'fa-solid fa-user-clock'
  },
  {
    id: 'disp-05',
    resourceId: 'analyst-elena',
    name: '⏳ PayPal Dispute Evidence Filing #DISP-9811 (10-Day Window)',
    startDate: '2026-10-03 12:00',
    endDate: '2026-10-12 17:00',
    eventColor: 'blue',
    iconCls: 'fa-solid fa-scale-balanced'
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

      columns: [
        {
          text: 'Swarm / Defense Resource',
          field: 'name',
          width: 250,
          htmlEncode: false,
          renderer: ({ record }) => `
            <div style="display:flex; flex-direction:column; gap:2px;">
              <span style="font-weight:600; color:#F8FAFC;">${record.name}</span>
              <span style="font-size:11px; color:#94A3B8;">${record.role || 'Resolution Unit'}</span>
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
            <div style="padding: 10px; font-family: Inter, sans-serif; font-size: 13px; line-height: 1.5; color: #fff;">
              <strong style="color: #38BDF8; display: block; margin-bottom: 4px;">${eventRecord.name}</strong>
              <div><strong>Start:</strong> ${eventRecord.startDate.toLocaleDateString()}</div>
              <div><strong>Deadline / End:</strong> ${eventRecord.endDate.toLocaleDateString()}</div>
              <div style="margin-top: 6px; font-size: 11px; color: #94A3B8;">
                Managed via AegisPay A2A Swarm & PayPal Developer API
              </div>
            </div>
          `
        }
      }
    });

    window.bryntumScheduler = bryntumSchedulerInstance;
    console.log('[Bryntum] Scheduler initialized successfully with Stockholm Dark theme.');
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
    name: `🚨 #${orderId} ($${amount.toFixed(2)}) — ${actionLabel}`,
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
