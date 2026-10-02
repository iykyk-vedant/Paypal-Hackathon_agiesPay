/**
 * AegisPay — AG Grid Real-Time Merchant Fraud Ops Dashboard
 * Autonomous Multi-Agent Defense for PayPal Commerce
 */

// Register Official AG Grid Enterprise / AG Studio License Key
const AG_GRID_LICENSE_KEY = "[TRIAL]_this_{AG_Studio_Pro}_Enterprise_key_{AG-144542}_is_granted_for_evaluation_only___Use_in_production_is_not_permitted___Please_report_misuse_to_legal@ag-grid.com___For_help_with_purchasing_a_production_key_please_contact_info@ag-grid.com___You_are_granted_a_{Single_Application}_Developer_License_for_one_application_only___All_Front-End_JavaScript_developers_working_on_the_application_would_need_to_be_licensed___This_key_will_deactivate_on_{16 November 2026}____[v3]_[03C]_MTc5NDc4NzIwMDAwMA==c9a04360d43d5014e2449ff1cd33ed26";
if (typeof agGrid !== 'undefined' && agGrid.LicenseManager) {
  agGrid.LicenseManager.setLicenseKey(AG_GRID_LICENSE_KEY);
}

// Global AG Grid API reference
let gridApi;

// Simulated KPI state
let kpiState = {
  totalVolume: 142890.0,
  totalTransactions: 1482,
  fraudIntercepted: 19650.0,
  attacksCount: 15
};

// Initial Realistic PayPal Transaction Data
const INITIAL_TRANSACTIONS = [
  {
    id: "tx_01",
    timestamp: "12:48:10",
    orderId: "PP-2026-9812",
    customer: "Alexander Wright",
    email: "a.wright@securemail.com",
    account: "ACCT-US-891240",
    amount: 4850.00,
    category: "Digital Gift Cards",
    location: "Bucharest, Romania (Proxy)",
    riskScore: 9.1,
    status: "Auto-Refunded (PayPal)",
    justification: "Account registered in San Jose, CA with average spend of $42. Order placed from offshore commercial VPN requesting high-denomination digital vouchers without physical delivery address.",
    factors: ["Cross-border IP Proxy", "Velocity Spike (+480%)", "High-Risk Digital Goods"],
    rawJson: {
      event_type: "CHECKOUT.ORDER.APPROVED",
      order_id: "PP-2026-9812",
      amount: "4850.00 USD",
      agent_decision: {
        score: 9.1,
        verdict: "ESCALATE_AND_REFUND",
        actuator_call: "POST /v2/payments/captures/CAP-9812/refund"
      }
    }
  },
  {
    id: "tx_02",
    timestamp: "12:45:22",
    orderId: "PP-2026-9811",
    customer: "Elena Rostova",
    email: "elena.r@fintech.io",
    account: "ACCT-US-310452",
    amount: 1499.00,
    category: "Electronics & Laptops",
    location: "Austin, TX, USA",
    riskScore: 5.4,
    status: "Under Review",
    justification: "Customer has consistent 3-year history with PayPal. First time shipping to alternate commercial address in Texas. Hold placed on capture pending one-time SMS verification.",
    factors: ["Address Mismatch", "Verified Buyer Profile"],
    rawJson: {
      event_type: "CHECKOUT.ORDER.APPROVED",
      order_id: "PP-2026-9811",
      amount: "1499.00 USD",
      agent_decision: {
        score: 5.4,
        verdict: "HOLD_FOR_REVIEW"
      }
    }
  },
  {
    id: "tx_03",
    timestamp: "12:43:05",
    orderId: "PP-2026-9810",
    customer: "Marcus Vance",
    email: "marcus.vance@workmail.org",
    account: "ACCT-US-102948",
    amount: 42.50,
    category: "Coffee & Subscription",
    location: "Seattle, WA, USA",
    riskScore: 1.1,
    status: "Approved",
    justification: "Recurring merchant payment profile. Matches existing home geolocation and verified payment method. Zero risk indicators.",
    factors: ["Verified Device", "Normal Spend Pattern"],
    rawJson: {
      event_type: "PAYMENT.CAPTURE.COMPLETED",
      order_id: "PP-2026-9810",
      amount: "42.50 USD",
      agent_decision: {
        score: 1.1,
        verdict: "AUTO_APPROVE"
      }
    }
  },
  {
    id: "tx_04",
    timestamp: "12:38:50",
    orderId: "PP-2026-9809",
    customer: "Sarah Jenkins",
    email: "sarah.j@designco.com",
    account: "ACCT-US-778219",
    amount: 185.00,
    category: "Home & Kitchen",
    location: "Denver, CO, USA",
    riskScore: 1.8,
    status: "Approved",
    justification: "Routine residential delivery with standard checkout latency (34 seconds). Account in good standing.",
    factors: ["Verified Address"],
    rawJson: {
      event_type: "PAYMENT.CAPTURE.COMPLETED",
      order_id: "PP-2026-9809",
      amount: "185.00 USD",
      agent_decision: {
        score: 1.8,
        verdict: "AUTO_APPROVE"
      }
    }
  },
  {
    id: "tx_05",
    timestamp: "12:31:14",
    orderId: "PP-2026-9808",
    customer: "CyberBot_Agent_99",
    email: "bot-executor@proxy-mesh.net",
    account: "ACCT-US-991204",
    amount: 3200.00,
    category: "Hardware Server Parts",
    location: "Amsterdam, Netherlands",
    riskScore: 9.6,
    status: "Account Locked",
    justification: "Headless browser automation signature detected. Rapid form fill (140ms), non-standard user-agent, rapid attempt to cycle stolen PayPal vaulted credit cards.",
    factors: ["Bot Signature", "Vault Cycling Anomaly", "TOR Exit Node"],
    rawJson: {
      event_type: "CHECKOUT.ORDER.APPROVED",
      order_id: "PP-2026-9808",
      amount: "3200.00 USD",
      agent_decision: {
        score: 9.6,
        verdict: "LOCK_AND_TERMINATE",
        actuator_call: "POST /v2/customer/disputes/prevent"
      }
    }
  },
  {
    id: "tx_06",
    timestamp: "12:25:40",
    orderId: "PP-2026-9807",
    customer: "Liam O'Connor",
    email: "liam.oc@dublin.ie",
    account: "ACCT-EU-551029",
    amount: 890.00,
    category: "Travel & Hospitality",
    location: "Dublin, Ireland",
    riskScore: 2.3,
    status: "Approved",
    justification: "Legitimate cross-border European payment via PayPal 3D-Secure 2.0. Bank authorization validated.",
    factors: ["3DS Verified", "Consistent Geolocation"],
    rawJson: {
      event_type: "PAYMENT.CAPTURE.COMPLETED",
      order_id: "PP-2026-9807",
      amount: "890.00 USD",
      agent_decision: {
        score: 2.3,
        verdict: "AUTO_APPROVE"
      }
    }
  }
];

// In-memory data store for the grid
let rowDataStore = [...INITIAL_TRANSACTIONS];

/* --------------------------------------------------------------------------
   AG Grid Column Definitions & Custom Cell Renderers
   -------------------------------------------------------------------------- */
const columnDefs = [
  {
    headerName: "Timestamp",
    field: "timestamp",
    width: 120,
    sortable: true,
    cellStyle: { fontFamily: "'JetBrains Mono', monospace", color: "#94A3B8" }
  },
  {
    headerName: "Order ID",
    field: "orderId",
    width: 150,
    sortable: true,
    filter: "agTextColumnFilter",
    cellRenderer: (params) => {
      return `<span style="font-family: 'JetBrains Mono', monospace; font-weight: 600; color: #38BDF8;">#${params.value}</span>`;
    }
  },
  {
    headerName: "Customer",
    field: "customer",
    width: 200,
    cellRenderer: (params) => {
      const email = params.data.email || "paypal-customer@sandbox.com";
      return `
        <div style="display: flex; flex-direction: column; justify-content: center; height: 100%;">
          <span style="font-weight: 600; color: #F8FAFC; line-height: 1.2;">${params.value}</span>
          <span style="font-size: 11px; color: #64748B;">${email}</span>
        </div>
      `;
    }
  },
  {
    headerName: "Amount",
    field: "amount",
    width: 140,
    sortable: true,
    comparator: (valueA, valueB) => valueA - valueB,
    cellRenderer: (params) => {
      const formatted = new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(params.value);
      return `<span style="font-weight: 700; color: #F8FAFC;">${formatted}</span>`;
    }
  },
  {
    headerName: "Category",
    field: "category",
    width: 180,
    filter: "agSetColumnFilter",
    cellStyle: { color: "#CBD5E1" }
  },
  {
    headerName: "Risk Score",
    field: "riskScore",
    width: 150,
    sortable: true,
    cellRenderer: (params) => {
      const score = Number(params.value);
      let tierClass = "safe";
      let icon = "fa-shield-check";
      let label = "Safe";

      if (score >= 7.0) {
        tierClass = "fraud";
        icon = "fa-triangle-exclamation";
        label = "High Risk";
      } else if (score >= 4.0) {
        tierClass = "review";
        icon = "fa-eye";
        label = "Review";
      }

      return `
        <div class="risk-score-cell">
          <span class="risk-pill ${tierClass}">
            <i class="fa-solid ${icon}"></i> ${score.toFixed(1)}
          </span>
        </div>
      `;
    }
  },
  {
    headerName: "Status",
    field: "status",
    width: 190,
    filter: "agSetColumnFilter",
    cellRenderer: (params) => {
      const val = params.value || "Approved";
      let badgeClass = "approved";
      let icon = "fa-check";

      if (val.includes("Refunded")) {
        badgeClass = "refunded";
        icon = "fa-rotate-left";
      } else if (val.includes("Locked")) {
        badgeClass = "locked";
        icon = "fa-lock";
      } else if (val.includes("Review")) {
        badgeClass = "review";
        icon = "fa-clock";
      }

      return `
        <div class="status-cell">
          <span class="status-badge ${badgeClass}">
            <i class="fa-solid ${icon}"></i> ${val}
          </span>
        </div>
      `;
    }
  },
  {
    headerName: "Case File",
    field: "id",
    width: 130,
    sortable: false,
    filter: false,
    cellRenderer: (params) => {
      return `
        <button class="grid-action-btn" onclick="openCaseFileById('${params.value}')">
          <i class="fa-solid fa-file-magnifying-glass"></i> Inspect
        </button>
      `;
    }
  }
];

// AG Grid Options (Enterprise Mode)
const gridOptions = {
  columnDefs: columnDefs,
  rowData: rowDataStore,
  defaultColDef: {
    flex: 1,
    minWidth: 110,
    resizable: true,
    sortable: true,
    filter: true,
    enableRowGroup: true,
    enableValue: true
  },
  enableRangeSelection: true,
  rowGroupPanelShow: "always",
  sideBar: {
    toolPanels: ["columns", "filters"],
    defaultToolPanel: ""
  },
  statusBar: {
    statusPanels: [
      { statusPanel: "agTotalRowCountComponent", align: "left" },
      { statusPanel: "agFilteredRowCountComponent", align: "left" },
      { statusPanel: "agSelectedRowCountComponent", align: "left" }
    ]
  },
  animateRows: true,
  rowSelection: "single",
  rowHeight: 52,
  headerHeight: 46,
  pagination: true,
  paginationPageSize: 10,
  onRowClicked: (event) => {
    // Open case modal on row click
    if (event.data) {
      openCaseFile(event.data);
    }
  }
};

/* --------------------------------------------------------------------------
   Initialization
   -------------------------------------------------------------------------- */
document.addEventListener("DOMContentLoaded", () => {
  const gridDiv = document.querySelector("#transactionsGrid");
  
  // Initialize AG Grid
  gridApi = agGrid.createGrid(gridDiv, gridOptions);

  // Setup Event Listeners & Real-Time Backend Connection
  setupEventListeners();
  updateKpiDisplay();
  initSSEConnection();
  logTerminal("AegisPay AG Grid Real-Time Dashboard connected.", "system");
});

/* --------------------------------------------------------------------------
   Real-Time Backend SSE Stream & Connection
   -------------------------------------------------------------------------- */
const BACKEND_URL = "http://localhost:8085";
let sseConnection = null;
let isSentinelRunning = false;
let sentinelInterval = null;

function initSSEConnection() {
  const statusTag = document.getElementById("backendStatusTag");
  const statusText = document.getElementById("backendStatusText");

  try {
    sseConnection = new EventSource(`${BACKEND_URL}/events/stream`);

    sseConnection.onopen = () => {
      if (statusTag) statusTag.classList.remove("offline");
      if (statusText) statusText.innerText = "Backend Live (Port 8085)";
      logTerminal("[SYSTEM] Connected to live AegisPay Multi-Agent SSE stream.", "system");
    };

    sseConnection.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data);
        handleIncomingBackendEvent(payload);
      } catch (err) {
        console.error("Error parsing SSE event data:", err);
      }
    };

    sseConnection.onerror = () => {
      if (statusTag) statusTag.classList.add("offline");
      if (statusText) statusText.innerText = "Backend Offline (Local Mode)";
    };
  } catch (err) {
    if (statusTag) statusTag.classList.add("offline");
    if (statusText) statusText.innerText = "Backend Offline (Local Mode)";
  }
}

function handleIncomingBackendEvent(data) {
  const orderId = data.order_id || `5O${Math.floor(100000 + Math.random() * 900000)}`;
  const riskScore = parseFloat(data.risk_score || 0.0);
  const shouldActuate = !!data.should_actuate;
  const analysis = data.investigation_result?.fraud_analysis || {};
  const txData = data.transaction_data || {};
  const purchaseUnits = txData.purchase_units || [{}];
  const rawAmt = purchaseUnits[0]?.amount?.value || txData.amount || 150.00;
  const amount = parseFloat(rawAmt);
  const payer = txData.payer || {};
  const customerName = payer.name ? `${payer.name.given_name || ''} ${payer.name.surname || ''}`.trim() || "PayPal Customer" : "PayPal Customer";
  const email = payer.email_address || "buyer@sandbox.paypal.com";
  const payerId = payer.payer_id || `PAYER-${Math.floor(100000 + Math.random() * 900000)}`;
  const item = purchaseUnits[0]?.items?.[0]?.name || "Retail Merchandise";
  const location = purchaseUnits[0]?.shipping?.address ? `${purchaseUnits[0].shipping.address.admin_area_2 || ''}, ${purchaseUnits[0].shipping.address.country_code || 'US'}` : "PayPal Verified";
  
  let status = "Approved";
  if (shouldActuate) {
    status = data.actuator_result?.action === "void_authorization" ? "Voided (PayPal)" : "Auto-Refunded (PayPal)";
  } else if (riskScore >= 4.0) {
    status = "Under Review";
  }

  // Log steps to terminal
  logTerminal(`[PayPal Stream] Ingested order ${orderId} (${customerName}, $${amount.toFixed(2)} USD).`, "monitor");
  setTimeout(() => {
    logTerminal(`[Orchestrator] Dispatched to InvestigationAgent. Gemini 2.5 Flash Risk Score: ${riskScore.toFixed(1)}/10.0.`, "investigation");
  }, 300);

  if (shouldActuate) {
    setTimeout(() => {
      logTerminal(`[ActuatorAgent] Risk >= 7.0! Executed PayPal Payments v2 ${data.actuator_result?.action || 'refund_capture'} on ${orderId}.`, "actuator");
    }, 600);
  }

  const channel3Data = data.investigation_result?.channel3_product_data || data.transaction_data?.channel3_product_data || null;
  const elasticIntel = data.investigation_result?.elastic_threat_intel || data.elastic_threat_intel || null;

  const row = {
    id: `tx_${Date.now()}_${Math.random().toString(36).substr(2, 4)}`,
    timestamp: new Date().toLocaleTimeString(),
    orderId: orderId,
    customer: customerName,
    email: email,
    account: payerId,
    amount: amount,
    category: item,
    location: location,
    riskScore: riskScore,
    status: status,
    justification: data.justification || analysis.justification || "AegisPay swarm fraud evaluation completed.",
    factors: data.signals || analysis.signals || ["PayPal Commerce Inspection"],
    channel3: channel3Data,
    elasticIntel: elasticIntel,
    rawJson: data
  };

  // Update KPI Metrics
  kpiState.totalVolume += amount;
  kpiState.totalTransactions += 1;
  if (shouldActuate) {
    kpiState.fraudIntercepted += amount;
    kpiState.attacksCount += 1;
  }
  updateKpiDisplay();

  // Apply row to AG Grid table with live animation
  if (gridApi) {
    gridApi.applyTransaction({ add: [row], addIndex: 0 });
  }

  // Stream into Bryntum Scheduler Timeline
  if (typeof window.addDisputeToBryntumScheduler === 'function') {
    window.addDisputeToBryntumScheduler(orderId, amount, riskScore, status, data.justification || "");
  }
}

async function triggerBackendScenario(scenarioName, fallbackFn) {
  try {
    const res = await fetch(`${BACKEND_URL}/simulate-scenario/${scenarioName}`, { method: "POST" });
    if (!res.ok) {
      throw new Error(`HTTP ${res.status}`);
    }
    // Event will arrive via SSE stream automatically!
  } catch (err) {
    console.warn(`Backend call failed (${err.message}), using client-side fallback.`);
    if (fallbackFn) fallbackFn();
  }
}

/* --------------------------------------------------------------------------
   Event Listeners & Controls
   -------------------------------------------------------------------------- */
function setupEventListeners() {
  // View Switcher Tabs (AG Grid vs. Bryntum Scheduler)
  const gridTabBtn = document.getElementById("viewGridTabBtn");
  const schedTabBtn = document.getElementById("viewSchedulerTabBtn");
  const gridSection = document.getElementById("gridTableSection");
  const schedSection = document.getElementById("bryntumSchedulerSection");

  if (gridTabBtn && schedTabBtn) {
    gridTabBtn.addEventListener("click", () => {
      gridTabBtn.classList.add("active");
      schedTabBtn.classList.remove("active");
      gridSection.classList.remove("hidden");
      schedSection.classList.add("hidden");
      if (gridApi) gridApi.sizeColumnsToFit();
      logTerminal("Switched to AG Grid Real-Time Surveillance view.", "system");
    });

    schedTabBtn.addEventListener("click", () => {
      schedTabBtn.classList.add("active");
      gridTabBtn.classList.remove("active");
      schedSection.classList.remove("hidden");
      gridSection.classList.add("hidden");
      if (window.bryntumScheduler && window.bryntumScheduler.refresh) {
        setTimeout(() => {
          window.bryntumScheduler.refresh();
        }, 80);
      }
      logTerminal("Switched to Bryntum Dispute Triage & Deadline Horizon view.", "system");
    });
  }

  // Quick Filter Input
  const quickFilter = document.getElementById("quickFilterInput");
  quickFilter.addEventListener("input", (e) => {
    if (gridApi) {
      gridApi.setGridOption("quickFilterText", e.target.value);
    }
  });

  // Export CSV Button
  document.getElementById("exportCsvBtn").addEventListener("click", () => {
    if (gridApi) {
      gridApi.exportDataAsCsv({
        fileName: `AegisPay_Fraud_Surveillance_${new Date().toISOString().slice(0, 10)}.csv`
      });
      logTerminal("AG Grid transaction surveillance data exported to CSV.", "system");
    }
  });

  // Scenario Buttons (Connected to live backend)
  document.getElementById("simNormalBtn").addEventListener("click", () => {
    triggerBackendScenario("legitimate_order", () => {
      simulateTransaction("Sarah Taylor", 45.00, "Online Bookstore", "Safe Grocery Purchase", 1.2, "Approved");
    });
  });

  document.getElementById("simMediumBtn").addEventListener("click", () => {
    triggerBackendScenario("chargeback_exploit", () => {
      simulateTransaction("Robert Garcia", 899.00, "Electronics & Laptops", "High-Value Laptop", 5.6, "Under Review");
    });
  });

  document.getElementById("simFraudBtn").addEventListener("click", () => {
    triggerBackendScenario("account_takeover", () => {
      simulateTransaction("Phantom Buyer 0x99", 3499.00, "Apple MacBook Pro 16", "Compromised Account Takeover", 9.4, "Auto-Refunded (PayPal)");
    });
  });

  const simTamperBtn = document.getElementById("simTamperBtn");
  if (simTamperBtn) {
    simTamperBtn.addEventListener("click", () => {
      triggerBackendScenario("price_tampering", () => {
        simulatePriceTamperingFallback();
      });
    });
  }

  document.getElementById("simVelocityBtn").addEventListener("click", () => {
    triggerBackendScenario("card_testing_bot", () => {
      simulateVelocityBurst();
    });
  });

  // Live Stream Sentinel Toggle Button
  const toggleSentinelBtn = document.getElementById("toggleSentinelBtn");
  const sentinelBtnText = document.getElementById("sentinelBtnText");
  if (toggleSentinelBtn) {
    toggleSentinelBtn.addEventListener("click", () => {
      isSentinelRunning = !isSentinelRunning;
      if (isSentinelRunning) {
        sentinelBtnText.innerText = "Stop Live Stream";
        toggleSentinelBtn.classList.remove("btn-outline-primary");
        toggleSentinelBtn.classList.add("btn-outline-danger");
        logTerminal("[SENTINEL] Live commerce stream activated (6s intervals).", "monitor");
        sentinelInterval = setInterval(() => {
          const scenarios = ["legitimate_order", "legitimate_order", "account_takeover", "card_testing_bot"];
          const pick = scenarios[Math.floor(Math.random() * scenarios.length)];
          triggerBackendScenario(pick);
        }, 6000);
      } else {
        sentinelBtnText.innerText = "Start Live Stream";
        toggleSentinelBtn.classList.remove("btn-outline-danger");
        toggleSentinelBtn.classList.add("btn-outline-primary");
        if (sentinelInterval) clearInterval(sentinelInterval);
        logTerminal("[SENTINEL] Live commerce stream paused.", "system");
      }
    });
  }

  // Custom Simulation Modal Controls
  const customModal = document.getElementById("customSimModal");
  document.getElementById("openSimulateModalBtn").addEventListener("click", () => {
    customModal.classList.remove("hidden");
  });

  document.getElementById("closeSimModalBtn").addEventListener("click", () => {
    customModal.classList.add("hidden");
  });

  document.getElementById("cancelSimModalBtn").addEventListener("click", () => {
    customModal.classList.add("hidden");
  });

  document.getElementById("customTxForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    const name = document.getElementById("custName").value;
    const amount = parseFloat(document.getElementById("custAmount").value);
    const category = document.getElementById("custItem").value;
    const location = document.getElementById("custLocation").value;

    const customPayload = {
      id: `5O${Math.floor(100000 + Math.random() * 900000)}TN${Math.floor(100000 + Math.random() * 900000)}`,
      intent: amount >= 3000 ? "CAPTURE" : "AUTHORIZE",
      amount: amount,
      payer: {
        email_address: document.getElementById("custAccount").value,
        name: { given_name: name.split(" ")[0] || "Custom", surname: name.split(" ")[1] || "Buyer" }
      },
      purchase_units: [
        {
          amount: { value: amount.toFixed(2), currency_code: "USD" },
          items: [{ name: category, quantity: "1", unit_amount: { value: amount.toFixed(2), currency_code: "USD" } }],
          shipping: { address: { admin_area_2: location, country_code: location.toLowerCase().includes("romania") ? "RO" : "US" } }
        }
      ]
    };

    try {
      await fetch(`${BACKEND_URL}/process-transaction`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(customPayload)
      });
    } catch (err) {
      simulateTransaction(name, amount, category, `Custom transaction from ${location}`, amount > 2000 ? 8.8 : 2.1, amount > 2000 ? "Auto-Refunded (PayPal)" : "Approved");
    }
    customModal.classList.add("hidden");
  });

  // Case File Modal Controls
  document.getElementById("closeModalBtn").addEventListener("click", closeCaseFileModal);
  document.getElementById("modalActionDismissBtn").addEventListener("click", closeCaseFileModal);

  document.getElementById("modalActionRefundBtn").addEventListener("click", () => {
    alert("PayPal API Invocation: POST /v2/payments/captures/refund executed successfully. Transaction marked as refunded.");
    closeCaseFileModal();
  });

  document.getElementById("modalActionLockBtn").addEventListener("click", () => {
    alert("AegisPay Actuator: Payment authorization voided on PayPal.");
    closeCaseFileModal();
  });

  document.getElementById("clearLogsBtn").addEventListener("click", () => {
    document.getElementById("terminalLogs").innerHTML = "";
  });

  document.getElementById("copyJsonBtn").addEventListener("click", () => {
    const jsonText = document.getElementById("modalRawJson").textContent;
    navigator.clipboard.writeText(jsonText).then(() => {
      alert("Case File JSON copied to clipboard!");
    });
  });
}

/* --------------------------------------------------------------------------
   Simulated Transaction Pipeline (Fallback)
   -------------------------------------------------------------------------- */
function simulateTransaction(customerName, amount, category, description, riskScore, status) {
  const orderNum = Math.floor(1000 + Math.random() * 9000);
  const now = new Date();
  const timeStr = now.toTimeString().split(" ")[0];
  const txId = `tx_${Date.now()}`;

  logTerminal(`[PayPal Webhook] Ingested order #PP-2026-${orderNum} for ${customerName} ($${amount.toFixed(2)} USD).`, "monitor");

  setTimeout(() => {
    logTerminal(`[Orchestrator] Evaluated #PP-2026-${orderNum}. Dispatching A2A task to InvestigationAgent.`, "orchestrator");
  }, 400);

  setTimeout(() => {
    logTerminal(`[InvestigationAgent] Gemini 2.5 Flash reasoned: Score ${riskScore}/10.0. Factors: ${category}.`, "investigation");
  }, 900);

  setTimeout(() => {
    if (riskScore >= 7.0) {
      logTerminal(`[ActuatorAgent] RISK >= 7.0 TRIGGERED! Executed PayPal Payments v2 Refund on order #PP-2026-${orderNum}.`, "actuator");
      kpiState.fraudIntercepted += amount;
      kpiState.attacksCount += 1;
    }

    let simElastic = null;
    if (riskScore >= 8.5) {
      simElastic = {
        incident_id: "ATK-8812",
        title: "Account Takeover with Foreign Tor Proxy",
        similarity_pct: 98.4,
        description: "High-velocity syndicate using Romanian & Dutch Tor exit nodes to purchase high-value hardware with 400% spending spikes.",
        matched_indicators: ["Tor Exit Node", "Cross-border Proxy", "Velocity Surge", "400% Amount Spike"],
        historical_resolution: "Auto-Refunded via PayPal Payments v2 refund_capture",
        esql_signature: "FROM aegispay_threat_intel | WHERE amount > 3000 AND location LIKE '%Romania%'"
      };
    } else if (riskScore >= 5.0) {
      simElastic = {
        incident_id: "CHG-5520",
        title: "Friendly Fraud & Repeat Chargeback Abuse",
        similarity_pct: 92.1,
        description: "Serial disputer with previous chargeback claims despite carrier signature validation.",
        matched_indicators: ["Dispute History Spike", "Excessive Claim Frequency", "High Value Physical Goods"],
        historical_resolution: "Flagged for Human Review & PayPal Dispute Evidence Filing",
        esql_signature: "FROM aegispay_threat_intel | WHERE amount > 800 AND risk_score > 5.0"
      };
    } else {
      simElastic = {
        incident_id: "SAFE-1001",
        title: "Verified Legitimate Residential Purchase",
        similarity_pct: 97.8,
        description: "Verified residential purchase matching 3-year account tenure and 3D-Secure authentication.",
        matched_indicators: ["Verified Buyer", "Normal Spending", "3DS Authenticated", "Seller Protection Eligible"],
        historical_resolution: "Auto-Approved without friction",
        esql_signature: "FROM aegispay_threat_intel | WHERE risk_score < 3.0"
      };
    }

    const newTx = {
      id: txId,
      timestamp: timeStr,
      orderId: `PP-2026-${orderNum}`,
      customer: customerName,
      email: `${customerName.toLowerCase().replace(/[^a-z]/g, "")}@sandbox.com`,
      account: `ACCT-US-${Math.floor(100000 + Math.random() * 900000)}`,
      amount: amount,
      category: category,
      location: "San Jose, CA (IP: 198.51.100.24)",
      riskScore: riskScore,
      status: status,
      justification: `Gemini 2.5 Assessment: ${description}. Evaluated against Elasticsearch threat memory. Risk grade: ${riskScore >= 7 ? "CRITICAL FRAUD" : "VERIFIED SAFE"}.`,
      factors: riskScore >= 7.0 ? ["Velocity Spike", "Geo Anomaly", "Unusual Item Category"] : ["Verified Buyer", "Normal Spending"],
      elasticIntel: simElastic,
      rawJson: {
        event_type: riskScore >= 7.0 ? "CHECKOUT.ORDER.VOIDED" : "PAYMENT.CAPTURE.COMPLETED",
        order_id: `PP-2026-${orderNum}`,
        amount: `${amount.toFixed(2)} USD`,
        agent_reasoning: {
          model: "gemini-2.5-flash",
          score: riskScore,
          verdict: status
        },
        elastic_threat_intel: simElastic
      }
    };

    kpiState.totalVolume += amount;
    kpiState.totalTransactions += 1;
    updateKpiDisplay();

    // Insert into AG Grid at top (index 0) with live row animation!
    if (gridApi) {
      gridApi.applyTransaction({ add: [newTx], addIndex: 0 });
    }

    // Stream into Bryntum Scheduler Timeline
    if (typeof window.addDisputeToBryntumScheduler === 'function') {
      window.addDisputeToBryntumScheduler(orderNum, amount, riskScore, status, description);
    }
  }, 1300);
}

function simulateVelocityBurst() {
  logTerminal(`[SIMULATION ALERT] Triggering high-frequency velocity burst across 3 consecutive orders!`, "actuator");
  simulateTransaction("AttackerBot_Session_A", 1850.00, "Digital Gift Cards", "Rapid order 1 of 3", 8.9, "Auto-Refunded (PayPal)");
  setTimeout(() => {
    simulateTransaction("AttackerBot_Session_B", 2400.00, "Digital Gift Cards", "Rapid order 2 of 3 (Same device ID)", 9.3, "Auto-Refunded (PayPal)");
  }, 600);
  setTimeout(() => {
    simulateTransaction("AttackerBot_Session_C", 3100.00, "Digital Gift Cards", "Rapid order 3 of 3 (Account blocked)", 9.8, "Account Locked");
  }, 1200);
}

function simulatePriceTamperingFallback() {
  logTerminal(`[Channel3 API] Querying normalized catalog (100M+ products across 25,000+ retailers)...`, "monitor");
  setTimeout(() => {
    logTerminal(`[InvestigationAgent] Target item 'Apple MacBook Pro 16' has Fair Market Value of $3,499.00.`, "investigation");
  }, 400);
  setTimeout(() => {
    logTerminal(`[Channel3 FMV] ALERT! Cart price slashed to $149.00 (-95.7% variance)! DOM Price Tampering detected!`, "actuator");
  }, 800);
  setTimeout(() => {
    logTerminal(`[ActuatorAgent] Risk 9.8/10 CRITICAL! Executed PayPal Payments v2 refund_capture to prevent merchant loss.`, "actuator");
  }, 1200);

  const orderNum = Math.floor(1000 + Math.random() * 9000);
  const txId = `tx_${Date.now()}`;
  const newTx = {
    id: txId,
    timestamp: new Date().toTimeString().split(" ")[0],
    orderId: `PP-2026-${orderNum}`,
    customer: "TamperBot Session_X",
    email: "exploit_user@darknet-market.org",
    account: "ACCT-US-918231",
    amount: 149.00,
    category: "Apple MacBook Pro 16",
    location: "Miami, FL, US",
    riskScore: 9.8,
    status: "Auto-Refunded (PayPal)",
    justification: "Channel3 Product Intelligence Alert: Cart Price Tampering detected! Order charged $149.00 for 'Apple MacBook Pro 16-inch M3 Max' (Verified Market Value: $3,499.00, Variance: -95.7%). Immediate PayPal Payments v2 refund_capture executed.",
    factors: ["CHANNEL3_PRICE_TAMPERING", "Cart Slashing (-95.7%)", "Severe FMV Discrepancy"],
    channel3: {
      item_queried: "Apple MacBook Pro 16",
      verified_title: "Apple MacBook Pro 16-inch M3 Max 36GB RAM 1TB SSD",
      brand: "Apple",
      retailer: "Best Buy",
      market_price: 3499.00,
      order_price: 149.00,
      variance_pct: -95.7,
      is_tampered: true,
      anomaly_type: "CART_PRICE_SLASHING_DETECTED",
      image_url: "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=400&q=80",
      channel3_verified: true
    },
    elasticIntel: {
      incident_id: "EXP-9102",
      title: "Client-Side Cart Price Tampering / Slashing",
      similarity_pct: 99.2,
      description: "Exploit injecting client-side DOM price manipulations, reducing $3,499.00 electronics to $149.00 prior to PayPal token creation.",
      matched_indicators: ["CHANNEL3_PRICE_TAMPERING", "Cart Slashing (-95.7%)", "DOM Manipulation", "Severe FMV Discrepancy"],
      historical_resolution: "Auto-Refunded via PayPal Payments v2 refund_capture",
      esql_signature: "FROM aegispay_threat_intel | WHERE amount > 3000 AND location LIKE '%Miami%'"
    },
    rawJson: {
      event_type: "PAYMENT.CAPTURE.REFUNDED",
      order_id: `PP-2026-${orderNum}`,
      amount: "149.00 USD",
      channel3_product_data: {
        verified_title: "Apple MacBook Pro 16-inch M3 Max",
        market_price: 3499.00,
        cart_price: 149.00,
        variance: "-95.7%"
      },
      elastic_threat_intel: {
        incident_id: "EXP-9102",
        title: "Client-Side Cart Price Tampering / Slashing",
        similarity_pct: 99.2
      }
    }
  };

  kpiState.totalVolume += 149.00;
  kpiState.totalTransactions += 1;
  kpiState.fraudIntercepted += 3499.00;
  kpiState.attacksCount += 1;
  updateKpiDisplay();

  if (gridApi) {
    gridApi.applyTransaction({ add: [newTx], addIndex: 0 });
  }
  if (typeof window.addDisputeToBryntumScheduler === 'function') {
    window.addDisputeToBryntumScheduler(orderNum, 149.00, 9.8, "Auto-Refunded (PayPal)", "Channel3 Price Slashing (-95.7%)");
  }
}

/* --------------------------------------------------------------------------
   UI Helpers & Case File Modal
   -------------------------------------------------------------------------- */
function updateKpiDisplay() {
  const volFormatted = new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(kpiState.totalVolume);
  const fraudFormatted = new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(kpiState.fraudIntercepted);

  document.getElementById("totalVolume").innerText = volFormatted;
  document.getElementById("totalTransactions").innerText = kpiState.totalTransactions.toLocaleString();
  document.getElementById("fraudIntercepted").innerText = fraudFormatted;
}

function logTerminal(message, type = "system") {
  const terminal = document.getElementById("terminalLogs");
  const time = new Date().toTimeString().split(" ")[0];
  const div = document.createElement("div");
  div.className = `log-entry ${type}`;
  div.innerHTML = `<span class="timestamp">[${time}]</span> ${message}`;
  terminal.appendChild(div);
  terminal.scrollTop = terminal.scrollHeight;
}

// Global modal opener for inline buttons
window.openCaseFileById = function(txId) {
  let targetRow;
  if (gridApi) {
    gridApi.forEachNode((node) => {
      if (node.data.id === txId) {
        targetRow = node.data;
      }
    });
  }
  if (targetRow) {
    openCaseFile(targetRow);
  }
};

function openCaseFile(tx) {
  document.getElementById("modalOrderId").innerText = `Order #${tx.orderId}`;
  document.getElementById("modalCustomerName").innerText = tx.customer;
  document.getElementById("modalAccountId").innerText = tx.account;
  document.getElementById("modalAmount").innerText = new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(tx.amount);
  document.getElementById("modalStatus").innerText = tx.status;
  document.getElementById("modalJustification").innerText = tx.justification;

  const scoreEl = document.getElementById("scoreValue");
  const scoreCategoryEl = document.getElementById("scoreCategory");
  const dial = document.getElementById("scoreDial");

  scoreEl.innerText = tx.riskScore.toFixed(1);

  if (tx.riskScore >= 7.0) {
    scoreCategoryEl.innerText = "High-Risk Fraud";
    scoreCategoryEl.className = "score-category-tag danger";
    dial.style.borderColor = "#EF4444";
    dial.style.background = "rgba(239, 68, 68, 0.2)";
  } else if (tx.riskScore >= 4.0) {
    scoreCategoryEl.innerText = "Medium Review";
    scoreCategoryEl.className = "score-category-tag review";
    dial.style.borderColor = "#F59E0B";
    dial.style.background = "rgba(245, 158, 11, 0.2)";
  } else {
    scoreCategoryEl.innerText = "Safe Verified";
    scoreCategoryEl.className = "score-category-tag safe";
    dial.style.borderColor = "#10B981";
    dial.style.background = "rgba(16, 185, 129, 0.2)";
  }

  // Channel3 Product Intelligence Section
  const ch3Section = document.getElementById("channel3FmvSection");
  const ch3Data = tx.channel3 || tx.rawJson?.investigation_result?.channel3_product_data || tx.rawJson?.channel3_product_data;
  if (ch3Section) {
    if (ch3Data && (ch3Data.is_tampered || ch3Data.channel3_verified || ch3Data.market_price)) {
      ch3Section.classList.remove("hidden");
      document.getElementById("ch3ProductTitle").innerText = ch3Data.verified_title || ch3Data.item_queried || "Verified Product";
      document.getElementById("ch3Brand").innerText = ch3Data.brand || "Verified Manufacturer";
      document.getElementById("ch3Retailer").innerText = ch3Data.retailer || "Retail Network (25k+ stores)";
      document.getElementById("ch3CartPrice").innerText = `$${parseFloat(ch3Data.order_price || tx.amount).toFixed(2)}`;
      document.getElementById("ch3MarketPrice").innerText = `$${parseFloat(ch3Data.market_price || 0).toFixed(2)}`;
      document.getElementById("ch3Variance").innerText = `${ch3Data.variance_pct || 0}%`;
      const imgEl = document.getElementById("ch3ProductImage");
      if (imgEl && ch3Data.image_url) {
        imgEl.src = ch3Data.image_url;
      }
      const badgeEl = document.getElementById("ch3TamperBadge");
      if (badgeEl) {
        if (ch3Data.is_tampered) {
          badgeEl.className = "tamper-alert-pill danger";
          badgeEl.innerHTML = '<i class="fa-solid fa-triangle-exclamation"></i> Price Slashing Detected';
        } else {
          badgeEl.className = "tamper-alert-pill safe";
          badgeEl.innerHTML = '<i class="fa-solid fa-circle-check"></i> Fair Market Value Verified';
        }
      }
    } else {
      ch3Section.classList.add("hidden");
    }
  }

  // Elasticsearch Threat Intelligence Section
  const elasticSection = document.getElementById("elasticThreatSection");
  const elData = tx.elasticIntel || tx.rawJson?.investigation_result?.elastic_threat_intel || tx.rawJson?.elastic_threat_intel;
  if (elasticSection) {
    if (elData && elData.incident_id) {
      elasticSection.classList.remove("hidden");
      document.getElementById("elasticIncidentId").innerText = `#${elData.incident_id}`;
      document.getElementById("elasticIncidentName").innerText = elData.title || "Known Threat Pattern";
      document.getElementById("elasticSimPct").innerText = `${elData.similarity_pct || 98.4}%`;
      document.getElementById("elasticIncidentDesc").innerText = elData.description || "Historical fraud signature retrieved from Elasticsearch serverless cluster.";
      
      const indGrid = document.getElementById("elasticIndicatorsGrid");
      if (indGrid) {
        indGrid.innerHTML = "";
        (elData.matched_indicators || []).forEach(ind => {
          const pill = document.createElement("span");
          pill.className = "elastic-ind-pill";
          pill.innerHTML = `<i class="fa-solid fa-tag"></i> ${ind}`;
          indGrid.appendChild(pill);
        });
      }

      const esqlEl = document.getElementById("elasticEsqlQuery");
      if (esqlEl) {
        esqlEl.innerText = elData.esql_signature || `FROM aegispay_threat_intel | WHERE incident_id == "${elData.incident_id}"`;
      }

      const matchBadge = document.getElementById("elasticMatchBadge");
      if (matchBadge) {
        if (tx.riskScore >= 7.0) {
          matchBadge.className = "elastic-match-pill danger";
        } else {
          matchBadge.className = "elastic-match-pill safe";
        }
      }
    } else {
      elasticSection.classList.add("hidden");
    }
  }

  // Factor pills
  const factorsContainer = document.getElementById("modalFactorsList");
  factorsContainer.innerHTML = "";
  (tx.factors || []).forEach(f => {
    const pill = document.createElement("span");
    pill.className = `factor-pill ${tx.riskScore >= 7.0 ? 'danger' : 'safe'}`;
    pill.innerHTML = `<i class="fa-solid fa-tag"></i> ${f}`;
    factorsContainer.appendChild(pill);
  });

  // Raw JSON
  document.getElementById("modalRawJson").textContent = JSON.stringify(tx.rawJson || tx, null, 2);

  // Show drawer
  document.getElementById("caseFileDrawer").classList.remove("hidden");
}

function closeCaseFileModal() {
  document.getElementById("caseFileDrawer").classList.add("hidden");
}
